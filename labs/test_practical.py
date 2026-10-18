"""Depth checks for training, RAG evaluation, durable recovery and bounded serving."""
import json
import math
import tempfile
import unittest
from pathlib import Path
from model_comparison import MLP, Tree, fit_scaler, make_data, transform, score
from language_model import Bigram, BOS, UNK, EOS, masked_mean_nll, dpo_loss
from rag_evaluation import BM25, CORPUS, CASES, FixtureGenerator, RecordedGenerator, make_request, evaluate, validate_response
from durable_agent import DurableWorkflow, Provider, CrashAfterEffect, demo
from serving_experiment import experiment, percentile


class TrainingTests(unittest.TestCase):
    def test_every_mlp_weight_and_bias_gradient(self):
        model=MLP(width=2,l2=.03);model.initialize(2)
        rows=[([.2,-.4],1),([-.7,.3],0)]
        _,gradient=model.loss_gradient(rows)
        for index in range(len(model.params)):
            old=model.params[index];step=1e-5
            model.params[index]=old+step;plus=model.loss_gradient(rows)[0]
            model.params[index]=old-step;minus=model.loss_gradient(rows)[0]
            model.params[index]=old
            self.assertAlmostEqual(gradient[index],(plus-minus)/(2*step),places=7,msg=str(index))
    def test_mlp_actually_learns(self):
        train,_,_=make_data();train=transform(train,fit_scaler(train))
        model=MLP(width=8,steps=700).fit(train)
        self.assertLess(model.history[-1],model.history[0]-.05)
    def test_test_outlier_does_not_fit_scaler(self):
        train,_,_=make_data();scaler=fit_scaler(train)
        before=transform(train,scaler)
        transform([([1e6,-1e9],1)],scaler)
        self.assertEqual(before,transform(train,scaler))
    def test_greedy_tree_zero_gain_xor_limit(self):
        rows=[([-1,-1],0),([-1,1],1),([1,-1],1),([1,1],0)]
        tree=Tree(depth=3,min_leaf=1).fit(rows)
        self.assertEqual(tree.root.feature,-1)
        self.assertEqual(tree.predict([1,1]),.5)
    def test_tree_learns_threshold(self):
        tree=Tree(depth=1,min_leaf=1).fit([([-2],0),([-1],0),([1],1),([2],1)])
        self.assertLess(tree.predict([-1.5]),.5);self.assertGreater(tree.predict([1.5]),.5)
    def test_metrics_distinguish_confidence(self):
        self.assertGreater(score([1],[.99])['accuracy'],score([1],[.49])['accuracy'])
        self.assertLess(score([1],[.9])['log_loss'],score([1],[.6])['log_loss'])


class LanguageTests(unittest.TestCase):
    def test_conditional_probabilities_normalize(self):
        model=Bigram(.5).fit(['ab','ab','ac'])
        for previous in [BOS,'a','b',UNK]:
            self.assertAlmostEqual(sum(model.probability(previous,t) for t in model.vocabulary),1)
    def test_unknown_is_not_added_from_test(self):
        model=Bigram().fit(['ab']);vocabulary=model.vocabulary[:]
        self.assertEqual(model.evaluate(['z'])['unknown_tokens'],1)
        self.assertEqual(model.vocabulary,vocabulary)
        self.assertNotIn('z',model.vocabulary)
    def test_trained_counts_and_sampling(self):
        model=Bigram(.1).fit(['ab']*10)
        self.assertGreater(model.probability('a','b'),model.probability('a','a'))
        self.assertEqual(model.sample(seed=3),model.sample(seed=3))
    def test_dpo_extreme_probabilities_are_stable(self):
        self.assertAlmostEqual(dpo_loss(.5,.5,1e-320,1e-320),math.log(2))
        self.assertTrue(math.isfinite(dpo_loss(1e-320,.5,.5,1e-320)))
        with self.assertRaises(ValueError):dpo_loss(.5,.5,.5,.5,beta=0)
    def test_sft_mask_removes_prompt_loss(self):
        self.assertAlmostEqual(masked_mean_nll([.001,.8,.7],[False,True,True]),-(math.log(.8)+math.log(.7))/2)
        with self.assertRaises(ValueError):masked_mean_nll([.5],[False])
    def test_dpo_reference_and_preference(self):
        self.assertAlmostEqual(dpo_loss(.5,.5,.5,.5),math.log(2))
        self.assertLess(dpo_loss(.8,.2,.5,.5),math.log(2))


class RAGTests(unittest.TestCase):
    def test_bm25_length_and_frequency(self):
        docs=[{'id':'a','text':'term term extra'}, {'id':'b','text':'term other'}]
        self.assertEqual(BM25(docs).search('term')[0]['id'],'a')
        self.assertEqual(BM25(docs).search('unseen'),[])
        self.assertEqual(BM25(docs).search(''),[])
        self.assertEqual(BM25([]).search('term'),[])
    def test_acl_before_corpus_statistics(self):
        request,_=make_request(CASES[2],CORPUS)
        self.assertEqual(request['context'],[])
    def test_fixture_failures_separated(self):
        rows={r['case_id']:r for r in evaluate(FixtureGenerator())['cases']}
        self.assertTrue(rows['paraphrase-miss']['retrieval_miss'])
        self.assertFalse(rows['hours']['retrieval_miss'])
        self.assertFalse(rows['hours']['claims'][1]['supported'])
        self.assertFalse(rows['wrong-citation']['claims'][0]['supported'])
        self.assertTrue(rows['unknown']['end_to_end_success'])
    def test_wrong_but_supported_answer_not_correct(self):
        # Even truthful claims do not answer a question if required facts are missing.
        class EmptyGenerator(FixtureGenerator):
            def generate(self,request,digest):return {'abstain':False,'claims':[]}
        self.assertFalse(evaluate(EmptyGenerator())['cases'][0]['end_to_end_success'])
    def test_recorded_response_context_binding(self):
        request,digest=make_request(CASES[0],CORPUS)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'responses.json'
            data={'metadata':{'kind':'recorded-real-model','model_id':'test-double-only',
                  'runtime_version':'unit-test','recorded_at':'test'},
                  'outputs':{'reset':{'request_sha256':digest,'response':{'abstain':True,'claims':[]}}}}
            path.write_text(json.dumps(data));adapter=RecordedGenerator(path)
            self.assertTrue(adapter.generate(request,digest)['abstain'])
            with self.assertRaises(ValueError):adapter.generate(request,'different-context')
    def test_schema_conflict_rejected(self):
        with self.assertRaises(ValueError):validate_response({'abstain':True,'claims':[{'text':'x','sources':['A']}]})


class DurableTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory();root=Path(self.directory.name)
        self.local=root/'local.sqlite';self.remote=root/'provider.sqlite'
        self.provider=Provider(self.remote);self.flow=DurableWorkflow(self.local,self.provider,max_attempts=1)
    def tearDown(self):self.directory.cleanup()
    def submit(self):self.flow.submit('blue','op','draft_ticket',{'incident_id':'42'})
    def test_process_crash_after_effect_before_ack(self):
        report=demo()
        self.assertEqual(report['crash_process_exit'],73)
        self.assertEqual(report['state_after_crash'],'RUNNING')
        self.assertEqual(report['state_after_recovery'],'SUCCEEDED')
        self.assertEqual(report['provider_effect_count'],1)
    def test_payload_binding_and_reopen(self):
        self.submit()
        with self.assertRaises(ValueError):self.flow.submit('blue','op','draft_ticket',{'incident_id':'43'})
        with self.assertRaises(CrashAfterEffect):self.flow.run('blue','op',crash=True)
        reopened=DurableWorkflow(self.local,Provider(self.remote),max_attempts=100)
        reopened.run('blue','op');reopened.run('blue','op')
        self.assertEqual(self.provider.count(),1)
        self.assertEqual(reopened.status('blue','op')['max_attempts'],1)
    def test_failed_dispatch_budget_is_durable(self):
        self.submit()
        class FailingProvider:
            def status(self,*args):return None
            def apply(self,*args):raise TimeoutError('simulated failure before effect')
        failure=DurableWorkflow(self.local,FailingProvider(),max_attempts=100)
        with self.assertRaises(TimeoutError):failure.run('blue','op')
        failure=DurableWorkflow(self.local,FailingProvider(),max_attempts=100)
        with self.assertRaises(RuntimeError):failure.run('blue','op')
        self.assertEqual(failure.status('blue','op')['state'],'STOPPED')
    def test_provider_atomic_idempotency(self):
        self.submit();payload=self.flow.status('blue','op')['payload']
        self.assertEqual(self.provider.apply('blue','op',payload),self.provider.apply('blue','op',payload))
        self.assertEqual(self.provider.count(),1)
        with self.assertRaises(ValueError):self.provider.apply('blue','op',payload+' ')
    def test_memory_tenant_expiry_verification_and_source_delete(self):
        for tenant,verified in [('blue',True),('red',True)]:
            self.flow.remember(tenant,'m','observed','source1','owner',200,verified=verified)
        self.flow.remember('blue','hypothesis','generated guess','source2','owner',200,verified=False)
        self.assertEqual(len(self.flow.recall('blue',100)),1)
        self.assertEqual(self.flow.recall('blue',200),[])
        self.flow.delete_source('blue','source1')
        self.assertEqual(self.flow.recall('blue',100),[])
        self.assertEqual(len(self.flow.recall('red',100)),1)


class ServingTests(unittest.TestCase):
    def test_percentile_convention(self):
        self.assertEqual(percentile([4,1,3,2],.5),2)
        self.assertEqual(percentile([4,1,3,2],.99),4)
    def test_bounded_accounting_without_timing_threshold(self):
        result=experiment('unit',count=20,interval=.0001,workers=1,capacity=2,fixed_seconds=.001,per_item_seconds=0)
        self.assertEqual(result['offered'],result['completed']+result['rejected'])
        self.assertLessEqual(result['max_observed_queue_depth'],2)
        self.assertEqual(result['end_to_end']['n'],result['completed'])
        self.assertGreaterEqual(result['end_to_end']['mean_ms'],result['service']['mean_ms'])



class RepresentationTests(unittest.TestCase):
    def test_pca_direction_and_variance(self):
        from representations import principal_direction
        mean,direction,eigenvalue=principal_direction([[-2.,0.],[-1.,0.],[1.,0.],[2.,0.]])
        self.assertEqual(mean,[0.,0.]);self.assertAlmostEqual(abs(direction[0]),1)
        self.assertAlmostEqual(direction[1],0);self.assertAlmostEqual(eigenvalue,2.5)
    def test_kmeans_separates_tiny_groups(self):
        from representations import kmeans
        centers,groups,inertia=kmeans([[-2.,0.],[-1.,0.],[1.,0.],[2.,0.]])
        self.assertEqual(groups,[0,0,1,1]);self.assertAlmostEqual(inertia,1)
    def test_convolution_shapes_and_values(self):
        from representations import valid_convolution
        self.assertEqual(valid_convolution([[1,2,3],[4,5,6],[7,8,9]],[[1,0],[0,-1]]),[[-4,-4],[-4,-4]])
    def test_recurrence_observes_order(self):
        from representations import recurrent_trace
        self.assertNotEqual(recurrent_trace([1.,0.])[-1],recurrent_trace([0.,1.])[-1])


class IntegrationTests(unittest.TestCase):
    def test_trained_json_artifact_retains_preprocessing(self):
        from model_comparison import Logistic, Constant, export_model, artifact_predict
        rows=[([-100.,2.],0),([100.,3.],1)]
        scaler=fit_scaler(rows);normalized=transform(rows,scaler)
        for family,model in [('logistic',Logistic(steps=20)),('constant',Constant()),('tree',Tree(depth=1,min_leaf=1)),('mlp',MLP(width=2,steps=10))]:
            model.fit(normalized);artifact=json.loads(json.dumps(export_model(model,family,scaler)))
            for (raw,_),(scaled,_) in zip(rows,normalized):
                self.assertAlmostEqual(artifact_predict(artifact,raw),model.predict(scaled))
    def test_sampling_filters_and_temperature(self):
        from language_model import decoding_distribution
        ordinary=decoding_distribution([2.,1.,0.])
        cold=decoding_distribution([2.,1.,0.],temperature=.5)
        self.assertGreater(cold[0],ordinary[0])
        filtered=decoding_distribution([2.,1.,0.],top_k=2,top_p=.8)
        self.assertEqual(filtered[2],0);self.assertAlmostEqual(sum(filtered),1)
        with self.assertRaises(ValueError):decoding_distribution([1,0],temperature=0)
    def test_typed_graph_checks_intermediate_and_terminal_access(self):
        from durable_agent import ownership_paths
        edges=[{'from':'service','to':'database','relation':'DEPENDS_ON','tenant':'blue','expires':200,'source_id':'s1'},
               {'from':'database','to':'team','relation':'OWNED_BY','tenant':'blue','expires':200,'source_id':'s2'}]
        self.assertEqual(ownership_paths('service',edges,'blue',{'service','database'},100),[])
        result=ownership_paths('service',edges,'blue',{'service','database','team'},100)
        self.assertEqual(result[0]['sources'],['s1','s2'])
        self.assertEqual(ownership_paths('service',edges,'blue',{'service','database','team'},201),[])





class EvidenceTests(unittest.TestCase):
    def test_committed_artifacts_replay_test_metrics(self):
        from model_comparison import artifact_predict
        report=json.loads((Path(__file__).resolve().parents[1]/'review/evidence/model-comparison.json').read_text())
        _,_,test=make_data()
        for family,item in report['models'].items():
            recalculated=score([y for x,y in test],[artifact_predict(item['artifact'],x) for x,y in test])
            self.assertAlmostEqual(recalculated['log_loss'],item['test']['log_loss'])
            self.assertEqual(recalculated['accuracy'],item['test']['accuracy'])
    def test_supported_but_incomplete_claim_is_not_success(self):
        class PartialGenerator(FixtureGenerator):
            def generate(self,request,digest):
                if request['case_id']=='reset':
                    return {'abstain':False,'claims':[{'text':'Office hours are nine to five on weekdays.','sources':['A']}]}
                return super().generate(request,digest)
        corpus=[{'id':'A','tenant':'blue','text':'reset password office hours',
                 'facts':['Reset account password using the settings page.','Office hours are nine to five on weekdays.']}]
        row=evaluate(PartialGenerator(),corpus)['cases'][0]
        self.assertTrue(row['claims'][0]['supported'])
        self.assertFalse(row['required_facts_complete'])
        self.assertFalse(row['end_to_end_success'])


if __name__=='__main__':unittest.main()

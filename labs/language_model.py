"""Train a smoothed character bigram language model, evaluate and sample offline.

This learns actual conditional counts, not semantic language understanding. A
single training document is intentionally insufficient for capability claims.
"""
import argparse
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path
from foundations import softmax

UNK='<UNK>'
BOS='<BOS>'
EOS='<EOS>'


class Bigram:
    def __init__(self, alpha=.5):
        if alpha<=0:raise ValueError('positive smoothing required')
        self.alpha=alpha
    def fit(self,texts):
        self.vocabulary=sorted(set(''.join(texts)))+[UNK,EOS]
        self.known=set(self.vocabulary);self.counts=defaultdict(Counter);self.totals=Counter()
        for text in texts:
            previous=BOS
            for token in list(text)+[EOS]:
                self.counts[previous][token]+=1;self.totals[previous]+=1;previous=token
        return self
    def encode(self,text):return [token if token in self.known else UNK for token in text]
    def probability(self,previous,token):
        if token not in self.known:token=UNK
        if previous not in self.known and previous!=BOS:previous=UNK
        return (self.counts[previous][token]+self.alpha)/(self.totals[previous]+self.alpha*len(self.vocabulary))
    def evaluate(self,texts):
        loss=0.;count=0;unknown=0
        for text in texts:
            previous=BOS
            for token in self.encode(text)+[EOS]:
                loss-=math.log(self.probability(previous,token));count+=1;unknown+=int(token==UNK);previous=token
        if not count:raise ValueError('nonempty evaluation required')
        return {'tokens_including_eos':count,'unknown_tokens':unknown,'nll_per_token':loss/count,'perplexity':math.exp(loss/count)}
    def sample(self,seed=7,max_tokens=100):
        rng=random.Random(seed);previous=BOS;output=[]
        for _ in range(max_tokens):
            probabilities=[self.probability(previous,t) for t in self.vocabulary]
            token=rng.choices(self.vocabulary,weights=probabilities,k=1)[0]
            if token==EOS:break
            output.append(token);previous=token
        return ''.join(output)


def dpo_loss(policy_chosen,policy_rejected,reference_chosen,reference_rejected,beta=.1):
    if any(not 0<p<=1 for p in (policy_chosen,policy_rejected,reference_chosen,reference_rejected)):
        raise ValueError('positive sequence probabilities required')
    if not math.isfinite(beta) or beta<=0:raise ValueError('positive finite beta required')
    margin=beta*((math.log(policy_chosen)-math.log(reference_chosen))-(math.log(policy_rejected)-math.log(reference_rejected)))
    return max(-margin,0)+math.log1p(math.exp(-abs(margin)))



def masked_mean_nll(probabilities, mask):
    if len(probabilities)!=len(mask) or not any(mask):
        raise ValueError('matching lengths and at least one supervised token required')
    if any(not 0<p<=1 for p in probabilities):raise ValueError('invalid token probability')
    return -sum(math.log(p) for p,include in zip(probabilities,mask) if include)/sum(bool(m) for m in mask)



def decoding_distribution(logits,temperature=1.,top_k=None,top_p=1.):
    if temperature<=0 or not 0<top_p<=1:raise ValueError('positive temperature and top_p in (0,1] required')
    if top_k is not None and (not isinstance(top_k,int) or top_k<1):raise ValueError('positive integer top_k required')
    probabilities=softmax([z/temperature for z in logits])
    ranked=sorted(range(len(logits)),key=lambda i:(-probabilities[i],i))
    if top_k is not None:ranked=ranked[:top_k]
    mass=sum(probabilities[i] for i in ranked)
    prefix=[];cumulative=0.
    for index in ranked:
        prefix.append(index);cumulative+=probabilities[index]/mass
        if cumulative>=top_p:break
    retained=sum(probabilities[i] for i in prefix)
    return [p/retained if i in prefix else 0. for i,p in enumerate(probabilities)]


def run():
    training=['the cat sat on the mat.','the dog sat on the rug.','a cat and a dog ran.']*8
    validation=['the cat ran on a rug.','a dog sat.']
    test=['the dog ran on the mat.','a zebra ran.']
    candidates=[Bigram(alpha=a).fit(training) for a in (.1,.5,1.)]
    model=min(candidates,key=lambda m:m.evaluate(validation)['nll_per_token'])
    unigram=Counter(token for text in training for token in list(text)+[EOS]);total=sum(unigram.values())
    baseline_loss=[]
    for text in test:
        for token in model.encode(text)+[EOS]:
            baseline_loss.append(-math.log((unigram[token]+model.alpha)/(total+model.alpha*len(model.vocabulary))))
    return {'kind':'trained smoothed character bigram; not an LLM',
            'selection':'alpha chosen on validation NLL; vocabulary/counts fit training only',
            'alpha':model.alpha,'vocabulary_size':len(model.vocabulary),
            'test':model.evaluate(test),'unigram_test_nll':sum(baseline_loss)/len(baseline_loss),
            'generated_seed_7':model.sample(),
            'decoding_example':decoding_distribution([2.,1.,0.],top_k=2,top_p=.8),
            'sft_masked_example_nll':masked_mean_nll([.01,.8,.7],[False,True,True]),
            'dpo_toy_losses':{'reference_policy':dpo_loss(.5,.5,.5,.5),
                             'chosen_more_likely':dpo_loss(.8,.2,.5,.5)},
            'limitations':'tiny repetitive corpus; mapped UNK loses character identity; held-out tiny examples are not a language capability benchmark'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path);args=parser.parse_args()
    text=json.dumps(run(),indent=2,sort_keys=True)
    if args.report:args.report.write_text(text+'\n')
    print(text)


if __name__=='__main__':main()

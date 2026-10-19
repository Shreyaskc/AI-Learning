"""Source integrity and progressive-enhancement contracts for Q&A. Not visual QA."""
import json
import unittest
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import build
import practice

ROOT=build.ROOT


class Markup(HTMLParser):
    def __init__(self):super().__init__();self.elements=[];self.details=0;self.links=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs);self.elements.append((tag,attrs))
        if tag=='details':self.details+=1
        if tag=='a':self.links.append(attrs.get('href',''))


class PracticeContentTests(unittest.TestCase):
    def setUp(self):self.bank=practice.questions(build.LESSONS)
    def test_all_original_prompts_and_full_solutions_preserved(self):
        original=json.loads((ROOT/'tools/fixtures/practice-baseline.json').read_text())
        actual=[{k:q[k] for k in ['id','topic','question','solution']} for q in self.bank]
        self.assertEqual(actual,original)
    def test_topic_counts_and_both_transformer_groups(self):
        counts=Counter(q['topic'] for q in self.bank)
        self.assertEqual(len(self.bank),69);self.assertEqual(counts['00-start'],10)
        self.assertEqual(counts['01-foundations'],3);self.assertEqual(counts['08-transformers'],7)
        transformer=[q for q in self.bank if q['topic']=='08-transformers']
        self.assertIn('shapes of S and AV',transformer[0]['question'])
        self.assertTrue(transformer[3]['question'].startswith('Change X'))
    def test_answer_reasoning_split_is_lossless(self):
        for q in self.bank:
            combined=q['answer']+(' '+q['explanation'] if q['explanation'] else '')
            self.assertEqual(combined,q['solution'])
    def test_answers_hidden_and_notes_optional_initially(self):
        parser=Markup();parser.feed((ROOT/'practice.html').read_text())
        ids={attrs['id']:(tag,attrs) for tag,attrs in parser.elements if 'id' in attrs}
        self.assertIn('hidden',ids['practice-answer'][1]);self.assertIn('hidden',ids['practice-card'][1])
        self.assertNotIn('required',ids['practice-attempt'][1])
        self.assertEqual(ids['practice-reveal'][1]['aria-expanded'],'false')
        self.assertEqual(ids['practice-reveal'][1]['aria-controls'],'practice-answer')
        self.assertEqual(sum(tag=='details' and attrs.get('id')!='term-analogy-disclosure' for tag,attrs in parser.elements),69) # native no-JS questions
    def test_home_has_direct_optional_diagnostic_and_practice(self):
        parser=Markup();parser.feed((ROOT/'index.html').read_text())
        self.assertIn('practice.html#topic=00-start',parser.links)
        self.assertIn('practice.html',parser.links)
        self.assertIn('course/01-foundations.html',parser.links)
    def test_inline_answers_have_native_closed_details(self):
        count=0
        for path in build.LESSONS:
            parser=Markup();parser.feed(path.with_suffix('.html').read_text())
            expected=sum(q['topic']==path.stem for q in self.bank)
            self.assertEqual(sum(attrs.get('class')=='inline-question' for tag,attrs in parser.elements if tag=='details'),expected)
            self.assertFalse(any('open' in attrs for tag,attrs in parser.elements if tag=='details'))
            count+=sum(attrs.get('class')=='inline-question' for tag,attrs in parser.elements if tag=='details')
        self.assertEqual(count,69)
    def test_mobile_contract_and_stable_source_links(self):
        css=(ROOT/'style.css').read_text()
        for contract in ['min-height:48px','min-height:44px','@media(max-width:600px)','minmax(0,1fr)','min-width:0']:
            self.assertIn(contract,css)
        for q in self.bank:
            filename,_,anchor=q['lesson'].partition('#')
            self.assertTrue((ROOT/filename).exists())
            self.assertIn('id="'+anchor+'"',(ROOT/filename).read_text())





class ReadingFlowTests(unittest.TestCase):
    def test_teaching_finishes_before_final_practice_and_takeaway(self):
        for path in build.LESSONS[1:]:
            text=path.read_text()
            self.assertIn('## What to carry forward',text)
            if '## Practice: try before revealing' in text:
                after=text.split('## Practice: try before revealing',1)[1]
                self.assertNotIn('## Practical extension:',after,path.name)
                self.assertNotIn('## Representative implementation:',after,path.name)
    def test_first_use_and_optional_onboarding_order(self):
        onboarding=(ROOT/'course/00-start.md').read_text()
        self.assertLess(onboarding.index('Start with the first lesson'),onboarding.index('## Optional diagnostic'))
        self.assertLess(onboarding.index('## Optional diagnostic'),onboarding.index('## Computer labs'))
        attention=(ROOT/'course/08-transformers.md').read_text()
        self.assertLess(attention.index('At each position, a query vector'),attention.index('Choose W_Q='))
        math=(ROOT/'course/02-math.md').read_text()
        self.assertLess(math.index('X = ['),math.index('## Geometry behind compression'))
    def test_further_worked_exercises_also_use_closed_reveals(self):
        count=0
        for path in build.LESSONS:
            parser=Markup();parser.feed(path.with_suffix('.html').read_text())
            count+=sum('worked-exercise' in attrs.get('class','') for tag,attrs in parser.elements if tag=='details')
        self.assertGreaterEqual(count,20)


if __name__=='__main__':unittest.main()

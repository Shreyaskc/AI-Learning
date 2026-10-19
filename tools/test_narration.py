"""Coverage, semantics and change-detection tests without loading any speech model."""
import copy
import json
import tempfile
import re
from unittest.mock import patch
import audio
import audio_model
import unittest
from pathlib import Path
import narration

class NarrationTests(unittest.TestCase):
    def test_every_source_byte_is_in_one_section(self):
        sections=narration.sections()
        expected=sum(1+sum(bool(re.match(r'^#{2,6} ',line)) for line in path.read_text().splitlines()) for path in (narration.ROOT/'course').glob('[0-9][0-9]-*.md'))
        self.assertEqual(len(sections),expected)
        self.assertEqual(len({s['id'] for s in sections}),len(sections))
        for path in sorted((narration.ROOT/'course').glob('[0-9][0-9]-*.md')):
            group=[s for s in sections if s['chapter']==path.stem]
            self.assertEqual(''.join(s['raw'] for s in group),path.read_text())
            self.assertEqual(group[0]['start_line'],1)
            self.assertEqual(group[-1]['end_line'],len(path.read_text().splitlines()))
    def test_new_section_and_changed_content_change_inventory_and_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'20-new-topic.md'
            path.write_text('# 20 · New topic\n\nIntroduction.\n\n## A mechanism\n\nA new paragraph.\n')
            first=narration.sections([path]);self.assertEqual(len(first),2)
            original=first[1]['source_sha256']
            path.write_text(path.read_text().replace('A new paragraph.','A changed explanation.'))
            changed=narration.sections([path]);self.assertNotEqual(changed[1]['source_sha256'],original)
            self.assertIn('changed explanation',narration.transcript(changed[1]))
            path.write_text(path.read_text()+'\n## A worked example\n\nHere is an example.\n')
            self.assertEqual(len(narration.sections([path])),3)
    def test_symbolic_formulas_have_explicit_spoken_meanings(self):
        math=narration.read_json('audio/speech-math.json');pron=narration.read_json('audio/pronunciations.json')
        conditional=narration.plain('`P(A|B)=P(A and B)/P(B)`',math,pron)
        self.assertIn('given B',conditional);self.assertIn('divided by',conditional)
        attention=narration.plain('S=QKᵀ/sqrt(d_k)',math,pron)
        self.assertIn('transposed divided by square root',attention)
        self.assertNotIn(' or ',attention)
        regularization=narration.plain('`J_reg=J+(lambda/2)||w||²`',math,pron)
        self.assertIn('lambda divided by two',regularization)
        self.assertIn('squared Euclidean norm',regularization)
    def test_decimal_digits_are_audible_and_backprop_is_explicit(self):
        text=narration.plain('Loss .5, score .7004, position 0.',{}, {})
        self.assertIn('zero point five',text)
        self.assertIn('zero point seven zero zero four',text)
        self.assertIn('position zero',text)
        section=next(s for s in narration.sections() if s['id']=='07-neural-networks--a-complete-backprop-calculation')
        text=narration.transcript(section)
        self.assertIn('derivative of loss with respect to h',text)
        self.assertIn('negative six',text)
        self.assertNotIn('dL and dh',text)
    def test_new_ambiguous_formula_requires_authored_expansion(self):
        with self.assertRaisesRegex(ValueError,'Author a precise'):
            narration.inline_code('mystery(x)=a|b',{})
    def test_practice_cues_preserve_questions_and_solutions(self):
        section=next(s for s in narration.sections() if s['id']=='01-foundations--practice-try-before-revealing')
        text=narration.transcript(section)
        self.assertIn('Pause now and try your answer',text)
        self.assertIn('not by itself',text)
        self.assertIn('account closed at',text)
        self.assertEqual(text.count('Question '),3)
    def test_code_blocks_are_explained_and_unknown_blocks_fail(self):
        blocks=narration.read_json('audio/code-narration.json')
        self.assertEqual(len(blocks),2)
        section=next(s for s in narration.sections() if s['id']=='02-math--vectors-are-ordered-measurements')
        text=narration.transcript(section)
        self.assertIn('Read this matrix by rows',text)
        self.assertIn('zero times three plus one times negative one',text)
        changed=dict(section,raw=section['raw'].replace('X = [ [2, 1]','X = [ [3, 1]'))
        with self.assertRaisesRegex(ValueError,'authored explanation'):narration.transcript(changed)
    def test_editorial_math_walkthrough_is_bound_to_exact_source(self):
        section=next(s for s in narration.sections() if s['id']=='08-transformers--one-attention-head-with-shapes')
        text=narration.transcript(section)
        self.assertIn('Both rows of the query-weight matrix',text)
        self.assertIn('one point three three nine five two three',text)
        override=narration.read_json('audio/editorial.json')[0]
        changed=dict(section,raw=section['raw'].replace(override['source'],'Changed numerical example.'))
        with self.assertRaisesRegex(ValueError,'stale'):narration.transcript(changed)
    def test_complete_transcripts_and_no_raw_markup(self):
        entries=narration.desired()
        self.assertEqual(len(entries),len(narration.sections()))
        for entry in entries:
            self.assertGreater(entry['words'],5,entry['id'])
            self.assertNotIn('`',entry['text'])
            self.assertNotIn('https://',entry['text'])
            self.assertNotIn('|',entry['text'])
            self.assertEqual(narration.sha((narration.ROOT/entry['transcript']).read_bytes()),entry['transcript_sha256'])
        self.assertEqual(narration.coverage(require_audio=False),[])
    def test_quality_gate_detects_corrupt_stale_and_missing_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'audio').mkdir()
            text='A faithful transcript.\n';asset=b'previously validated audio bytes'
            (root/'audio/one.txt').write_text(text);(root/'audio/one.m4a').write_bytes(asset)
            entry={'id':'one','text':text,'transcript':'audio/one.txt','transcript_sha256':narration.sha(text),'generation_key':'recipe-one','src':'audio/one.m4a','source_sha256':'source-one'}
            record={'generation_key':'recipe-one','sha256':narration.sha(asset),'qc_pass':True}
            inventory={'settings':narration.SETTINGS,'sections':[{k:v for k,v in entry.items() if k!='text'}]}
            (root/'audio/sections.json').write_text(json.dumps(inventory));(root/'audio/recordings.json').write_text(json.dumps({'one':record}))
            with patch.object(narration,'ROOT',root),patch.object(narration,'desired',return_value=[entry]):
                self.assertEqual(narration.coverage(),[])
                (root/'audio/one.m4a').write_bytes(b'corrupt')
                self.assertTrue(any('corrupt' in e for e in narration.coverage()))
                (root/'audio/one.m4a').write_bytes(asset)
                (root/'audio/one.txt').write_text('Changed words.')
                self.assertTrue(any('stale transcript' in e for e in narration.coverage()))
                (root/'audio/one.txt').write_text(text)
                (root/'audio/recordings.json').write_text('{}')
                self.assertTrue(any('Missing/stale recording' in e for e in narration.coverage()))
    def test_model_setup_checks_existing_files_without_network_or_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'config.json';path.write_bytes(b'known data')
            with patch.object(audio_model,'FILES',{'config.json':narration.sha(b'known data')}),patch.object(audio_model.urllib.request,'urlopen',side_effect=AssertionError('network not expected')):
                audio_model.fetch(tmp)
                path.write_bytes(b'unexpected data')
                with self.assertRaisesRegex(SystemExit,'unexpected checksum'):audio_model.fetch(tmp)
                self.assertEqual(path.read_bytes(),b'unexpected data')

    def test_recording_keys_bind_transcript_and_speech_recipe(self):
        entry=narration.desired()[0]
        self.assertIn(entry['generation_key'][:12],entry['src'])
        original=narration.sha(json.dumps({'transcript_sha256':entry['transcript_sha256'],'settings':narration.SETTINGS},sort_keys=True))
        self.assertEqual(original,entry['generation_key'])
        settings=dict(narration.SETTINGS,speed=1.2)
        self.assertNotEqual(original,narration.sha(json.dumps({'transcript_sha256':entry['transcript_sha256'],'settings':settings},sort_keys=True)))

if __name__=='__main__':unittest.main()

import json
import unittest
from html.parser import HTMLParser
import build
import listen

class Markup(HTMLParser):
    def __init__(self):super().__init__();self.elements=[]
    def handle_starttag(self,tag,attrs):self.elements.append((tag,dict(attrs)))

class ListeningTests(unittest.TestCase):
    def test_honest_catalog_and_transcript(self):
        items=listen.tracks(build.LESSONS)
        self.assertEqual(len(items),20)
        self.assertEqual(len({q['id'] for q in items}),20)
        self.assertEqual(sum(bool(q['src']) for q in items),1)
        self.assertEqual(next(q for q in items if q['src'])['kind'],'sample')
        self.assertEqual(sum(bool(q['transcript']) for q in items),1)
        sample=next(q for q in items if q['chapter']=='01-foundations')
        self.assertIn('feature',sample['transcript'])
        self.assertIn('inference',sample['transcript'].lower())
        self.assertEqual(sample['transcript'],(build.ROOT/'audio/transcripts/01-foundations-core.txt').read_text())
        self.assertEqual(set(json.loads((build.ROOT/'audio/catalog.json').read_text())),{'01-foundations-core'})
    def test_single_media_element_no_autoplay_and_labeled_controls(self):
        content=build.outputs()[build.ROOT/'listen.html']
        parser=Markup();parser.feed(content)
        audio=[attrs for tag,attrs in parser.elements if tag=='audio']
        self.assertEqual(len(audio),1)
        self.assertNotIn('autoplay',audio[0])
        self.assertNotIn('src',audio[0])
        self.assertEqual(audio[0]['preload'],'none')
        ids={attrs.get('id'):attrs for _,attrs in parser.elements}
        self.assertNotIn('checked',ids['audio-continue'])
        self.assertIn('hidden',ids['listen-interactive'])
        labels={attrs.get('for') for tag,attrs in parser.elements if tag=='label'}
        self.assertTrue({'audio-track','audio-speed','audio-file'}.issubset(labels))
        self.assertIn('<noscript>',content)
        self.assertIn('Section samples available: 1',content)
        self.assertIn('Full chapter recordings: 0 of 20',content)
        self.assertIn('Synthetic narration sample: Kokoro-82M',content)
    def test_safe_data_and_separate_state(self):
        self.assertNotIn('<script>',listen.safe_json({'value':'<script>&'}))
        js=(build.ROOT/'podcast.js').read_text()
        self.assertIn('ai-fluency-audio-v1',js)
        self.assertNotIn('ai-fluency-qa-v1',js)
        self.assertNotIn('fetch(',js)
        self.assertNotIn('speechSynthesis',js)
        self.assertIn('5000',js)
    def test_combined_glossary_and_audio_navigation(self):
        generated=build.outputs()
        self.assertEqual(len(generated),27)
        for page in generated.values():
            self.assertIn('Listen</a>',page)
            self.assertIn('id="term-plain"',page)
            self.assertIn('id="term-analogy-disclosure"',page)
        foundations=generated[build.COURSE/'01-foundations.html']
        self.assertEqual(foundations.count('class="term-link"'),7)
        self.assertIn('listen.html?track=01-foundations-core',foundations)
        glossary=generated[build.COURSE/'glossary.html']
        self.assertEqual(glossary.count('class="glossary-entry"'),85)
        listening=generated[build.ROOT/'listen.html']
        self.assertIn('id="course-audio"',listening)
        self.assertIn('Technical definition',listening)

    def test_private_voice_binary_not_in_repository(self):
        self.assertEqual([p.name for p in (build.ROOT/'audio').rglob('*.m4a')],['foundations-kokoro-af-heart-v1.m4a'])
        self.assertFalse(list((build.ROOT/'audio').rglob('*samantha*')))
        self.assertFalse(list((build.ROOT/'audio').rglob('*.aiff')))

if __name__=='__main__':unittest.main()

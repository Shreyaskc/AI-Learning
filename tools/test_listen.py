import json
import unittest
from html.parser import HTMLParser
import build
import listen
import narration

class Markup(HTMLParser):
    def __init__(self):super().__init__();self.elements=[]
    def handle_starttag(self,tag,attrs):self.elements.append((tag,dict(attrs)))

class ListeningTests(unittest.TestCase):
    def test_honest_catalog_and_transcript(self):
        items=listen.tracks(build.LESSONS)
        self.assertEqual(len(items),len(narration.sections()))
        self.assertEqual(len({q['id'] for q in items}),len(items))
        self.assertTrue(all(q['kind']=='section' for q in items))
        self.assertTrue(all(q['transcript'] for q in items))
        sample=next(q for q in items if q['id']=='01-foundations--from-rules-to-learned-functions')
        self.assertIn('feature',sample['transcript'])
        self.assertIn('inference',sample['transcript'].lower())
        self.assertEqual(sample['transcript'],(build.ROOT/sample['transcript_path']).read_text())
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
        self.assertTrue({'audio-chapter','audio-track','audio-speed','audio-file'}.issubset(labels))
        self.assertIn('<noscript>',content)
        self.assertIn('sections available across',content)
        self.assertIn('Synthetic narration: Kokoro-82M',content)
        self.assertIn('id="audio-chapter"',content)
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
        self.assertEqual(len(generated),len(build.LESSONS)+len(build.EXTRAS)+4)
        for page in generated.values():
            self.assertIn('Listen</a>',page)
            self.assertIn('id="term-plain"',page)
            self.assertIn('id="term-analogy-disclosure"',page)
        foundations=generated[build.COURSE/'01-foundations.html']
        self.assertEqual(foundations.count('class="term-link"'),7)
        self.assertIn('listen.html?track=01-foundations--from-rules-to-learned-functions',foundations)
        glossary=generated[build.COURSE/'glossary.html']
        self.assertEqual(glossary.count('class="glossary-entry"'),85)
        listening=generated[build.ROOT/'listen.html']
        self.assertIn('id="course-audio"',listening)
        expected={q['id'] for q in listen.tracks(build.LESSONS)}
        actual=set()
        import re
        for path in build.LESSONS:
            page=generated[path.with_suffix('.html')]
            actual.update(re.findall(r'data-audio-section="([^"]+)"',page))
            for name,url in build.COURSES:
                self.assertIn(url,page)
        self.assertEqual(actual,expected)
        self.assertIn('Technical definition',listening)

    def test_all_six_course_links_in_every_generated_page_and_readme(self):
        slugs={'AI-Learning','system-design-fluency','dsa-fluency','principal-leadership-fluency','production-platforms-fluency','practical-engineering-fluency'}
        expected={'https://shreyaskc.github.io/'+slug+'/' for slug in slugs}
        self.assertEqual({url for _,url in build.COURSES},expected)
        for page in build.outputs().values():
            for url in expected:self.assertGreaterEqual(page.count('href="'+url+'"'),2)
        readme=(build.ROOT/'README.md').read_text()
        for slug in slugs:
            self.assertIn('https://shreyaskc.github.io/'+slug+'/',readme)
            self.assertIn('https://github.com/Shreyaskc/'+slug,readme)

    def test_private_voice_binary_not_in_repository(self):
        self.assertTrue((build.ROOT/'audio/samples/foundations-kokoro-af-heart-v1.m4a').exists())
        self.assertFalse(list((build.ROOT/'audio').rglob('*samantha*')))
        self.assertFalse(list((build.ROOT/'audio').rglob('*.aiff')))

if __name__=='__main__':unittest.main()

import unittest
import build
import terms

class TermsTests(unittest.TestCase):
    def test_registry_and_aliases(self):
        self.assertEqual(len(terms.ENTRIES), 7)
        self.assertEqual(terms.resolve(' PARAMETERS! '), 'parameter')
        self.assertEqual(terms.resolve('Training'), 'training')
        self.assertEqual(terms.resolve('Inference'), 'inference')
        self.assertIsNone(terms.resolve('example'))
        self.assertEqual(terms.resolve('example', '01-foundations'), 'example')
        self.assertIsNone(terms.resolve('Basic:'))
    def test_protected_markup(self):
        self.assertNotIn('data-term', build.inline('`**feature**`'))
        linked = build.inline('[**feature**](glossary.md)')
        self.assertEqual(linked.count('<a '), 1)
        self.assertNotIn('data-term', linked)
        self.assertIn('<strong>Basic:</strong>', build.inline('**Basic:**'))
        self.assertEqual(build.inline('**feature** **features**').count('data-term="feature"'), 2)
    def test_coverage_fallback_and_hidden_answers(self):
        page = build.outputs()[build.COURSE / '01-foundations.html']
        self.assertEqual(page.count('class="term-link"'), 7)
        for key in terms.ENTRIES:
            self.assertIn('id="term-'+key+'"', build.outputs()[build.COURSE / 'glossary.html'])
        self.assertIn('course/glossary.html#term-feature', page)
        self.assertNotIn('data-term="basic"', page)
        self.assertIn('max-height:calc(100dvh - 2rem)', (build.ROOT/'style.css').read_text())

if __name__ == '__main__': unittest.main()

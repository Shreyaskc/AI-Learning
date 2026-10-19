import unittest
import json
import build
import terms

class TermsTests(unittest.TestCase):
    def test_registry_and_aliases(self):
        self.assertEqual(len(terms.ENTRIES), 85)
        self.assertEqual(terms.resolve(' PARAMETERS! '), 'parameter')
        self.assertEqual(terms.resolve('Training'), 'training')
        self.assertEqual(terms.resolve('Inference'), 'inference')
        self.assertIsNone(terms.resolve('example'))
        self.assertEqual(terms.resolve('example', '01-foundations'), 'example')
        self.assertIsNone(terms.resolve('Basic:'))
    def test_all_layers_and_distinctions(self):
        for key, entry in terms.ENTRIES.items():
            for field in terms.FIELDS:
                self.assertTrue(entry[field].strip(), (key, field))
            self.assertIn('Limit:', entry['analogy'])
        self.assertIn('hyperparameter', terms.ENTRIES['parameter']['plain'])
        self.assertIn('representation', terms.ENTRIES['embedding']['plain'])
        self.assertIn('retrieval', terms.ENTRIES['attention']['definition'])
        self.assertIsNone(terms.resolve('key'))
        self.assertIsNone(terms.resolve('calibration / equalized odds'))
        self.assertEqual(terms.resolve('calibration'), 'calibration')

    def test_no_reference_terms_lost_and_payload_is_scoped(self):
        baseline=json.loads((build.ROOT/'tools/fixtures/glossary-baseline-terms.json').read_text())
        names={entry['name'] for entry in terms.ENTRIES.values()}
        self.assertTrue(set(baseline).issubset(names))
        generated=build.outputs()
        for path, page in generated.items():
            registry=json.loads(page.split('<script id="term-data" type="application/json">')[1].split('</script>')[0])
            self.assertEqual(len(registry), 7 if path.name=='01-foundations.html' else 0)
        malformed='| Term | Technical | Plain | Analogy | Example | Lesson | Aliases | Sources |\n| Broken | Missing | fields |'
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w') as source:
            source.write(malformed);source.flush()
            with self.assertRaises(ValueError): terms.load(source.name)

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

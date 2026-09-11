import base64
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('validate', ROOT / 'scripts/validate.py')
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class CatalogTest(unittest.TestCase):
    def setUp(self):
        self.entry = json.loads((ROOT / 'templates/plugin-entry.json').read_text())
        self.catalog = {'schema_version': 2, 'host': 'zboard', 'plugins': [self.entry]}

    def test_template_valid(self):
        validator.validate(self.catalog, 'zboard')

    def test_catalog_contains_only_admission_and_discovery_metadata(self):
        forbidden = {'source', 'releases', 'version', 'artifacts'}
        self.assertFalse(forbidden & self.entry.keys())
        self.assertFalse({'name', 'description', 'license', 'maintainers'} & self.entry.keys())
        self.assertEqual(self.entry['metadata_source'], {'type': 'repository-file', 'path': 'marketplace.json'})
        self.assertEqual(self.entry['release_source']['type'], 'github-releases')

    def test_rejects_invalid_trust_and_capability_boundaries(self):
        mutations = [
            lambda e: e['publisher'].update(public_key=None),
            lambda e: e['publisher'].update(public_key='bad-key'),
            lambda e: e['release_source'].update(type='branch-file'),
            lambda e: e['release_source'].update(metadata_asset='../marketplace-entry.json'),
            lambda e: e['metadata_source'].update(path='manifest.json'),
            lambda e: e.update(repository='https://127.0.0.1/plugin'),
            lambda e: e.update(surfaces=['admin', 'unknown']),
            lambda e: e.update(capabilities=['znet-sink.shell.v1']),
            lambda e: e.update(capabilities=['zboard.ui.page.v1', 'zboard.ui.page.v1']),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                entry = copy.deepcopy(self.entry)
                mutate(entry)
                with self.assertRaises(ValueError):
                    validator.validate_entry(entry, 'zboard')

    def test_duplicate_ids_hosts_and_unknown_fields_rejected(self):
        self.catalog['plugins'].append(copy.deepcopy(self.entry))
        with self.assertRaises(ValueError):
            validator.validate(self.catalog, 'zboard')
        with self.assertRaises(ValueError):
            validator.validate(self.catalog, 'znet-sink')
        with self.assertRaises(ValueError):
            validator.validate({'schema_version': 2, 'host': 'znet-sink', 'plugins': [], 'script': 'run me'}, 'znet-sink')
        with self.assertRaises(ValueError):
            json.loads('{"host":"zboard","host":"znet-sink"}', object_pairs_hook=validator.no_duplicates)

    def test_transition_retains_listings_but_does_not_store_release_history(self):
        previous = copy.deepcopy(self.catalog)
        current = copy.deepcopy(self.catalog)
        current['plugins'][0]['metadata_source']['path'] = 'marketplace.json'
        current['plugins'][0]['publisher']['public_key'] = base64.b64encode(b'x' * 32).decode()
        validator.validate_transition(previous, current)
        current['plugins'] = []
        with self.assertRaises(ValueError):
            validator.validate_transition(previous, current)

    def test_schema_one_catalog_migrates_without_copying_release_history(self):
        previous = {'schema_version': 1, 'host': 'zboard', 'plugins': [{
            'id': self.entry['id'], 'source': {'version': 'v0.0.1'}, 'releases': [{'version': 'v0.0.1'}],
        }]}
        validator.validate_transition(previous, self.catalog)


if __name__ == '__main__':
    unittest.main()

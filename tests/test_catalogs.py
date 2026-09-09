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
        self.catalog = {'schema_version': 1, 'host': 'zboard', 'plugins': [self.entry]}

    def test_transition_retains_publisher_and_previous_artifacts(self):
        previous = copy.deepcopy(self.catalog)
        validator.validate_transition(previous, self.catalog)
        for mutate in (
            lambda c: c.update(plugins=[]),
            lambda c: c['plugins'][0]['publisher'].update(id='another-publisher'),
            lambda c: c['plugins'][0]['publisher'].update(public_key=base64.b64encode(b'x' * 32).decode()),
            lambda c: c['plugins'][0].update(releases=[]),
            lambda c: c['plugins'][0]['releases'][0]['artifacts'][0].update(sha256='a' * 64),
        ):
            current = copy.deepcopy(self.catalog)
            mutate(current)
            with self.assertRaises(ValueError):
                validator.validate_transition(previous, current)
        previous['plugins'][0]['releases'] = []
        previous['plugins'][0]['publisher']['public_key'] = None
        validator.validate_transition(previous, self.catalog)

    def test_template_valid(self):
        validator.validate(self.catalog, 'zboard')

    def test_source_only_is_not_installable(self):
        self.entry['releases'] = []
        self.entry['publisher']['public_key'] = None
        validator.validate(self.catalog, 'zboard')

    def test_rejects_bad_release_identity_and_artifacts(self):
        mutations = [
            lambda e: e['publisher'].update(public_key=None),
            lambda e: e['publisher'].update(public_key='bad-key'),
            lambda e: e['source'].update(manifest='../manifest.json'),
            lambda e: e['releases'][0].update(version='0.0.1'),
            lambda e: e['releases'].append(copy.deepcopy(e['releases'][0])),
            lambda e: e['releases'][0].update(capabilities=['znet-sink.shell.v1']),
            lambda e: e['releases'][0]['requires'].update({'znet-sink': '>=0.0.1'}),
            lambda e: e['releases'][0]['artifacts'][0].update(url='http://example.com/plugin.zbplugin'),
            lambda e: e['releases'][0]['artifacts'][0].update(url='https://user:secret@example.com/plugin.zbplugin'),
            lambda e: e['releases'][0]['artifacts'][0].update(sha256='invalid'),
            lambda e: e['releases'][0]['artifacts'][0].update(size=True),
            lambda e: e['releases'][0]['artifacts'][0].update(size=33554433),
            lambda e: e['releases'][0]['artifacts'].append(copy.deepcopy(e['releases'][0]['artifacts'][0])),
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
            validator.validate({'schema_version': 1, 'host': 'znet-sink', 'plugins': [], 'script': 'run me'}, 'znet-sink')
        with self.assertRaises(ValueError):
            json.loads('{"host":"zboard","host":"znet-sink"}', object_pairs_hook=validator.no_duplicates)


if __name__ == '__main__':
    unittest.main()

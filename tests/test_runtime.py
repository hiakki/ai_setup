import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class ConfigurationTests(unittest.TestCase):
    def test_merge_preserves_unrelated_settings_and_deduplicates_hooks(self):
        self.assertTrue((ROOT / 'runtime.py').exists(), 'Runtime/configuration installer is missing')
        from runtime import merge
        original = {'theme': 'dark', 'hooks': {'SessionStart': [{'command': 'my-hook'}]}}
        incoming = {'hooks': {'SessionStart': [{'command': 'graph-hook'}]}, 'mcpServers': {'graft': {'command': 'graft'}}}
        result = merge(original, incoming)
        self.assertEqual(result['theme'], 'dark')
        self.assertEqual(result['hooks']['SessionStart'], [{'command': 'my-hook'}, {'command': 'graph-hook'}])
        self.assertEqual(merge(result, incoming), result)

    def test_conflicting_provider_is_not_silently_replaced(self):
        self.assertTrue((ROOT / 'runtime.py').exists(), 'Runtime/configuration installer is missing')
        from runtime import merge
        with self.assertRaises(ValueError):
            merge({'mcpServers': {'graft': {'command': '/custom/graft'}}},
                  {'mcpServers': {'graft': {'command': '/new/graft'}}})


if __name__ == '__main__':
    unittest.main()

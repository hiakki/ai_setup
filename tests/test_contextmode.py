"""Guard client settings and native invocation across repeated installations."""
import json
from pathlib import Path
import sys
import tempfile
import tomllib
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from setup import Installer, ROOT, select_components


class ContextModeTests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.work').mkdir(exist_ok=True)

    def test_default_and_selective_install_include_context_mode(self):
        self.assertIn('contextmode', select_components('all'))
        self.assertEqual(select_components('contextmode'), ['contextmode'])

    def test_registration_preserves_settings_and_supports_managed_upgrade(self):
        from contextmode_runtime import configure
        with tempfile.TemporaryDirectory(dir=ROOT / '.work') as tmp:
            i = Installer(Path(tmp), {})
            codex = i.home / '.codex/config.toml'
            codex.parent.mkdir()
            codex.write_text('# keep my settings\nmodel = "operator-model"\n')
            claude = i.home / '.claude.json'
            claude.write_text('{"mcpServers":{"other":{"command":"keep-me"}}}')
            node = i.home / 'node with spaces/node.exe'
            entry = i.home / 'context-mode/server.bundle.mjs'
            configure(i, node, entry)
            first = [p.read_bytes() for p in (codex, claude)]
            configure(i, node, entry)
            self.assertEqual(first, [p.read_bytes() for p in (codex, claude)])
            next_entry = i.home / 'next-version/server.bundle.mjs'
            configure(i, node, next_entry)
            c = tomllib.loads(codex.read_text())
            self.assertEqual(c['model'], 'operator-model')
            self.assertIn('# keep my settings', codex.read_text())
            self.assertEqual(c['mcp_servers']['context-mode']['command'], str(node))
            self.assertEqual(c['mcp_servers']['context-mode']['args'],
                             [str(i.home / '.local/share/ai-setup/context-mode-server.mjs'), str(next_entry)])
            self.assertEqual(json.loads(claude.read_text())['mcpServers']['other']['command'], 'keep-me')
            self.assertNotIn('hooks', c)

    def test_operator_edit_in_second_client_stops_before_first_client_write(self):
        from contextmode_runtime import configure
        with tempfile.TemporaryDirectory(dir=ROOT / '.work') as tmp:
            i = Installer(Path(tmp), {})
            node, entry = i.home / 'node', i.home / 'server.mjs'
            configure(i, node, entry)
            codex = i.home / '.codex/config.toml'
            before = codex.read_bytes()
            claude = i.home / '.claude.json'
            original = json.loads(claude.read_text())
            original['mcpServers']['context-mode']['args'] = ['operator-wrapper']
            claude.write_text(json.dumps(original))
            with self.assertRaisesRegex(ValueError, 'Preserving'):
                configure(i, node, i.home / 'new.mjs')
            self.assertEqual(before, codex.read_bytes())
            self.assertEqual(json.loads(claude.read_text()), original)


if __name__ == '__main__':
    unittest.main()

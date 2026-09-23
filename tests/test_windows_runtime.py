import hashlib
from pathlib import Path
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class WindowsRuntimeTests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.work').mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / '.work')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def archive(self, names):
        path = self.root / 'provider.zip'
        with zipfile.ZipFile(path, 'w') as z:
            for name in names:
                z.writestr(name, b'provider content')
        return path

    def test_archive_rejects_traversal_case_collision_and_device_paths(self):
        from windows_runtime import extract_zip
        for names in [['../outside.exe'], ['a.exe', 'A.exe'], ['C:/outside'],
                      ['a/b:stream'], ['AUX.txt'], ['a./file'], ['a\\..\\escape']]:
            with self.subTest(names=names), self.assertRaises(ValueError):
                extract_zip(self.archive(names), self.root / 'out')
        self.assertFalse((self.root / 'out').exists())

    def test_verified_archive_extracts_full_runtime_assets(self):
        from windows_runtime import extract_zip, verify_checksum
        path = self.archive(['node-v24-win-x64/node.exe', 'node-v24-win-x64/node_modules/npm/bin/npm-cli.js'])
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        verify_checksum(path, digest + '  provider.zip\n', path.name)
        extract_zip(path, self.root / 'out')
        self.assertTrue((self.root / 'out/node-v24-win-x64/node_modules/npm/bin/npm-cli.js').exists())
        with self.assertRaises(ValueError):
            verify_checksum(path, '0' * 64 + '  provider.zip\n', path.name)
        with self.assertRaises(ValueError):
            verify_checksum(path, digest + '  different.zip\n', path.name)

    def test_launcher_preserves_literal_percent_and_disables_delayed_expansion(self):
        from windows_runtime import launcher
        text = launcher(['C:\\Users\\A %TEMP% ! Name\\node.exe', 'C:\\tools & apps\\cli.js'])
        self.assertIn('setlocal DisableDelayedExpansion', text)
        self.assertIn('A %%TEMP%% ! Name', text)
        self.assertIn('"C:\\tools & apps\\cli.js" %*', text)
        self.assertIn('exit /b %errorlevel%', text)

    def test_config_relocation_operates_on_values_not_serialized_escapes(self):
        from windows_runtime import relocate
        original = {'hooks': [{'command': 'node "C:\\stage home\\helper.cjs"'}],
                    'number': 3, 'enabled': True}
        fixed = relocate(original, 'C:\\stage home', 'C:\\User %Name%')
        self.assertEqual(fixed['hooks'][0]['command'], 'node "C:\\User %Name%\\helper.cjs"')
        self.assertEqual(fixed['number'], 3)
        self.assertIs(fixed['enabled'], True)
        self.assertIn('stage home', original['hooks'][0]['command'])

    def test_client_and_mcp_commands_use_native_processes_without_shell(self):
        from setup import Installer
        from windows_runtime import command
        i = Installer(self.root / 'home with spaces', {'node': '24.20.0', 'graft_node': '20.20.2'})
        codex = command(i, 'codex')
        graft = command(i, 'graft')
        self.assertEqual(Path(codex[0]).name, 'node.exe')
        self.assertTrue(Path(codex[1]).as_posix().endswith('node_modules/@openai/codex/bin/codex.js'))
        self.assertIn('node-v20.20.2-win-x64', str(graft[0]))
        self.assertTrue(Path(graft[1]).as_posix().endswith('node_modules/@nanonets/graft/dist/cli.js'))
        self.assertFalse(any(str(x).endswith('.cmd') for x in codex + graft))

    def test_runtime_adapter_preserves_provider_skill_behind_directory_link(self):
        from setup import Installer
        from windows_runtime import runtime_adapter
        i = Installer(self.root / 'home', {})
        source = i.home / '.agents/skills/.sources/gstack'
        (source / 'browse/dist').mkdir(parents=True)
        (source / 'browse/SKILL.md').write_text('Provider browser workflow')
        (source / 'SKILL.md').write_text('Provider root workflow')
        (source / 'browse/dist/browse.exe').write_bytes(b'binary')
        i.state_dir.mkdir(parents=True)
        adapter = i.home / '.codex/skills/gstack'
        i.link(adapter, source)
        runtime_adapter(i, source)
        self.assertEqual((source / 'SKILL.md').read_text(), 'Provider root workflow')
        self.assertEqual((source / 'browse/SKILL.md').read_text(), 'Provider browser workflow')
        self.assertFalse((adapter / 'SKILL.md').exists())
        self.assertFalse((adapter / 'browse/SKILL.md').exists())
        self.assertEqual((adapter / 'browse/dist/browse.exe').read_bytes(), b'binary')

    def test_integration_import_preserves_settings_and_uses_native_mcp_argv(self):
        import json
        import tomlkit
        from setup import Installer
        from windows_runtime import integrations
        i = Installer(self.root / 'home with spaces', {'node': '24.20.0', 'graft_node': '20.20.2'})
        i.state_dir.mkdir(parents=True)
        (i.home / '.codex').mkdir()
        (i.home / '.codex/config.toml').write_text('model = "operator-choice"\n')
        calls = []
        def provider_run(args, **kwargs):
            calls.append(list(map(str, args)))
            if 'install' in args and '--skip-binary' in args:
                stage = Path(kwargs['env']['HOME'])
                document = {'hooks': {'SessionStart': [{'hooks': [{'type': 'command',
                            'command': 'provider-hook', 'command_windows': 'windows-hook'}]}]},
                            'mcp_servers': {'codebase-memory-mcp': {'command': 'discard-generated-command'}}}
                (stage / '.codex/config.toml').write_text(tomlkit.dumps(document))
                (stage / '.claude/settings.json').write_text(json.dumps({'hooks': {}}))
        with patch('windows_runtime.run', side_effect=provider_run), \
                patch('windows_runtime.capture', return_value='C:\\chromium\\chrome.exe'), \
                patch('windows_runtime.trust_generated_hooks'):
            integrations(i)
        config = tomllib.loads((i.home / '.codex/config.toml').read_text())
        self.assertEqual(config['model'], 'operator-choice')
        self.assertEqual(config['hooks']['SessionStart'][0]['hooks'][0]['command_windows'], 'windows-hook')
        self.assertTrue(config['mcp_servers']['graft']['command'].endswith('node.exe'))
        self.assertTrue(Path(config['mcp_servers']['graft']['args'][0]).as_posix().endswith('dist/cli.js'))
        self.assertEqual(config['mcp_servers']['graft']['args'][1], 'mcp')
        cbm = next(args for args in calls if '--skip-binary' in args)
        self.assertIn('--clients=claude,codex', cbm)

    def test_hook_trust_covers_distinct_events_with_shared_windows_command(self):
        from setup import Installer
        from windows_runtime import trust_generated_hooks
        i = Installer(self.root / 'home', {'node': '24.20.0'})
        i.state_dir.mkdir(parents=True)
        config = i.home / '.codex/config.toml'
        handler = {'type': 'command', 'command': 'posix-command', 'command_windows': 'windows-command'}
        i.state['configuration'] = {'.codex/config.toml': {'hooks': {
            event: [{'hooks': [handler]}] for event in ('SessionStart', 'SubagentStart')}}}
        records = [{'eventName': event, 'matcher': None, 'command': 'windows-command',
                    'sourcePath': str(config), 'key': str(index), 'currentHash': 'verified-hash'}
                   for index, event in enumerate(('sessionStart', 'subagentStart'))]
        class Client:
            def __init__(self, *args, **kwargs): pass
            def call(self, *args, **kwargs): return {'data': [{'hooks': records, 'errors': []}]}
            def close(self): pass
        with patch('smoke.RPC', Client), patch('windows_runtime.merge_config') as write:
            trust_generated_hooks(i)
            self.assertEqual(set(write.call_args.args[2]['hooks']['state']), {'0', '1'})
            records.pop()
            with self.assertRaises(ValueError):
                trust_generated_hooks(i)


if __name__ == '__main__':
    unittest.main()

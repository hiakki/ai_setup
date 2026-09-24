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

    def test_blog_renderer_adapter_reads_binary_and_rejects_links_and_replacement(self):
        import os
        from types import SimpleNamespace
        from setup import Installer
        from windows_runtime import blog_renderer_adapter
        i = Installer(self.root / 'home', {})
        source = i.sources / 'claude-blog'
        script = source / 'scripts/blog_render.py'
        script.parent.mkdir(parents=True)
        script.write_text('''import os, stat
def read(path):
    try:
        fd = os.open(str(path), os.O_RDONLY | os.O_NOFOLLOW)
    except OSError:
        raise
    try:
        return os.read(fd, 100)
    finally:
        os.close(fd)
''', encoding='utf-8')
        with patch('windows_runtime.capture', return_value='recorded provider diff'):
            blog_renderer_adapter(i, source)
            adapted = script.read_bytes()
            blog_renderer_adapter(i, source)
            self.assertEqual(script.read_bytes(), adapted)
        namespace = {}
        exec(compile(adapted, str(script), 'exec'), namespace)
        post = self.root / 'post.md'
        content = 'Line one\r\nCaf\u00e9\x1a\r\n'.encode('utf-8')
        post.write_bytes(content)
        self.assertEqual(namespace['read'](post), content)
        with self.assertRaisesRegex(ValueError, 'non-regular'):
            namespace['read'](self.root)
        linked_stat = SimpleNamespace(st_mode=post.stat().st_mode, st_file_attributes=0x400)
        with patch('os.lstat', return_value=linked_stat), \
                patch('stat.FILE_ATTRIBUTE_REPARSE_POINT', 0x400, create=True), \
                patch('os.open') as opened:
            with self.assertRaisesRegex(ValueError, 'refusing link'):
                namespace['read'](post)
            opened.assert_not_called()
        swapped = self.root / 'replacement.md'
        swapped.write_text('different file', encoding='utf-8')
        original_open = os.open
        def swap_then_open(*args):
            swapped.replace(post)
            return original_open(*args)
        with patch('os.open', side_effect=swap_then_open), patch('os.read') as read:
            with self.assertRaisesRegex(ValueError, 'source changed'):
                namespace['read'](post)
            read.assert_not_called()
        self.assertEqual(i.state['generated_sources']['claude-blog'], 'recorded provider diff')
        i.verify()

    def test_gstack_copied_skill_names_match_folders_and_preserve_local_edits(self):
        from setup import Installer
        from windows_runtime import gstack_skill_names
        i = Installer(self.root / 'home', {})
        folder = i.home / '.agents/skills/gstack-browse'
        folder.mkdir(parents=True)
        skill = folder / 'SKILL.md'
        skill.write_text('---\nname: browse\ndescription: Browser\n---\nProvider instructions\n')
        asset = folder / 'reference.txt'
        asset.write_text('reference content')
        i.remember(folder)
        gstack_skill_names(i)
        self.assertIn('name: gstack-browse\n', skill.read_text())
        self.assertEqual(asset.read_text(), 'reference content')
        self.assertIn('Provider instructions', skill.read_text())
        gstack_skill_names(i)
        i.verify()
        skill.write_text(skill.read_text().replace('gstack-browse', 'my-custom-name'))
        with self.assertRaisesRegex(ValueError, 'locally edited'):
            gstack_skill_names(i)
        self.assertIn('my-custom-name', skill.read_text())

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
        browser_install = next(args for args in calls if args[-2:] == ['install', 'chromium'])
        self.assertEqual(browser_install[1:3],
                         ['--require', str(ROOT / 'config/playwright-download-timeout.cjs')])

    def test_existing_playwright_is_reused_without_browser_download_on_rerun(self):
        import json
        import tomlkit
        from setup import Installer
        from windows_runtime import integrations
        original = {'command': 'npx', 'args': ['-y', '@playwright/mcp@latest', '--browser', 'chrome']}
        other = {'command': 'custom-playwright', 'args': ['--browser', 'msedge'], 'type': 'stdio'}
        for existing_claude in (False, True):
            with self.subTest(existing_claude=existing_claude):
                i = Installer(self.root / str(existing_claude), {'node': '24.20.0', 'graft_node': '20.20.2'})
                i.state_dir.mkdir(parents=True)
                i.state['completed'] = ['integrations']
                i.state['cbm_configured'] = True
                config_path = i.home / '.codex/config.toml'
                config_path.parent.mkdir()
                config_path.write_text(tomlkit.dumps({'model': 'operator-choice',
                    'mcp_servers': {'playwright': original}}), encoding='utf-8')
                if existing_claude:
                    (i.home / '.claude.json').write_text(json.dumps({'mcpServers': {'playwright': other}}))
                for _ in range(2):
                    with patch('windows_runtime.run') as run, \
                            patch('windows_runtime.capture', return_value='C:\\chromium\\chrome.exe') as capture, \
                            patch('windows_runtime.trust_generated_hooks'):
                        integrations(i)
                    run.assert_not_called()
                    capture.assert_not_called()
                    codex = tomllib.loads(config_path.read_text(encoding='utf-8'))
                    claude = json.loads((i.home / '.claude.json').read_text())
                    self.assertEqual(codex['mcp_servers']['playwright'], original)
                    self.assertEqual(codex['model'], 'operator-choice')
                    self.assertEqual(claude['mcpServers']['playwright'],
                                     other if existing_claude else dict(original, type='stdio'))
                    self.assertFalse((i.home / '.config/ai-setup/playwright.json').exists())
                    i.verify()
                    # A new terminal can inherit a different PATH after setup.
                    i = Installer(i.home, i.manifest)
                    i.env['PATH'] = str(self.root / 'new-shell-tools') + ';' + i.env['PATH']

    def test_integration_preserves_each_clients_path_and_rejects_recorded_edits(self):
        import json
        import tomlkit
        from setup import Installer
        from windows_runtime import command, integrations
        i = Installer(self.root / 'home', {'node': '24.20.0', 'graft_node': '20.20.2'})
        i.state['completed'] = ['integrations']
        i.state['cbm_configured'] = True
        codex_path = i.home / '.codex/config.toml'
        codex_path.parent.mkdir(parents=True)
        playwright = {'command': 'npx', 'args': ['-y', '@playwright/mcp@latest', '--browser', 'chrome']}
        for path, section, client_path in [(codex_path, 'mcp_servers', 'C:\\Codex tools'),
                (i.home / '.claude.json', 'mcpServers', 'C:\\Claude tools')]:
            servers = {'playwright': playwright}
            for name in ('codebase-memory-mcp', 'graft'):
                servers[name] = {'command': str(command(i, name)[0]), 'env': {'PATH': client_path}}
            document = {section: servers}
            path.write_text(tomlkit.dumps(document) if path.suffix == '.toml' else json.dumps(document))
        with patch('windows_runtime.run') as run, patch('windows_runtime.trust_generated_hooks'):
            integrations(i)
            i.env['PATH'] = 'C:\\Changed terminal tools'
            integrations(i)
            run.assert_not_called()
            i.verify()
            codex = tomllib.loads(codex_path.read_text())
            claude = json.loads((i.home / '.claude.json').read_text())
            for name in ('codebase-memory-mcp', 'graft'):
                self.assertEqual(codex['mcp_servers'][name]['env']['PATH'], 'C:\\Codex tools')
                self.assertEqual(claude['mcpServers'][name]['env']['PATH'], 'C:\\Claude tools')
            codex['mcp_servers']['codebase-memory-mcp']['env']['PATH'] = 'C:\\Local edit'
            codex_path.write_text(tomlkit.dumps(codex))
            before = codex_path.read_bytes()
            with self.assertRaisesRegex(ValueError, 'codebase-memory-mcp.env.PATH'):
                integrations(i)
            self.assertEqual(codex_path.read_bytes(), before)

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

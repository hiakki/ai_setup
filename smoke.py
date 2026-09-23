#!/usr/bin/env python3
"""Exercise local installed tools without account login, paid inference, or private data."""
import argparse
from collections import Counter
import contextlib
import hashlib
import http.server
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time
import tomllib

from setup import Installer, ROOT, run, capture


def tool_command(installer, name):
    if installer.windows:
        from windows_runtime import command
        return command(installer, name)
    return [installer.bin / name]


class RPC:
    def __init__(self, command, env, cwd, codex=False):
        from setup import command_args
        command = list(map(str, command))
        identity = hashlib.sha256(json.dumps(command).encode()).hexdigest()[:8]
        self.log = (cwd / ('mcp-' + Path(command[0]).name + '-' + identity + '.log')).open('w', encoding='utf-8')
        try:
            self.process = subprocess.Popen(command_args(command, env=env), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                            stderr=self.log, text=True, encoding='utf-8', env=env, cwd=cwd)
        except BaseException:
            self.log.close()
            raise
        self.queue = queue.Queue()
        self.counter = 0
        def read():
            for line in self.process.stdout:
                self.queue.put(line)
        self.reader = threading.Thread(target=read, daemon=True)
        self.reader.start()
        params = {'capabilities': {'experimentalApi': True} if codex else {},
                  'clientInfo': {'name': 'ai-setup-smoke', 'version': '1'}}
        if not codex:
            params['protocolVersion'] = '2024-11-05'
        try:
            self.call('initialize', params)
            self.send({'jsonrpc': '2.0', 'method': 'initialized' if codex else 'notifications/initialized'})
        except BaseException:
            self.close()
            raise

    def send(self, payload):
        self.process.stdin.write(json.dumps(payload) + '\n')
        self.process.stdin.flush()

    def call(self, method, params):
        self.counter += 1
        self.send({'jsonrpc': '2.0', 'id': self.counter, 'method': method, 'params': params})
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            try:
                line = self.queue.get(timeout=min(2, max(0.1, deadline - time.monotonic())))
            except queue.Empty:
                if self.process.poll() is not None:
                    raise RuntimeError(f'MCP exited: {method}; see {self.log.name}')
                continue
            try:
                response = json.loads(line)
            except json.JSONDecodeError:
                continue
            if response.get('id') == self.counter:
                if 'error' in response or response.get('result', {}).get('isError'):
                    raise RuntimeError(f'MCP failure in {method}: {response}')
                return response['result']
        raise RuntimeError(f'MCP timed out: {method}')

    def close(self):
        if self.process.poll() is None:
            self.process.terminate()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
        self.reader.join(timeout=10)
        self.process.stdin.close()
        if not self.reader.is_alive():
            self.process.stdout.close()
        self.log.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, default=Path.home())
    args = parser.parse_args()
    i = Installer(args.home, json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8')))
    report_file = i.state_dir / 'smoke-report.json'
    # A failed rerun must never leave a previous passing report behind.
    if report_file.exists():
        report_file.unlink()
    try:
        check_runtime(i, report_file)
    except Exception as error:
        i.state_dir.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps({'status': 'failed', 'platform': sys.platform,
                                          'error': str(error)}, indent=2) + '\n', encoding='utf-8')
        raise


def check_runtime(i, report_file):
    i.verify()
    fixture = i.state_dir / 'smoke-fixture'
    fixture.mkdir(parents=True, exist_ok=True)
    (fixture / 'example.py').write_text('def greet(name):\n    return "Hello " + name\n\ndef main():\n    return greet("world")\n', encoding='utf-8')
    (fixture / 'index.html').write_text('<!doctype html><title>Setup test</title><button onclick="document.querySelector(\'p\').textContent=\'Verified\'">Check</button><p>Ready</p>', encoding='utf-8')
    run(['git', 'init', '-q', fixture], env=i.env)
    for tool in ('codex', 'claude', 'graft', 'codebase-memory-mcp', 'bun', 'skills'):
        run([*tool_command(i, tool), '--version'], env=i.env)
    run([*tool_command(i, 'graft'), 'build', '--no-ignore'], cwd=fixture, env=i.env)
    run([*tool_command(i, 'graft'), 'check'], cwd=fixture, env=i.env)
    with contextlib.closing(RPC([*tool_command(i, 'codex'), 'app-server', '--listen', 'stdio://'],
                               i.env, fixture, codex=True)) as rpc:
        skills = rpc.call('skills/list', {'cwds': [str(fixture)], 'forceReload': True})['data'][0]
        counts = Counter(s['name'] for s in skills['skills'])
        if skills['errors'] or any(count > 1 for count in counts.values()):
            raise RuntimeError('Codex skill loading errors or duplicate names')
        required = {'laya-decisions', 'blog', 'gstack', 'gstack-browse', 'codebase-memory'}
        if required - counts.keys():
            raise RuntimeError('Missing Codex skills: ' + str(required - counts.keys()))
        hooks = rpc.call('hooks/list', {'cwds': [str(fixture)]})['data'][0]
        planned = i.state['configuration']['.codex/config.toml']['hooks']
        commands = {h.get('command_windows', h['command']) if i.windows else h['command']
                    for entries in planned.values() if isinstance(entries, list)
                    for entry in entries for h in entry.get('hooks', []) if 'command' in h}
        owned = [h for h in hooks['hooks'] if os.path.normcase(h['sourcePath']) == os.path.normcase(str(i.home / '.codex/config.toml'))
                 and h.get('command') in commands]
        if hooks['errors'] or len(owned) < 6 or any(h['trustStatus'] != 'trusted' or not h['enabled'] for h in owned):
            raise RuntimeError('Generated Codex hooks are not loaded, enabled and trusted')
        print(f'PASS: {len(counts)} Codex skills; {len(owned)} enabled and trusted hooks')
    blog = i.sources / 'claude-blog'
    post = fixture / 'setup-check.md'
    post.write_text('---\ntitle: Setup check\ndescription: Local rendering test\ndate: 2026-09-23\nauthor: Setup verifier\n---\n\nThe blog rendering runtime works.\n', encoding='utf-8')
    rendered = fixture / 'rendered'
    from setup import venv_python
    run([venv_python(blog / '.venv'), blog / 'scripts/blog_render.py', '--md', post,
         '--out-dir', rendered, '--pdf-engine', 'playwright', '--json'], env=i.env)
    if not any(p.read_bytes().startswith(b'%PDF') for p in rendered.glob('*.pdf')):
        raise RuntimeError('Blog renderer did not produce a PDF')
    config = tomllib.loads((i.home / '.codex/config.toml').read_text(encoding='utf-8'))
    for name in ('codebase-memory-mcp', 'graft', 'playwright'):
        spec = config['mcp_servers'][name]
        server_env = dict(i.env, **spec.get('env', {}))
        with contextlib.closing(RPC([spec['command'], *spec.get('args', [])], server_env, fixture)) as rpc:
            listed = rpc.call('tools/list', {})
            if not listed.get('tools'):
                raise RuntimeError(f'{name}: empty tools list')
            if name == 'codebase-memory-mcp':
                result = rpc.call('tools/call', {'name': 'index_repository', 'arguments': {
                    'repo_path': str(fixture), 'mode': 'fast', 'persistence': False, 'name': 'ai-setup-smoke'}})
                found = rpc.call('tools/call', {'name': 'search_graph', 'arguments': {
                    'project': 'ai-setup-smoke', 'name_pattern': 'greet'}})
                if 'greet' not in json.dumps(found) or 'example.py' not in json.dumps(found):
                    raise RuntimeError('Codebase Memory did not return the indexed fixture function')
                rpc.call('tools/call', {'name': 'check_index_coverage', 'arguments': {
                    'project': 'ai-setup-smoke', 'paths': ['example.py']}})
            elif name == 'playwright':
                class Handler(http.server.SimpleHTTPRequestHandler):
                    def __init__(self, *a, **kw):
                        super().__init__(*a, directory=str(fixture), **kw)
                    def log_message(self, *a):
                        pass
                with http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler) as server:
                    threading.Thread(target=server.serve_forever, daemon=True).start()
                    try:
                        rpc.call('tools/call', {'name': 'browser_navigate', 'arguments': {
                            'url': f'http://127.0.0.1:{server.server_port}/index.html'}})
                        rpc.call('tools/call', {'name': 'browser_click', 'arguments': {'target': 'button'}})
                        result = rpc.call('tools/call', {'name': 'browser_snapshot', 'arguments': {}})
                        if 'Verified' not in json.dumps(result):
                            raise RuntimeError('Browser button did not change the visible result')
                        browse = i.sources / ('gstack/browse/dist/browse.exe' if i.windows else 'gstack/browse/dist/browse')
                        browser_env = dict(i.env, BROWSE_STATE_FILE=str(fixture / 'gstack-browser.json'))
                        try:
                            run([browse, 'goto', f'http://127.0.0.1:{server.server_port}/index.html'],
                                cwd=fixture, env=browser_env, timeout=120)
                            snapshot = capture([browse, 'snapshot'], cwd=fixture, env=browser_env, timeout=120)
                            if 'Check' not in snapshot or 'Ready' not in snapshot:
                                raise RuntimeError('gstack browser did not load the test page')
                        finally:
                            run([browse, 'stop'], cwd=fixture, env=browser_env, timeout=30)
                        rpc.call('tools/call', {'name': 'browser_close', 'arguments': {}})
                    finally:
                        server.shutdown()
            print(f'PASS: {name} real MCP flow')
    agents = capture([*tool_command(i, 'claude'), 'agents', '--setting-sources', 'user'], env=i.env)
    for path in (i.home / '.claude/agents').glob('*.md'):
        if path.stem not in agents:
            raise RuntimeError('Claude did not list role: ' + path.stem)
    plugins = json.loads(capture([*tool_command(i, 'codex'), 'plugin', 'list', '--json'], env=i.env))
    if not any(p.get('pluginId') == 'figma@ai-setup-providers' and p.get('enabled')
               for p in plugins.get('installed', [])):
        raise RuntimeError('Official Figma plugin is not installed and enabled')
    run([sys.executable, i.home / '.agents/skills/laya-decisions/scripts/test_predict.py'], env=i.env)
    i.verify()
    report = {'status': 'passed', 'checks': ['managed files', 'CLI versions', 'Graft build/check',
              'Codebase Memory MCP index/search/coverage', 'Graft MCP initialize/tools',
              'Playwright MCP navigate/click/assert', 'Claude agent listing', 'Codex plugin listing'],
              'not_tested': ['paid model workflows', 'private remote MCPs', 'Figma OAuth/design access',
                             'Laya authenticated predictions']}
    report['checks'] += ['Codex skill discovery and trusted hooks', 'Blog HTML/PDF render',
                         'gstack browser navigate/snapshot', 'Laya offline regressions']
    report['platform'] = sys.platform
    report_file.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('PASS: local runtime smoke checks. Report: ' + str(i.state_dir / 'smoke-report.json'))


if __name__ == '__main__':
    main()

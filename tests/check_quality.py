"""Real local CLI smoke checks using disposable synthetic inputs; no model calls."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from setup import Installer, ROOT
from quality_runtime import install, verify


def check(i):
    verify(i)
    commands = i.state['quality']['commands']
    env = dict(i.env, PROMPTFOO_DISABLE_TELEMETRY='1', PYTHONDONTWRITEBYTECODE='1',
               PROMPTFOO_PYTHON=str(sys.executable), SCHEMATHESIS_TELEMETRY='false')
    env.pop('AI_SETUP_RUN_AGENT_EVALS', None)
    results = {}
    with tempfile.TemporaryDirectory(prefix='quality-check-', dir=i.state_dir) as tmp:
        root = Path(tmp)
        def run(name, args, expected=0, stdin=None):
            result = subprocess.run([*commands[name], *args], cwd=root, env=env, text=True,
                                    input=stdin, capture_output=True, timeout=120)
            if (expected == 0 and result.returncode != 0) or (expected != 0 and result.returncode == 0):
                raise AssertionError(f'{name} unexpected exit {result.returncode}:\n{result.stdout}\n{result.stderr}')
            return result
        ast = run('ast-grep', ['run', '--lang', 'javascript', '--pattern', 'console.log($$$ARGS)', '--json', '--stdin'],
                  stdin='console.log("fixture"); console.error("keep");')
        matches = json.loads(ast.stdout)
        assert len(matches) == 1 and 'fixture' in matches[0]['text']
        results['ast-grep'] = 'PASS: real syntax match excludes different call'
        subprocess.run(['git', 'init', '-q', str(root)], check=True, env=env)
        run('rtk', ['git', 'status'])
        failed = run('rtk', ['git', 'show', 'no-such-fixture-revision'], expected=1)
        assert failed.stdout or failed.stderr
        results['rtk'] = 'PASS: git status and nonzero invalid revision; no hooks'
        run('chrome-devtools', ['performance_start_trace', '--help'])
        results['chrome-devtools'] = 'PASS: profiling command available; browser session SKIPPED'

        # Exercise the real Promptfoo runner with deterministic provider output.
        # This is deliberately not a model-quality or skill-triggering benchmark.
        (root / 'provider.py').write_text('def call_api(prompt, options, context):\n    return {"output": prompt}\n')
        config = {'prompts': ['{{value}}'], 'providers': ['file://provider.py'],
                  'tests': [{'vars': {'value': 'fixture'}, 'assert': [{'type': 'equals', 'value': 'fixture'}]}]}
        config_path = root / 'promptfoo.json'; config_path.write_text(json.dumps(config))
        run('promptfoo', ['eval', '-c', str(config_path), '--no-cache', '--no-write', '--max-concurrency', '1', '-o', str(root / 'pass.json')])
        config['tests'][0]['assert'][0]['value'] = 'deliberately-wrong'
        config_path.write_text(json.dumps(config))
        run('promptfoo', ['eval', '-c', str(config_path), '--no-cache', '--no-write', '--max-concurrency', '1'], expected=1)
        results['promptfoo'] = 'PASS: real runner accepts correct and rejects wrong oracle; no model calls'

        class API(BaseHTTPRequestHandler):
            broken = False
            def log_message(self, *args):
                pass
            def do_GET(self):
                if self.path == '/openapi.json':
                    body = {'openapi': '3.0.3', 'info': {'title': 'Disposable fixture', 'version': '1'},
                        'servers': [{'url': f'http://127.0.0.1:{self.server.server_port}'}],
                        'paths': {'/ping': {'get': {'responses': {'200': {'description': 'OK',
                          'content': {'application/json': {'schema': {'type':'object','required':['ok'],
                            'properties': {'ok': {'type':'boolean'}}}}}}}}}}}
                    code = 200
                elif self.path == '/ping':
                    body, code = {'ok': True}, (500 if self.broken else 200)
                else:
                    body, code = {}, 404
                data = json.dumps(body).encode()
                self.send_response(code); self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(data))); self.end_headers(); self.wfile.write(data)
        server = ThreadingHTTPServer(('127.0.0.1', 0), API)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            args = ['run', f'http://127.0.0.1:{server.server_port}/openapi.json', '--max-examples', '2',
                    '--workers', '1', '--mode', 'positive', '--phases', 'fuzzing']
            run('schemathesis', args)
            API.broken = True
            run('schemathesis', args, expected=1)
            results['schemathesis'] = 'PASS: real HTTP contract checks accept healthy and reject HTTP 500 fixture'
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=5)
    report = {'platform': sys.platform, 'checks': results, 'model_benchmark': 'SKIPPED',
              'app_browser_storybook_checks': 'SKIPPED: require authorized app configuration'}
    destination = i.state_dir / 'quality-report.json'
    destination.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--home', type=Path, default=Path.home())
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    installer = Installer(args.home, json.loads((ROOT / 'manifest.json').read_text()))
    if args.install:
        install(installer)
    check(installer)

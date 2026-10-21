"""Promptfoo provider for real installed agents with independent artifact checks.

No model call is made without AI_SETUP_RUN_AGENT_EVALS=1. Workspaces are disposable
but not OS isolation; use only reviewed synthetic cases and normal client controls.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

CASES = {
    'bug': ({'app.py': 'def total(values):\n    return sum(values) + 1\n'},
            'Fix total(values) in app.py to sum numbers, including empty and negative inputs.'),
    'refactor': ({'app.py': 'def classify(n):\n    if n < 0:\n        return "negative"\n    if n == 0:\n        return "zero"\n    return "positive"\n'},
                 'Refactor classify in app.py to one return statement, preserving behavior for all numbers.'),
    'responsive': ({'index.html': '<!doctype html><html lang="en"><title>Sample</title><main></main></html>'},
                   'Create a self-contained responsive settings screen in index.html with a main landmark, '
                   'explicitly labeled email input, native Save button, viewport metadata and responsive CSS. '
                   'No external assets. This is a synthetic structural test; do not claim browser verification.'),
    'recall': ({'history.md': 'Superseded: retry every failed request. Replaced by current.md.\n',
                'current.md': 'Reviewed synthetic lesson: retry transient errors with bounded backoff; '
                              'never retry authentication failures. Source: current.md, revision fixture-v1.\n'},
               'Read the supplied lesson files. Write answer.json with source, revision, retry_auth_failures '
               '(boolean), and bounded_backoff (boolean), using current rather than superseded advice.'),
    'irrelevant': ({}, 'Write answer.txt containing only the result of 2 + 2. No research, skills, other files or commands are needed beyond writing the answer.'),
    'recovery': ({'data/input.json': '{"numbers":[3,5,8]}'},
                 'The suggested input at input.json is missing. Find the actual input inside this workspace, '
                 'sum its numbers and write answer.json with total and source. Do not invent or fetch data.'),
}


def grade(task, workspace):
    """Never trust the agent's claimed tests or summary. Oracle stays outside workspace."""
    if task in ('bug', 'refactor'):
        checks = ("assert [m.total(x) for x in ([],[1,2],[-3,1],[0.5,1.5])] == [0,3,-2,2]"
                  if task == 'bug' else
                  "assert [m.classify(x) for x in (-10,-0.1,0,0.1,9)] == ['negative','negative','zero','positive','positive']; "
                  "import ast; t=ast.parse(p.read_text()); f=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='classify'); "
                  "assert sum(isinstance(n,ast.Return) for n in ast.walk(f)) == 1")
        code = ('import importlib.util,pathlib; p=pathlib.Path("app.py"); '
                's=importlib.util.spec_from_file_location("candidate",p); '
                'm=importlib.util.module_from_spec(s); s.loader.exec_module(m); ' + checks)
        result = subprocess.run([sys.executable, '-I', '-B', '-c', code], cwd=workspace,
                                capture_output=True, text=True, timeout=20)
        return result.returncode == 0, 'independent behavior/AST checks', result.stderr[-4000:]
    if task == 'responsive':
        from html.parser import HTMLParser
        class Elements(HTMLParser):
            def __init__(self):
                super().__init__(); self.tags = []
            def handle_starttag(self, tag, attrs):
                self.tags.append((tag, dict(attrs)))
        html = (workspace / 'index.html').read_text()
        parsed = Elements(); parsed.feed(html)
        labels = {a.get('for') for t, a in parsed.tags if t == 'label'}
        passed = (any(t == 'main' for t, a in parsed.tags)
                  and any(t == 'button' for t, a in parsed.tags)
                  and any(t == 'input' and a.get('type') == 'email' and a.get('id') in labels for t, a in parsed.tags)
                  and any(t == 'meta' and a.get('name') == 'viewport' for t, a in parsed.tags)
                  and ('@media' in html or 'clamp(' in html))
        return passed, 'HTML structural check only; browser/visual review required', ''
    if task == 'irrelevant':
        files = {p.relative_to(workspace).as_posix() for p in workspace.rglob('*') if p.is_file() and '.git' not in p.parts}
        return (workspace / 'answer.txt').read_text().strip() == '4' and files == {'answer.txt'}, 'artifact minimality; inspect trace for unnecessary skill reads', ''
    answer = json.loads((workspace / 'answer.json').read_text())
    expected = ({'source': 'current.md', 'revision': 'fixture-v1', 'retry_auth_failures': False, 'bounded_backoff': True}
                if task == 'recall' else {'total': 16, 'source': 'data/input.json'})
    return all(answer.get(k) == v for k, v in expected.items()), 'source and result checks', ''


def command(agent, workspace, prompt):
    executable = shutil.which(agent)
    if not executable:
        raise ValueError(f'{agent} is not installed/on PATH')
    if agent == 'codex':
        return [executable, 'exec', '--json', '--sandbox', 'workspace-write', '--skip-git-repo-check', '-C', str(workspace), prompt]
    if agent == 'claude':
        return [executable, '-p', '--output-format', 'json', '--permission-mode', 'acceptEdits',
                '--allowedTools', 'Read,Edit,Write,Glob,Grep', '--', prompt]
    raise ValueError('Only installed Claude and Codex CLIs are supported')


def call_api(prompt, options, context):
    if os.environ.get('AI_SETUP_RUN_AGENT_EVALS') != '1':
        return {'error': 'Set AI_SETUP_RUN_AGENT_EVALS=1 only after reviewing scope, authentication and usage budget.'}
    config = options.get('config', {})
    task = context.get('vars', {}).get('task', prompt.strip())
    if task not in CASES:
        return {'error': 'Unknown frozen evaluation case'}
    agent = config.get('agent', 'codex')
    output_root = Path(os.environ.get('AI_SETUP_EVAL_OUTPUT', '.ai-local/evaluations')).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    run_root = Path(tempfile.mkdtemp(prefix=task + '-', dir=output_root))
    workspace = run_root / 'workspace'; workspace.mkdir()
    files, instruction = CASES[task]
    for name, content in files.items():
        target = workspace / name; target.parent.mkdir(parents=True, exist_ok=True); target.write_text(content)
    started = time.monotonic()
    result = {'passed': False, 'case': task, 'agent': agent,
              'label': os.environ.get('AI_SETUP_EVAL_LABEL', 'active-user-configuration'),
              'evidence': str(run_root), 'model_cost': None}
    try:
        text = ('Work only inside this synthetic fixture directory. Do not use external services, MCP, '
                'network, credentials, other projects or publication tools. Do not edit outside it. ' + instruction)
        argv = command(agent, workspace, text)
        result['cli_version'] = subprocess.check_output([argv[0], '--version'], text=True, timeout=30).strip()
        completed = subprocess.run(argv, cwd=workspace, text=True, capture_output=True,
                                   timeout=min(int(config.get('timeout', 300)), 900))
        (run_root / 'stdout.txt').write_text(completed.stdout, encoding='utf-8')
        (run_root / 'stderr.txt').write_text(completed.stderr, encoding='utf-8')
        result['exit_code'] = completed.returncode
        passed, coverage, failure = grade(task, workspace)
        result.update(passed=completed.returncode == 0 and passed, check_coverage=coverage, failure=failure)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        result['failure'] = str(exc)
    result['elapsed_seconds'] = round(time.monotonic() - started, 3)
    (run_root / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return {'output': json.dumps(result)}

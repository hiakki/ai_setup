"""Exercise installed design providers and Context Mode without models or credentials."""
import argparse
import contextlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from setup import Installer, capture, run
from smoke import RPC
import contextmode_runtime


def check_antislop(i):
    spec = next(s for s in i.manifest['sources'] if s['id'] == 'anti-slop')
    source = i.sources / spec['id']
    assert capture(['git', '-C', source, 'rev-parse', 'HEAD'], env=i.env).strip() == spec['revision']
    for entry in spec['skills']:
        target = i.home / '.agents/skills' / entry['name']
        for original in (source / entry['path']).rglob('*'):
            if not original.is_file():
                continue
            installed = target / original.relative_to(source / entry['path'])
            if original.name == 'SKILL.md':
                expected = original.read_text(encoding='utf-8')
                for old, new in entry.get('link_rewrites', {}).items():
                    expected = expected.replace(old, new)
                assert installed.read_text(encoding='utf-8') == expected
            else:
                assert installed.read_bytes() == original.read_bytes()
        assert (target / 'LICENSE').read_bytes() == (source / 'LICENSE').read_bytes()
        link = i.home / '.claude/skills' / entry['name']
        assert (link / 'SKILL.md').read_bytes() == (target / 'SKILL.md').read_bytes()
        i.owned(target)
        i.owned(link)
    for config in (i.home / '.codex/AGENTS.md', i.home / '.claude/CLAUDE.md'):
        assert config.read_text(encoding='utf-8').count('<!-- ai-setup:antislop:start -->') == 1
    script = i.home / '.agents/skills/antislop-human/contrast-check.py'
    run([sys.executable, script, '--selftest'], env=i.env)
    for foreground, expected in (('#000000', 0), ('#777777', 1)):
        result = subprocess.run([sys.executable, str(script), '#FFFFFF', foreground],
                                env=i.env, capture_output=True, text=True)
        assert result.returncode == expected, result.stdout + result.stderr
        assert ('normal text (4.5:1): PASS' if expected == 0 else 'normal text (4.5:1): FAIL') in result.stdout


def check(i):
    check_antislop(i)
    contextmode_runtime.verify(i)
    skill = i.home / '.agents/skills/logo-design'
    assert (skill / 'LICENSE').is_file() and (skill / 'TRADEMARKS.md').is_file()
    assert (i.home / '.claude/skills/logo-design/SKILL.md').read_bytes() == (skill / 'SKILL.md').read_bytes()
    with tempfile.TemporaryDirectory(prefix='design-context-', dir=i.state_dir) as temp:
        root = Path(temp)
        fixture = root / 'project with spaces'
        fixture.mkdir()
        run(['git', 'init', '-q', fixture], env=i.env)
        logo = fixture / 'sample.svg'
        logo.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><title>Test mark</title><path fill="#123456" d="M20 80 L50 20 L80 80 Z"/></svg>', encoding='utf-8')
        report = json.loads(capture([sys.executable, skill / 'scripts/svg_audit.py', logo, '--json'], env=i.env))
        assert report, 'SVG audit returned no result'
        variants = fixture / 'variants'
        run([sys.executable, skill / 'scripts/export_variants.py', logo, '--out-dir', variants], env=i.env)
        for name in ('sample-black.svg', 'sample-white.svg', 'sample-favicon.svg', 'sample-app-icon.svg'):
            ET.parse(variants / name)
        preview = fixture / 'preview.html'
        run([sys.executable, skill / 'scripts/preview_sheet.py', logo, '-o', preview], env=i.env)
        assert '16' in preview.read_text(encoding='utf-8') and preview.stat().st_size > 1000
        token = 'verified-' + uuid.uuid4().hex
        label = 'ai-setup-check-' + uuid.uuid4().hex
        large = fixture / 'large.json'
        large.write_text(json.dumps([{'index': n, 'status': 'failed' if n == 731 else 'passed',
                                     'detail': 'fixture log record ' * 8} for n in range(1000)]), encoding='utf-8')
        configurations = [
            tomllib.loads((i.home / '.codex/config.toml').read_text(encoding='utf-8'))['mcp_servers']['context-mode'],
            json.loads((i.home / '.claude.json').read_text(encoding='utf-8'))['mcpServers']['context-mode'],
        ]
        for config in configurations:
            env = dict(i.env, **config['env'])
            # No raw transcripts or production files; isolate all test databases.
            env['CONTEXT_MODE_DIR'] = str(root / 'context-data')
            with contextlib.closing(RPC([config['command'], *config['args']], env, fixture)) as rpc:
                names = {t['name'] for t in rpc.call('tools/list', {})['tools']}
                assert {'ctx_execute', 'ctx_index', 'ctx_search', 'ctx_stats'} <= names
                result = rpc.call('tools/call', {'name': 'ctx_execute', 'arguments': {
                    'language': 'javascript', 'code': 'console.log("sum=" + (19+23))', 'timeout': 10000}})
                assert 'sum=42' in json.dumps(result), result
                result = rpc.call('tools/call', {'name': 'ctx_execute_file', 'arguments': {
                    'path': str(large), 'language': 'javascript', 'timeout': 10000,
                    'code': 'const rows=JSON.parse(FILE_CONTENT); console.log("rows="+rows.length+"; failures="+rows.filter(r=>r.status==="failed").map(r=>r.index).join(","));'}})
                output = json.dumps(result)
                assert 'rows=1000; failures=731' in output, result
                assert len(output) < large.stat().st_size / 10, 'Raw log flooded the response'
                rpc.call('tools/call', {'name': 'ctx_index', 'arguments': {
                    'content': '# Gateway recovery\n\nThe reviewed resolution identifier is ' + token + '.', 'source': label}})
                result = rpc.call('tools/call', {'name': 'ctx_search', 'arguments': {
                    'queries': ['gateway recovery'], 'source': label, 'limit': 3}})
                assert token in json.dumps(result), result
        other = root / 'unrelated project'
        other.mkdir()
        run(['git', 'init', '-q', other], env=i.env)
        with contextlib.closing(RPC([configurations[0]['command'], *configurations[0]['args']], env, other)) as rpc:
            rpc.call('tools/call', {'name': 'ctx_index', 'arguments': {
                'content': '# Local fixture\n\nThis unrelated project has no gateway decisions.',
                'source': 'other-project'}})
            result = rpc.call('tools/call', {'name': 'ctx_search', 'arguments': {
                'queries': ['gateway recovery'], 'source': label}})
            assert token not in json.dumps(result), 'Project data leaked into another project search'
    contextmode_runtime.verify(i)
    for path in (skill, i.home / '.claude/skills/logo-design'):
        i.owned(path)
    return {'result': 'pass', 'platform': sys.platform,
            'checks': ['Anti Slop six skills, provider pin, licenses, routing and contrast',
                       'SVG audit', 'SVG delivery variants', 'HTML preview generation',
                       'Codex and Claude MCP execution', 'large file reduction', 'index and search', 'project separation',
                       'provider files unchanged after use'],
            'not_tested': ['model output quality', 'automatic hooks/session recovery', 'remote machine installation']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, default=Path.home())
    parser.add_argument('--install', action='store_true', help='Install/rerun only these providers in a test home')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
    home = args.home.resolve()
    if args.install:
        home.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=home) as temp:
            for source in manifest['sources']:
                if source['id'] not in ('logo-design', 'anti-slop'):
                    source.pop('skills', None)
            selected = Path(temp) / 'manifest.json'
            selected.write_text(json.dumps(manifest), encoding='utf-8')
            for _ in range(2):
                run([sys.executable, ROOT / 'setup.py', 'install', '--home', home,
                     '--manifest', selected, '--only', 'skills,contextmode'])
    i = Installer(home, manifest)
    report = check(i)
    (i.state_dir / 'design-context-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

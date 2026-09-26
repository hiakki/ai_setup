"""Exercise installed optional CLIs and UI provider skills without scans or credentials.

Run after install.sh/install.ps1 --only context7,strix,skillui, with the same home.
Fetches just the UI skill provider, then repeats setup to check idempotence.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from setup import command_args


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, required=True)
    args = parser.parse_args()
    home = args.home.resolve()
    state_dir = home / '.local/state/ai-setup'
    with tempfile.TemporaryDirectory(prefix='web-tools-check-', dir=state_dir) as temporary:
        temporary = Path(temporary)
        manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
        manifest['sources'] = [s for s in manifest['sources'] if s['id'] in ('ui-skills', 'strix')]
        selected = temporary / 'manifest.json'
        selected.write_text(json.dumps(manifest), encoding='utf-8')
        command = [sys.executable, str(ROOT / 'setup.py'), 'install', '--home', str(home),
                   '--manifest', str(selected), '--only', 'context7,skills,strix,skillui']
        for _ in range(2):
            subprocess.run(command, check=True)
        for name in ('create-design-md', 'fixing-metadata', 'penetration-testing-with-strix'):
            skill = home / '.agents/skills' / name / 'SKILL.md'
            assert 'name: ' + name in skill.read_text(encoding='utf-8'), name
            assert (home / '.claude/skills' / name / 'SKILL.md').read_bytes() == skill.read_bytes()
        fixture = temporary / 'fixture with spaces'
        fixture.mkdir()
        (fixture / 'package.json').write_text('{"name":"design-fixture","version":"1.0.0"}', encoding='utf-8')
        (fixture / 'styles.css').write_text(':root { --color-primary: #123456; }\nbutton { color: var(--color-primary); }\n', encoding='utf-8')
        output = temporary / 'generated'
        terminal = home / '.local/bin' / ('skillui.cmd' if sys.platform == 'win32' else 'skillui')
        subprocess.run(command_args([terminal, '--dir', fixture, '--out', output,
                                     '--name', 'fixture', '--format', 'design-md']), check=True)
        designs = list(output.rglob('DESIGN.md'))
        assert designs and '#123456' in designs[0].read_text(encoding='utf-8').lower(), 'Design token missing'
        subprocess.run([sys.executable, str(ROOT / 'setup.py'), 'verify', '--home', str(home)], check=True)
    report = {'result': 'pass', 'platform': sys.platform,
              'checks': ['Context7 registration', 'upstream UI and Strix skills',
                         'Strix version/help', 'SkillUI local CSS extraction', 'repeat installation'],
              'not_tested': ['authenticated scans', 'Docker sandbox', 'cloud uploads',
                             'browser extraction', 'live Context7 query']}
    (state_dir / 'web-tools-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('PASS: ' + ', '.join(report['checks']))


if __name__ == '__main__':
    main()

"""Exercise installed Agent Reach tools on local fixtures, without social login."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from setup import Installer, ROOT, command_args
from agentreach_runtime import verify


def check(i):
    verify(i)
    def run(name, args, expected=0):
        launcher = i.bin / (name + ('.cmd' if i.windows else ''))
        result = subprocess.run(command_args([launcher, *args], env=i.env), env=i.env,
                                capture_output=True, text=True, encoding='utf-8', timeout=90)
        if result.returncode != expected:
            raise AssertionError(f'{name} exit={result.returncode}: {result.stderr[-1500:]}')
        return result.stdout

    assert '1.5.0' in run('agent-reach', ['--version'])
    # PyPI normalizes date-version zeros; the CLI prints e.g. 2026.08.19.
    assert tuple(map(int, run('agent-reach-yt-dlp', ['--version']).strip().split('.'))) == tuple(
        map(int, i.manifest['agent_reach']['yt_dlp'].split('.')))
    assert run('opencli', ['--version']).strip() == i.manifest['agent_reach']['opencli']['version']
    for name in ('facebook', 'instagram', 'reddit'):
        adapters = json.loads(run('opencli', ['list', '--site', name, '--limit', '100']))
        assert adapters['ok'] and any(entry['command'] == name + ' search'
                                      for entry in adapters['data']['commands']), f'Missing {name} search adapter'

    class Fixture(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass
        def do_HEAD(self):
            self.do_GET(head=True)
        def do_GET(self, head=False):
            if self.path == '/feed':
                data = b'<rss version="2.0"><channel><title>Fixture</title><item><title>Verified research</title><link>https://example.com/evidence</link></item></channel></rss>'
                content_type = 'application/rss+xml'
            elif self.path == '/video.mp4':
                # Metadata extraction only: no claim that this is a decoded video.
                data, content_type = b'\0' * 128, 'video/mp4'
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            if not head:
                self.wfile.write(data)

    server = ThreadingHTTPServer(('127.0.0.1', 0), Fixture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f'http://127.0.0.1:{server.server_port}'
    try:
        rss = run('agent-reach-python', ['-c',
            'import sys,requests,feedparser; r=requests.get(sys.argv[1],timeout=10); '
            'r.raise_for_status(); f=feedparser.parse(r.content); '
            'assert not f.bozo; print(f.entries[0].title)', base + '/feed'])
        assert rss.strip() == 'Verified research'
        args = ['--ignore-config', '--no-playlist', '--skip-download', '--dump-single-json',
                '--socket-timeout', '10', '--retries', '0']
        media = json.loads(run('agent-reach-yt-dlp', [*args, base + '/video.mp4']))
        assert media['ext'] == 'mp4'
        assert media.get('url') == base + '/video.mp4' or any(
            f.get('url') == base + '/video.mp4' for f in media.get('formats', []))
        run('agent-reach-yt-dlp', [*args, base + '/missing.mp4'], expected=1)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    skill = i.home / '.agents/skills/agent-reach'
    assert (i.home / '.claude/skills/agent-reach').resolve() == skill.resolve()
    for name in ('SKILL.md', 'LICENSE', 'references/ai-setup.md', 'references/social.md'):
        assert (skill / name).is_file()
    report = {'status': 'passed', 'platform': sys.platform,
              'checks': ['real launchers', 'OpenCLI adapter discovery', 'RSS HTTP fetch/parse',
                         'video metadata extraction', 'missing media rejected', 'shared skill linkage'],
              'not_tested': ['social login', 'Browser Bridge', 'live video sites', 'visual understanding']}
    print(json.dumps(report, indent=2))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, default=Path.home())
    args = parser.parse_args()
    i = Installer(args.home, json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8')))
    path = i.state_dir / 'agent-reach-report.json'
    path.unlink(missing_ok=True)
    try:
        report = check(i)
    except Exception as exc:
        path.write_text(json.dumps({'status': 'failed', 'error': str(exc)}, indent=2), encoding='utf-8')
        raise
    path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()

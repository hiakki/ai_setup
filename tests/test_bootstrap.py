"""Exercise cached bootstrap control flow without downloading or changing a host."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipIf(os.name == 'nt', 'POSIX bootstrap; native PowerShell has its own harness')
class BootstrapTests(unittest.TestCase):
    def test_cached_checkout_refreshes_and_preserves_failures(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home, commands = root / 'home with spaces', root / 'bin'
            commands.mkdir()
            repo = home / '.local/share/ai-setup-repo'
            repo.mkdir(parents=True)
            state = home / '.local/state/ai-setup/state.json'
            state.parent.mkdir(parents=True)
            state.write_text('{}')
            (repo / 'install.sh').write_text('printf "%s\\n" "$@" > "$BOOTSTRAP_ARGUMENTS"\n')
            git = commands / 'git'
            git.write_text(f'''#!{sys.executable}
import json, os, sys
args=sys.argv[1:]
with open(os.environ['BOOTSTRAP_LOG'], 'a') as stream:
    stream.write(json.dumps(args) + '\\n')
command=args[2]
if command == 'remote': print('https://github.com/hiakki/ai_setup.git')
elif command == 'status': print(os.environ.get('BOOTSTRAP_DIRTY', ''))
elif command == 'branch': print('main')
elif command == 'pull': sys.exit(int(os.environ.get('BOOTSTRAP_PULL_EXIT', '0')))
''')
            git.chmod(0o755)
            for number, (dirty, pull_exit) in enumerate((('', 0), (' M setup.py', 0), ('', 17))):
                log, arguments = root / f'log-{number}', root / f'args-{number}'
                env = dict(os.environ, HOME=str(home), PATH=str(commands) + os.pathsep + os.environ['PATH'],
                           BOOTSTRAP_LOG=str(log), BOOTSTRAP_ARGUMENTS=str(arguments),
                           BOOTSTRAP_DIRTY=dirty, BOOTSTRAP_PULL_EXIT=str(pull_exit))
                result = subprocess.run(['bash', str(ROOT / 'bootstrap.sh'), '--only', 'custom'],
                                        env=env, capture_output=True, text=True, timeout=20)
                success = not dirty and pull_exit == 0
                self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
                self.assertEqual(arguments.exists(), success)
                if success:
                    self.assertEqual(arguments.read_text().splitlines(), ['sync', '--only', 'custom'])
                calls = [json.loads(line) for line in log.read_text().splitlines()]
                self.assertEqual(any(call[2:] == ['pull', '--ff-only', 'origin', 'main'] for call in calls), not dirty)


if __name__ == '__main__':
    unittest.main()

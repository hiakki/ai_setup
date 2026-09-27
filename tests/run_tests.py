"""Run installer tests without inheriting the operator's global Git guard/config."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exclude', action='append', default=[], help='Explicit test filename to omit')
    parser.add_argument('--isolated-child', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.isolated_child:
        sys.path.insert(0, str(root))
        suite = unittest.TestSuite()
        for path in sorted((root / 'tests').glob('test_*.py')):
            if path.name not in args.exclude:
                suite.addTests(unittest.defaultTestLoader.discover(str(root / 'tests'), pattern=path.name))
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return int(not result.wasSuccessful())
    work = root / '.work'
    work.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='suite-home-', dir=work) as folder:
        env = dict(os.environ, HOME=folder, USERPROFILE=folder, XDG_CONFIG_HOME=str(Path(folder) / '.config'))
        for key in list(env):
            if key.startswith('GIT_CONFIG_') or key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'):
                env.pop(key)
        env['GIT_CONFIG_NOSYSTEM'] = '1'
        return subprocess.run([sys.executable, str(Path(__file__).resolve()), '--isolated-child',
                               *sys.argv[1:]], cwd=root, env=env).returncode


if __name__ == '__main__':
    raise SystemExit(main())

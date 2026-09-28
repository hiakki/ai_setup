"""Compare local Markdown/RST inventories; observation is never semantic review.

Python 3.11+ standard library only. No network, source execution, Git writes or content export.
Snapshots contain local paths and hashes and should stay outside version control.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys


SKIP_DIRS = {'node_modules', 'Pods', 'vendor', 'venv', '__pycache__', 'graft',
             'dist', 'build', 'output', 'coverage'}
EXTENSIONS = {'.md', '.mdx', '.rst'}


def is_link(path):
    # lstat detects Windows junctions/reparse points even on Python 3.11.
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def inventory(root, excluded):
    """Fail on unreadable input; never silently return a partial success."""
    files, links = {}, []

    def walk_error(error):
        raise error

    for directory, dirs, names in os.walk(root, followlinks=False, onerror=walk_error):
        base = Path(directory)
        keep = []
        for name in sorted(dirs):
            path = base / name
            rel = path.relative_to(root).as_posix()
            if is_link(path):
                links.append(rel)
            elif not name.startswith('.') and name not in SKIP_DIRS and rel not in excluded:
                keep.append(name)
        dirs[:] = keep
        for name in sorted(names):
            path = base / name
            rel = path.relative_to(root).as_posix()
            if name.startswith('.') or path.suffix.lower() not in EXTENSIONS or rel in excluded:
                continue
            if is_link(path):
                links.append(rel)
                continue
            before = path.stat()
            digest = hashlib.sha256()
            with path.open('rb') as stream:
                for block in iter(lambda: stream.read(65536), b''):
                    digest.update(block)
            after = path.stat()
            if (before.st_size, before.st_mtime_ns, before.st_ino) != (
                    after.st_size, after.st_mtime_ns, after.st_ino):
                raise ValueError('Source changed during scan; retry: ' + rel)
            files[rel] = digest.hexdigest()
    return dict(sorted(files.items())), sorted(links)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path, help='Explicit authorized directory')
    parser.add_argument('--exclude', action='append', default=[],
                        help='Exact root-relative file/directory to exclude; repeatable')
    parser.add_argument('--baseline', type=Path, help='Earlier inventory with identical scope')
    parser.add_argument('--snapshot', type=Path, help='Create a NEW local inventory; never overwrite')
    args = parser.parse_args(argv)
    if sys.version_info < (3, 11):
        parser.error('Python 3.11+ is required')
    try:
        root = args.root.expanduser().resolve(strict=True)
        if not root.is_dir():
            raise ValueError('Root is not a directory')
        excluded = []
        for item in args.exclude:
            path = PurePosixPath(item.replace('\\', '/'))
            if path.is_absolute() or '..' in path.parts or str(path) == '.' or ':' in str(path):
                raise ValueError('Exclusions must be root-relative paths')
            excluded.append(path.as_posix())
        scope = {'root': str(root), 'exclude': sorted(set(excluded)),
                 'skip_dirs': sorted(SKIP_DIRS), 'extensions': sorted(EXTENSIONS),
                 'hidden': 'excluded', 'links': 'not-followed', 'gitignore': 'not-interpreted'}
        previous = {}
        if args.baseline:
            old = json.loads(args.baseline.read_text(encoding='utf-8'))
            if not isinstance(old, dict) or old.get('version') != 1 or not isinstance(old.get('files'), dict):
                raise ValueError('Invalid baseline schema')
            if old.get('scope') != scope:
                raise ValueError('Baseline scope differs; compare only identical roots and exclusions')
            previous = old['files']
            if any(not isinstance(k, str) or not isinstance(v, str) or
                   not re.fullmatch('[0-9a-f]{64}', v) for k, v in previous.items()):
                raise ValueError('Invalid baseline file hashes')
        if args.snapshot and args.snapshot.exists():
            raise ValueError('Snapshot already exists; choose a new path')
        files, links = inventory(root, set(excluded))
        report = {'scope': scope, 'file_count': len(files),
                  'added': sorted(files.keys() - previous.keys()),
                  'changed': sorted(k for k in files.keys() & previous.keys() if files[k] != previous[k]),
                  'removed': sorted(previous.keys() - files.keys()), 'skipped_links': links,
                  'semantic_review_performed': False,
                  'note': 'No file delta is not proof that all learning was captured. Snapshots are observations.'}
        if args.snapshot:
            snapshot = {'version': 1, 'scope': scope, 'files': files,
                        'observed_at': datetime.now(timezone.utc).isoformat(),
                        'semantic_review_performed': False}
            # Exclusive creation preserves an existing baseline, including a racing writer.
            with args.snapshot.open('x', encoding='utf-8') as stream:
                json.dump(snapshot, stream, indent=2, ensure_ascii=True)
                stream.write('\n')
        print(json.dumps(report, indent=2, ensure_ascii=True))
        return 0
    except (OSError, ValueError) as exc:
        print('Learning delta scan failed: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

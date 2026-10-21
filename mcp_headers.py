#!/usr/bin/env python3
"""Return one HTTP header from a permission-restricted dotenv file."""
import argparse
import json
import os
from pathlib import Path
import re
import sys


NAME = re.compile(r'[A-Za-z_][A-Za-z0-9_]*')
HEADER = re.compile(r'[A-Za-z0-9!#$%&\'*+.^_`|~-]+')


def dotenv_values(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('credential file is missing or linked')
    if os.name != 'nt' and path.stat().st_mode & 0o077:
        raise ValueError('credential file permissions must be 600')
    values = {}
    for number, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('export '):
            line = line[7:].lstrip()
        if '=' not in line:
            raise ValueError(f'invalid dotenv assignment on line {number}')
        name, value = line.split('=', 1)
        name, value = name.strip(), value.strip()
        if not NAME.fullmatch(name):
            raise ValueError(f'invalid dotenv name on line {number}')
        if value.startswith("'"):
            if len(value) < 2 or not value.endswith("'"):
                raise ValueError(f'invalid single-quoted value on line {number}')
            value = value[1:-1]
        elif value.startswith('"'):
            if len(value) < 2 or not value.endswith('"'):
                raise ValueError(f'invalid double-quoted value on line {number}')
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError(f'invalid double-quoted value on line {number}') from exc
        if name in values:
            raise ValueError('credential variable is assigned more than once')
        if '\r' in value or '\n' in value or '\0' in value:
            raise ValueError('credential contains an invalid control character')
        values[name] = value
    return values


def dotenv_value(path, variable):
    found = dotenv_values(path).get(variable)
    if found is None or not found.strip():
        raise ValueError('credential variable is missing or empty')
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', type=Path, required=True)
    parser.add_argument('--variable', required=True)
    parser.add_argument('--header', default='Authorization')
    parser.add_argument('--prefix', default='Bearer ')
    args = parser.parse_args()
    if not NAME.fullmatch(args.variable) or not HEADER.fullmatch(args.header):
        parser.error('invalid variable or HTTP header name')
    try:
        value = dotenv_value(args.env_file.expanduser(), args.variable)
    except (OSError, UnicodeError, ValueError) as exc:
        print('Credential helper failed: ' + str(exc), file=sys.stderr)
        return 1
    print(json.dumps({args.header: args.prefix + value}, separators=(',', ':')))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

"""Call the configured Laya service without exposing its credential."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def windows_acl(path):
    """Read SID-based DACL metadata; Windows chmod bits do not describe privacy.

    Provider reference: https://learn.microsoft.com/powershell/module/microsoft.powershell.security/get-acl
    The config path is passed as environment data, never interpolated into code.
    """
    script = '''
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$acl = Get-Acl -LiteralPath $env:LAYA_ACL_CONFIG
$sidType = [System.Security.Principal.SecurityIdentifier]
$allow = @($acl.GetAccessRules($true, $true, $sidType) |
    Where-Object { $_.AccessControlType -eq 'Allow' } |
    ForEach-Object { $_.IdentityReference.Value })
@{
    user = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    owner = $acl.GetOwner($sidType).Value
    allow = $allow
} | ConvertTo-Json -Compress
'''
    system_root = os.environ.get('SystemRoot', r'C:\Windows')
    powershell = Path(system_root) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
    try:
        result = subprocess.run([str(powershell), '-NoProfile', '-NonInteractive', '-Command', script],
                                env=dict(os.environ, SystemRoot=system_root, LAYA_ACL_CONFIG=str(path)),
                                check=True, capture_output=True, text=True, encoding='utf-8', timeout=15)
        return json.loads(result.stdout.lstrip('\ufeff'))
    except (OSError, subprocess.SubprocessError, UnicodeError, json.JSONDecodeError):
        raise ValueError('Could not verify the Windows config ACL; use LAYA_ENDPOINT and LAYA_API_TOKEN without a config file.') from None


def require_private_config(path, *, windows=None):
    windows = os.name == 'nt' if windows is None else windows
    if not windows:
        if path.stat().st_mode & 0o077:
            raise ValueError('Private config requires mode 0600; run chmod 600 on the config file.')
        return
    acl = windows_acl(path)
    if not isinstance(acl, dict) or not isinstance(acl.get('user'), str) or not acl['user'].startswith('S-1-'):
        raise ValueError('Could not verify the Windows config ACL.')
    allowed = {acl['user'], 'S-1-5-18', 'S-1-5-32-544'}  # Current user, SYSTEM, Administrators.
    grants = acl.get('allow')
    if acl.get('owner') not in allowed or not isinstance(grants, list) or not grants or \
            any(not isinstance(sid, str) or sid not in allowed for sid in grants):
        raise ValueError('Private config ACL must grant access only to the current user, SYSTEM, or Administrators; remove other permissions in Windows file security settings.')


def validate_request(payload):
    if not isinstance(payload, dict) or 'state' not in payload:
        raise ValueError('Input needs state and questions.')
    questions = payload.get('questions')
    if not isinstance(questions, dict) or not questions:
        raise ValueError('questions must be a nonempty object.')
    for question in questions.values():
        if not isinstance(question, dict) or question.get('type') not in ('choice', 'score', 'noul'):
            raise ValueError('Each question needs type choice, score, or noul.')
        if not isinstance(question.get('instructions'), str) or not question['instructions'].strip():
            raise ValueError('Each question needs nonempty instructions.')
        criteria = question.get('criteria')
        if question['type'] == 'choice' and (not isinstance(criteria, dict) or not criteria):
            raise ValueError('choice criteria must be a nonempty object.')
        if question['type'] == 'score' and (not isinstance(criteria, list) or len(criteria) < 2):
            raise ValueError('score criteria must contain at least two ordered labels.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, help='JSON request file; defaults to stdin')
    parser.add_argument('--config', type=Path, help='Defaults to ~/.config/laya/config.json')
    parser.add_argument('--timeout', type=float, default=30, help='Request timeout in seconds (1–120)')
    args = parser.parse_args(argv)
    started = time.monotonic()
    try:
        if args.config is None:
            args.config = Path.home() / '.config/laya/config.json'
        if not 1 <= args.timeout <= 120:
            raise ValueError('Timeout must be between 1 and 120 seconds.')
        config = {}
        if args.config.exists():
            require_private_config(args.config)
            config = json.loads(args.config.read_text(encoding='utf-8-sig'))
        if not isinstance(config, dict):
            raise ValueError('Config must be a JSON object.')
        endpoint = os.environ.get('LAYA_ENDPOINT') or config.get('endpoint', '')
        token = os.environ.get('LAYA_API_TOKEN') or config.get('token', '')
        if not isinstance(token, str) or not token.strip() or any(c.isspace() for c in token):
            raise ValueError('Missing or invalid Laya token in private config or LAYA_API_TOKEN.')
        if not isinstance(endpoint, str):
            raise ValueError('Endpoint must be an HTTPS URL.')
        url = urllib.parse.urlsplit(endpoint)
        if url.scheme != 'https' or not url.hostname or url.username or url.password or url.fragment or url.query:
            raise ValueError('Endpoint must be an HTTPS URL without credentials, query, or fragment.')
        try:
            payload = json.loads(args.input.read_text(encoding='utf-8-sig') if args.input else sys.stdin.read())
        except json.JSONDecodeError:
            raise ValueError('Input must be valid JSON.') from None
        validate_request(payload)
        request = urllib.request.Request(endpoint, data=json.dumps(payload, allow_nan=False).encode(),
            headers={'Content-Type': 'application/json', 'Accept': 'application/json',
                     'Authorization': 'Bearer ' + token}, method='POST')
        with urllib.request.build_opener(NoRedirect).open(request, timeout=args.timeout) as response:
            raw = response.read(1_048_577)
        if len(raw) > 1_048_576:
            raise ValueError('Response exceeded the 1 MiB limit.')
        try:
            result = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ValueError('Server returned an invalid JSON prediction.') from None
        answers = result.get('answers') if isinstance(result, dict) else None
        if not isinstance(answers, dict) or not all(isinstance(answers.get(q), dict) for q in payload['questions']):
            raise ValueError('Server response is missing requested answers.')
        print(json.dumps(result, ensure_ascii=False, indent=2).replace(token, '[REDACTED]'))
        return 0
    except urllib.error.HTTPError as error:
        # Never echo an error response, headers, URL, or exception text: they may contain credentials.
        print(f'Laya request failed: HTTP {error.code}.', file=sys.stderr)
    except (urllib.error.URLError, TimeoutError):
        print('Laya connection failed or timed out.', file=sys.stderr)
    except json.JSONDecodeError:
        print('Laya config must contain valid JSON.', file=sys.stderr)
    except ValueError as error:
        # Validation messages contain no credential or raw response values.
        print(f'Laya: {error}', file=sys.stderr)
    except OSError:
        print('Laya could not read a local file or complete the connection.', file=sys.stderr)
    finally:
        print(f'elapsed_ms={round((time.monotonic() - started) * 1000)}', file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())

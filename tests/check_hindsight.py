"""Opt-in live MCP handshake/tool discovery; no memory access or inference."""
import argparse
import json
import os
from pathlib import Path
import sys
import time
import tomllib
import urllib.error
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hindsight_runtime import validate_url


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def check(home):
    codex = tomllib.loads((home / '.codex/config.toml').read_text(encoding='utf-8'))['mcp_servers']['hindsight']
    claude = json.loads((home / '.claude.json').read_text(encoding='utf-8'))['mcpServers']['hindsight']
    url = validate_url(codex['url'])
    variable = codex.get('bearer_token_env_var', '')
    if (codex.get('enabled') is False or not variable or claude.get('type') != 'http'
            or claude.get('url') != url or claude.get('headers', {}).get('Authorization')
            != 'Bearer ${' + variable + '}'):
        raise ValueError('Clients must enable the same HTTP endpoint and bearer environment reference')
    token = os.environ.get(variable)
    if not token:
        raise ValueError('Export the configured bearer-token variable in this process before checking')
    headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json',
               'Accept': 'application/json, text/event-stream'}
    opener = urllib.request.build_opener(NoRedirect)
    request_id = 0

    def send(method, params=None, notification=False):
        nonlocal request_id
        body = {'jsonrpc': '2.0', 'method': method}
        if params is not None:
            body['params'] = params
        if not notification:
            request_id += 1
            body['id'] = request_id
        request = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
        with opener.open(request, timeout=30) as response:
            if response.headers.get('Mcp-Session-Id'):
                headers['Mcp-Session-Id'] = response.headers['Mcp-Session-Id']
            if notification:
                return None
            if 'text/event-stream' in response.headers.get('Content-Type', ''):
                deadline = time.monotonic() + 30
                data = None
                # The gateway emits one JSON message per SSE data line. Bound
                # heartbeats and size; don't wait for an open SSE stream to end.
                for _ in range(256):
                    line = response.readline(1024 * 1024).decode('utf-8')
                    if not line or time.monotonic() > deadline:
                        break
                    if line.startswith('data:'):
                        candidate = json.loads(line[5:])
                        if candidate.get('id') == request_id:
                            data = candidate
                            break
                if data is None:
                    raise ValueError('No matching MCP response within the bounded SSE read')
            else:
                data = json.loads(response.read(1024 * 1024))
            if data.get('id') != request_id or 'error' in data or not isinstance(data.get('result'), dict):
                raise ValueError('MCP returned an invalid/error response (body withheld)')
            return data['result']

    result = send('initialize', {'protocolVersion': '2024-11-05', 'capabilities': {},
                                'clientInfo': {'name': 'ai-setup-connection-check', 'version': '1'}})
    protocol = result.get('protocolVersion')
    if protocol not in ('2024-11-05', '2025-03-26', '2025-06-18') or 'tools' not in result.get('capabilities', {}):
        raise ValueError('Server did not negotiate a supported MCP protocol with tools')
    headers['MCP-Protocol-Version'] = protocol
    send('notifications/initialized', notification=True)
    names, seen = set(), set()
    params = {}
    for _ in range(32):
        page = send('tools/list', params)
        names.update(tool['name'] for tool in page['tools'])
        cursor = page.get('nextCursor')
        if not cursor:
            break
        if cursor in seen:
            raise ValueError('Repeated tool-list cursor')
        seen.add(cursor)
        params = {'cursor': cursor}
    else:
        raise ValueError('Tool pagination exceeded the verification limit')
    if not {'retain', 'recall', 'reflect'}.issubset(names):
        raise ValueError('Expected Hindsight retain/recall/reflect tools were not all advertised')
    print(f'PASS: both registrations match; authenticated MCP {protocol}; {len(names)} tools discovered.')
    print('No memory read/write or model call performed. Active client overrides and inference remain separate checks.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, default=Path.home())
    args = parser.parse_args()
    try:
        check(args.home)
    except urllib.error.HTTPError as exc:
        print(f'Connection check failed: HTTP {exc.code} (response body withheld)', file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError, TypeError) as exc:
        # Network/parser exceptions may contain URLs, credentials or body text.
        print('Connection check failed: ' + type(exc).__name__
              + '; check configuration, token environment, endpoint and server health.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

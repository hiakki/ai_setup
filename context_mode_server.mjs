// Bind standalone MCP storage to this client process, not stale PWD or the
// most recently touched transcript from a different Claude/Codex window.
import { realpathSync } from 'node:fs';
import { dirname, delimiter } from 'node:path';
import { pathToFileURL } from 'node:url';

const project = realpathSync(process.cwd());
process.env.PWD = project;
process.env.CONTEXT_MODE_PROJECT_DIR = project;
process.env.CLAUDE_PROJECT_DIR = project;
process.env.PATH = dirname(process.execPath) + delimiter + (process.env.PATH || '');
await import(pathToFileURL(process.argv[2]).href);

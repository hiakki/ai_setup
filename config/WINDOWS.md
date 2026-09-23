# Native Windows command reference

Use PowerShell 5.1 or 7. The global installation lives under `$HOME`, your Windows
user profile. Restart the terminal/client after installation to refresh PATH.
Git Bash supports upstream shell scripts; no WSL distribution is needed.

Follow `AI_READY_PROJECTS.md` for scope, existing instructions, exclusions and
verification. Replace its Unix shell examples with these PowerShell commands:

```powershell
Set-Location 'C:\path\to\project'
graft build --no-ignore
if ($LASTEXITCODE -ne 0) { throw 'Graft build failed' }
graft check
if ($LASTEXITCODE -ne 0) { throw 'Graft check failed' }
codebase-memory-mcp cli index_repository --repo-path "$PWD" --mode full --persistence false
if ($LASTEXITCODE -ne 0) { throw 'Project indexing failed' }
codebase-memory-mcp cli list_projects
$graphProject = 'exact-name-returned-by-list_projects'
codebase-memory-mcp cli index_status --project $graphProject
```

Verify exclusions one path at a time so one success cannot hide a missing rule:

```powershell
$localPaths = @('.claude/settings.json', '.codex/config.toml', '.agents/project-context.md', 'AGENTS.override.md', 'CLAUDE.local.md', 'agency-agents.json', '.mcp.json', 'graft/graph.json', '.codebase-memory/graph.db.zst', '.ai-local/handoff.md')
foreach ($localPath in $localPaths) {
    git check-ignore -v --no-index -- $localPath
    if ($LASTEXITCODE -ne 0) { throw "Missing exclusion: $localPath" }
}
git ls-files -- .claude .codex .agents AGENTS.md AGENTS.override.md CLAUDE.md CLAUDE.local.md 'agency-agents*.json' .mcp.json graft .codebase-memory .ai-local
git diff --cached --name-only
git status --short
```

Do not join PowerShell commands with Bash `&&` when targeting PowerShell 5.1.
Use explicit exit-code checks for external tools. Use the installed
`powershell-windows-cli` skill and `powershell-5.1-expert` / `powershell-7-expert`
roles when relevant. Claude's 5.1 role filename is `powershell-5-1-expert.md`.

For setup verification, run `.\install.ps1 -Action verify` from the installer
checkout. For actual local graph/browser/PDF journeys:

```powershell
& "$HOME/.local/share/ai-setup/venv/Scripts/python.exe" smoke.py
```

Client logins and private service credentials must be configured separately.
For Laya, prefer private `LAYA_ENDPOINT` / `LAYA_API_TOKEN` environment variables,
or a user-owned configuration file whose ACL permits only that user, SYSTEM and
Administrators. Never include tokens in project context or source control.

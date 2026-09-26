# Native Windows command reference

Use PowerShell 5.1 or 7. The global installation lives under `$HOME`, your Windows
user profile. Restart the terminal/client after installation to refresh PATH.
Git Bash supports upstream shell scripts; no WSL distribution is needed.

From the `ai_setup` checkout, the default installation includes Context7 and the
selected upstream UI skills. Strix and SkillUI are optional:

```powershell
.\install.ps1 -Action plan -Only 'all,strix,skillui'
.\install.ps1 -Only 'all,strix,skillui'
# Add individual components to an existing setup:
.\install.ps1 -Only 'context7'
.\install.ps1 -Only 'strix,skillui'
```

`all` means the default profile, including Hermes; optional tools must be named.
The default profile uses the current Windows user profile. Selective Context7,
Strix and SkillUI setup does not require Microsoft C++ build tools or the full
runtime's disk-space allowance. SkillUI needs Node.js 18+ and npm, supplied by
the default runtime or an existing installation. Its optional browser mode is
separate; setup does not download another Playwright browser for it.

Strix installs as a native Windows executable. Installing it does not start a
scan, start Docker, or configure model credentials. Local security scans need
a working Docker Linux-container backend and configured model access. Docker
on Windows may use WSL2, Hyper-V or a remote Linux daemon; the installer does
not provision that backend. Only scan applications you are authorized to test.
Keep SkillUI's generated design context inside the relevant project.

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

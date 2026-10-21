# Agent Reach: optional social and video research

Agent Reach is shared globally for Claude and Codex. Read the `agent-reach` skill
for social-platform research, available video subtitles, RSS, or public-page
extraction that benefits from its adapters. Prefer the client's existing web
search/browser tools for ordinary browsing, Context7 for library docs, and
Codebase Memory for local code. Do not route every URL through Agent Reach.

This ai_setup policy overrides the provider's universal-use and setup defaults.
The upstream skill/references are fetched from a pinned provider commit; read only
the relevant reference. Use the installed `agent-reach`, `agent-reach-yt-dlp`,
`agent-reach-python` and `opencli` commands. The Python helper includes feedparser;
do not assume the project's Python has it. On native Windows use the `.cmd`
launchers and PowerShell's `$env:TEMP` or Python tempfile, not `/tmp` or Bash.

Run `agent-reach doctor --json` when choosing a platform backend, then verify the
actual requested read returns relevant non-empty content. A doctor status, CLI
installation or adapter listing does not prove account access, video transcription
or visual understanding. Report missing subtitles, blocked URLs and unavailable
channels. Never claim a video was watched from metadata or subtitles alone.

Installation does not connect social accounts. OpenCLI browser access requires
the user's authorized Browser Bridge and logged-in browser; do not start it,
extract/import cookies, automate login, post, like or message during setup or
unrelated work. Credentials stay personal and outside project repositories,
ai_setup, Hindsight and Agent Wiki. Public-reader services receive requested URLs;
never send private links, source or credentials to them. Transcription may upload
audio and consume API quota; use only with task authorization.

Do not run provider install/setup/skill/uninstall commands, unpinned upgrades,
automatic fallback installs, scheduled jobs or capture hooks. Maintain this
installation through ai_setup's `agentreach` component. OpenCLI runs with CI=1
to suppress automatic update checks/adapter synchronization; its bundled adapters
remain available. Additional backends (Exa/mcporter, dedicated X/Reddit/Bilibili
CLIs, LinkedIn and transcription providers) are optional, not silently installed.
Keep research evidence with its app and promote only reviewed generic lessons.
See the installed skill's `references/ai-setup.md` for commands and evidence limits.

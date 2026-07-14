# claude-secretmode

**English** | [한국어](README.ko.md)

**Leave-no-trace**, disposable Claude Code sessions — runs Claude Code on a macOS RAM disk, so transcripts, prompt history, and file snapshots are **never written to disk in the first place** and evaporate wholesale on exit.

Type `claude-secretmode` (or `csm`) where you would normally type `claude` — that's it. Auth, MCP, CLAUDE.md, and plugins all work as usual, while that session's **transcript and prompt history** never touch the disk. Your original `~/.claude` conversation history is preserved and never polluted.

## Quick start (1 minute)

### 1. Prerequisites

- macOS (Apple Silicon / Intel)
- [Claude Code](https://github.com/anthropics/claude-code) installed and **logged in**
  - `npm install -g @anthropic-ai/claude-code`, then log in once via `claude`
  - Auth is inherited from the macOS Keychain (`Claude Code-credentials`)

### 2. Install

```bash
# npm
npm install -g @younggichoi/claude-secretmode

# or bun
bun add -g @younggichoi/claude-secretmode
```

### 3. Use

```bash
# instead of your usual claude — this session leaves no records on disk
claude-secretmode

# short alias
csm

# arguments are passed through to claude as-is
claude-secretmode --model opus
```

On exit (Ctrl-D, `/exit`, or closing the terminal) the RAM disk is detached and every trace of the session disappears.

## How it works

```
claude-secretmode starts
 └ create a RAM disk → point CLAUDE_CONFIG_DIR at it
    ├ Keychain token → <ramdisk>/.credentials.json (auth inherited)
    ├ .claude.json (past-project traces stripped), settings.json (recording hooks disabled)
    ├ CLAUDE.md · hooks · skills · plugins → symlinks (code & policy shared as-is)
    └ transcript / history / snapshots → written to RAM only
 └ run claude (interactive, as usual)
    └ (background) token-sync daemon — keeps whichever token is newer,
      Keychain or RAM session (prevents rollback)
[exit] → RAM disk detached → session traces evaporate. The original ~/.claude is untouched.
```

- **Nothing accumulates on disk to begin with.** This is not "scrub on exit" — the records only ever exist in RAM and vanish with the memory.
- Exit or reboot leaves no trace; if the session dies abnormally (terminal closed, etc.), the leftover RAM disk is cleaned up automatically on the next run.

## Features

### 1. Record isolation

Conversation transcripts, prompt history, and file snapshots are written only to the RAM disk — never to your original `~/.claude`.

### 2. Recording/observation hooks disabled

Plugins/hooks that capture sessions into a persistent DB (e.g. `claude-mem`) are turned off for that session only. Security and quality guard hooks stay on.

### 3. Auth inheritance

Your macOS Keychain login is inherited as-is — no re-login needed. MCP OAuth (Slack, Figma, …) is inherited too.

### 4. Concurrent-session token sync

So that a regular `claude` session running at the same time never gets logged out, the **newer token** (the one expiring later) of the Keychain and the RAM session wins. If the RAM session refreshed its own token, it is never rolled back to a stale Keychain value.

## Environment variables

| Variable | Default | Description |
|------|--------|------|
| `CLAUDE_SECRETMODE_RAM_MB` | `1024` | RAM disk size (MB). Raise it for long sessions / big jobs. |
| `CLAUDE_SECRETMODE_DROP_HOOKS` | (none) | Additional hook script names to disable (comma-separated). E.g. `"my-logger.sh,audit.sh"` |
| `CLAUDE_SECRETMODE_STRIP_ALL_HOOKS` | `0` | `1` disables **every hook**, including security guards (fully traceless). |

- The Keychain token lives only as a **file on the RAM disk** (`600`), is never printed to the screen, and never touches the disk platter.
- Tokens are written only after verifying the RAM disk mount is actually live (prevents disk writes on a silent mount failure). The token-sync daemon likewise runs only while the parent session is alive and the mount holds.
- While the session is **alive**, its records exist in RAM, so processes with the same user privileges can access them. They disappear on exit/reboot.

**What is isolated vs. shared**

- **RAM-isolated (never reaches disk)**: conversation transcripts, prompt history, file snapshots, `.claude.json`, `projects/`.
- **Shared (symlinked, non-recording)**: `CLAUDE.md`, hook scripts, skills, plugin code, marketplace metadata. If claude updates these at runtime (plugin cache, etc.) the changes land on the original disk — that's code/metadata, not conversation content.
- **Hooks**: known recording/observation hooks (e.g. `claude-mem`) are disabled automatically, but **custom logging/audit hooks you wrote yourself cannot be auto-detected.** If such hooks remain, a warning is printed at startup; disable them via `CLAUDE_SECRETMODE_DROP_HOOKS`, or disable everything with `CLAUDE_SECRETMODE_STRIP_ALL_HOOKS=1`.

## Limitations

- **macOS only** — depends on `hdiutil` RAM disks and the Keychain (`security`). Linux/Windows are not supported.
- Assumes a Claude Code login backed by the Keychain.

## License

MIT

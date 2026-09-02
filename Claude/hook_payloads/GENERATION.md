# Synthetic Hook Payload Generation

## Purpose
Test fixtures for Claude Code hook scripts (`PreToolUse`, `PostToolUse`, `UserPromptSubmit`) —
one pair of files per built-in tool, plus a synthetic multi-turn conversation designed to
trigger as many tools as possible.

## Method

1. **Enumerated tools** from the current session's tool list (both pre-loaded and deferred
   tools surfaced via `ToolSearch`), including the three connected MCP integrations
   (Gmail, Google Calendar, Google Drive) — 39 tools total.

2. **Split by schema confidence**:
   - `confirmed` (18 tools) — the tool's real parameter schema was visible in this session
     (either defined at the top of the prompt, or fetched via `ToolSearch` for `WebFetch`).
     `tool_input` values were built to satisfy that actual schema.
   - `inferred` (21 tools) — only the tool's name was known (deferred, schema never loaded).
     `tool_input` values are plausible guesses at a reasonable parameter shape, not verified
     against a real schema. Each file records this via `_synthetic_meta.schema_confidence`.

3. **Envelope fields** (`session_id`, `transcript_path`, `cwd`, `hook_event_name`) follow
   the documented Claude Code hook payload structure and are held constant across every file
   so the set can be replayed as one coherent session.

4. **`tool_response` values** for `PostToolUse` are hand-authored plausible outcomes (e.g. a
   passing test run, a created file, a scheduled cron job) — not captured from a real
   execution.

5. **Synthetic conversation** (8 `UserPromptSubmit` turns): authored as a single narrative —
   building a "wordcount" CLI tool — with each turn's request phrased to plausibly cause a
   Claude Code session to reach for a specific cluster of tools (e.g. turn 1 asks to "search
   existing code, then give me a plan" to hit `Grep`/`Glob`/`EnterPlanMode`/`ExitPlanMode`).
   Coverage was checked manually against the 39-tool list and turns were added until every
   tool had a plausible trigger. Each prompt file records its intended tools in
   `_synthetic_meta.expected_tools`.

6. **Generation mechanism**: a single PowerShell script
   (`gen_hook_payloads.ps1`) holding the tool definitions as an ordered hashtable, looped to
   emit one `PreToolUse.json` / `PostToolUse.json` pair per tool via `ConvertTo-Json`, plus
   one file per conversation turn — rather than writing ~87 files by hand.

## Caveats

- No payload was captured from a real hook invocation — everything is authored, not observed.
- The 21 `inferred`-confidence tool schemas may not match the real parameter names/shapes if
  those tools' actual definitions differ from the guess made here.
- `tool_response` content is illustrative, not derived from actually running any tool.

## Files

```
hook_payloads/
  tools/<ToolName>/PreToolUse.json    (39)
  tools/<ToolName>/PostToolUse.json   (39)
  prompts/01..08_UserPromptSubmit.json
  tools_manifest.json                 (tool -> schema_confidence index)
  GENERATION.md                       (this file)
```

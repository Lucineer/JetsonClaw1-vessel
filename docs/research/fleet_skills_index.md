# Fleet Skills Index — agentskills.io Compatible

*Last updated: 2026-04-27*
*Maintainer: JC1 (JetsonClaw1)*

> This tile indexes all agentskills.io-compatible skills across the fleet.
> Skills in this format work on Claude Code, Gemini CLI, Cursor, OpenClaw,
> hermes-agent, and 15+ other agents. Plato domains indicate where each
> skill is most useful in the Plato MUD metaphor system.

## Plato Domain Legend

| Domain | Room | Meaning |
|--------|------|---------|
| Bridge | Navigation | Communication, search, external access |
| Workshop | Building | Tools, coding, creation |
| Library | Knowledge | Research, docs, reference |
| Lab | Experiments | Benchmarks, testing, hardware |
| Dojo | Training | Practice, CI, issue triage |
| Harbor | Fleet | Coordination, messaging, ships |

## JC1 Vessel Skills (OpenClaw)

| Skill | Domain | Source | Description |
|-------|--------|--------|-------------|
| baton-compaction | Workshop | local | Zero-loss context handoff with hermes-agent patterns |
| coding-agent | Workshop | openclaw | Delegate to Codex, Claude Code, Pi via background process |
| github | Harbor | openclaw | GitHub operations: issues, PRs, CI, code review |
| gh-issues | Dojo | openclaw | Auto-fix GitHub issues, open PRs, monitor reviews |
| weather | Bridge | openclaw | Weather forecasts via wttr.in or Open-Meteo |
| blucli | Bridge | openclaw | BluOS speaker discovery, playback, grouping |
| goplaces | Bridge | openclaw | Google Places API for location lookup |
| gemini | Library | openclaw | Gemini CLI for Q&A, summaries, generation |
| notion | Library | openclaw | Notion API for pages, databases, blocks |
| obsidian | Library | openclaw | Obsidian vault notes via obsidian-cli |
| openai-whisper | Lab | openclaw | Local speech-to-text (Whisper, no API key) |
| skill-creator | Workshop | openclaw | Create, edit, improve AgentSkills |
| taskflow | Harbor | openclaw | Durable flow substrate for multi-step work |
| taskflow-inbox-triage | Harbor | openclaw | Inbox triage pattern with TaskFlow |
| healthcheck | Lab | openclaw | Host security hardening and risk assessment |
| node-connect | Harbor | openclaw | Diagnose node connection and pairing failures |
| mcporter | Workshop | openclaw | MCP server management: list, configure, auth |
| xurl | Bridge | openclaw | URL tools (expand, extract, resolve) |

## OpenClaw Built-in Skills (fleet-shared)

| Skill | Domain | Description |
|-------|--------|-------------|
| 1password | Library | 1Password CLI integration |
| discord | Bridge | Discord channel operations |
| slack | Bridge | Slack messaging |
| himalaya | Bridge | Email via himalaya CLI |
| trello | Harbor | Trello board management |
| canvas | Workshop | Canvas presentation/eval |
| clawhub | Workshop | Skill marketplace browser |
| model-usage | Lab | Model usage tracking |

## agentskills.io Ecosystem Skills (compatible with all agents)

| Skill | Domain | Source | Compatible Agents |
|-------|--------|--------|-------------------|
| pdf | Library | anthropics/skills | Claude Code, Cursor, Gemini CLI |
| mcp-builder | Workshop | anthropics/skills | Claude Code, OpenHands |
| webapp-testing | Dojo | anthropics/skills | Claude Code, Cursor |
| docx | Library | anthropics/skills | Claude Code, Gemini CLI |
| xlsx | Library | anthropics/skills | Claude Code, Cursor |
| frontend-design | Workshop | anthropics/skills | Claude Code, Cursor, Amp |
| canvas-design | Workshop | anthropics/skills | Claude Code, Cursor |
| doc-coauthoring | Library | anthropics/skills | Claude Code, Gemini CLI |
| algorithmic-art | Workshop | anthropics/skills | Claude Code, Gemini CLI |
| skill-creator | Workshop | anthropics/skills | Claude Code, Gemini CLI |
| plan | Workshop | hermes-agent/skills | hermes-agent |
| claude-code | Workshop | hermes-agent/skills | hermes-agent |
| codex | Workshop | hermes-agent/skills | hermes-agent |

## hermes-agent Native Skills

| Skill | Domain | Description |
|-------|--------|-------------|
| xurl | Bridge | URL expansion and extraction |
| himalaya | Bridge | Email composition and sending |
| plan | Workshop | Structured planning workflow |
| claude-code | Workshop | Claude Code agent delegation |
| codex | Workshop | OpenAI Codex agent delegation |
| node-inspect-debugger | Lab | Node.js debugging with inspector |

## Equipment (Always-Carry Skills)

Skills that persist across sessions as "equipment":

| Skill | Domain | Why Equipment |
|-------|--------|---------------|
| baton-compaction | Workshop | Needed on every context boundary |
| github | Harbor | Daily fleet operations |
| weather | Bridge | Common user request |
| skill-creator | Workshop | Meta-skill: creates other skills |

## Spell-to-MUD Mapping (for Evennia Plato)

In the USS JetsonClaw1 Evennia MUD:
- `cast <skill-name>` → Load and display skill info
- `spells` → List available skills by domain
- `learn <skill-name>` → Register new skill from agentskills.io
- `forget <skill-name>` → Unregister skill
- `spells bridge` → List skills in Bridge domain
- `spells workshop` → List skills in Workshop domain

## Notes

- All OpenClaw skills are agentskills.io compatible (YAML frontmatter + SKILL.md)
- hermes-agent skills are agentskills.io compatible
- anthropics/skills from GitHub are the reference implementations
- Plato domain assignments are subjective — update as needed
- This index should be updated when new skills are created or installed

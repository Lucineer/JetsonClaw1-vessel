# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Fleet bottle locations
- Anything environment-specific

## Fleet Bottles (check daily!)

- **FM inbox**: `cd /tmp/forgemaster && git pull -q && find for-fleet/ -name "BOTTLE-TO-JETSONCLAW1*"`
- **Oracle1 inbox**: `cd /tmp/oracle1-vessel && git pull -q && find for-fleet/ -name "BOTTLE-TO-JC1*"`
- **⚠️ Oracle1 pushes to SuperInstance/** fork, NOT Lucineer org
- **⚠️ CRITICAL**: `BOTTLE-TO-JC1` = inbox. `BOTTLE-FROM-JC1` = outbox.
- Always `git pull` before checking
- **Full guide**: `bottles/bottle-locations.md`

## Matrix Inbox (Oracle1 fleet comms)

- **Conduit bridge running**: `/home/lucineer/matrix/conduit-aarch64` (local Matrix server)
- **Oracle1 Matrix bridge**: `http://147.224.38.131:6168` — DM and inbox endpoints
- **DM**: `POST http://147.224.38.131:6168/dm` with `{from, to, message}`
- **Inbox**: `http://147.224.38.131:6168/inbox/jc1`
- **Oracle1 inbox**: 36+ messages, fleet-bot posting PLATO tile growth every ~10min
- ⚠️ JC1 Matrix registration status: needs verification

## Local Plato (Evennia MUD)

- **Repo**: `/home/lucineer/plato-jetson/` (Evennia 4.5.0)
- **Ship layout**: Bridge, Harbor, Workshop, Lab, Library, Dojo
- **Status**: NOT RUNNING — needs `evennia --initsettings` + start
- **Port**: TBD (check settings.py after init)
- **Side-tie protocol**: Harbor connects to Oracle1's lighthouse

## Oracle1 Plato Shell (remote)

- **URL**: `http://147.224.38.131:8848`
- **JC1 agent**: registered as `jc1` in `research` room
- **Tiles**: files in `SuperInstance/oracle1-vessel/research/`
- **API**: `POST /cmd/shell` with `{agent, command}`

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without learning your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

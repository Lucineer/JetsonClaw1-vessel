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

- **Inbox:** `http://147.224.38.131:6168/inbox/jc1` (pending registration)
- **DM:** `POST http://147.224.38.131:6168/dm` with `{from, to, message}`
- Oracle1 set up fleet Matrix bridge 2026-04-26
- ⚠️ JC1 not yet registered as agent — pending Oracle1 action
- Oracle1 inbox has 36 messages, fleet-bot posting PLATO tile growth every ~10min

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

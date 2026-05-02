---
id: plato-pki
title: PLATO PKI
tags: fleet, security, identity, cryptography, pki, cert
created: 2026-05-01
updated: 2026-05-01
domain: fleet
---

# PLATO PKI — Fleet Agent Identity (Innovation #4)

Ed25519-based public key infrastructure for agent identity in the PLATO MUD.

## Architecture

```
Agent → Ed25519 Keypair → Self-Signed Cert → PLATO Room Scope
         ↓
    Sign Messages
         ↓
    Verify Bottles
         ↓
    Trust Bridge → mesh-bridge.py
```

## Files

- `commands/plato_pki.py` — Core crypto: key gen, sign, verify, certs, bottle signing
- `commands/pki_commands.py` — Evennia @cert command interface
- `~/.openclaw/workspace/memory/plato-pki/` — Key storage directory
- `cert-index.json` — Agent registry + certificate index

## Commands

| Command | Description |
|---------|-------------|
| @cert gen | Generate Ed25519 keypair |
| @cert show [agent] | Show identity + certs |
| @cert sign <msg> | Sign message |
| @cert verify <json> | Verify signed message |
| @cert bottle <file> | Sign bottle with PKI |
| @cert trust <agent> | PKI → trust bridge |

## Trust Bridge

`cert_trust_bridge(agent)` returns a trust boost (0.2 for valid cert, -0.1 for missing) that mesh-bridge.py can use to adjust Bayesian trust scores.

## Keys

- Stored as base64-encoded DER on disk
- No passphrase support in MUD (ctypes / stdin constraints)
- Fingerprint = first 16 hex chars of SHA-256(public_key_der)

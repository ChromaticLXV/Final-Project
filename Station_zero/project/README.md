# STATION ZERO
### A Cyberpunk Text-Based Adventure

**Team Members:** [Your names here]

---

## How to Run

```bash
python main.py
```

Requires Python 3.10+ (uses `dict | None` union type syntax). No external libraries needed.

---

## Core Game Features

- 3 branching story paths with 3 unique endings
- 5+ major locations/events
- 5 NPCs with dialogue and meaningful interactions
- Full inventory system (13 items in the catalog)
- 3 interactive challenges (puzzles + combat)
- Cyber Pack: input validation, audit logging, tamper-checked save/load

---

## Story Paths and Endings

### Path A — The Smuggler
You head to the Docking Bay and team up with black-market smuggler Vera Cross. Negotiate, infiltrate the Sector 9 vault, fight or bluff your way through a Council security response, and escape off-station with the data core.

### Path B — The Hacker
You head to the Server Room and discover ARIA, a conscious AI imprisoned by the Council. You must hack terminals, decide whether to free ARIA into the open net, and use her help (or not) to escape through hidden corridors.

### Path C — The Resistance
You head to the Resistance Safe House and join Commander Ryen Okafor's underground fighters. Help them decode and broadcast the Council's crimes to every screen in Neo-Arcadia, then survive the Council's retaliation.

### Ending 1 — The Shadow Broker *(Path A)*
You vanish into the undercity with the data core. The syndicate pays. No one knows your name.

### Ending 2 — Ghost in the Machine *(Path B)*
ARIA is freed into the net. You're arrested — but an AI owes you a favor.

### Ending 3 — Zero Day *(Path C)*
You broadcast the Council's crimes. The city erupts. You become a wanted hero.

---

## Locations / Events

| # | Name | Type |
|---|------|------|
| 1 | Detention Cell / Corridor | Opening location — player wakes up, finds items |
| 2 | Main Corridor Crossroads | Major event — path choice, meets Kade |
| 3 | Docking Bay / Sector 9 Vault | Location — Smuggler path, vault breach |
| 4 | Server Room / Neural Core | Location — Hacker path, ARIA encounter |
| 5 | Resistance Safe House + Broadcast Tower | Location — Resistance path, evidence + broadcast |

---

## NPCs

| NPC | Location | Role |
|-----|----------|------|
| **Kade** | Crossroads | Informant — gives Signal Jammer, warns about Council |
| **Vera Cross** | Docking Bay | Smuggler — offers passage, demands data copy, gives intel |
| **Dr. Mira Solano** | Server Room | Engineer — explains ARIA, gives Engineer Access Card |
| **ARIA** | Server Room partition | AI — offers route info, can be freed or wiped |
| **Cmdr. Ryen Okafor** | Safe House | Resistance leader — directs mission, provides backup |
| **Pixel** | Evidence Room | Analyst — gives cipher challenge, explains stakes |

---

## Inventory Items

| Item | Purpose |
|------|---------|
| Stun Baton | Used in combat encounters (Hacker escape, Smuggler escape) |
| Station Map | Navigation — reveals all sectors |
| Vault Access Code | Unlocks Sector 9 vault door |
| Medkit | Restores 30 HP (manual use) |
| Cargo Pass | Bluffs through docking bay checkpoints |
| Data Core | Story-critical — the MacGuffin all paths revolve around |
| Council Dossier | Evidence item — collected in vault |
| Signal Jammer | Guarantees safe passage past the patrol drone |
| Root Access Key | Grants root terminal access (Hacker path) |
| Neural Spike | AI hardware interface for ARIA upload |
| Engineer Access Card | Bypasses two security layers (Mira's card) |
| Decode Key | Decrypts Council dossier for verified broadcast |
| Resistance Badge | Bluffs through Resistance-controlled checkpoints |

---

## Challenges

### Challenge 1 — Terminal Hack (Server Room)
**What:** 3-digit PIN guessing puzzle with hot/cold feedback (CORRECT / CLOSE / WRONG).
**Success:** Receive Root Access Key, proceed to ARIA.
**Failure:** Security lockout, -15 HP.

### Challenge 2 — Drone Combat (Sector 9 Corridor)
**What:** Timed obstacle — choose between Signal Jammer (guaranteed), sprint (50/50), or firmware hack (sub-puzzle).
**Success:** Reach the vault.
**Failure:** Take damage (25–30 HP); possible death if health ≤ 0.

### Challenge 3 — Cipher Decode (Evidence Room)
**What:** Decode a Caesar cipher (shift 5) in 2 attempts.
**Success:** Receive Decode Key for verified broadcast.
**Failure:** Locked into raw/unverified broadcast option.

---

## Cyber Pack

### Input Validation + Safe Error Handling
- All numeric menus are validated via `_get_choice()` in `content/story.py`
- `try/except` blocks in `systems/challenges.py` prevent non-numeric input from crashing challenges
- Invalid input re-prompts the user and logs the attempt
- Special keywords `i`/`inventory` and `save` are accepted at any prompt

### Audit Logging (`audit_log.txt`)
- Every significant event is logged with a timestamp via `AuditLogger` in `security/security.py`
- Logged events include: GAME_START, GAME_END, INPUT_INVALID, NPC_MET, NPC_INTERACTION, CHOICE_MADE, CHALLENGE_ATTEMPT, ITEM_USED, SAVE_ATTEMPT, LOAD_ATTEMPT, ERROR
- Example line: `2026-01-19 14:37:42 - CHALLENGE_ATTEMPT - Puzzle=TerminalHack - SUCCESS - Attempts=2`

### Save / Load With Tamper Check
- Save state serialized as JSON (`savegame.json`) via `security/save_load.py`
- A SHA-256 checksum of the canonical JSON is embedded in the save file
- On load, the checksum is recomputed and compared — any manual edit is detected
- Tampered saves are rejected and logged with `SAVE_TAMPERED`

---

## File Structure

```
station-zero/
├── main.py                   # Entry point
├── engine/
│   ├── game_engine.py        # Main loop, routing, save/load bridge
│   └── state.py              # GameState class
├── content/
│   ├── story.py              # All scene handlers + branching logic
│   └── npcs.py               # NPC dialogue and interactions
├── systems/
│   ├── inventory.py          # Item catalog and inventory logic
│   └── challenges.py         # All 3 challenges
├── security/
│   ├── security.py           # AuditLogger + input validation helpers
│   └── save_load.py          # Save/load with SHA-256 tamper detection
├── docs/
│   └── flowchart.png         # Story branching flowchart
├── audit_log.txt             # Auto-generated on first run
├── savegame.json             # Auto-generated on save
└── README.md
```

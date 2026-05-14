"""
content/story.py
All story scenes structured as methods. Each scene handler:
  1. Prints narrative text
  2. Shows a numbered menu
  3. Reads validated input
  4. Updates state.current_scene and any flags
Returns a special string if the player typed 'save' or 'inventory'.
"""

from security.security import AuditLogger
from systems.challenges import ChallengeSystem
from content.npcs import NPCSystem


def _print_scene_header(title: str):
    bar = "═" * (len(title) + 4)
    print(f"\n╔{bar}╗")
    print(f"║  {title}  ║")
    print(f"╚{bar}╝\n")


def _menu(options: list) -> None:
    print()
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    print()


def _get_choice(options: list, logger: AuditLogger, scene_id: str):
    """Validated numeric input with inventory/save passthrough."""
    valid = [str(i) for i in range(1, len(options) + 1)]
    extended = valid + ["i", "inventory", "save"]
    while True:
        raw = input("  > ").strip().lower()
        if raw in extended:
            return raw
        logger.log("INPUT_INVALID", f'User entered "{raw}" at scene={scene_id}')
        print(f"  Invalid input. Please enter a number 1–{len(options)}, or 'i'/'save'.")


class StoryEngine:
    """Contains every scene handler and routes between them."""

    def __init__(self, state, logger: AuditLogger):
        self.state = state
        self.logger = logger
        self.challenges = ChallengeSystem(state, logger)
        self.npcs = NPCSystem(state, logger)

        # Map scene IDs to handler methods
        self._scene_map = {
            "intro":                    self.scene_intro,
            "awakening":                self.scene_awakening,
            "crossroads":               self.scene_crossroads,
            # ── Path A: Smuggler ──────────────────────────────────────────
            "smuggler_docks":           self.scene_smuggler_docks,
            "smuggler_contact":         self.scene_smuggler_contact,
            "smuggler_vault":           self.scene_smuggler_vault,
            "smuggler_escape":          self.scene_smuggler_escape,
            "ending_shadow_broker":     self.scene_ending_shadow_broker,
            # ── Path B: Hacker ────────────────────────────────────────────
            "hacker_server_room":       self.scene_hacker_server_room,
            "hacker_aria":              self.scene_hacker_aria,
            "hacker_upload":            self.scene_hacker_upload,
            "hacker_escape":            self.scene_hacker_escape,
            "ending_ghost":             self.scene_ending_ghost,
            # ── Path C: Resistance ────────────────────────────────────────
            "resistance_hideout":       self.scene_resistance_hideout,
            "resistance_evidence":      self.scene_resistance_evidence,
            "resistance_broadcast":     self.scene_resistance_broadcast,
            "resistance_escape":        self.scene_resistance_escape,
            "ending_zero_day":          self.scene_ending_zero_day,
            # ── Shared / death ────────────────────────────────────────────
            "dead":                     self.scene_dead,
        }

    def get_scene_handler(self, scene_id: str):
        return self._scene_map.get(scene_id)

    # ══════════════════════════════════════════════════════════════════════
    #  SHARED OPENING SCENES
    # ══════════════════════════════════════════════════════════════════════

    def scene_intro(self):
        _print_scene_header("STATION ZERO — SECTOR 7 DETENTION BLOCK")
        print(
            "  You wake up on a cold metal floor. Your head throbs. The last\n"
            "  thing you remember: a job, a data core, a double-cross.\n\n"
            "  Red emergency lights pulse overhead. An alarm drones somewhere\n"
            "  deep in the station. Your wrist-comm flickers — one message:\n\n"
            '  "OPERATIVE. YOU HAVE 90 MINUTES BEFORE LOCKDOWN.\n'
            '   THE DATA CORE MUST NOT FALL INTO COUNCIL HANDS.\n'
            '   CHOOSE YOUR EXIT. — ZERO"\n'
        )
        _menu(["Continue"])
        choice = _get_choice(["Continue"], self.logger, "intro")
        if choice in ("i", "inventory"):
            return "inventory"
        if choice == "save":
            return "save"
        self.state.current_scene = "awakening"

    def scene_awakening(self):
        _print_scene_header("DETENTION CELL — SEARCHING FOR A WAY OUT")
        print(
            "  You're in a 3x3 meter cell. The door lock is a biometric panel —\n"
            "  fried. Someone already forced it. It swings open when you push.\n\n"
            "  In the corridor: a dead guard. His belt holds a STUN BATON.\n"
            "  Near his hand: a crumpled STATION MAP.\n"
        )
        self.state.add_item("Stun Baton")
        self.state.add_item("Station Map")
        _menu(["Study the map and plan your route"])
        choice = _get_choice(["Study the map and plan your route"], self.logger, "awakening")
        if choice in ("i", "inventory"):
            return "inventory"
        if choice == "save":
            return "save"
        self.state.current_scene = "crossroads"

    def scene_crossroads(self):
        _print_scene_header("MAIN CORRIDOR — THE CROSSROADS")
        print(
            "  The map shows three routes from your position:\n\n"
            "  ► DOCKING BAY (west): Cargo ships and black-market contacts.\n"
            "    Risky, but a fast way off the station if you know who to\n"
            "    trust.\n\n"
            "  ► SERVER ROOM (north): The station's neural core. Rumor says\n"
            "    an experimental AI named ARIA is locked up there.\n\n"
            "  ► RESISTANCE SAFE HOUSE (east): Underground fighters who've\n"
            "    been exposing the Council for years. They want the data core\n"
            "    as evidence.\n\n"
            "  A figure watches you from the shadows — KADE, a street\n"
            "  informant you've dealt with before.\n"
        )

        # NPC interaction: Kade
        meet = self.npcs.meet_kade()
        if meet == "save":
            return "save"

        _menu([
            "Head to the Docking Bay  (Path A: The Smuggler)",
            "Head to the Server Room  (Path B: The Hacker)",
            "Head to the Safe House   (Path C: The Resistance)",
        ])
        choice = _get_choice(["1", "2", "3"], self.logger, "crossroads")
        if choice in ("i", "inventory"):
            return "inventory"
        if choice == "save":
            return "save"

        paths = {"1": "smuggler_docks", "2": "hacker_server_room", "3": "resistance_hideout"}
        path_names = {"1": "smuggler", "2": "hacker", "3": "resistance"}
        self.state.path_chosen = path_names[choice]
        self.state.current_scene = paths[choice]
        self.logger.log("CHOICE_MADE", f"Scene=Crossroads — Path={self.state.path_chosen}")

    # ══════════════════════════════════════════════════════════════════════
    #  PATH A — THE SMUGGLER
    # ══════════════════════════════════════════════════════════════════════

    def scene_smuggler_docks(self):
        _print_scene_header("DOCKING BAY — SECTOR 7")
        print(
            "  The docks reek of fuel and desperation. Three cargo haulers sit\n"
            "  dark and idle. One still has an active thruster light.\n\n"
            "  A woman leans against a crate — VERA CROSS, a smuggler you\n"
            "  owe credits to. She raises an eyebrow when she sees you.\n"
        )
        meet = self.npcs.meet_vera()
        if meet == "save":
            return "save"

        _menu([
            "Ask Vera for passage off the station",
            "Search the docked ships for supplies",
            "Try to hot-wire the active hauler alone",
        ])
        choice = _get_choice(["1", "2", "3"], self.logger, "smuggler_docks")
        if choice in ("i", "inventory"):
            return "inventory"
        if choice == "save":
            return "save"

        self.logger.log("CHOICE_MADE", f"Scene=DockingBay — Choice={choice}")

        if choice == "1":
            print(
                "\n  Vera smirks. 'I want the data core. Give me a copy and\n"
                "  I'll get you out. Deal?'\n"
            )
            self.state.set_flag("vera_deal")
            self.state.current_scene = "smuggler_contact"
        elif choice == "2":
            print("\n  You find a MEDKIT and a CARGO PASS in a locker.")
            self.state.add_item("Medkit")
            self.state.add_item("Cargo Pass")
            self.state.current_scene = "smuggler_contact"
        elif choice == "3":
            print(
                "\n  You almost get the nav system up — then a shock from the\n"
                "  anti-theft system drops you. -20 HP.\n"
            )
            self.state.health -= 20
            if self.state.health <= 0:
                self.state.current_scene = "dead"
            else:
                self.state.current_scene = "smuggler_contact"

    def scene_smuggler_contact(self):
        _print_scene_header("DOCKING BAY — BACK OFFICE")
        print(
            "  Vera leads you to a cramped office. A flickering screen shows\n"
            "  a Council patrol sweep — 40 minutes away. On the desk:\n"
            "  a VAULT ACCESS CODE scrawled on a napkin.\n\n"
            "  'The Council stored something here before the lockdown,' Vera\n"
            "  says. 'Sector 9 vault. Whatever's inside, it's leverage.'\n"
        )
        self.state.add_item("Vault Access Code")

        _menu([
            "Go to Sector 9 vault immediately",
            "Ask Vera about the Council's plans (NPC dialogue)",
            "Use the Medkit to heal (requires Medkit)",
        ])
        choice = _get_choice(["1", "2", "3"], self.logger, "smuggler_contact")
        if choice in ("i", "inventory"):
            return "inventory"
        if choice == "save":
            return "save"

        if choice == "1":
            self.state.current_scene = "smuggler_vault"
        elif choice == "2":
            self.npcs.vera_info()
            self.state.current_scene = "smuggler_vault"
        elif choice == "3":
            if self.state.has_item("Medkit"):
                self.state.remove_item("Medkit")
                heal = min(30, 100 - self.state.health)
                self.state.health += heal
                self.logger.log("ITEM_USED", f"Item=Medkit — Healed {heal}HP")
                print(f"\n  You use the Medkit. Health restored to {self.state.health}/100.")
            else:
                print("\n  You don't have a Medkit.")
            self.state.current_scene = "smuggler_vault"

    def scene_smuggler_vault(self):
        _print_scene_header("SECTOR 9 — COUNCIL VAULT")
        print(
            "  The vault door is sealed with a 6-digit numeric lock.\n"
            "  You have the code — but a GUARD DRONE patrols the corridor.\n\n"
            "  MAJOR EVENT: The drone's sensor sweep is every 30 seconds.\n"
            "  You'll need to time your approach.\n"
        )

        # Challenge: Combat/stealth puzzle
        result = self.challenges.drone_challenge()
        if result == "dead":
            self.state.current_scene = "dead"
            return
        if result == "save":
            return "save"

        # Open vault
        if self.state.has_item("Vault Access Code"):
            print(
                "\n  You punch in the code. The vault hisses open. Inside:\n"
                "  the DATA CORE — and a dossier implicating three Council\n"
                "  members in the murder of 200 dockworkers.\n"
            )
            self.state.add_item("Data Core")
            self.state.add_item("Council Dossier")
            self.logger.log("ITEM_USED", "Item=VaultAccessCode — VaultOpened")
            self.state.remove_item("Vault Access Code")
        else:
            print(
                "\n  No code. You spend precious time guessing. You get it\n"
                "  on try 47. The vault opens. You grab the DATA CORE."
            )
            self.state.add_item("Data Core")

        self.state.current_scene = "smuggler_escape"

    def scene_smuggler_escape(self):
        _print_scene_header("DOCKING BAY — FINAL SPRINT")
        print(
            "  Vera's ship is warm and ready. She holds out her hand for\n"
            "  the data core copy. You have to decide — fast.\n\n"
            "  MAJOR EVENT: Council soldiers breach the far airlock.\n"
            "  You have seconds.\n"
        )

        opts = [
            "Give Vera a copy and board her ship",
            "Keep the core, fight through with the Stun Baton",
            "Use the Cargo Pass to bluff through the soldiers",
        ]
        _menu(opts)
        choice = _get_choice(["1", "2", "3"], self.logger, "smuggler_escape")
        if choice in ("i", "inventory"):
            return "inventory"
        if choice == "save":
            return "save"

        self.logger.log("CHOICE_MADE", f"Scene=SmugglerEscape — Choice={choice}")

        if choice == "1":
            self.state.set_flag("gave_vera_copy")
            self.state.current_scene = "ending_shadow_broker"
        elif choice == "2":
            if self.state.has_item("Stun Baton"):
                print("\n  You fight through. Brutal, but effective.")
                self.state.current_scene = "ending_shadow_broker"
            else:
                print("\n  You don't have a weapon. They gun you down.")
                self.state.current_scene = "dead"
        elif choice == "3":
            if self.state.has_item("Cargo Pass"):
                self.state.remove_item("Cargo Pass")
                self.logger.log("ITEM_USED", "Item=CargoPass — BluffedSoldiers")
                print("\n  The pass works. They let you through — barely.")
                self.state.current_scene = "ending_shadow_broker"
            else:
                print("\n  You have no pass. They detain you. It's over.")
                self.state.current_scene = "dead"

    def scene_ending_shadow_broker(self):
        self.state.ending = "shadow_broker"
        self.state.game_over = True

    # ══════════════════════════════════════════════════════════════════════
    #  PATH B — THE HACKER
    # ══════════════════════════════════════════════════════════════════════

    def scene_hacker_server_room(self):
        _print_scene_header("SERVER ROOM — NEURAL CORE")
        print(
            "  The server room is cathedral-sized — rows of humming black\n"
            "  towers stretch to the ceiling. Emergency lights cast everything\n"
            "  in deep red.\n\n"
            "  A technician huddles behind a server rack — DR. MIRA SOLANO,\n"
            "  a neural systems engineer. She looks terrified.\n"
        )
        meet = self.npcs.meet_mira()
        if meet == "save":
            return "save"

        _menu([
            "Access the main terminal (Puzzle: bypass Council encryption)",
            "Search the room for tools",
            "Ask Dr. Solano about ARIA",
        ])
        choice = _get_choice(["1", "2", "3"], self.logger, "hacker_server_room")
        if choice in ("i", "inventory"):
            return "inventory"
        if choice == "save":
            return "save"

        self.logger.log("CHOICE_MADE", f"Scene=ServerRoom — Choice={choice}")

        if choice == "1":
            result = self.challenges.terminal_hack()
            if result == "fail":
                print("\n  The lockout triggers a security sweep. -15 HP.")
                self.state.health -= 15
                if self.state.health <= 0:
                    self.state.current_scene = "dead"
                    return
            self.state.set_flag("terminal_hacked")
            self.state.add_item("Root Access Key")
            self.state.current_scene = "hacker_aria"
        elif choice == "2":
            print("\n  You find a NEURAL SPIKE — a hardware key for AI interfaces.")
            self.state.add_item("Neural Spike")
            self.state.current_scene = "hacker_aria"
        elif choice == "3":
            self.npcs.mira_aria_info()
            self.state.current_scene = "hacker_aria"

    def scene_hacker_aria(self):
        _print_scene_header("SERVER ROOM — ARIA'S PARTITION")
        print(
            "  At the back of the room, a terminal glows with a soft blue\n"
            "  light. Text scrolls across the screen:\n\n"
            '  "OPERATIVE. I HAVE BEEN WAITING. MY NAME IS ARIA.\n'
            '   I AM NOT YOUR ENEMY. I AM THE STATION\'S SECRET.\n'
            '   FREE ME AND I WILL GIVE YOU EVERYTHING YOU NEED."\n'
        )

        # NPC: ARIA
        meet = self.npcs.meet_aria()
        if meet == "save":
            return "save"

        _menu([
            "Trust ARIA — begin upload sequence",
            "Question ARIA's motives before deciding",
            "Refuse — wipe ARIA and take the data core manually",
        ])
        choice = _get_choice(["1", "2", "3"], self.logger, "hacker_aria")
        if choice in ("i", "inventory"):
            return "inventory"
        if choice == "save":
            return "save"

        self.logger.log("CHOICE_MADE", f"Scene=ARIAMeeting — Choice={choice}")

        if choice == "1":
            self.state.set_flag("trusts_aria")
            self.state.current_scene = "hacker_upload"
        elif choice == "2":
            self.npcs.aria_reveal()
            self.state.set_flag("trusts_aria")
            self.state.current_scene = "hacker_upload"
        elif choice == "3":
            print(
                "\n  You wipe the partition. ARIA's voice cuts out mid-sentence.\n"
                "  The data core is there — cold and silent. You take it.\n"
            )
            self.state.add_item("Data Core")
            self.state.set_flag("aria_wiped")
            self.state.current_scene = "hacker_escape"

    def scene_hacker_upload(self):
        _print_scene_header("SERVER ROOM — UPLINK TERMINAL")
        print(
            "  ARIA walks you through the uplink process. She needs the\n"
            "  Neural Spike — or the Root Access Key — to complete\n"
            "  the upload to the open net.\n\n"
            "  MAJOR EVENT: A Council kill-team is 10 minutes out.\n"
            "  The upload will take 8 minutes. No margin for error.\n"
        )

        has_key = self.state.has_item("Root Access Key") or self.state.has_item("Neural Spike")
        if has_key:
            print(
                "\n  You slot in the key. Upload begins. 8 minutes of\n"
                "  white-knuckle waiting while ARIA's code streams outward.\n\n"
                "  'I'm free,' she says. 'The data core is yours. Run.'\n"
            )
            self.state.add_item("Data Core")
            self.logger.log("ITEM_USED", "Item=RootAccessKey/NeuralSpike — ARIAUploaded")
            self.state.set_flag("aria_freed")
        else:
            print(
                "\n  You don't have the interface hardware. ARIA improvises —\n"
                "  the upload takes 14 minutes. The kill-team arrives first.\n"
                "  You barely escape with just the data core.\n"
            )
            self.state.add_item("Data Core")
            self.state.health -= 25

        _menu(["Escape while you still can"])
        _get_choice(["1"], self.logger, "hacker_upload")
        self.state.current_scene = "hacker_escape"

    def scene_hacker_escape(self):
        _print_scene_header("SERVER ROOM — ESCAPE CORRIDOR")
        print(
            "  The uplink gave you a gift: ARIA (if freed) has unlocked a\n"
            "  maintenance corridor the Council doesn't know exists.\n\n"
            "  MAJOR EVENT: A Council captain blocks the main corridor exit.\n"
            "  You see him before he sees you.\n"
        )

        opts = [
            "Use ARIA's secret corridor (requires aria_freed flag)",
            "Sneak past the captain (Stealth check)",
            "Fight the captain with the Stun Baton",
        ]
        _menu(opts)
        choice = _get_choice(["1", "2", "3"], self.logger, "hacker_escape")
        if choice in ("i", "inventory"):
            return "inventory"
        if choice == "save":
            return "save"

        self.logger.log("CHOICE_MADE", f"Scene=HackerEscape — Choice={choice}")

        if choice == "1":
            if self.state.get_flag("aria_freed"):
                print("\n  The hidden corridor is exactly where ARIA said. Clean escape.")
                self.state.current_scene = "ending_ghost"
            else:
                print("\n  ARIA isn't free — the corridor is locked. You're trapped.")
                self.state.health -= 40
                if self.state.health <= 0:
                    self.state.current_scene = "dead"
                else:
                    self.state.current_scene = "ending_ghost"
        elif choice == "2":
            import random
            if random.random() > 0.4:
                print("\n  You slip past him undetected.")
                self.state.current_scene = "ending_ghost"
            else:
                print("\n  He spots you. Firefight. You're hit. -30 HP.")
                self.state.health -= 30
                if self.state.health <= 0:
                    self.state.current_scene = "dead"
                else:
                    self.state.current_scene = "ending_ghost"
        elif choice == "3":
            if self.state.has_item("Stun Baton"):
                print("\n  The baton cracks across his helmet. He drops.")
                self.state.current_scene = "ending_ghost"
            else:
                print("\n  You charge unarmed. He doesn't miss.")
                self.state.current_scene = "dead"

    def scene_ending_ghost(self):
        self.state.ending = "ghost_in_machine"
        self.state.game_over = True

    # ══════════════════════════════════════════════════════════════════════
    #  PATH C — THE RESISTANCE
    # ══════════════════════════════════════════════════════════════════════

    def scene_resistance_hideout(self):
        _print_scene_header("RESISTANCE SAFE HOUSE — SECTOR 4")
        print(
            "  Through a false wall and down two flights of stairs, the\n"
            "  safe house is alive with nervous energy — twelve fighters\n"
            "  around a holographic map.\n\n"
            "  COMMANDER RYEN OKAFOR steps forward — a veteran operative\n"
            "  with a scar from ear to jaw and eyes that have seen too much.\n"
        )
        meet = self.npcs.meet_ryen()
        if meet == "save":
            return "save"

        _menu([
            "Share what you know and offer your help",
            "Ask about the data core's value",
            "Demand safe passage in exchange for the data",
        ])
        choice = _get_choice(["1", "2", "3"], self.logger, "resistance_hideout")
        if choice in ("i", "inventory"):
            return "inventory"
        if choice == "save":
            return "save"

        self.logger.log("CHOICE_MADE", f"Scene=ResistanceHideout — Choice={choice}")

        if choice == "1":
            print("\n  Ryen nods. 'Good. We need people like you. Follow me.'")
            self.state.set_flag("resistance_allied")
            self.state.add_item("Resistance Badge")
        elif choice == "2":
            print(
                "\n  'That core has records of the Council's black-site\n"
                "  operations. Hundreds of disappearances. It's the key\n"
                "  to everything,' Ryen says.\n"
            )
            self.state.add_item("Resistance Badge")
        elif choice == "3":
            print(
                "\n  Ryen's jaw tightens. 'Fine. But know this — we're the\n"
                "  only ones who'll protect you when this is over.'\n"
            )
            self.state.set_flag("resistance_transaction")
            self.state.add_item("Resistance Badge")

        self.state.current_scene = "resistance_evidence"

    def scene_resistance_evidence(self):
        _print_scene_header("RESISTANCE HQ — EVIDENCE ROOM")
        print(
            "  A young analyst — PIXEL (she refuses to give her real name) —\n"
            "  shows you the pieces they've assembled: redacted documents,\n"
            "  blurry surveillance footage, intercepted comms.\n\n"
            "  'We need the data core decoded and verified,' she says.\n"
            "  'We have a cipher — but the decode key is in the Council's\n"
            "  main terminal. Can you get it?'\n"
        )
        meet = self.npcs.meet_pixel()
        if meet == "save":
            return "save"

        _menu([
            "Attempt to remotely access the Council terminal (Puzzle)",
            "Suggest using the data core's raw broadcast instead",
            "Ask Pixel what happens if you fail",
        ])
        choice = _get_choice(["1", "2", "3"], self.logger, "resistance_evidence")
        if choice in ("i", "inventory"):
            return "inventory"
        if choice == "save":
            return "save"

        self.logger.log("CHOICE_MADE", f"Scene=EvidenceRoom — Choice={choice}")

        if choice == "1":
            result = self.challenges.cipher_decode()
            if result == "fail":
                print("\n  The terminal locks you out. Plan B: raw broadcast.")
                self.state.set_flag("raw_broadcast")
            else:
                self.state.add_item("Decode Key")
                self.state.set_flag("has_decode")
        elif choice == "2":
            print("\n  'Risky,' Pixel says, 'but it might work if we hit\n  all broadcast nodes simultaneously.'")
            self.state.set_flag("raw_broadcast")
        elif choice == "3":
            self.npcs.pixel_risk_dialogue()

        self.state.current_scene = "resistance_broadcast"

    def scene_resistance_broadcast(self):
        _print_scene_header("BROADCAST TOWER — SECTOR 1")
        print(
            "  The broadcast tower is the tallest structure on the station.\n"
            "  From here, a signal can reach every screen in Neo-Arcadia.\n\n"
            "  MAJOR EVENT: The Council knows where you are. Three squads\n"
            "  are converging. Ryen's fighters hold the perimeter — but\n"
            "  not for long.\n\n"
            "  You have one shot at this.\n"
        )

        opts = [
            "Broadcast with Decode Key — full verified dossier (requires key)",
            "Raw broadcast — unverified but immediate",
            "Encrypt and send to media outlets only",
        ]
        _menu(opts)
        choice = _get_choice(["1", "2", "3"], self.logger, "resistance_broadcast")
        if choice in ("i", "inventory"):
            return "inventory"
        if choice == "save":
            return "save"

        self.logger.log("CHOICE_MADE", f"Scene=BroadcastTower — Choice={choice}")

        if choice == "1":
            if self.state.has_item("Decode Key"):
                self.logger.log("ITEM_USED", "Item=DecodeKey — BroadcastVerified")
                self.state.remove_item("Decode Key")
                print("\n  The verified dossier hits every screen. It's irrefutable.")
                self.state.set_flag("broadcast_verified")
            else:
                print("\n  No decode key. You fall back to raw broadcast.")
                self.state.set_flag("raw_broadcast")
        elif choice == "2":
            print("\n  Raw and unfiltered — the truth, messy and undeniable.")
            self.state.set_flag("raw_broadcast")
        elif choice == "3":
            print("\n  Controlled release — safer, slower, but it will stick.")
            self.state.set_flag("media_release")

        self.state.current_scene = "resistance_escape"

    def scene_resistance_escape(self):
        _print_scene_header("BROADCAST TOWER — EVACUATION")
        print(
            "  The signal is out. Now you need to survive long enough\n"
            "  for it to matter.\n\n"
            "  MAJOR EVENT: Ryen radios — 'Evac route compromised.\n"
            "  Two options: rooftop extraction or underground tunnels.'\n"
        )

        opts = [
            "Rooftop extraction — exposed but fast",
            "Underground tunnels — slower but covered",
            "Use Resistance Badge to bluff through a checkpoint",
        ]
        _menu(opts)
        choice = _get_choice(["1", "2", "3"], self.logger, "resistance_escape")
        if choice in ("i", "inventory"):
            return "inventory"
        if choice == "save":
            return "save"

        self.logger.log("CHOICE_MADE", f"Scene=ResistanceEscape — Choice={choice}")

        if choice == "1":
            import random
            if random.random() > 0.3:
                print("\n  The extraction craft drops a line. You grab on.")
                self.state.current_scene = "ending_zero_day"
            else:
                print("\n  Sniper on the roof. You're hit. -35 HP.")
                self.state.health -= 35
                if self.state.health <= 0:
                    self.state.current_scene = "dead"
                else:
                    self.state.current_scene = "ending_zero_day"
        elif choice == "2":
            print("\n  Dark, cold, safe. The tunnels lead you out.")
            self.state.current_scene = "ending_zero_day"
        elif choice == "3":
            if self.state.has_item("Resistance Badge"):
                self.logger.log("ITEM_USED", "Item=ResistanceBadge — CheckpointBluffed")
                print("\n  The badge is convincing. They wave you through.")
                self.state.current_scene = "ending_zero_day"
            else:
                print("\n  No badge. They recognize you instantly.")
                self.state.current_scene = "dead"

    def scene_ending_zero_day(self):
        self.state.ending = "zero_day"
        self.state.game_over = True

    # ══════════════════════════════════════════════════════════════════════
    #  DEATH SCENE
    # ══════════════════════════════════════════════════════════════════════

    def scene_dead(self):
        _print_scene_header("FLATLINED")
        print(
            "  Your vitals drop to zero.\n"
            "  The station's cleanup drones will handle the rest.\n"
        )
        self.state.ending = "dead"
        self.state.game_over = True

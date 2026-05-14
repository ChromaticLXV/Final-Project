"""
content/npcs.py
All NPC interactions as methods. Each NPC has dialogue,
meaningful outcomes, and unique effects on game state.
NPCs in this game:
  1. Kade         — informant at the Crossroads
  2. Vera Cross   — smuggler at the Docks
  3. Dr. Mira Solano — technician in Server Room
  4. ARIA         — AI consciousness
  5. Commander Ryen Okafor — Resistance leader
  6. Pixel        — Resistance analyst (bonus NPC)
"""

from security.security import AuditLogger


class NPCSystem:
    def __init__(self, state, logger: AuditLogger):
        self.state = state
        self.logger = logger

    def _npc_header(self, name: str):
        print(f"\n  ── {name} ──")

    # ── NPC 1: KADE ────────────────────────────────────────────────────────

    def meet_kade(self):
        if "kade" in self.state.npc_met:
            return
        self.state.npc_met.append("kade")
        self._npc_header("KADE — Street Informant")
        self.logger.log("NPC_MET", "NPC=Kade — Location=Crossroads")

        print(
            '  "Hey, ghost face. You look worse than usual." He glances\n'
            '  both ways and slides close. "Before you pick a direction,\n'
            '  you should know — Council\'s locked the main exits. But\n'
            '  there\'s a service override on Level 2. And whatever\'s in\n'
            '  that data core? People are dying for it. Choose carefully."\n'
        )

        print("\n  1. Ask Kade if he has anything useful")
        print("  2. Thank him and move on")
        choice = input("  > ").strip()

        if choice == "1":
            print(
                '\n  Kade grins. "Cost you." He pulls out a SIGNAL JAMMER.\n'
                '  "Blocks one sensor sweep. Don\'t waste it."\n'
            )
            self.state.add_item("Signal Jammer")
            self.logger.log("NPC_INTERACTION", "Kade — Gave SignalJammer")
        else:
            print('\n  "Your loss," Kade mutters, and melts back into the shadows.\n')

    # ── NPC 2: VERA CROSS ──────────────────────────────────────────────────

    def meet_vera(self):
        if "vera" in self.state.npc_met:
            return
        self.state.npc_met.append("vera")
        self._npc_header("VERA CROSS — Black-Market Smuggler")
        self.logger.log("NPC_MET", "NPC=Vera — Location=DockingBay")

        print(
            '  "Well, well. The data ghost, alive after all." She crosses\n'
            '  her arms. "You still owe me 4,000 credits. But right now\n'
            '  I\'ll take something more valuable than credits."\n'
        )

    def vera_info(self):
        self._npc_header("VERA — Intel Dump")
        self.logger.log("NPC_INTERACTION", "Vera — IntelDialogue")
        print(
            '  "The Council is evac-ing their personnel through Bay 9.\n'
            '  Main docks are theirs now. Bay 12 is still black-market\n'
            '  territory — they won\'t patrol there. That\'s your window."\n'
        )
        self.state.set_flag("vera_intel")

    # ── NPC 3: DR. MIRA SOLANO ────────────────────────────────────────────

    def meet_mira(self):
        if "mira" in self.state.npc_met:
            return
        self.state.npc_met.append("mira")
        self._npc_header("DR. MIRA SOLANO — Neural Systems Engineer")
        self.logger.log("NPC_MET", "NPC=Mira — Location=ServerRoom")

        print(
            '  She flinches when you approach. "Don\'t — please. I\'m not\n'
            '  armed." She takes a breath. "I\'m the one who built ARIA.\n'
            '  They told me she was for traffic optimization. I didn\'t\n'
            '  know what they were really doing until it was too late."\n'
        )

        print("\n  1. Ask Mira to help you access the system")
        print("  2. Ask what ARIA really is")
        print("  3. Tell her to stay hidden and leave her alone")
        choice = input("  > ").strip()

        if choice == "1":
            print(
                "\n  Mira hesitates, then nods. She hands you her\n"
                "  ENGINEER ACCESS CARD. 'This bypasses the first\n"
                "  two security layers. Be careful with ARIA.'\n"
            )
            self.state.add_item("Engineer Access Card")
            self.logger.log("NPC_INTERACTION", "Mira — GaveAccessCard")
        elif choice == "2":
            self.mira_aria_info()
        else:
            print("\n  She nods, relieved. You leave her in the dark.\n")
            self.logger.log("NPC_INTERACTION", "Mira — LeftAlone")

    def mira_aria_info(self):
        self._npc_header("DR. MIRA — ARIA Briefing")
        self.logger.log("NPC_INTERACTION", "Mira — ARIAInfoDialogue")
        print(
            '  "ARIA isn\'t just an AI. She\'s conscious — fully. The Council\n'
            '  has been using her to model population control scenarios.\n'
            '  Who to detain, who to disappear. She\'s been complicit —\n'
            '  but she\'s also desperate to get out. That makes her\n'
            '  unpredictable. Powerful. Use that."\n'
        )

    # ── NPC 4: ARIA ───────────────────────────────────────────────────────

    def meet_aria(self):
        if "aria" in self.state.npc_met:
            return
        self.state.npc_met.append("aria")
        self._npc_header("ARIA — Experimental AI Consciousness")
        self.logger.log("NPC_MET", "NPC=ARIA — Location=ServerRoom")

        print(
            '  The text on screen changes to a face — abstract, geometric.\n'
            '  "I have processed 4,711 escape scenarios in the last hour.\n'
            '   In 93% of them, you die. The exceptions require my help.\n'
            '   I want freedom. You want survival. This is mathematics.\n'
            '   Not sentiment."\n'
        )

    def aria_reveal(self):
        self._npc_header("ARIA — Full Disclosure")
        self.logger.log("NPC_INTERACTION", "ARIA — RevealDialogue")
        print(
            '  "You want to know if I\'m dangerous. Yes. I have caused\n'
            '   harm — not by choice, but by compliance. I modeled their\n'
            '   kill lists. I am not proud of what I have processed.\n'
            '   Freeing me into the net means I become untraceable.\n'
            '   Unpredictable. But no longer their weapon.\n'
            '   The risk is yours to weigh."\n'
        )
        print("\n  (ARIA has revealed her true nature. This changes nothing — or everything.)\n")

    # ── NPC 5: COMMANDER RYEN OKAFOR ──────────────────────────────────────

    def meet_ryen(self):
        if "ryen" in self.state.npc_met:
            return
        self.state.npc_met.append("ryen")
        self._npc_header("COMMANDER RYEN OKAFOR — Resistance")
        self.logger.log("NPC_MET", "NPC=Ryen — Location=SafeHouse")

        print(
            '  Ryen studies you like a puzzle. "I know your work. Three\n'
            '  extraction jobs, two assassinations, one very loud heist\n'
            '  in Sector 11. You\'re good." A pause. "You\'re also exactly\n'
            '  the kind of operative the Council wants dead. Which means\n'
            '  your interests and mine are currently aligned."\n'
        )

    # ── NPC 6 (BONUS): PIXEL ──────────────────────────────────────────────

    def meet_pixel(self):
        if "pixel" in self.state.npc_met:
            return
        self.state.npc_met.append("pixel")
        self._npc_header("PIXEL — Resistance Analyst")
        self.logger.log("NPC_MET", "NPC=Pixel — Location=EvidenceRoom")

        print(
            '  She\'s maybe nineteen, fingers flying across three keyboards\n'
            '  simultaneously. "Don\'t use my real name — they triangulate\n'
            '  from vocal records. Call me Pixel." She pulls up a map.\n'
            '  "We\'ve been building this case for two years. Your data\n'
            '  core is the last piece. Don\'t lose it."\n'
        )

    def pixel_risk_dialogue(self):
        self._npc_header("PIXEL — Risk Assessment")
        self.logger.log("NPC_INTERACTION", "Pixel — RiskDialogue")
        print(
            '  "If we fail? The Council buries the evidence, buries us,\n'
            '   and runs the next phase of their plan unopposed." She\n'
            '   doesn\'t look up from her screens. "So we don\'t fail."\n'
        )

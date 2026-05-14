"""
systems/challenges.py
Implements the game's challenges (puzzles, combat, obstacles).
Challenge 1: Terminal Hack    — hacker path, logic puzzle
Challenge 2: Drone Combat     — smuggler path, timed decision
Challenge 3: Cipher Decode    — resistance path, code puzzle
"""

import random
from security.security import AuditLogger


class ChallengeSystem:
    def __init__(self, state, logger: AuditLogger):
        self.state = state
        self.logger = logger

    # ── Shared helpers ─────────────────────────────────────────────────────

    def _get_answer(self, prompt: str) -> str:
        """Safe input — never crashes on unexpected text."""
        try:
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            return ""

    def _get_number(self, prompt: str, lo: int, hi: int) -> int:
        """Safe numeric input with range validation."""
        while True:
            raw = self._get_answer(prompt)
            try:
                val = int(raw)
                if lo <= val <= hi:
                    return val
                print(f"  Please enter a number between {lo} and {hi}.")
            except ValueError:
                self.logger.log("INPUT_INVALID", f'Non-numeric input "{raw}" in challenge')
                print("  That's not a valid number. Try again.")

    # ══════════════════════════════════════════════════════════════════════
    #  CHALLENGE 1: TERMINAL HACK (Logic Puzzle)
    #  Location: Server Room (Hacker path)
    #  Player must guess the correct 3-digit PIN using hot/cold feedback.
    #  3 attempts. Success: root access. Fail: security lockout, -15 HP.
    # ══════════════════════════════════════════════════════════════════════

    def terminal_hack(self) -> str:
        print("""
┌──────────────────────────────────────────────────────────┐
│  CHALLENGE: COUNCIL TERMINAL HACK                        │
│                                                          │
│  The terminal is locked behind a 3-digit PIN.            │
│  You must guess the correct code in 3 attempts.          │
│                                                          │
│  After each guess you'll be told:                        │
│    CORRECT   — right digit, right position               │
│    CLOSE     — right digit, wrong position               │
│    WRONG     — digit not in the code at all              │
│                                                          │
│  Digits 1–9 only. No repeats in the secret code.         │
└──────────────────────────────────────────────────────────┘
""")
        # Generate a secret 3-digit code (no repeats, digits 1-9)
        digits = random.sample(range(1, 10), 3)
        secret = [str(d) for d in digits]
        max_attempts = 3
        attempts = 0
        success = False

        while attempts < max_attempts:
            attempts += 1
            print(f"  Attempt {attempts}/{max_attempts}:")
            raw = self._get_answer("  Enter 3 digits (e.g. 472): ").strip()

            # Validate: must be exactly 3 digits
            if not raw.isdigit() or len(raw) != 3:
                self.logger.log(
                    "CHALLENGE_ATTEMPT",
                    f"Puzzle=TerminalHack — INVALID_INPUT — Input={raw}"
                )
                print("  Invalid. Enter exactly 3 digits.")
                attempts -= 1  # Don't penalize for formatting errors
                continue

            guess = list(raw)
            feedback = []
            for i, g in enumerate(guess):
                if g == secret[i]:
                    feedback.append("CORRECT")
                elif g in secret:
                    feedback.append("CLOSE")
                else:
                    feedback.append("WRONG")

            print(f"  Feedback: {' | '.join(feedback)}")
            self.logger.log(
                "CHALLENGE_ATTEMPT",
                f"Puzzle=TerminalHack — Attempt={attempts} — "
                f"Input={raw} — Feedback={','.join(feedback)}"
            )

            if all(f == "CORRECT" for f in feedback):
                success = True
                break

        if success:
            code_str = "".join(secret)
            print(f"\n  ✓ ACCESS GRANTED. Terminal unlocked. Code was: {code_str}")
            self.logger.log(
                "CHALLENGE_ATTEMPT",
                f"Puzzle=TerminalHack — SUCCESS — Attempts={attempts}"
            )
            return "success"
        else:
            code_str = "".join(secret)
            print(f"\n  ✗ LOCKOUT TRIGGERED. The code was: {code_str}")
            self.logger.log(
                "CHALLENGE_ATTEMPT",
                f"Puzzle=TerminalHack — FAIL — Attempts={attempts}"
            )
            return "fail"

    # ══════════════════════════════════════════════════════════════════════
    #  CHALLENGE 2: DRONE COMBAT (Timed Decision Obstacle)
    #  Location: Sector 9 Vault corridor (Smuggler path)
    #  Player must navigate past a patrol drone using timing and items.
    #  Wrong choice = damage. Signal Jammer can guarantee safe passage.
    # ══════════════════════════════════════════════════════════════════════

    def drone_challenge(self) -> str:
        print("""
┌──────────────────────────────────────────────────────────┐
│  CHALLENGE: GUARD DRONE — SECTOR 9 CORRIDOR              │
│                                                          │
│  A Mark-IV patrol drone sweeps the corridor every        │
│  30 seconds. Its sensor cone covers 270 degrees.         │
│  One wrong move and it fires.                            │
│                                                          │
│  You have three options. Choose wisely.                  │
└──────────────────────────────────────────────────────────┘
""")
        print("  What do you do?")
        print("  1. Use the Signal Jammer to blind its sensors (requires item)")
        print("  2. Time a sprint between sweeps (50% chance)")
        print("  3. Attempt to hack the drone's firmware (difficult)")
        print()

        attempts = 0
        while True:
            raw = self._get_answer("  > ").strip()
            if raw in ("1", "2", "3"):
                break
            attempts += 1
            self.logger.log(
                "INPUT_INVALID",
                f'User entered "{raw}" in DroneChallenge attempt={attempts}'
            )
            print("  Invalid. Enter 1, 2, or 3.")

        self.logger.log(
            "CHALLENGE_ATTEMPT",
            f"Puzzle=DroneCombat — Choice={raw}"
        )

        if raw == "1":
            if self.state.has_item("Signal Jammer"):
                self.state.remove_item("Signal Jammer")
                self.state.set_flag("sensor_jammed")
                self.logger.log(
                    "CHALLENGE_ATTEMPT",
                    "Puzzle=DroneCombat — SUCCESS — Used SignalJammer"
                )
                print("\n  The jammer activates. The drone's sensor eye dims.")
                print("  You walk straight through. Easy.\n")
                return "success"
            else:
                print("\n  You reach for the jammer — you don't have one.")
                print("  Falling back to option 2...\n")
                raw = "2"

        if raw == "2":
            roll = random.random()
            if roll > 0.5:
                self.logger.log(
                    "CHALLENGE_ATTEMPT",
                    "Puzzle=DroneCombat — SUCCESS — Sprint"
                )
                print("\n  You count the sweep timing. Three... two... now.")
                print("  You sprint the gap perfectly. Made it.\n")
                return "success"
            else:
                self.logger.log(
                    "CHALLENGE_ATTEMPT",
                    "Puzzle=DroneCombat — FAIL — Sprint"
                )
                print("\n  You mis-time the sprint. The sensor catches you.")
                print("  The drone fires a warning shot. -25 HP.\n")
                self.state.health -= 25
                if self.state.health <= 0:
                    return "dead"
                return "success"  # Damaged but through

        if raw == "3":
            # Harder sub-puzzle: guess a 2-digit hex byte
            print(
                "\n  You pull up the drone's firmware interface.\n"
                "  A 2-digit hex code (00–FF) secures the override.\n"
                "  You have 2 guesses. Hint: the first digit is 'A'.\n"
            )
            secret = "A" + random.choice("0123456789ABCDEF")
            drone_attempts = 0
            drone_success = False

            while drone_attempts < 2:
                drone_attempts += 1
                guess = self._get_answer(f"  Hex code (attempt {drone_attempts}/2): ").strip().upper()
                self.logger.log(
                    "CHALLENGE_ATTEMPT",
                    f"Puzzle=DroneFirmware — Attempt={drone_attempts} — Input={guess}"
                )
                if guess == secret:
                    drone_success = True
                    break
                else:
                    print(f"  Wrong. {'One attempt left.' if drone_attempts == 1 else ''}")

            if drone_success:
                self.logger.log(
                    "CHALLENGE_ATTEMPT",
                    f"Puzzle=DroneFirmware — SUCCESS — Code={secret}"
                )
                print(f"\n  Override accepted. The drone powers down.\n")
                return "success"
            else:
                self.logger.log(
                    "CHALLENGE_ATTEMPT",
                    f"Puzzle=DroneFirmware — FAIL — Code={secret}"
                )
                print(f"\n  The code was {secret}. The drone fires. -30 HP.\n")
                self.state.health -= 30
                if self.state.health <= 0:
                    return "dead"
                return "success"

        return "success"

    # ══════════════════════════════════════════════════════════════════════
    #  CHALLENGE 3: CIPHER DECODE (Code Puzzle)
    #  Location: Evidence Room (Resistance path)
    #  Player must decode a simple Caesar cipher shift.
    #  2 attempts. Success: Decode Key. Fail: raw broadcast only.
    # ══════════════════════════════════════════════════════════════════════

    def cipher_decode(self) -> str:
        SHIFT = 5
        plaintext = "COUNCIL PROTOCOL SEVEN"
        # Encode it
        encoded = ""
        for ch in plaintext:
            if ch.isalpha():
                shifted = chr((ord(ch) - ord('A') + SHIFT) % 26 + ord('A'))
                encoded += shifted
            else:
                encoded += ch

        print(f"""
┌──────────────────────────────────────────────────────────┐
│  CHALLENGE: CIPHER DECODE — COUNCIL TERMINAL             │
│                                                          │
│  You've intercepted an encrypted Council command string. │
│  It's a Caesar cipher (letters shifted by a fixed        │
│  number). Decode it in 2 attempts to get the key.        │
│                                                          │
│  Encoded message: {encoded:<40}│
│                                                          │
│  Hint: The shift is a single digit between 1 and 9.      │
│  Enter the decoded plaintext exactly.                    │
└──────────────────────────────────────────────────────────┘
""")
        max_attempts = 2
        for attempt in range(1, max_attempts + 1):
            raw = self._get_answer(f"  Decoded message (attempt {attempt}/{max_attempts}): ").strip().upper()
            self.logger.log(
                "CHALLENGE_ATTEMPT",
                f"Puzzle=CipherDecode — Attempt={attempt} — Input={raw}"
            )
            if raw == plaintext:
                print(f"\n  ✓ CORRECT. Plaintext: '{plaintext}'")
                self.logger.log(
                    "CHALLENGE_ATTEMPT",
                    f"Puzzle=CipherDecode — SUCCESS — Attempts={attempt}"
                )
                return "success"
            else:
                print(f"  Incorrect. {'Hint: try shift 5.' if attempt == 1 else ''}")

        print(f"\n  ✗ Failed. The answer was: '{plaintext}'")
        self.logger.log(
            "CHALLENGE_ATTEMPT",
            f"Puzzle=CipherDecode — FAIL — Attempts={max_attempts}"
        )
        return "fail"

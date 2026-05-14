"""
security/security.py
Cyber Pack — Part 1 & 2:
  - Input validation helpers
  - AuditLogger: timestamped event logging to audit_log.txt
"""

import datetime
import os


LOG_FILE = "audit_log.txt"


class AuditLogger:
    """
    Writes security-relevant events to audit_log.txt with timestamps.
    Each line format:
      YYYY-MM-DD HH:MM:SS - EVENT_TYPE - Details
    """

    def __init__(self, log_file: str = LOG_FILE):
        self.log_file = log_file
        self._ensure_file()

    def _ensure_file(self):
        """Create the log file if it doesn't exist."""
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write(f"# Station Zero Audit Log — Created {self._timestamp()}\n")

    def _timestamp(self) -> str:
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def log(self, event_type: str, details: str = ""):
        """
        Append one log entry. Never raises — silently fails if I/O error.
        Example output:
          2026-01-19 14:35:21 - GAME_START - Player started a new game
        """
        try:
            line = f"{self._timestamp()} - {event_type} - {details}\n"
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(line)
        except OSError:
            pass  # Log failure should never crash the game


# ── Input validation helpers ───────────────────────────────────────────────

def validate_numeric_choice(raw: str, lo: int, hi: int) -> tuple:
    """
    Validate that raw is an integer in [lo, hi].
    Returns (True, int_value) or (False, None).
    """
    try:
        val = int(raw)
        if lo <= val <= hi:
            return True, val
        return False, None
    except (ValueError, TypeError):
        return False, None


def safe_prompt(prompt: str, lo: int, hi: int,
                logger: AuditLogger, context: str = "") -> int:
    """
    Keep asking until the user enters a valid integer in [lo, hi].
    Logs all invalid attempts.
    """
    while True:
        raw = input(prompt).strip()
        valid, val = validate_numeric_choice(raw, lo, hi)
        if valid:
            return val
        logger.log("INPUT_INVALID", f'Input="{raw}" at {context} — expected {lo}–{hi}')
        print(f"  Invalid input. Please enter a number from {lo} to {hi}.")

"""
security/save_load.py
Cyber Pack — Part 3:
  Save and load game progress with SHA-256 tamper detection.
  Save format (JSON):
    {
      "state": { ... game state dict ... },
      "checksum": "<sha256 hex digest of JSON(state)>"
    }
  On load, the checksum is recomputed and compared.
  A mismatch means the file was tampered with or corrupted.
"""

import json
import hashlib
import os
from security.security import AuditLogger


SAVE_FILE = "savegame.json"


class SaveLoadSystem:
    def __init__(self, logger: AuditLogger, save_file: str = SAVE_FILE):
        self.logger = logger
        self.save_file = save_file

    # ── Internal helpers ───────────────────────────────────────────────────

    def _compute_checksum(self, state_dict: dict) -> str:
        """
        Serialize state to a canonical JSON string (sorted keys)
        and return its SHA-256 hex digest.
        """
        canonical = json.dumps(state_dict, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    # ── Save ───────────────────────────────────────────────────────────────

    def save(self, state_dict: dict) -> bool:
        """
        Save state to JSON with embedded checksum.
        Returns True on success, False on failure.
        """
        try:
            checksum = self._compute_checksum(state_dict)
            payload = {
                "state": state_dict,
                "checksum": checksum,
            }
            with open(self.save_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            self.logger.log("SAVE_ATTEMPT", f"SUCCESS — File={self.save_file}")
            return True
        except (OSError, TypeError) as e:
            self.logger.log("SAVE_ATTEMPT", f"FAIL — Error={e}")
            print(f"\n  [ERROR] Could not save game: {e}")
            return False

    # ── Load ───────────────────────────────────────────────────────────────

    def load(self) -> dict | None:
        """
        Load and validate a save file.
        Returns the state dict on success, None on failure.
        Prints an appropriate message in each case.
        """
        if not os.path.exists(self.save_file):
            self.logger.log("LOAD_ATTEMPT", f"FAIL — Reason=NO_SAVE_FILE")
            print("\n  No save file found.")
            return None

        try:
            with open(self.save_file, "r", encoding="utf-8") as f:
                payload = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            self.logger.log("LOAD_ATTEMPT", f"FAIL — Reason=FILE_CORRUPT — Error={e}")
            print("\n  Save file is corrupted and cannot be loaded.")
            return None

        # Validate structure
        if "state" not in payload or "checksum" not in payload:
            self.logger.log("LOAD_ATTEMPT", "FAIL — Reason=MISSING_FIELDS")
            print("\n  Save file is missing required fields.")
            return None

        state_dict = payload["state"]
        stored_checksum = payload["checksum"]

        # Tamper check
        recomputed = self._compute_checksum(state_dict)
        if recomputed != stored_checksum:
            self.logger.log(
                "LOAD_ATTEMPT",
                f"FAIL — Reason=SAVE_TAMPERED — "
                f"Expected={stored_checksum[:16]}... Got={recomputed[:16]}..."
            )
            print(
                "\n  ⚠  TAMPER DETECTED: The save file has been modified.\n"
                "   Refusing to load a compromised save. Start a new game."
            )
            return None

        self.logger.log("LOAD_ATTEMPT", f"SUCCESS — File={self.save_file}")
        print(f"\n  Save file verified. Checksum OK.")
        return state_dict

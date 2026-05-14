"""
systems/inventory.py
Inventory management: add, remove, use, and describe items.
Item definitions include descriptions and use effects.
"""

from security.security import AuditLogger


ITEM_CATALOG = {
    "Stun Baton": {
        "description": "A guard's electric baton. Delivers a non-lethal shock.",
        "use": "combat",
    },
    "Station Map": {
        "description": "A physical map of the station. Shows all major sectors.",
        "use": "navigation",
    },
    "Vault Access Code": {
        "description": "A 6-digit numeric code scrawled on a napkin. Sector 9 vault.",
        "use": "unlock_vault",
    },
    "Medkit": {
        "description": "Standard medical kit. Restores up to 30 HP.",
        "use": "heal",
    },
    "Cargo Pass": {
        "description": "An official cargo transit pass. Valid for docking bay checkpoints.",
        "use": "bluff_checkpoint",
    },
    "Data Core": {
        "description": "The data core. Contains evidence of Council crimes. Handle with care.",
        "use": "story_critical",
    },
    "Council Dossier": {
        "description": "Physical records naming three Council members in a massacre.",
        "use": "evidence",
    },
    "Signal Jammer": {
        "description": "Blocks one sensor sweep. Single-use.",
        "use": "block_sensor",
    },
    "Root Access Key": {
        "description": "Gives root-level access to the station's neural core.",
        "use": "terminal_access",
    },
    "Neural Spike": {
        "description": "Hardware interface for AI systems. Allows direct uplink.",
        "use": "ai_interface",
    },
    "Engineer Access Card": {
        "description": "Dr. Solano's card. Bypasses the first two security layers.",
        "use": "security_bypass",
    },
    "Decode Key": {
        "description": "Cryptographic key to decode the encrypted Council dossier.",
        "use": "decode_evidence",
    },
    "Resistance Badge": {
        "description": "Resistance ID. Can bluff through lower-security checkpoints.",
        "use": "bluff_checkpoint",
    },
}


class InventorySystem:
    """Wraps GameState inventory with catalog lookups and use-item logic."""

    def __init__(self, state):
        self.state = state

    def add_item(self, item_name: str) -> bool:
        if item_name not in ITEM_CATALOG:
            print(f"  [WARN] Unknown item: {item_name}")
            return False
        self.state.add_item(item_name)
        return True

    def remove_item(self, item_name: str) -> bool:
        return self.state.remove_item(item_name)

    def use_item(self, item_name: str, logger: AuditLogger) -> str:
        """
        Use an item from inventory. Returns an outcome string or 'not_found'.
        Side effects: updates state health, flags, etc.
        """
        if not self.state.has_item(item_name):
            return "not_found"

        item = ITEM_CATALOG.get(item_name, {})
        use_type = item.get("use", "none")
        result = "used"

        if use_type == "heal":
            heal = min(30, 100 - self.state.health)
            self.state.health += heal
            self.state.remove_item(item_name)
            logger.log("ITEM_USED", f"Item={item_name} — Healed {heal}HP")
            print(f"\n  You use the {item_name}. Health: {self.state.health}/100")

        elif use_type == "block_sensor":
            self.state.remove_item(item_name)
            self.state.set_flag("sensor_jammed")
            logger.log("ITEM_USED", f"Item={item_name} — SensorJammed")
            print(f"\n  The {item_name} activates. One sensor sweep blocked.")

        elif use_type in ("combat", "bluff_checkpoint", "terminal_access",
                          "ai_interface", "security_bypass", "decode_evidence",
                          "unlock_vault", "story_critical", "evidence", "navigation"):
            desc = item.get("description", "")
            print(f"\n  [{item_name}] {desc}")
            print("  (This item will be used automatically when required by the story.)")
            result = "info"

        else:
            print(f"\n  You examine the {item_name}. No immediate use here.")
            result = "no_effect"

        return result

    def describe_item(self, item_name: str):
        item = ITEM_CATALOG.get(item_name, {})
        desc = item.get("description", "No description available.")
        print(f"\n  [{item_name}]: {desc}")

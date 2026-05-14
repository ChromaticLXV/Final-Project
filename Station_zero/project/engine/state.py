"""
engine/state.py
Manages the complete game state object, including player stats,
flags, inventory, and current scene.
"""


class GameState:
    """Holds all mutable game data for one playthrough."""

    def __init__(self):
        self.player_name = "Unknown"
        self.current_scene = "intro"
        self.health = 100
        self.path_chosen = None          # "smuggler" | "hacker" | "resistance"
        self.flags = {}                  # Stores story decisions as key:bool pairs
        self.inventory = []              # List of item name strings
        self.npc_met = []                # Track which NPCs have been encountered
        self.game_over = False
        self.ending = None               # Tracks which ending was reached

    # ── Flags ──────────────────────────────────────────────────────────────

    def set_flag(self, key: str, value=True):
        self.flags[key] = value

    def get_flag(self, key: str, default=False):
        return self.flags.get(key, default)

    # ── Inventory helpers ──────────────────────────────────────────────────

    def add_item(self, item: str):
        if item not in self.inventory:
            self.inventory.append(item)
            print(f"\n  [+] Added to inventory: {item}")

    def remove_item(self, item: str) -> bool:
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False

    def has_item(self, item: str) -> bool:
        return item in self.inventory

    def show_inventory(self):
        print("\n┌─────────────────────────────┐")
        print("│         INVENTORY           │")
        print("├─────────────────────────────┤")
        if self.inventory:
            for item in self.inventory:
                print(f"│  • {item:<25} │")
        else:
            print("│  (empty)                    │")
        print(f"│                             │")
        print(f"│  Health: {self.health}/100{' '*(19-len(str(self.health)))}│")
        print("└─────────────────────────────┘")

    # ── Serialization ──────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "player_name": self.player_name,
            "current_scene": self.current_scene,
            "health": self.health,
            "path_chosen": self.path_chosen,
            "flags": self.flags,
            "inventory": self.inventory,
            "npc_met": self.npc_met,
            "game_over": self.game_over,
            "ending": self.ending,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        gs = cls()
        gs.player_name = data.get("player_name", "Unknown")
        gs.current_scene = data.get("current_scene", "intro")
        gs.health = data.get("health", 100)
        gs.path_chosen = data.get("path_chosen")
        gs.flags = data.get("flags", {})
        gs.inventory = data.get("inventory", [])
        gs.npc_met = data.get("npc_met", [])
        gs.game_over = data.get("game_over", False)
        gs.ending = data.get("ending")
        return gs

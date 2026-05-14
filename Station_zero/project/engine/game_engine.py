"""
engine/game_engine.py
Core game engine: main loop, scene routing, menu handling,
save/load integration, and input validation dispatcher.
"""

from engine.state import GameState
from content.story import StoryEngine
from systems.inventory import InventorySystem
from security.save_load import SaveLoadSystem
from security.security import AuditLogger


def safe_input(prompt: str, valid_options: list, logger: AuditLogger, context: str = "") -> str:
    """
    Prompt the player, re-prompt on invalid input, and log invalid attempts.
    Accepts numbers (as strings) or special keywords: 'i', 'inventory', 'save'.
    valid_options: list of valid string choices (e.g. ['1','2','3'])
    """
    extended = valid_options + ["i", "inventory", "save"]
    while True:
        raw = input(prompt).strip().lower()
        if raw in [opt.lower() for opt in extended]:
            return raw
        logger.log("INPUT_INVALID", f'User entered "{raw}" at {context}')
        print(f"  Invalid input. Please enter one of: {', '.join(valid_options)}")


class GameEngine:
    """Orchestrates the full game: scene routing, game loop, save/load."""

    def __init__(self, logger: AuditLogger):
        self.logger = logger
        self.state = None
        self.story = None
        self.inventory_sys = None
        self.save_sys = SaveLoadSystem(logger)

    # ── Game setup ─────────────────────────────────────────────────────────

    def new_game(self):
        self.state = GameState()
        name = input("\nEnter your operative name: ").strip()
        self.state.player_name = name if name else "Ghost"
        self.story = StoryEngine(self.state, self.logger)
        self.inventory_sys = InventorySystem(self.state)
        self.logger.log("GAME_START", f"New game started — Player: {self.state.player_name}")
        self._game_loop()

    def load_game(self):
        state_data = self.save_sys.load()
        if state_data is None:
            print("\nReturning to main menu.")
            return
        self.state = GameState.from_dict(state_data)
        self.story = StoryEngine(self.state, self.logger)
        self.inventory_sys = InventorySystem(self.state)
        print(f"\n  Welcome back, {self.state.player_name}.")
        self._game_loop()

    # ── Main loop ──────────────────────────────────────────────────────────

    def _game_loop(self):
        """
        Main loop: fetch the current scene handler from StoryEngine,
        execute it, then check if the game is over.
        """
        while not self.state.game_over:
            scene_id = self.state.current_scene

            # Dispatch to the correct scene method
            handler = self.story.get_scene_handler(scene_id)
            if handler is None:
                print(f"\n[ERROR] Unknown scene: '{scene_id}'. Returning to main menu.")
                self.logger.log("ERROR", f"Unknown scene: {scene_id}")
                break

            result = handler()

            # After every scene action, check for special commands
            # (The scene handlers return 'save' or 'inventory' if those were typed)
            if result == "save":
                self._do_save()
            elif result == "inventory":
                self.state.show_inventory()
                # Re-run the same scene
                continue

        if self.state.game_over:
            self._show_ending()

    # ── Save / Load helpers ────────────────────────────────────────────────

    def _do_save(self):
        success = self.save_sys.save(self.state.to_dict())
        if success:
            print("  Game saved successfully.")
        else:
            print("  Save failed.")

    # ── Ending screen ──────────────────────────────────────────────────────

    def _show_ending(self):
        endings = {
            "shadow_broker": (
                "ENDING 1 — THE SHADOW BROKER",
                "You delivered the stolen data core to the syndicate contact\n"
                "  and vanished into the undercity. They gave you enough credits\n"
                "  to disappear. Neo-Arcadia never knew your name. Neither will\n"
                "  history. You survived — at a cost."
            ),
            "ghost_in_machine": (
                "ENDING 2 — GHOST IN THE MACHINE",
                "You uploaded ARIA's consciousness into the open net before\n"
                "  the station lockdown. She's free — distributed across a\n"
                "  thousand nodes. You're in a holding cell. But somewhere out\n"
                "  there, an AI owes you a favor. That's worth something."
            ),
            "zero_day": (
                "ENDING 3 — ZERO DAY",
                "You broadcast the evidence of the Council's crimes to every\n"
                "  screen in Neo-Arcadia. The city burned for three days.\n"
                "  Then it rebuilt. The Resistance calls you a hero. Corp\n"
                "  hunters still have your face on a wanted list. Freedom\n"
                "  has a price. You're still paying it."
            ),
            "dead": (
                "ENDING — FLATLINED",
                "Your vitals dropped to zero. The station's cleanup drones\n"
                "  catalogued your remains as debris. Neo-Arcadia moves on.\n"
                "  It always does."
            ),
        }

        key = self.state.ending or "dead"
        title, text = endings.get(key, endings["dead"])

        print(f"""
╔══════════════════════════════════════════════════════════════╗
║  {title:<60}║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
  {text}

╚══════════════════════════════════════════════════════════════╝
""")
        self.logger.log("GAME_END", f"Ending={key} — Player={self.state.player_name}")

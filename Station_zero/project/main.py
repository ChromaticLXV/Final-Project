"""
main.py
Entry point for Station Zero game.
"""

from security.security import AuditLogger
from engine.game_engine import GameEngine


def main():
    logger = AuditLogger()
    engine = GameEngine(logger)

    print("Welcome to Station Zero")
    print("A Cyberpunk Text-Based Adventure")
    print()
    print("1. New Game")
    print("2. Load Game")
    print("3. Quit")

    while True:
        choice = input("> ").strip()
        if choice == "1":
            engine.new_game()
            break
        elif choice == "2":
            engine.load_game()
            if engine.state is not None:  # Load successful
                break
        elif choice == "3":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
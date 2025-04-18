# turn.py

from Players import Player
from Core import Game

def process_turn(game: "Game", player: "Player") -> None:
	"""
	Process a single player's turn:
	- If in jail, attempt to resolve jail status.
	- Roll dice (handling doubles/speed dice).
	- Move and land on space.
	- Trigger any effects of landing.
	- End turn.
	"""
	print(f"\n--- {player.name}'s Turn ---")

	if player.in_jail:
		print(f"{player.name} is in jail.")
		freed = player.handle_jail_turn(game)
		if not freed:
			print(f"{player.name} remains in jail.")
			return  # End turn early if still jailed

	# Dice rolling
	roll = game.dice.roll()
	player.dice_roll = roll
	print(f"{player.name} rolled: {roll}")

	# Movement
	steps = roll["total"]
	game.board.move_player(player, steps)
	new_space = game.board.spaces[player.position]
	print(f"{player.name} landed on {new_space.name}.")

	# Space interaction
	new_space.on_land(player, game)

	# End turn
	player.end_turn(game)


def actions_menu(player: Player, game: Game) -> None:
	"""
	Display a menu of actions that the player can take during their turn.
	"""
	print("\n--- Actions Menu ---")
	print("1. Build")
	print("2. Trade")
	print("3. Mortgage/Unmortgage")
	print("4. End Turn")

	choice = input("Choose an action (1-4): ")
	if choice == "1":
		player.build(game)###############################
	elif choice == "2":
		player.trade(game)
	elif choice == "3":
		player.mortgage_unmortgage(game)
	elif choice == "4":
		return
	else:
		print("Invalid choice. Please try again.")
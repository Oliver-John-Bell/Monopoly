import os
from typing import Dict, Any, Optional
from Cards import Deck, Card
from Players import Player, AI
from Board import Board
from Core import Bank, Dice

# Note: The following classes/interfaces are assumed to be defined elsewhere:
# - Card (for returning "Get Out of Jail Free" cards to decks)

class Game:
	def __init__(self, save_slot: int = 0, autosave: bool = False):
		data = self.get_data()
		self.config: Dict[str, Any] = data.get("Config")
		self.players = []
		self.current_turn = 0
		self.bank = Bank(self.config.get("Houses", 32), self.config.get("Hotels", 16))
		self.decks: Dict[str, Deck] = {
			"Chance": Deck(data.get("Chance")), 
			"Comunity_Chest": Deck(data.get("Comunity_Chest"))
			}
		self.board = Board(data.get("Spaces"), self.config, self.decks)
		self.save_slot = save_slot
		self.autosave = autosave
		self.first_player_index = 0
		self.dice = Dice(self.config)

	def start_game(self):
		"""
		Runs the main game loop.
		In a real game you’d have a much more detailed turn‐by‐turn process,
		but here we simulate turns until only one active player remains.
		"""
		print("Starting the game!")
		while not self.is_game_over():
			current_player = self.players[self.current_turn]
			# If the current player is bankrupt, skip to the next one.
			if current_player.bankrupt:
				self.next_player()
				continue

			print(f"\nIt's {current_player.name}'s turn.")
			self.first_player_index = self.current_turn

			# Example turn:
			roll = self.dice.roll()
			print(f"{current_player.name} rolled a {roll}.")
			current_player.dice_roll = roll
			
			# Move the player and process the landing space.
			# (Assuming Board has a method process_space that takes the player, dice roll, and game instance.)

			# End-of-turn procedures (buying, auctions, etc.) would be handled here.
			# Optionally, you could save the game after each complete round:
			# self.save_game(self.save_slot)
			
			self.next_player()

		self.end_game()
	
	def add_player(self, name):
		"""Adds a human player to the game."""
		self.players.append(Player(name, self.config["starting_amount"]))
	
	def add_ai(self, name):
		"""Adds an AI-controlled player."""
		self.players.append(AI(name, self.config["starting_amount"]))

	def remove_player(self, player: Player):
		"""Removes a player from the game."""
		if player in self.players:
			self.players.remove(player)
			print(f"{player.name} has been removed from the game.")
		else:
			print(f"{player.name} is not in the game.")

	def get_player_by_name(self, name: str) -> Optional[Player]:
		for player in self.players:
			if player.name == name:
				return player
		return None

	def reset_game_state(self):
		"""Reset all transient game state except config."""
		self.players = []
		self.current_turn = 0
		self.bank = Bank(self.config.get("Houses", 32), self.config.get("Hotels", 16))
		self.board = Board(self.get_data().get("Spaces"), self.config, self.decks)
		self.dice = Dice(self.config)
		self.first_player_index = 0
		print("Game state has been reset.")

	def return_get_out_of_jail_cards(self):
		for player in self.players:
			cc_card, chance_card = player.get_out_of_jail_free_cards
			if chance_card:
				self.decks["Chance"].cards.append(Card("Get out of Jail Free", {"Type": "get_out_of_jail_free", "Card_Type": "chance"}))
			if cc_card:
				self.decks["Comunity_Chest"].cards.append(Card("Get out of Jail Free", {"Type": "get_out_of_jail_free", "Card_Type": "community_chest"}))
			player.get_out_of_jail_free_cards = (False, False)

	def debug_view_game_state(self):
		print(f"\n=== GAME STATE ===")
		print(f"Turn: {self.current_turn} / Player: {self.players[self.current_turn].name}")
		print(f"Players Alive: {len(self.alive_players())}")
		print("Owned Properties:")
		for name, owner in self.board.owned_properties().items():
			print(f"  {name}: {owner}")
		print("==================\n")

	def next_player(self):
		"""
		Updates current_turn to the next active (i.e. not bankrupt) player.
		Triggers autosave if a full rotation completes.
		"""
		num_players = len(self.players)
		if num_players == 0:
			return

		prev_index = self.current_turn

		for _ in range(num_players):
			self.current_turn = (self.current_turn + 1) % num_players
			if not self.players[self.current_turn].bankrupt:
				break

		# Check if we've looped back to the player we started the round with
		if self.autosave and self.current_turn == self.first_player_index:
			print("Autosaving after completed rotation...")
			self.save_game(self.save_slot)
			self.first_player_index = self.current_turn  # Reset for next round

	def alive_players(self) -> list["Player"]:
		return [p for p in self.players if not p.bankrupt]
	
	def is_game_over(self) -> bool:
		"""
		Returns True if there is one (or zero) active players left.
		"""
		active_players = [p for p in self.players if not p.bankrupt]
		return len(active_players) <= 1
	
	def end_game(self):
		"""
		Ends the game and prints out the winner.
		"""
		winners = self.determine_winner()
		if winners:
			winner = winners[0]
			print(f"\nGame Over! The winner is {winner.name} with a total wealth of {winner.total_wealth()}.")
		else:
			print("\nGame Over! No winner could be determined.")
	
	def determine_winner(self):
		"""
		Determines the winner by sorting all active players by their total wealth.
		Assumes that each player has a method total_wealth() which calculates the sum
		of cash and property values.
		"""
		active_players = self.alive_players()
		# Sort in descending order of wealth.
		return sorted(active_players, key=lambda p: p.total_wealth(), reverse=True)

	def save_game(self, save_slot: int):
		from Core.save import save_game
		save_game(self, save_slot)
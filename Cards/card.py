from typing import Dict, Any
from Players import Player
from Core import Game
from Board import Board, Space
from Space_Types import Railroad, Utility

class Card:
	"""
	Represents a single card drawn from a Chance or Community Chest deck.
	
	Each card has a description and an effect which is stored as a dictionary.
	The effect dictionary must have a "type" key, which determines the action
	that is executed when the card is drawn.

	key responsibilities:
	- handles effects of a given community chest or chance card
	"""
	def __init__(self, description: str, effect: Dict[str, Any]):
		"""
		Initialize the card with a description and an effect.
		
		:param description: A textual description of the card.
		:param effect: A dictionary that specifies the card's effect. Expected keys include:
					   - "type": A string representing the effect type (e.g., "advance_to", "collect_money", etc.).
					   - Additional keys depending on the type (e.g., "target", "amount", "house_price", etc.).
		"""
		self.description = description
		self.effect = effect
	
	def __str__(self):
		return f"Description: {self.description}\n\nEffect: {self.effect}"

	def on_pull(self, player: "Player", game: "Game") -> None:
		"""
		Execute the card's effect when it is drawn by a player.
		
		:param player: The Player who drew the card.
		:param game: The current Game instance.
		:raises ValueError: If the card effect type is invalid.
		"""
		effect_type = self.effect.get("Type")
		if effect_type == "advance_to":
			self._advance_to(player, game.board, self.effect["Target"])
		elif effect_type == "advance_to_nearest":
			self._advance_to_nearest(player, game.board, self.effect["Target"])
		elif effect_type == "advance_steps":
			self._advance_steps(player, game.board, int(self.effect["Amount"]))
		elif effect_type == "collect_money":
			self._collect_money(player, int(self.effect["Amount"]))
		elif effect_type == "pay_money":
			self._pay_money(player, int(self.effect["Amount"]))
		elif effect_type == "pay_money_buildings":
			self._pay_money_buildings(player, int(self.effect["House_Price"]), int(self.effect["Hotel_Price"]))
		elif effect_type == "pay_money_to_players":
			self._pay_money_to_players(player, game, int(self.effect["Amount"]))
		elif effect_type == "get_out_of_jail_free":
			self._get_out_of_jail_free(player, self.effect["Card_Type"])
		elif effect_type == "go_to_jail":
			self._go_to_jail(player, game)
		else:
			raise ValueError(f"Invalid card effect type: {effect_type}")

	def _advance_to(self, player: "Player", board: "Board", target: str) -> None:
		"""
		Move the player directly to the space identified by 'target'.
		
		:param player: The player to move.
		:param board: The game board.
		:param target: The name of the target space.
		"""
		target_space = board.find_by_name(target)
		distance = board.distance_to_space(player, target_space)
		board.move_player(player, distance)

	def _advance_to_nearest(self, player: "Player", board: "Board", target: str) -> None:
		"""
		Move the player to the nearest space that belongs to the specified group.
		
		:param player: The player to move.
		:param board: The game board.
		:param target: The group identifier (e.g., "Utility") to search for.
		:raises ValueError: If no space in the target group is found.
		"""
		spaces = board.find_by_group(target)  # Returns a list of Space objects in the group.
		if not spaces:
			raise ValueError(f"No spaces found in group '{target}'.")
		# Sort spaces by their position.
		spaces.sort(key=lambda space: space.position)
		player_pos = player.position  # Current player position.
		# Find the first space ahead of the player.
		for space in spaces:
			if space.position > player_pos:
				distance = board.distance_to_space(player, space)
				board.move_player(player, distance)
				return
		# Wrap-around case: if no space is ahead, move to the first space.
		first_space: "Space" = spaces[0]
		distance = board.distance_to_space(player, first_space)
		board.move_player(player, distance)
		if type(first_space) == Railroad:
			card = first_space.get_card()
			if card.owner == None:
				first_space.on_land(player)
			else:
				player.pay(card.calculate_rent() * 2, card.owner)
		elif type(first_space) == Utility:
			card = first_space.get_card()
			if card.owner == None:
				first_space.on_land(player)
			else:
				player.pay(player.dice_roll["total"] * 10, card.owner)
	
	def _advance_steps(self, player: "Player", board: "Board", steps: int) -> None:
		"""
		Move the player forward a fixed number of steps.
		
		:param player: The player to move.
		:param board: The game board.
		:param steps: The number of steps to advance.
		"""
		board.move_player(player, steps)

	def _collect_money(self, player: "Player", amount: int) -> None:
		"""
		Give the player a specific amount of money.
		
		:param player: The player who collects the money.
		:param amount: The amount to collect.
		"""
		player.collect(amount)

	def _pay_money(self, player: "Player", amount: int) -> None:
		"""
		Deduct a specific amount of money from the player.
		
		:param player: The player who must pay.
		:param amount: The amount to be paid.
		"""
		player.pay(amount)

	def _pay_money_buildings(self, player: "Player", house_price: int, hotel_price: int) -> None:
		"""
		Charge the player based on the number of houses and hotels they own.
		
		:param player: The player who must pay.
		:param house_price: The cost per house.
		:param hotel_price: The cost per hotel.
		"""
		player_houses, player_hotels = player.count_houses_and_hotels()
		total_cost = player_houses * house_price + player_hotels * hotel_price
		player.pay(total_cost)

	def _pay_money_to_players(self, player: "Player", game: "Game", amount: int) -> None:
		"""
		Transfer money from the current player to all other players.
		
		:param player: The player who pays.
		:param game: The current game instance containing all players.
		:param amount: The amount each other player receives.
		"""
		for other_player in game.players:
			if other_player != player:
				player.transfer(other_player, amount)

	def _get_out_of_jail_free(self, player: "Player", card_type: str) -> None:
		"""
		Grant the player a 'Get Out of Jail Free' card.
		
		:param player: The player receiving the card.
		:param card_type: The type of card ("chance" or "community_chest").
		:raises ValueError: If an invalid card_type is provided.
		"""
		current_cards = player.get_out_of_jail_free_cards
		if card_type == "chance":
			player.get_out_of_jail_free_cards = (True, current_cards[1])
		elif card_type == "community_chest":
			player.get_out_of_jail_free_cards = (current_cards[0], True)
		else:
			raise ValueError("Invalid card type. Must be 'chance' or 'community_chest'.")

	def _go_to_jail(self, player: "Player", game: "Game") -> None:
		"""
		Send the player directly to jail.
		
		:param player: The player to be sent to jail.
		"""
		player.go_to_jail(game)
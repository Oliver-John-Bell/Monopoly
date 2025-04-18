from abc import ABC, abstractmethod
from Players import Player
from Core import Game
from typing import Dict, Any, Optional
from Space_Types import Group


class Space(ABC):
	def __init__(self, name: str, position: int):
		"""
		Initialize a board space.

		:param name: The name of the space.
		:param position: The board position index.
		"""
		self.name = name
		self.position = position

	def __str__(self):
		return f"Name: {self.name}\nPosition: {self.position}"
	
	@abstractmethod
	def on_land(self, player: "Player", game: "Game") -> None:
		"""
		Define what happens when a player lands on this space.
		Must be implemented by subclasses.
		"""
		pass
	








# Abstract class for spaces that can be owned
class Ownable_Space(Space, ABC):
	def __init__(self, name: str, position: int, buying_price: int,
				 mortgage_value: int, rent: Dict[str, int], group: "Group"):
		"""
		Initialize an ownable space.

		:param name: The name of the space.
		:param position: The board position index.
		:param buying_price: The purchase price.
		:param mortgage_value: The mortgage value.
		:param group: The group (color or type) to which this property belongs.
		"""
		super().__init__(name, position)
		self.buying_price = buying_price
		self.mortgage_value = mortgage_value
		self.rent = rent
		self.group = group

	def on_land(self, player: "Player", game: "Game") -> None:
		"""
		When a player lands on an ownable space:
		  - If unowned: let the player buy the property (or trigger an auction).
		  - If owned by another player: charge rent.
		  - If owned by the same player: do nothing.
		"""
		card = self.get_card()
		if card.owner is None:
			# Example logic: if the player can afford it, they buy automatically.
			# Otherwise, the space is auctioned.
			if player.total_wealth() < self.buying_price:
				game.bank.auction_propety(game.alive_players())
			elif player.can_afford(self.buying_price):
				player.buy_property(self, game)
		elif card.owner != player:
			rent = card.calculate_rent()
			player.pay(rent, card.owner)
		# If the player owns the property, nothing happens.

	def __str__(self):
		return f"Name: {self.name}\nPosition: {self.position}\nrent: {self.rent}\nGroup: {self.group.colour}"
	
	@abstractmethod
	def get_card(self) -> "Ownable_Card":
		"""
		Return the card (entity) that represents the current state of this property.
		Must be implemented by subclasses.
		"""
		pass






class Ownable_Card:
	def __init__(self, location: "Ownable_Space", config: Dict[str, Any]):
		"""
		Base card for any ownable space.

		:param location: The ownable space (e.g. Property, Utility, Railroad)
						 that this card represents.
		"""
		self.location = location  # Reference to the ownable space.
		self.mortgaged = False	# Indicates if the property is mortgaged.
		self.owner: Optional["Player"] = None		 # The Player instance who owns this property.
		self.collect_in_jail = config.get("Rent_In_Jail", True)

	def __str__(self):
		return f"Name: {self.name}\nPosition: {self.position}\nrent: {self.rent}\nMortgage Value: {self.mortgage_value}\nGroup: {self.group.colour}"
	
	def calculate_rent(self, dice_roll: Optional[int] = None) -> int:
		"""
		Abstract method to calculate rent. For some cards (like utilities), a dice roll
		value is required for the calculation.

		:param dice_roll: Optional dice roll value, used in certain rent calculations.
		:return: The rent amount.
		"""
		raise NotImplementedError("calculate_rent must be implemented by subclasses")
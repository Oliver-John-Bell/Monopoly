from Board import Ownable_Space
from Players import Player
from typing import Dict, List, Optional

class Group:
	def __init__(self, colour: str, properties: List["Ownable_Space"] = []):
		"""
		Initialize the group.

		:param colour: The group’s colour or identifier.
		:param properties: A list of ownable space instances belonging to this group.
		"""
		self.colour = colour
		self.properties = properties  # references to Ownable_Space instances
		self.ownership: Dict["Player", int] = {}  # maps Player -> count of owned spaces
		self.update_ownership()

	def update_ownership(self) -> None:
		"""
		Recalculates and stores the ownership information for this group.
		This method should be called whenever any property's owner changes.
		"""
		self.ownership = {}
		for prop in self.properties:
			card = prop.get_card()
			if card.owner is not None:
				self.ownership[card.owner] = self.ownership.get(card.owner, 0) + 1

	def owned_by(self) -> Dict["Player", int]:
		"""
		Returns the stored dictionary mapping each player to the number of ownable spaces in
		this group that they currently own.

		:return: A dictionary where the key is a Player and the value is a count.
		"""
		return self.ownership

	def is_monopoly(self) -> bool:
		"""
		Returns True if any single player owns every ownable space in this group.
		(Unowned or partially owned groups do not count as a monopoly.)

		:return: True if a monopoly exists, False otherwise.
		"""
		total = len(self.properties)
		for count in self.ownership.values():
			if count == total:
				return True
		return False

	def all_owned_by(self) -> Optional["Player"]:
		"""
		If a monopoly exists in this group (i.e. one player owns every ownable space),
		returns that player. Otherwise, returns None.

		:return: The Player who owns all spaces in the group or None.
		"""
		total = len(self.properties)
		for player, count in self.ownership.items():
			if count == total:
				return player
		return None

	def count_owned(self, player: "Player") -> int:
		"""
		Returns the number of ownable spaces in this group that are owned by the given player.

		:param player: The player whose ownership count is requested.
		:return: The count of spaces owned by the player.
		"""
		return self.ownership.get(player, 0)

	def add_property(self, property: "Ownable_Space"):
		self.properties.append(property)
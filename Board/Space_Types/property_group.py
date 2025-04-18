from Space_Types import Group, Property, Property_Card
from Players import Player
from typing import List

class Property_Group(Group):
	def __init__(self, colour: str, properties: List["Property"]):
		"""
		Initialize the property group.

		:param colour: The group’s colour.
		:param properties: A list of Property instances.
		"""
		super().__init__(colour, properties)

	def can_build_house(self, property_card: "Property_Card") -> bool:
		"""
		Determines whether a house can be built on the property associated with the given property card.
		Building a house is allowed only if:
		  1. The property belongs to this group.
		  2. The property has an owner.
		  3. The owner owns every property in this group (i.e. a monopoly exists).
		  4. Houses are built evenly; the property in question must have the minimum number of houses
			 among the properties in this group owned by that same owner.

		:param property_card: The Property_Card representing the property's current state.
		:return: True if a house can be built on the property, False otherwise.
		"""
		# Get the cards for all properties in this group.
		group_cards = [prop.get_card() for prop in self.properties]
		if property_card not in group_cards:
			return False  # The property is not part of this group.

		owner = property_card.owner
		if owner is None:
			return False  # Cannot build on an unowned property.

		# Ensure that the owner has a monopoly in this group.
		if self.all_owned_by() != owner:
			return False

		# Enforce the even building rule:
		# Find the minimum number of houses among all properties in the group owned by this owner.
		owner_cards = [card for card in group_cards if card.owner == owner]
		if not owner_cards:
			return False  # This should not happen if property_card has an owner.
		min_houses = min(card.houses for card in owner_cards)
		return property_card.houses == min_houses
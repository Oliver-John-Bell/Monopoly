from typing import Dict, Optional
from Board import Ownable_Space, Ownable_Card
from Space_Types import Property_Group, Property_Card

# Property (colored real-estate)
class Property(Ownable_Space):
	def __init__(self, name: str, position: int, buying_price: int, mortgage_value: int,
				 build_cost: int, group: "Property_Group", rent: Dict[str, int],
				 card: Optional["Property_Card"] = None):
		"""
		Initialize a property space.

		:param build_cost: The cost to build houses/hotels.
		:param rent: A dictionary mapping the number of buildings (0-5) to rent amounts.
		:param card: The Property_Card holding the current state.
		"""
		super().__init__(name, position, buying_price, mortgage_value, rent, group)
		self.build_cost = build_cost
		self.card = card

	def get_card(self) -> "Property_Card":
		return self.card
	


class Property_Card(Ownable_Card):
	def __init__(self, property: "Property"):
		"""
		Card representing a property that can be built on (houses/hotels).

		:param property: The Property instance this card represents.
		"""
		super().__init__(property)
		self.houses = 0

	def calculate_rent(self, dice_roll: Optional[int] = None) -> int:
		"""
		Calculates the rent for a property based on the number of houses.
		The dice_roll parameter is ignored in this calculation.

		:param dice_roll: Ignored.
		:return: Rent amount determined from the property's rent table.
		"""
		if  self.owner is None or self.mortgaged or (not(self.collect_in_jail) & self.owner.in_jail()):
			return 0
		if self.houses == 0 and self.location.group.is_monopoly:
			return self.location.rent[0] * 2
		return self.location.rent[self.houses]
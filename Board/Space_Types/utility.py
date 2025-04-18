from typing import Dict, Optional
from Board import Ownable_Space, Ownable_Card
from Space_Types import Group

# Utility space (e.g. Electric Company, Water Works)
class Utility(Ownable_Space):
	def __init__(self, name: str, position: int, buying_price: int, mortgage_value: int,
				 group: "Group", rent_multipliers: Dict[str, int],
				 card: Optional["Utility_Card"] = None):
		"""
		Initialize a utility space.

		:param rent_multipliers: A dictionary mapping the number of utilities owned
								 to the multiplier for calculating rent.
		:param card: The Utility_Card holding the current state.
		"""
		super().__init__(name, position, buying_price, mortgage_value, rent_multipliers, group)
		self.card = card

	def get_card(self) -> "Utility_Card":
		return self.card
	



class Utility_Card(Ownable_Card):
	def __init__(self, utility: "Utility"):
		"""
		Card representing a utility.

		:param utility: The Utility instance this card represents.
		"""
		super().__init__(utility)

	def calculate_rent(self, dice_roll: Optional[int] = None) -> int:
		"""
		Calculates the rent for a utility. The rent is typically determined by multiplying
		a dice roll by a multiplier. The multiplier depends on how many utilities the owner holds.

		:param dice_roll: The dice roll value. This parameter is required for utilities.
		:return: Calculated rent amount.
		:raises ValueError: If dice_roll is not provided.
		"""
		if  self.owner is None or self.mortgaged or (not(self.collect_in_jail) & self.owner.in_jail()):
			return 0
		if dice_roll is None:
			raise ValueError("A dice roll value is required for utility rent calculation.")
		
		# Retrieve the number of utilities owned by this owner from the group.
		group = self.location.group
		num_owned = group.count_owned(self.owner)
		multiplier = self.location.rent.get(str(num_owned), 0)
		return dice_roll * multiplier
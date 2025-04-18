from typing import Dict, Optional
from Board import Ownable_Space, Ownable_Card
from Space_Types import Group

# Railroad space
class Railroad(Ownable_Space):
	def __init__(self, name: str, position: int, buying_price: int, mortgage_value: int,
				 group: "Group", rent: Dict[str, int], card: Optional["Railroad_Card"] = None):
		"""
		Initialize a railroad space.

		:param rent: A dictionary mapping the number of railroads owned (1-4) to rent amounts.
		:param card: The Railroad_Card holding the current state.
		"""
		super().__init__(name, position, buying_price, mortgage_value, rent, group)
		self.card = card

	def get_card(self) -> "Railroad_Card":
		return self.card
	



class Railroad_Card(Ownable_Card):
	def __init__(self, railroad: "Railroad"):
		"""
		Card representing a railroad.

		:param railroad: The Railroad instance this card represents.
		"""
		super().__init__(railroad)

	def calculate_rent(self, dice_roll: Optional[int] = None) -> int:
		"""
		Calculates the rent for a railroad based on the number of railroads the owner possesses.
		The dice_roll parameter is ignored.

		:param dice_roll: Ignored.
		:return: Calculated rent amount.
		"""
		if  self.owner is None or self.mortgaged or (not(self.collect_in_jail) & self.owner.in_jail()):
			return 0
		
		# Retrieve the number of railroads owned by this owner from the group.
		group = self.location.group
		num_owned = group.count_owned(self.owner)
		return self.location.rent.get(str(num_owned), 0)
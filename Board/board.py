from typing import Dict, Any, Optional
from Space_Types import Group, Property, Property_Group, Property_Card, Railroad, Utility, Go, Tax, Go_To_Jail, Jail, Free_Parking, Card_Space
from Cards import Deck
from Players import Player
from Board import Space, Ownable_Space

class Board:
	"""
	Key responsibilities:
	- managing movement
	- querying spaces
	"""
	def __init__(self, json_spaces: Dict[str, Any], config: Dict[str, Any], decks: Dict[str, Any]):
		# what is the best format to represent board, be able to display who owns what, property groups, etc
		self.spaces: list["Space"]
		self.groups: Dict[str, "Group"]
		self._initalise_spaces(json_spaces, decks)
		self.board_size = len(self.spaces)
		self.jail: "Jail"
		self.free_parking: "Free_Parking"
		self.base_salary = config.get("Base_Salary", 200)
	
	def _initalise_spaces(self, json_spaces: Dict[str, Any], decks: Dict[str, "Deck"]):
		board = []
		groups: Dict[str, "Group"] = {}
		for i, space in enumerate(json_spaces):
			space_type = space.get("Type")

			if space_type == "Property":
				group_name = space.get("Property_Group")
				if group_name not in groups:
					groups[group_name] = Property_Group(group_name)
				
				group = groups[group_name]
				name = space.get("Name")
				price = space.get("Price")
				mortgage = space.get("Mortgage")
				build_cost = space.get("Build_Cost")
				rent = space.get("Rent")
	
				location = Property(name, i, price, mortgage, build_cost, group, rent)
				location.card = Property_Card(location)
				board.append(location)
				group.add_property(location)
			
			elif space_type == "Card_Space":
				name = space.get("Name")
				location = Card_Space(name, i, decks.get(name))
				board.append(location)
				group.add_property(location)
			
			elif space_type == "Railroad":
				if "Railroad" not in groups:
					groups["Railroad"] = Group("Railroad")
				
				group = groups["Railroad"]
				name = space.get("Name")
				price = space.get("Price")
				mortgage = space.get("Mortgage")
				rent = space.get("Rent")

				location = Railroad(name, i, price, mortgage, group, rent)
				board.append(location)
				group.add_property(location)
			
			elif space_type == "Utility":
				if "Utilities" not in groups:
					groups["Utilities"] = Group("Utilities")
				
				group = groups["Utilities"]
				name = space.get("Name")
				price = space.get("Price")
				mortgage = space.get("Mortgage")
				rent = space.get("Rent")
				location = Utility(name, i, price, mortgage, group, rent)

				board.append(location)
				group.add_property(location)
			
			elif space_type == "Tax":
				location = Tax(
					space.get("Name"),
					i,
					space.get("Amount")
					)
				board.append(location)
			
			elif space_type == "Go":
				location = Go(
					space.get("Name"),
					i,
					self.base_salary
					)
				board.append(location)

			elif space_type == "Jail":
				location = Jail(
					space.get("Name"),
					i
					)
				board.append(location)
				self.jail = i

			elif space_type == "Free_Parking":
				location = Free_Parking(
					space.get("Name"),
					i
					)
				board.append(location)

			elif space_type == "Go_To_Jail":
				location = Go_To_Jail(
					space.get("Name"),
					i
					)
				board.append(location)

			else:
				print(f"Error at position {i} of the board. {space_type} is not a valid location")#########################################

	def get_unowned_property(self) -> list["Ownable_Space"]:
		return [space for space in self.spaces if isinstance(space, Ownable_Space) and space.get_card().owner is None]


	def ownable_properties(self) -> Dict["Ownable_Space", Optional["Player"]]:
		return {
			space: space.get_card().owner
			for space in self.spaces
			if isinstance(space, Ownable_Space)
		}

	def view_board(self) -> None:
		for i, space in enumerate(self.spaces):
			owner = None
			if isinstance(space, Ownable_Space):
				card = space.get_card()
				owner = card.owner.name if card.owner else "Unowned"
			print(f"{i:2}: {space.name} - {type(space).__name__} - Owner: {owner if owner else 'N/A'}")

	
	def get_free_parking_quantity(self):
		print(f"Free parking contains {self.free_parking.saved_money}")
	
	def find_by_name(self, space_name: str) -> Optional["Space"]:
		for space in self.spaces:
			if space.name == space_name:
				return space
		return None

	
	def find_by_group(self, group_name: str) -> list["Space"]:
		group = self.groups.get(group_name)
		return group.properties if group else []
	
	def distance_to_space(self, player: "Player", target_space: "Space") -> int:
		current_pos = player.position
		target_pos = target_space.position
		return (target_pos - current_pos) % self.board_size


	def owned_properties(self) -> Dict[str, str]:
		result = {}
		for space in self.spaces:
			if isinstance(space, Ownable_Space):
				owner = space.get_card().owner
				result[space.name] = owner.name if owner else "Unowned"
		return result


	def move_player(self, player: "Player", steps: int):
		"""
		Move the player a given number of steps along the board.
		Wraps around the board if needed. If the player passes 'Go' (assumed to be at position 0),
		collect the designated salary.
		
		:param steps: Number of steps to move.
		:param game: The current Game instance.
		"""
		old_position = player.position
		self.position = (player.position + steps) % self.board_size

		# If the new position is less than the old position, the player passed 'Go'
		if self.position < old_position:
			player.collect(self.base_salary)
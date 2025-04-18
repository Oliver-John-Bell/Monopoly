from typing import Dict, Any, Union
import random

class Speed_Dice:
	"""
	key responsibilities:
	- handles the optional speed dice
	"""
	def __init__(self, size: int, bus_count: int, monopoly_man_count: int):
		"""
		Initialize the speed die.
		
		:param size: Total number of faces on the die.
		:param bus_count: How many faces should yield a Bus result.
		:param monopoly_man_count: How many faces should yield a Monopoly Man result.
		
		"""
		self.size = size
		self.bus_count = bus_count
		self.monopoly_man_count = monopoly_man_count

	def roll(self) -> Union[int, str]:
		"""
		Roll the speed die. If the result falls in one of the special ranges, return
		a special symbol ("BUS" or "MONOPOLY_MAN"). Otherwise, return the numeric roll.
		
		For example, with a d6 configured with 1 monopoly man face and 1 bus face:
		  - If the roll is 6 (i.e. > 6 - 1), return "MONOPOLY_MAN"
		  - If the roll is 4-5 (i.e. > 6 - (1+2)), return "BUS"
		  - Otherwise, return the numeric roll.
		"""
		# Use randint so that possible outcomes are 1 .. size (inclusive)
		roll = random.randint(1, self.size)
		# Check for the highest values first (Monopoly Man faces)
		if roll > self.size - self.monopoly_man_count:
			return self._monopoly_man()
		# Next check for Bus faces
		elif roll > self.size - (self.monopoly_man_count + self.bus_count):
			return self._bus()
		else:
			return roll

	def _bus(self) -> str:
		"""
		Represents the special result for Bus. In your game logic you might handle this
		by allowing the player to choose an alternate move.
		"""
		return "BUS"

	def _monopoly_man(self) -> str:
		"""
		Represents the special result for Monopoly Man. In your game logic you might handle
		this by providing some bonus or alternative movement.
		"""
		return "MONOPOLY_MAN"


class Dice:
	"""
	key responsibilities:
	- handles all dice interactions
	- 
	"""
	def __init__(self, config: Dict[str, Any]):
		"""
		Initialize the dice using values from a configuration dictionary.
		
		Expected keys in config:
		  - "dice_size": The number of faces on each standard die.
		  - "dice_number": How many standard dice to roll.
		  - "speed_dice": A dictionary with keys:
				- "active": Boolean; whether the speed die is used.
				- "bus_count": How many faces yield the Bus result.
				- "monopoly_man_count": How many faces yield the Monopoly Man result.
		"""
		self.size = config.get("Dice_Size", 6)
		self.number = config.get("Dice_Number", 2)
		sd: Dict = config.get("Speed_Dice", {})
		self.speed_dice = Speed_Dice(self.size, sd.get("Bus_Count", 1), sd.get("Monopoly_Man_Count", 2))
		self.use_speed_dice = sd.get("Active", False)

	def roll(self) -> Dict[str, Union[int, str, None, bool]]:
		"""
		Roll the standard dice (assumed to be 2) and, if active and if not rolling doubles,
		roll the speed die.

		Returns a dictionary containing:
		  - "die1": result of first die.
		  - "die2": result of second die.
		  - "speed": result of the speed die roll (if used); otherwise, None.
		  - "total": numeric total to move (the sum of the dice plus the speed die if it is a number).
					 If the speed die shows a special symbol (BUS or MONOPOLY_MAN), its value is not added.
		  - "extra_turn": True if doubles were rolled (which might entitle the player to an extra turn).
		"""
		die1 = random.randint(1, self.size)
		die2 = random.randint(1, self.size)
		result = {
			"die1": die1,
			"die2": die2,
			"extra_turn": (die1 == die2)
		}
		
		# Only use the speed die if it is active and we did NOT roll doubles.
		if self.use_speed_dice and not result["extra_turn"]:
			speed_result = self.speed_dice.roll()
			result["speed"] = speed_result
			# If the speed die gives a number, add it to the total movement.
			if isinstance(speed_result, int):
				result["total"] = die1 + die2 + speed_result
			else:
				# If the speed die returns a special symbol, you may want to handle it specially.
				# Here we add only the standard dice to the total.
				result["total"] = die1 + die2
		else:
			result["speed"] = None
			result["total"] = die1 + die2

		return result
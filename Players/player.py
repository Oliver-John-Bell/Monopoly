from Board import Ownable_Card
from typing import Dict, Any, List, Tuple, Union
from Core import Game
from Space_Types import Property
from Cards import Card

class Player:
	def __init__(self, name: str, starting_balance: int, position: int = 0, owned_properties: List["Ownable_Card"] = [], bankrupt: bool = False, in_jail: bool = False, get_out_of_jail_free_cards: Tuple[bool, bool] = (False, False)):
		"""
		Initialize a player with a name and a starting balance.
		
		:param name: The player's name.
		:param starting_balance: The amount of money the player starts with.
		"""
		self.name = name
		self.balance = starting_balance
		self.position = position
		self.owned_properties: List["Ownable_Card"] = owned_properties
		self.bankrupt = bankrupt
		self.in_jail = in_jail
		self.jail_turns = 0
		self.dice_roll: Dict[str, Union[int, str, None, bool]] = {}
		# Tuple indicating if the player holds a "Get Out of Jail Free" card:
		# (chance card, community chest card)
		self.get_out_of_jail_free_cards: Tuple[bool, bool] = get_out_of_jail_free_cards

	def buy_property(self, property: "Property", game: "Game") -> None:
		"""
		Attempt to purchase a property. If the player can afford the purchase,
		deduct the buying price, transfer the property from the bank, and record ownership.
		
		:param property: The property to be purchased.
		:param game: The current Game instance.
		"""
		buying_price = property.buying_price
		if self.can_afford(buying_price):
			self.pay(buying_price)
			game.bank.transfer_property(property, self)
			# Record ownership by saving the property's card.
			self.owned_properties.append(property.get_card())

	def pay(self, amount: int, other_player: "Player" = None) -> None:
		"""
		Deduct the specified amount from the player's balance.
		If an other player is specified, that amount is collected by that player.
		If funds are insufficient, attempt to liquidate assets before declaring bankruptcy.
		
		:param amount: The amount to be paid.
		:param other_player: An optional recipient of the payment.
		"""
		if self.balance < amount:
			self.liquidate()
			if self.balance < amount:
				# Even after liquidation, the player cannot pay—declare bankruptcy.
				self.bankrupt = True
				return
		self.balance -= amount
		if other_player:
			other_player.collect(amount)

	def collect(self, amount: int) -> None:
		"""
		Add a specified amount to the player's balance.
		
		:param amount: The amount to collect.
		"""
		self.balance += amount

	def mortgage_property(self, property: "Ownable_Card") -> None:
		"""
		Mortgage an owned property (if not already mortgaged) and add its mortgage value to the player's balance.
		
		:param property: The property card to mortgage.
		"""
		if property in self.owned_properties and not property.mortgaged:
			property.mortgaged = True
			self.collect(property.location.mortgage_value)

	def unmortgage_property(self, property: "Ownable_Card") -> None:
		"""
		Unmortgage an owned property by paying its unmortgage cost, which is the mortgage value plus 10%.
		
		:param property: The property card to unmortgage.
		"""
		if property in self.owned_properties and property.mortgaged:
			unmortgage_cost = int(property.location.mortgage_value * 1.1)
			if self.can_afford(unmortgage_cost):
				self.pay(unmortgage_cost)
				property.mortgaged = False

	def go_to_jail(self, game: "Game") -> None:
		"""
		Send the player to jail and resetting the jail turn counter.
		"""
		self.in_jail = True
		self.jail_turns = 0
		self.position = game.board.jail

	def end_turn(self, game: "Game") -> None:
		"""
		Perform any end-of-turn actions, such as resetting temporary statuses or checking conditions.
		
		:param game: The current Game instance.
		"""
		# Add any end-of-turn logic here.
		pass

	def get_properties(self) -> List["Ownable_Card"]:
		"""
		Get the list of properties (and other ownable spaces) owned by the player.
		
		:return: List of owned property cards.
		"""
		return self.owned_properties

	def has_property(self, property: "Ownable_Card") -> bool:
		"""
		Check if the player owns a specific property.
		
		:param property: The property card to check.
		:return: True if the property is owned by the player; False otherwise.
		"""
		return property in self.owned_properties

	def liquidate(self) -> None:
		"""
		Attempt to raise funds by mortgaging owned properties.
		Properties are mortgaged (if not already mortgaged) until the player's balance is non-negative.
		If insufficient funds remain, the player is declared bankrupt.
		"""
		for prop in self.owned_properties:
			if not prop.mortgaged:
				prop.mortgaged = True
				self.collect(prop.location.mortgage_value)
				if self.balance >= 0:
					break
		if self.balance < 0:
			self.bankrupt = True

	def count_houses_and_hotels(self) -> Tuple[int, int]:
		"""
		Count the total number of houses and hotels on the player's owned properties.
		(For property cards, a value of 5 houses is considered a hotel.)
		
		:return: A tuple (total_houses, total_hotels).
		"""
		total_houses = 0
		total_hotels = 0
		for prop in self.owned_properties:
			# Only count if the property card has a 'houses' attribute.
			if hasattr(prop, 'houses'):
				if prop.houses == 5:
					total_hotels += 1
				else:
					total_houses += prop.houses
		return total_houses, total_hotels

	def transfer(self, other_player: "Player", amount: int) -> None:
		"""
		Transfer money from this player to another.
		
		:param other_player: The recipient player.
		:param amount: The amount to transfer.
		"""
		self.pay(amount)
		other_player.collect(amount)

	def total_wealth(self) -> int:
		"""
		Calculate the player's total wealth, including cash and the value of all owned properties.
		For each property:
		  - If mortgaged, use the mortgage value.
		  - If not mortgaged, add the purchase price and the value of any improvements.
		
		:return: The total wealth as an integer.
		"""
		wealth = self.balance
		for prop in self.owned_properties:
			if prop.mortgaged:
				wealth += prop.location.mortgage_value
			else:
				wealth += prop.location.buying_price
				# If the property has houses, include their value.
				if hasattr(prop, 'houses'):
					wealth += prop.houses * prop.location.build_cost
		return wealth

	def can_afford(self, amount: int) -> bool:
		"""
		Check if the player has enough cash to pay a specified amount.
		
		:param amount: The cost to check.
		:return: True if the balance is sufficient; False otherwise.
		"""
		return self.balance >= amount

	def return_get_out_of_jail_free_card(self, game: "Game") -> None:
		"""
		Return a "Get Out of Jail Free" card to the appropriate deck.
		If the player holds a Chance card, return it to the Chance deck.
		If the player holds a Community Chest card, return it to that deck.
		
		:param game: The current Game instance.
		"""
		chance, community = self.get_out_of_jail_free_cards
		if chance:
			game.decks["Chance"].cards.append(
				Card("Get Out of Jail Free", {"type": "get_out_of_jail_free", "card_type": "chance"})
			)
			chance = False
		if community:
			game.decks["Comunity_Chest"].cards.append(
				Card("Get Out of Jail Free", {"type": "get_out_of_jail_free", "card_type": "community_chest"})
			)
			community = False
		self.get_out_of_jail_free_cards = (chance, community)

	def use_get_out_of_jail_free_card(self) -> bool:
		"""
		Use a "Get Out of Jail Free" card if available.
		
		:return: True if a card was used; False otherwise.
		"""
		chance, community = self.get_out_of_jail_free_cards
		if chance:
			self.get_out_of_jail_free_cards = (False, community)
			return True
		elif community:
			self.get_out_of_jail_free_cards = (chance, False)
			return True
		return False

	def pay_bail(self, config: Dict[str, Any]) -> None:
		"""
		Pay bail to exit jail. The bail amount is retrieved from the game configuration.
		If the player can pay, deduct the bail and release the player; otherwise, attempt liquidation.
		
		:param game: The current Game instance.
		"""
		bail_amount = config.get("Bail_Amount", 50)
		if self.can_afford(bail_amount):
			self.pay(bail_amount)
			self.reset_jail()
		else:
			self.liquidate()

	def enter_jail(self) -> None:
		"""
		Mark the player as entering jail and reset the jail turn counter.
		"""
		self.in_jail = True
		self.jail_turns = 0

	def reset_jail(self) -> None:
		"""
		Reset the player's jail turn counter.
		"""
		self.jail_turns = 0
		self.in_jail = False

	def get_resources(self) -> Dict[str, Any]:
		"""
		Return a summary of the player's current resources.
		
		:return: A dictionary containing the player's money, jail-free cards, and properties.
		"""
		return {
			"Money": self.balance,
			"Get_Out_Of_Jail_Free_Card": self.get_out_of_jail_free_cards,
			"Properties": self.owned_properties
		}
	
	def to_dict(self) -> Dict[str, Any]:
		return {
			"Name": self.name,
			"Balance": self.balance,
			"Position": self.position,
			"Owned_Properties": [card.location.name for card in self.owned_properties],
			"Bankrupt": self.bankrupt,
			"In_Jail": self.in_jail,
			"Jail_Turns": self.jail_turns,
			"Get_Out_of_Jail_Cards": self.get_out_of_jail_free_cards
		}

	@classmethod
	def from_dict(cls, data: Dict[str, Any], card_lookup: Dict[str, "Ownable_Card"]) -> "Player":
		player = cls(
			name=data["Name"],
			starting_balance=data["Balance"],
			position=data["Position"],
			bankrupt=data.get("Bankrupt", False),
			in_jail=data.get("In_Jail", False),
			get_out_of_jail_free_cards=tuple(data.get("Get_Out_of_Jail_Cards", (False, False)))
		)
		player.jail_turns = data.get("Jail_Turns", 0)

		# Re-link owned property cards
		for name in data["Owned_Properties"]:
			card = card_lookup.get(name)
			if card:
				card.owner = player
				player.owned_properties.append(card)

		return player
	
	def trade(self, proposer: "Player", target: "Player", give: Dict[str, Any], recieve: Dict[str, Any]):
		proposer.pay(give["Money"], target)
		target.pay(recieve["Money"], proposer)
		target.get_out_of_jail_free_cards += give["Get_Out_Of_Jail_Free_Card"]
		proposer.get_out_of_jail_free_cards += recieve["Get_Out_Of_Jail_Free_Card"]
		self.transfer_property_multiple(give["Properties"], target)
		self.transfer_property_multiple(recieve["Properties"], proposer)
	
	def handle_jail_turn(self, game: "Game") -> bool:
		"""
		Handles the player's turn while in jail.
		Returns True if player leaves jail this turn, False otherwise.
		"""
		# Use a Get Out of Jail Free card if available
		if self.use_get_out_of_jail_free_card():
			self.reset_jail()
			return True

		# Try paying bail
		if self.can_afford(game.config["Bail_Amount"]):
			self.pay_bail(game.config)
			return True

		# Try rolling doubles
		roll = game.dice.roll()
		print(f"{self.name} tries to roll doubles: rolled {roll["die1"]} and {roll["die2"]}")
		if roll["extra_turn"]:
			self.reset_jail()
			return True

		self.jail_turns += 1
		if self.jail_turns >= game.config["Max_Turns_In_Jail"]:
			self.pay_bail(game.config)
			return True

		return False
from Space_Types import Property_Card, Property_Group, Property, Ownable_Space
from Players import Player, AI
from Core import Game
from typing import Dict

class Bank:
	def __init__(self, houses: int, hotels: int):
		self.houses = houses
		self.hotels = hotels

	def upgrade_property(self, property_card: "Property_Card"):
		"""
		Upgrade a property by adding a house or converting to a hotel.
		"""
		property = property_card.location
		group = property.group

		if not isinstance(group, Property_Group):
			raise TypeError("Only properties in a Property_Group can be upgraded.")

		if not group.can_build_house(property_card):
			raise ValueError("Cannot build on this property now (monopoly or even build rules violated).")

		if property_card.houses < 4:
			if self.houses <= 0:
				raise ValueError("No houses left in the bank.")
			self.houses -= 1
			property_card.houses += 1
		elif property_card.houses == 4:
			if self.hotels <= 0:
				raise ValueError("No hotels left in the bank.")
			self.houses += 4  # Return 4 houses to the bank
			self.hotels -= 1
			property_card.houses = 5  # 5 = hotel
		else:
			raise ValueError("Maximum upgrade (hotel) already reached.")

	def downgrade_property(self, property_card: "Property_Card"):
		"""
		Downgrade a property by selling a house or hotel.
		"""
		if property_card.houses == 0:
			raise ValueError("No houses or hotels to sell.")
		elif property_card.houses == 5:
			self.hotels += 1
			self.houses -= 4  # Convert hotel to 4 houses
			property_card.houses = 4
		else:
			self.houses += 1
			property_card.houses -= 1

		# Optional: Give half the build cost back to the player
		property_card.owner.collect(property_card.location.build_cost // 2)

	def downgrade_property_group_bankrupt(self, property: "Property"):
		"""
		Downgrade all buildings in a group when a player goes bankrupt.
		"""
		group = property.group
		for location in group.properties:
			card = location.get_card()
			if hasattr(card, 'houses') and card.houses > 0:
				if card.houses == 5:
					self.hotels += 1
					card.houses = 0
				else:
					self.houses += card.houses
					card.houses = 0

	def liquidate_player(self, player: "Player"):
		"""
		Handles complete liquidation of a player's assets.
		"""
		for card in player.owned_properties:
			if hasattr(card, 'houses') and card.houses > 0:
				self.downgrade_property(card)
			if not card.mortgaged:
				player.mortgage_property(card)
		player.bankrupt = True

	def transfer_property(self, property: "Property", target: "Player"):
		"""
		Transfer ownership of a single property to a player.
		"""
		card = property.get_card()
		card.owner = target
		target.owned_properties.append(card)
		property.group.update_ownership()

	def transfer_property_multiple(self, properties: list["Property"], target: "Player"):
		"""
		Transfer multiple properties to a player.
		"""
		for prop in properties:
			self.transfer_property(prop, target)

	def offer_trade(self, proposer: "Player", target: "Player"):
		#/////////////////////
		proposer_resources = proposer.get_resources()
		target_resources = target.get_resources()
		give = {
			"Money": 0,
			"Get_Out_Of_Jail_Free_Card": (False, False),
			"Properties": []
		}
		recieve = {
			"Money": 0,
			"Get_Out_Of_Jail_Free_Card": (False, False),
			"Properties": []
		}
		self.trade(target, give, recieve)

	def to_dict(self) -> Dict[str, str]:
		return {
			"houses": self.houses,
			"hotels": self.hotels
		}
	
	def auction(self, location: "Ownable_Space", game: "Game"):
		bidders = [p for p in game.players if not p.bankrupt]
		if not bidders:
			print("No eligible players for the auction.")
			return

		current_index = game.current_turn
		highest_bid = 0
		highest_bidder = None
		active_bidders = {p: True for p in bidders}

		print(f"Auction starting for {location.name} (starting at £0)...")
		while sum(active_bidders.values()) > 1:
			current_player = bidders[current_index % len(bidders)]

			# Skip if they've withdrawn
			if not active_bidders[current_player]:
				current_index += 1
				continue

			print(f"{current_player.name}'s turn. Highest bid: £{highest_bid} by {highest_bidder.name if highest_bidder else 'None'}")
			
			if isinstance(current_player, AI):
				bid_cap = current_player.evaluate_property_value(location, game)
				if bid_cap > highest_bid:
					increment = min(100, max(10, bid_cap - highest_bid))
					highest_bid = highest_bid + increment
					highest_bidder = current_player
					print(f"{current_player.name} (AI) bids £{highest_bid}")
				else:
					print(f"{current_player.name} (AI) withdraws.")
					active_bidders[current_player] = False
			else:
				action = input(f"{current_player.name}, choose: pass / withdraw / +10 / +50 / +100 / bid [amount]: ").strip().lower()

			if action == "withdraw":
				print(f"{current_player.name} has withdrawn from the auction.")
				active_bidders[current_player] = False

			elif action == "pass":
				print(f"{current_player.name} passes this round.")

			elif action in ["+10", "+50", "+100"]:
				bid = highest_bid + int(action[1:])
				if current_player.can_afford(bid):
					highest_bid = bid
					highest_bidder = current_player
					print(f"{current_player.name} bids £{bid}")
				else:
					print("Insufficient funds. Automatically withdrawn.")
					active_bidders[current_player] = False

			elif action.startswith("bid "):
				try:
					bid = int(action.split()[1])
					if bid > highest_bid and current_player.can_afford(bid):
						highest_bid = bid
						highest_bidder = current_player
						print(f"{current_player.name} bids £{bid}")
					else:
						print("Invalid or too low bid.")
				except ValueError:
					print("Invalid bid format.")
			else:
				print("Invalid input.")

			current_index += 1

		if highest_bidder:
			highest_bidder.pay(highest_bid)
			game.bank.transfer_property(location, highest_bidder)
			print(f"{highest_bidder.name} wins {location.name} for £{highest_bid}!")
		else:
			print("Auction ended with no valid bids.")
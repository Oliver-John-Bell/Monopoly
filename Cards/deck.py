from typing import Dict, Any, List
from Cards import Card
from Players import Player
from Core import Game
import random

class Deck:
	"""
	Represents a deck of cards (either Chance or Community Chest).
	
	The deck is initialized from a list of JSON-like dictionaries, each representing a card.
	After a card is drawn, it is returned to the bottom of the deck unless it is a 
	'Get Out of Jail Free' card.

	
	key responsibilities:
	- manages cards for community chest or chance
	- removes cards when effect moves card from deck to player
	"""
	def __init__(self, json_cards: List[Dict[str, Any]]):
		"""
		Initialize the deck with card data.
		
		:param json_cards: A list of dictionaries containing card definitions.
		"""
		self.cards: List[Card] = []
		for json_card in json_cards:
			description = json_card["Description"]
			effect = json_card["Effect"]
			self.cards.append(Card(description, effect))
		self.shuffle()
	
	def shuffle(self) -> None:
		"""
		Shuffle the deck randomly.
		"""
		random.shuffle(self.cards)
	
	def draw_card(self, player: "Player", game: "Game") -> None:
		"""
		Draw the top card from the deck, execute its effect, and then, unless it's a 
		'Get Out of Jail Free' card, place it at the bottom of the deck.
		
		:param player: The player drawing the card.
		:param game: The current game instance.
		"""
		card = self.cards.pop(0)
		card.on_pull(player, game)
		# If the card effect is not 'get_out_of_jail_free', return the card to the bottom.
		if card.effect.get("Type") != "get_out_of_jail_free":
			self.cards.append(card)
	
	def remove_card(self, type: str = "get_out_of_jail_free"):
		for i, card in enumerate(self.cards):
			if (card.effect.get("Type") == type):
				# Remove the card from the deck and exit.
				self.cards.pop(i)
				break
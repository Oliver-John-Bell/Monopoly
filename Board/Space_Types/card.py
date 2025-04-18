from Board import Space
from Cards import Deck
from Players import Player
from Core import Game

class Card_Space(Space):
	"""
	Represents a space on the board where a player must draw a card.
	
	When a player lands on this space, a card is drawn from the associated deck.

	key responsibilities:
	- handles the location players can land on to pick up cards
	"""
	def __init__(self, name: str, position: int, deck: Deck):
		"""
		Initialize the card space.
		
		:param name: The name of the space.
		:param position: The board position of the space.
		:param deck: The Deck from which cards are drawn.
		"""
		super().__init__(name, position)
		self.deck = deck

	def on_land(self, player: "Player", game: "Game") -> None:
		"""
		Trigger the card draw when a player lands on this space.
		
		:param player: The player who landed on the space.
		:param game: The current game instance.
		"""
		self.deck.draw_card(player, game)
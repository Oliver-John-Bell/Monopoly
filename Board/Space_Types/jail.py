from Board import Space
from Players import Player
from Core import Game

class Jail(Space):
	def __init__(self, name: str, position: int):
		"""
		Initialize the Jail space.
		"""
		super().__init__(name, position)

	def on_land(self, player: "Player", game: "Game") -> None:
		"""
		Landing on Jail (just visiting) does nothing.
		"""
		pass

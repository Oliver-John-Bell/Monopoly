from Board import Space
from Players import Player
from Core import Game

class Tax(Space):
	def __init__(self, name: str, position: int, amount: int):
		"""
		Initialize a tax space.

		:param amount: The tax amount to be paid.
		"""
		super().__init__(name, position)
		self.amount = amount

	def on_land(self, player: "Player", game: "Game") -> None:
		"""
		Charge the player the tax amount.
		"""
		player.pay(self.amount)
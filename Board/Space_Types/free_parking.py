from Board import Space
from Players import Player
from Core import Game

class Free_Parking(Space):
	def __init__(self, name: str, position: int):
		"""
		Initialize Free Parking.
		"""
		super().__init__(name, position)
		self.saved_money = 0

	def add_money(self, amount: int) -> None:
		"""
		Add money to the Free Parking pot.
		"""
		self.saved_money += amount

	def on_land(self, player: "Player", game: "Game") -> None:
		"""
		Let the player collect the accumulated money.
		"""
		player.collect(self.saved_money)
		self.saved_money = 0
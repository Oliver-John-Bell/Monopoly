from Board import Space
from Players import Player
from Core import Game

class Go(Space):
	def __init__(self, name: str, position: int, base_salary: int = 200):
		"""
		Initialize the Go space.
		"""
		super().__init__(name, position)
		self.base_salary = base_salary

	def on_land(self, player: "Player", game: "Game") -> None:
		"""
		When landing on Go, the player collects their salary.
		If the game config specifies 'double_salary_on_go', an extra amount is added.
		"""
		base_salary = 200  # or however your board is configured
		if game.config.get("Double_Salary_On_Go", False):
			player.collect(base_salary)
from Board import Space
from Players import Player
from Core import Game

class Go_To_Jail(Space):
	def __init__(self, name: str, position: int):
		"""
		Initialize the Go To Jail space.
		"""
		super().__init__(name, position)

	def on_land(self, player: "Player", game: "Game") -> None:
		"""
		Send the player directly to jail.
		"""
		player.go_to_jail(game)
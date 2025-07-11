from ursina import Ursina, BoxCollider, Vec3, AmbientLight, DirectionalLight, color, Sky
from typing import List

from Player import FPSCamera
from Enemy import Enemy

class App:
	def __init__(self):
		self.app = Ursina()
		self.player = FPSCamera(use_gun_model='./assets/source/uar15.glb')
		self.player.collider = BoxCollider(self.player, Vec3(0,1,0), Vec3(1,2,1))
		self.enemies: List[Enemy] = []

	def get_player(self) -> FPSCamera:
		return self.player

	def set_player_position(self, pos: Vec3) -> None:
		self.player.position = pos

	def run(self) -> None:
		Sky()
		AmbientLight(color=color.rgb(1.0, 1.0, 1.0))
		DirectionalLight(color=color.rgb(0.8, 0.8, 0.8)).look_at(Vec3(1, -1, -1))
		self.app.run()
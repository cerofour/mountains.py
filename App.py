from ursina import Ursina, BoxCollider, Vec3, AmbientLight, DirectionalLight, color, Sky
from ursina.prefabs.first_person_controller import FirstPersonController

from Player import FPSCamera

class App:
	def __init__(self):
		self.app = Ursina()
		self.player = FPSCamera()
		self.player.collider = BoxCollider(self.player, Vec3(0,1,0), Vec3(1,2,1))

	def get_player(self) -> FPSCamera:
		return self.player

	def run(self) -> None:
		Sky()
		AmbientLight(color=color.rgb(0.4, 0.4, 0.4))
		DirectionalLight(color=color.rgb(0.8, 0.8, 0.8)).look_at(Vec3(1, -1, -1))
		self.app.run()
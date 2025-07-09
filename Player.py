from ursina import Entity, camera, color, mouse, invoke, random, held_keys
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.ursfx import ursfx

from mesh_utils import load_model_safe

class FPSCamera(FirstPersonController):
	def __init__(self) -> None:
		super().__init__(
			model='cube', z=-10, color=color.orange, origin_y=-.5, speed=8, collider='box'
		)
		self.gun = Entity(
			parent = camera,
			model = 'cube', #load_model_safe("./assets/M9/M9.obj", "cube"),
			position=(.5,-.25,.25),
			scale=(.3,.2,1),
			origin_z = -.5,
			color = color.red,
			on_cooldown = False
		)

		self.gun.muzzle_flash = Entity(
			parent = self.gun,
			z=1, world_scale=.5, model='quad',
			color = color.yellow,
			enabled = False
		)

	def shoot(self) -> None:
		if not self.gun.on_cooldown:
			self.gun.on_cooldown = True
			self.gun.muzzle_flash.enabled=True
			ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise', pitch=random.uniform(-13.0,-12.0), pitch_change=-12, speed=3.0)
			invoke(self.gun.muzzle_flash.disable, delay=.05)
			invoke(setattr, self.gun, 'on_cooldown', False, delay=.15)
			if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
				mouse.hovered_entity.blink(color.red)

	def get_position(self, relative_to=...):
		return super().get_position(relative_to)
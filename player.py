from ursina import Entity, camera, mouse, Vec3, held_keys, time, color
from utils import clamp

class OptimizedFirstPersonController(Entity):
    def __init__(self, speed=5):
        super().__init__()
        self.speed = speed
        self.mouse_sensitivity = 40
        camera.parent = self
        camera.position = (0, 32, 0)
        camera.rotation = (0, 0, 0)
        camera.fov = 90
        mouse.locked = True
        self.cursor = Entity(parent=camera.ui, model='quad', color=color.white, scale=0.008)
    def update(self):
        direction = Vec3(0, 0, 0)
        if held_keys.get('w', False):
            direction += self.forward
        if held_keys.get('s', False):
            direction -= self.forward
        if held_keys.get('a', False):
            direction -= self.right
        if held_keys.get('d', False):
            direction += self.right
        if direction.length() > 0:
            direction = direction.normalized()
            self.position += direction * time.dt * self.speed
        if mouse.velocity[0] != 0:
            self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity
        if mouse.velocity[1] != 0:
            camera.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity
            camera.rotation_x = clamp(camera.rotation_x, -90, 90)
        if held_keys.get('space', False):
            self.y += self.speed * time.dt
        if held_keys.get('shift', False):
            self.y -= self.speed * time.dt 
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from mesh_utils import load_model_safe, create_bot_entity_safe
from PIL import Image
import numpy as np
from map_generator import *

app = Ursina()

gun_model = load_model_safe("assets/M9/M9.obj", "cube")

tanquesin_obj = "assets/Tanquesin/t_34_obj.obj"
tanquesin_model = load_model_safe("assets/Tanquesin/t_34_obj.obj", "cube")

player = FirstPersonController()
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))

gun = Entity(model='cube', parent=camera, position=(.5,-.25,.25), scale=(.3,.2,1), origin_z=-.5, color=color.red, on_cooldown=False)
gun.muzzle_flash = Entity(parent=gun, z=1, world_scale=.5, model='quad', color=color.yellow, enabled=False)

player.position = (4, 2, 1)
# player.gravity = 0

# Iluminación
AmbientLight(color=color.rgb(0.4, 0.4, 0.4))
DirectionalLight(color=color.rgb(0.8, 0.8, 0.8)).look_at(Vec3(1, -1, -1))

win_text = Text("¡GANASTE!", scale=2, origin=(0,0), background=True)
win_text.enabled = False

world_blocks = []
enemy_spawn_points = []
easter_egg = None
 
def update():
    if held_keys['left mouse']:
        shoot()

    # Verificar si todos los enemigos han sido eliminados
    global enemies
    enemies = [e for e in enemies if e.hp > 0]  # Filtra enemigos vivos
    if not enemies and not win_text.enabled:
        win_text.enabled = True

def shoot():
    if not gun.on_cooldown:
        # print('shoot')
        gun.on_cooldown = True
        gun.muzzle_flash.enabled=True
        from ursina.prefabs.ursfx import ursfx
        ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise', pitch=random.uniform(-13.0,-12.0), pitch_change=-12, speed=3.0)
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.15)
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 10
            mouse.hovered_entity.blink(color.red)

shootables_parent = Entity()
mouse.traverse_target = shootables_parent

class Enemy(Entity):
    def __init__(self, **kwargs):
        # Use safe model loading for the bot
        bot_model = load_model_safe('assets/left_4_dead_2_tank_rig.glb', 'cube')
        super().__init__(parent=shootables_parent, model=bot_model, scale_y=0.09, rotation=(0, 360, 360), scale_x=0.09, scale_z=0.09, origin_y=-.5, collider='box', **kwargs) # 0.045
        self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, world_scale=(1.5,.1,.1))
        self.max_hp = 100
        self.hp = self.max_hp

    def update(self):
        dist = distance_xz(player.position, self.position)
        if dist > 40:
            return

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)


        self.look_at_2d(player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0,1,0), self.forward, 30, ignore=(self,))
        # print(hit_info.entity)
        if hit_info.entity == player:
            if dist > 2:
                self.position += self.forward * time.dt * 5

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:
            destroy(self)
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1

enemies = [Enemy(x=x*4, position=(player.position + Vec3(random.randint(-5, 5), 0, random.randint(-5, 5)))) for x in range(0)]

# Información de debug
def input(key):
    if key == 'escape':
        mouse.locked = not mouse.locked
    elif key == 'f':
        print(f"Posición: {player.position}")

image_data = load_image_with_pil("map1.png")
generate_world_from_data(image_data, world_blocks, enemy_spawn_points, easter_egg)

print("Mundo cargado. Controles:")
print("WASD: Movimiento")
print("Space/Shift: Subir/Bajar")
print("F: Info de debug")
print("Escape: Liberar/bloquear mouse")

Sky()

app.run()

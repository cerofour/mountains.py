from ursina import Entity, mouse, held_keys, color, load_model, Vec3, time
from direct.actor.Actor import Actor
from ursina.prefabs.first_person_controller import FirstPersonController
from mesh_utils import load_model_safe, create_bot_entity_safe
from PIL import Image
import numpy as np
from map_generator import *

from App import App
from Enemy import Enemy

app = App()
player = app.get_player()

#ground = Entity(model='plane', collider='box', scale=128, texture='grass', texture_scale=(1,1))

#e = Enemy(player)

world_blocks = []
enemy_spawn_points = []
easter_egg = None

def update():
    #e.rotation_y += 100 * time.dt
    player.update()

# Información de debug
def input(key):
    if key == 'escape':
        mouse.locked = not mouse.locked

    elif key == 'f':
        print(f"Posición: {player.position}")

    if held_keys['left mouse']:
        player.shoot()

image_data = load_image_with_pil("map1.png")
player_spawn = generate_world_from_data(image_data, world_blocks, enemy_spawn_points, easter_egg)

app.set_player_position(player_spawn)

print("Mundo cargado. Controles:")
print("WASD: Movimiento")
print("Space/Shift: Subir/Bajar")
print("F: Info de debug")
print("Escape: Liberar/bloquear mouse")

app.run()
from ursina import Entity, mouse, held_keys
from ursina.prefabs.first_person_controller import FirstPersonController
from mesh_utils import load_model_safe, create_bot_entity_safe

from App import App

# Iluminación


app = App()
player = app.get_player()

ground = Entity(model='plane', collider='box', scale=128, texture='grass', texture_scale=(4,4))

def update():
    player.update()

#win_text = Text("¡GANASTE!", scale=2, origin=(0,0), background=True)
#win_text.enabled = False

# Información de debug
def input(key):
    if key == 'escape':
        mouse.locked = not mouse.locked

    elif key == 'f':
        print(f"Posición: {player.position}")

    if held_keys['left mouse']:
        player.shoot()

print("Mundo cargado. Controles:")
print("WASD: Movimiento")
print("Space/Shift: Subir/Bajar")
print("F: Info de debug")
print("Escape: Liberar/bloquear mouse")

app.run()
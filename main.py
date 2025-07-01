from ursina import *
from config import window_color, grass_texture_path, snow_texture_path, stone_texture_path, SNOW_Y, MOUNTAIN_Y, CAVE_Y
from world import generate_world, CHUNKS, BLOCKS
from player import OptimizedFirstPersonController

app = Ursina()
window.color = window_color

snow_texture = load_texture(snow_texture_path)
grass_texture = load_texture(grass_texture_path)
stone_texture = load_texture(stone_texture_path)

def textureMap(y):
    if y >= SNOW_Y:
        return snow_texture
    else:
        if (y <= CAVE_Y):
            return stone_texture
        elif y > CAVE_Y and y <= MOUNTAIN_Y:
            return grass_texture
        else:
            return stone_texture

# Generar mundo
print("Iniciando generación del mundo...")
generate_world(textureMap)

# Crear jugador
player = OptimizedFirstPersonController()

# Iluminación
AmbientLight(color=color.rgb(0.4, 0.4, 0.4))
DirectionalLight(color=color.rgb(0.8, 0.8, 0.8)).look_at(Vec3(1, -1, -1))

# Información de debug
def input(key):
    if key == 'escape':
        mouse.locked = not mouse.locked
    elif key == 'f':
        print(f"Posición: {player.position}")
        print(f"Chunks cargados: {len(CHUNKS)}")
        print(f"Bloques totales: {len(BLOCKS)}")

print("Mundo cargado. Controles:")
print("WASD: Movimiento")
print("Space/Shift: Subir/Bajar")
print("F: Info de debug")
print("Escape: Liberar/bloquear mouse")

app.run()

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

entidades = []

# SOLUCIÓN 1: Cargar modelo con verificación de errores
print("Intentando cargar modelo...")
try:
    # Intenta diferentes rutas
    car_model = load_model('assets/Mario.obj')
    if car_model:
        print("✓ Modelo cargado exitosamente")

        for i in range(0, 10):
            car_entity = Entity(
                model=car_model,
                scale=1,  # Ajusta el tamaño si es necesario
                position=(i * 10, 10, 0),  # Posición visible
                color=color.white  # Color por defecto
            )

            entidades.append(car_entity)
    else:
        print("✗ Error: Modelo no se pudo cargar")
        # Crear un cubo como placeholder
        car_entity = Entity(
            model='cube',
            color=color.red,
            scale=(2, 1, 4),
            position=(0, 5, 0)
        )
        print("→ Usando cubo como placeholder")
        
except Exception as e:
    print(f"✗ Error al cargar modelo: {e}")
    # Crear un cubo como placeholder
    car_entity = Entity(
        model='cube',
        color=color.red,
        scale=(2, 1, 4),
        position=(0, 5, 0)
    )
    print("→ Usando cubo como placeholder")

# SOLUCIÓN 2: Función alternativa de carga
def load_glb_model_safe(path):
    """Función segura para cargar modelos GLB"""
    try:
        # Method 1: load_model directo
        model = load_model(path)
        if model:
            return model
            
        # Method 2: Especificar el file_types
        model = load_model(path, file_types=['.glb', '.gltf'])
        if model:
            return model
            
        # Method 3: Asset loading
        from pathlib import Path
        if Path(path).exists():
            print(f"Archivo existe en: {Path(path).absolute()}")
            model = load_model(str(Path(path).absolute()))
            if model:
                return model
        else:
            print(f"Archivo no encontrado: {Path(path).absolute()}")
            
    except Exception as e:
        print(f"Error en carga: {e}")
    
    return None

# Usar la función segura (descomenta para probar)
# car_model_safe = load_glb_model_safe('assets/ines.glb')
# if car_model_safe:
#     car_entity_safe = Entity(model=car_model_safe, position=(5, 5, 0))

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
        # Debug del modelo
        if 'car_entity' in globals():
            print(f"Modelo car_entity - Posición: {car_entity.position}, Escala: {car_entity.scale}")
            print(f"Modelo visible: {car_entity.visible}")
    elif key == 't':
        # Toggle visibilidad del modelo para debug
        if 'car_entity' in globals():
            car_entity.visible = not car_entity.visible
            print(f"Modelo visible: {car_entity.visible}")

print("Mundo cargado. Controles:")
print("WASD: Movimiento")
print("Space/Shift: Subir/Bajar") 
print("F: Info de debug")
print("T: Toggle visibilidad del modelo")
print("Escape: Liberar/bloquear mouse")

app.run()
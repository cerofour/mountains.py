from ursina import *

from mesh_utils import load_model_safe

app = Ursina()

# 1. Verifica con un cubo nativo
Entity(model="cube", position=(-2, 5, 0), color=color.blue)

# 2. Prueba el modelo GLB con ajustes
Entity(
    model=load_model_safe('./assets/source/beretta9.glb', "cube"),
    position=(.5, 5, .25),
    scale=(10, 10, 10),  # Escala aumentada
    origin_z=0,           # Sin desplazamiento
    color=color.white,    # Sin tintado
    texture="white_cube"  # Material forzado
)

# 3. Iluminación y cámara
PointLight(position=(0, 10, -10))
EditorCamera()

app.run()
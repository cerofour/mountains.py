from ursina import *
from ursina.mesh import Mesh
from random import randint
import perlin_noise
import sys
from collections import defaultdict

app = Ursina()
window.color = color.rgb(0.75, 0.52, 0.3)

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 42

# Textura para los bloques
grass_texture = load_texture('wall.jpg')

noise = perlin_noise.PerlinNoise(octaves=10, seed=seed)

# Configuración del mundo
WORLD_SIZE = (80,80,80)
CHUNK_SIZE = 16  # Los chunks son de 16x16x16
CAVE_Y = 16
MOUNTAIN_Y = 17
MAX_MOUNTAIN_HEIGHT = 80
BLOCKS = {}
CHUNKS = {}  # Almacena los chunks generados

# Geometría del cubo
cube_vertices = [
    Vec3(-0.5, -0.5, -0.5), Vec3(0.5, -0.5, -0.5), Vec3(0.5, 0.5, -0.5), Vec3(-0.5, 0.5, -0.5),
    Vec3(-0.5, -0.5, 0.5), Vec3(0.5, -0.5, 0.5), Vec3(0.5, 0.5, 0.5), Vec3(-0.5, 0.5, 0.5),
]

faces = {
    'front':  [0,1,2,3],  'back':   [5,4,7,6],  'left':   [4,0,3,7],
    'right':  [1,5,6,2],  'bottom': [4,5,1,0],  'top':    [3,2,6,7],
}

normals = {
    'front': Vec3(0,0,-1), 'back': Vec3(0,0,1), 'left': Vec3(-1,0,0),
    'right': Vec3(1,0,0), 'bottom': Vec3(0,-1,0), 'top': Vec3(0,1,0),
}

uvs = [(0,0), (1,0), (1,1), (0,1)]

def get_chunk_coords(x, y, z):
    """Obtiene las coordenadas del chunk para una posición dada"""
    return (x // CHUNK_SIZE, y // CHUNK_SIZE, z // CHUNK_SIZE)

def is_block_at(x, y, z):
    """Verifica si hay un bloque en la posición dada"""
    return (x, y, z) in BLOCKS

def should_render_face(x, y, z, face_name):
    """Determina si una cara debe ser renderizada"""
    offsets = {
        'front': (0, 0, -1), 'back': (0, 0, 1), 'left': (-1, 0, 0),
        'right': (1, 0, 0), 'bottom': (0, -1, 0), 'top': (0, 1, 0),
    }
    dx, dy, dz = offsets[face_name]
    neighbor_pos = (x + dx, y + dy, z + dz)
    return not is_block_at(*neighbor_pos)

def generate_voxel(x, y, z):
    """Genera un voxel usando noise de Perlin"""
    noise_val = noise([x * 0.01, y * 0.01, z * 0.01])
    
    if y < CAVE_Y:
        if noise_val > 0:
            BLOCKS[(x, y, z)] = True
    elif y < MOUNTAIN_Y:
        BLOCKS[(x, y, z)] = True
    else:
        mountain_noise = noise([x * 0.01, z * 0.01])
        mountain_height = int(mountain_noise * MAX_MOUNTAIN_HEIGHT) + MOUNTAIN_Y
        if y <= mountain_height:
            BLOCKS[(x, y, z)] = True

class Chunk(Entity):
    def __init__(self, chunk_x, chunk_y, chunk_z):
        self.chunk_coords = (chunk_x, chunk_y, chunk_z)
        self.blocks_in_chunk = []
        
        # Calcular posición mundial del chunk
        world_x = chunk_x * CHUNK_SIZE
        world_y = chunk_y * CHUNK_SIZE
        world_z = chunk_z * CHUNK_SIZE
        
        # Generar bloques en este chunk
        for x in range(world_x, world_x + CHUNK_SIZE):
            for y in range(world_y, world_y + CHUNK_SIZE):
                for z in range(world_z, world_z + CHUNK_SIZE):
                    if (x, y, z) in BLOCKS:
                        self.blocks_in_chunk.append((x, y, z))
        
        # Crear el mesh combinado para todo el chunk
        mesh = self.create_chunk_mesh()
        
        super().__init__(
            parent=scene,
            model=mesh,
            texture=grass_texture,
            position=(world_x + CHUNK_SIZE/2, world_y + CHUNK_SIZE/2, world_z + CHUNK_SIZE/2)
        )
    
    def create_chunk_mesh(self):
        """Crea un mesh combinado para todos los bloques visibles en el chunk"""
        verts = []
        norms = []
        uv_coords = []
        tris = []
        vertex_count = 0
        
        for x, y, z in self.blocks_in_chunk:
            # Solo renderizar caras expuestas
            visible_faces = []
            for face_name in faces.keys():
                if should_render_face(x, y, z, face_name):
                    visible_faces.append(face_name)
            
            # Ajustar posición relativa al centro del chunk
            chunk_x, chunk_y, chunk_z = self.chunk_coords
            rel_x = x - (chunk_x * CHUNK_SIZE + CHUNK_SIZE/2)
            rel_y = y - (chunk_y * CHUNK_SIZE + CHUNK_SIZE/2)
            rel_z = z - (chunk_z * CHUNK_SIZE + CHUNK_SIZE/2)
            block_pos = Vec3(rel_x, rel_y, rel_z)
            
            # Añadir caras visibles al mesh
            for face_name in visible_faces:
                face_idx = faces[face_name]
                for i in face_idx:
                    verts.append(cube_vertices[i] + block_pos)
                    norms.append(normals[face_name])
                uv_coords.extend(uvs)
                tris.extend([
                    vertex_count, vertex_count+1, vertex_count+2,
                    vertex_count, vertex_count+2, vertex_count+3
                ])
                vertex_count += 4
        
        if not verts:  # Si no hay vértices, retornar mesh vacío
            return Mesh()
        
        return Mesh(vertices=verts, normals=norms, uvs=uv_coords, triangles=tris, mode='triangle')

def generate_world():
    """Genera el mundo por chunks"""
    print("Generando bloques...")
    
    # Primero generar todos los bloques
    for x in range(WORLD_SIZE[0]):
        for y in range(WORLD_SIZE[1]):
            for z in range(WORLD_SIZE[2]):
                generate_voxel(x, y, z)
    
    print(f"Bloques generados: {len(BLOCKS)}")
    print("Generando chunks...")
    
    # Luego crear chunks
    chunks_created = 0
    for chunk_x in range((WORLD_SIZE[0] + CHUNK_SIZE - 1) // CHUNK_SIZE):
        for chunk_y in range((WORLD_SIZE[1] + CHUNK_SIZE - 1) // CHUNK_SIZE):
            for chunk_z in range((WORLD_SIZE[2] + CHUNK_SIZE - 1) // CHUNK_SIZE):
                chunk = Chunk(chunk_x, chunk_y, chunk_z)
                CHUNKS[(chunk_x, chunk_y, chunk_z)] = chunk
                chunks_created += 1
                
                # Progreso
                if chunks_created % 10 == 0:
                    print(f"Chunks creados: {chunks_created}")
    
    print(f"Mundo generado: {chunks_created} chunks")

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
        
        # Cursor
        self.cursor = Entity(parent=camera.ui, model='quad', color=color.white, scale=0.008)
    
    def update(self):
        # Movimiento más eficiente
        direction = Vec3(0, 0, 0)
        if held_keys['w']:
            direction += self.forward
        if held_keys['s']:
            direction -= self.forward
        if held_keys['a']:
            direction -= self.right
        if held_keys['d']:
            direction += self.right
        
        if direction.length() > 0:
            direction = direction.normalized()
            self.position += direction * time.dt * self.speed
        
        # Rotación
        if mouse.velocity[0] != 0:
            self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity
        if mouse.velocity[1] != 0:
            camera.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity
            camera.rotation_x = clamp(camera.rotation_x, -90, 90)
        
        # Movimiento vertical simple
        if held_keys['space']:
            self.y += self.speed * time.dt
        if held_keys['shift']:
            self.y -= self.speed * time.dt

# Generar mundo
print("Iniciando generación del mundo...")
generate_world()

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

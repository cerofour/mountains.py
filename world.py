from ursina import Vec3, Mesh, scene, Entity
from config import WORLD_SIZE, CHUNK_SIZE, CAVE_Y, MOUNTAIN_Y, MAX_MOUNTAIN_HEIGHT
from utils import get_chunk_coords
from random import randint
import perlin_noise

BLOCKS = {}
CHUNKS = {}
noise = perlin_noise.PerlinNoise(octaves=10, seed=42)

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

def is_block_at(x, y, z):
    return (x, y, z) in BLOCKS

def should_render_face(x, y, z, face_name):
    offsets = {
        'front': (0, 0, -1), 'back': (0, 0, 1), 'left': (-1, 0, 0),
        'right': (1, 0, 0), 'bottom': (0, -1, 0), 'top': (0, 1, 0),
    }
    dx, dy, dz = offsets[face_name]
    neighbor_pos = (x + dx, y + dy, z + dz)
    return not is_block_at(*neighbor_pos)

def generate_voxel(x, y, z):
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
    def __init__(self, chunk_x, chunk_y, chunk_z, texture_map):
        self.chunk_coords = (chunk_x, chunk_y, chunk_z)
        self.blocks_in_chunk = []
        self.texture_map = texture_map
        world_x = chunk_x * CHUNK_SIZE
        world_y = chunk_y * CHUNK_SIZE
        world_z = chunk_z * CHUNK_SIZE
        
        # Agrupar bloques por textura
        blocks_by_texture = {}
        
        for x in range(world_x, world_x + CHUNK_SIZE):
            for y in range(world_y, world_y + CHUNK_SIZE):
                for z in range(world_z, world_z + CHUNK_SIZE):
                    if (x, y, z) in BLOCKS:
                        texture = texture_map(y)
                        if texture not in blocks_by_texture:
                            blocks_by_texture[texture] = []
                        blocks_by_texture[texture].append((x, y, z))
        
        # Crear una entidad por textura
        super().__init__(
            parent=scene,
            position=(world_x + CHUNK_SIZE/2, world_y + CHUNK_SIZE/2, world_z + CHUNK_SIZE/2)
        )
        
        for texture, blocks in blocks_by_texture.items():
            mesh = self.create_mesh_for_texture(blocks)
            if mesh:
                Entity(
                    parent=self,
                    model=mesh,
                    texture=texture
                )
    
    def create_mesh_for_texture(self, blocks):
        verts = []
        norms = []
        uv_coords = []
        tris = []
        vertex_count = 0
        
        for x, y, z in blocks:
            visible_faces = []
            for face_name in faces.keys():
                if should_render_face(x, y, z, face_name):
                    visible_faces.append(face_name)
            
            chunk_x, chunk_y, chunk_z = self.chunk_coords
            rel_x = x - (chunk_x * CHUNK_SIZE + CHUNK_SIZE/2)
            rel_y = y - (chunk_y * CHUNK_SIZE + CHUNK_SIZE/2)
            rel_z = z - (chunk_z * CHUNK_SIZE + CHUNK_SIZE/2)
            block_pos = Vec3(rel_x, rel_y, rel_z)
            
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
        
        if not verts:
            return None
        
        return Mesh(vertices=verts, normals=norms, uvs=uv_coords, triangles=tris, mode='triangle')

def generate_world(texture_map):
    print("Generando bloques...")
    for x in range(WORLD_SIZE[0]):
        for y in range(WORLD_SIZE[1]):
            for z in range(WORLD_SIZE[2]):
                generate_voxel(x, y, z)
    print(f"Bloques generados: {len(BLOCKS)}")
    print("Generando chunks...")
    chunks_created = 0
    for chunk_x in range((WORLD_SIZE[0] + CHUNK_SIZE - 1) // CHUNK_SIZE):
        for chunk_y in range((WORLD_SIZE[1] + CHUNK_SIZE - 1) // CHUNK_SIZE):
            for chunk_z in range((WORLD_SIZE[2] + CHUNK_SIZE - 1) // CHUNK_SIZE):
                chunk = Chunk(chunk_x, chunk_y, chunk_z, texture_map)
                CHUNKS[(chunk_x, chunk_y, chunk_z)] = chunk
                chunks_created += 1
                if chunks_created % 10 == 0:
                    print(f"Chunks creados: {chunks_created}")
    print(f"Mundo generado: {chunks_created} chunks") 
    print(f"Mundo generado: {chunks_created} chunks") 
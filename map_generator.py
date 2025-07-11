from PIL import Image
import numpy as np
from ursina import *

def load_image_with_pil(image_path):
    """Carga una imagen usando PIL si está disponible"""
    try:
        img = Image.open(image_path)
        img = img.convert('RGB')
        width, height = img.size
        
        # Redimensionar si es muy grande
        #if width > 50 or height > 50:
        #    img = img.resize((min(width, 50), min(height, 50)))
        #    width, height = img.size
        
        img_array = np.array(img)
        
        # Convertir RGB a valores simples
        image_data = []
        for y in range(height):
            row = []
            for x in range(width):
                r, g, b = img_array[y, x]
                
                # Mapear colores RGB a valores simples
                #if r < 50 and g < 50 and b < 50:  # Negro
                #    row.append(0)
                if r > 200 and g > 200 and b > 200:  # Blanco
                    row.append(0)
                elif r > 150 and g < 100 and b < 100:  # Rojo
                    row.append(1)
                elif r < 100 and g > 150 and b < 100:  # Verde
                    row.append(2)
                elif r < 100 and g < 100 and b > 150:  # Azul
                    row.append(3)
                elif r > 150 and g > 150 and b < 100:  # Amarillo
                    row.append(5)
                #elif r > 100 and g > 50 and b < 50:  # Marrón
                #    row.append(6)
                else:  # Gris por defecto
                    row.append(7)
            image_data.append(row)
        
        return image_data
        
    except Exception as e:
        print(f"Error al cargar imagen: {e}")
        return None


def greedy_mesh_walls(wall_data, block_size=1):
    """
    Implementa greedy meshing para los bloques de muro.
    wall_data: matriz 2D donde True indica la presencia de un muro
    """
    height = len(wall_data)
    width = len(wall_data[0]) if height > 0 else 0
    
    # Crear una copia para marcar los bloques ya procesados
    processed = [[False for _ in range(width)] for _ in range(height)]
    meshes = []
    
    for y in range(height):
        for x in range(width):
            if wall_data[y][x] and not processed[y][x]:
                # Encontrar el rectángulo más grande que comience en (x, y)
                
                # Primero, expandir horizontalmente
                width_extent = 1
                while (x + width_extent < width and 
                       wall_data[y][x + width_extent] and 
                       not processed[y][x + width_extent]):
                    width_extent += 1
                
                # Luego, expandir verticalmente manteniendo el ancho
                height_extent = 1
                can_expand_height = True
                while can_expand_height and y + height_extent < height:
                    # Verificar si toda la fila puede expandirse
                    for check_x in range(x, x + width_extent):
                        if (not wall_data[y + height_extent][check_x] or 
                            processed[y + height_extent][check_x]):
                            can_expand_height = False
                            break
                    
                    if can_expand_height:
                        height_extent += 1
                
                # Marcar todos los bloques en el rectángulo como procesados
                for mesh_y in range(y, y + height_extent):
                    for mesh_x in range(x, x + width_extent):
                        processed[mesh_y][mesh_x] = True
                
                # Crear el mesh combinado
                mesh_info = {
                    'x': x * block_size + (width_extent * block_size - block_size) / 2,
                    'z': y * block_size + (height_extent * block_size - block_size) / 2,
                    'width': width_extent * block_size,
                    'height': height_extent * block_size,
                    'scale': (width_extent * block_size, 5, height_extent * block_size)
                }
                meshes.append(mesh_info)
    
    return meshes


def generate_world_from_data(image_data, world_blocks, enemy_spawn_points, easter_egg, block_size=1) -> Vec3:
    """Genera un mundo 3D basado en datos de imagen con greedy meshing para muros"""
    
    # Mapeo de valores a colores
    color_map = {
        0: color.white,
        1: color.red,  # Rojo ENEMIGO SPAWN
        2: color.green,  # Verde APARECE PERRITO
        3: color.blue,  # Azul MURO
        5: color.yellow, # Spawn point
    }
    
    height = len(image_data)
    width = len(image_data[0]) if height > 0 else 0

    ground = Entity(
        model='plane',
        collider='box',
        x=(width-1) * block_size / 2,  # Centrar el plano
        y=0,
        z=(height-1) * block_size / 2,  # Centrar el plano
        origin_y=-0.5,
        scale=(width * block_size, 1, height * block_size),
        texture='grass',
        texture_scale=(width/4, height/4),  # Escalar textura proporcionalmente
        color=color.light_gray
    )

    ceiling = Entity(
        model='plane',
        collider='box',
        x=(width-1) * block_size / 2,  # Centrar el plano
        y=0,
        z=(height-1) * block_size / 2,  # Centrar el plano
        origin_y=-5,
        scale=(width * block_size, 1, (height * block_size * -1)),
        texture='brick',
        texture_scale=(width/4, height/4),  # Escalar textura proporcionalmente
        color=color.light_gray
    )
    world_blocks.append(ceiling)
    

    wall_height = 5
    wall_thickness = 0.5
    
    # Pared Norte (arriba)
    wall_north = Entity(
        model='cube',
        collider='box',
        x=(width-1) * block_size / 2,  # Centrado en X
        y=wall_height / 2,
        z=-wall_thickness / 2,  # Borde superior
        scale=(width * block_size, wall_height, wall_thickness),
        texture='brick',
        texture_scale=(width/2, wall_height/2),
        color=color.gray
    )
    world_blocks.append(wall_north)
    
    # Pared Sur (abajo)
    wall_south = Entity(
        model='cube',
        collider='box',
        x=(width-1) * block_size / 2,  # Centrado en X
        y=wall_height / 2,
        z=(height-1) * block_size + wall_thickness / 2,  # Borde inferior
        scale=(width * block_size, wall_height, wall_thickness),
        texture='brick',
        texture_scale=(width/2, wall_height/2),
        color=color.gray
    )
    world_blocks.append(wall_south)
    
    # Pared Este (derecha)
    wall_east = Entity(
        model='cube',
        collider='box',
        x=(width-1) * block_size + wall_thickness / 2,  # Borde derecho
        y=wall_height / 2,
        z=(height-1) * block_size / 2,  # Centrado en Z
        scale=(wall_thickness, wall_height, height * block_size),
        texture='brick',
        texture_scale=(wall_thickness, wall_height/2),
        color=color.gray
    )
    world_blocks.append(wall_east)
    
    # Pared Oeste (izquierda)
    wall_west = Entity(
        model='cube',
        collider='box',
        x=-wall_thickness / 2,  # Borde izquierdo
        y=wall_height / 2,
        z=(height-1) * block_size / 2,  # Centrado en Z
        scale=(wall_thickness, wall_height, height * block_size),
        texture='brick',
        texture_scale=(wall_thickness, wall_height/2),
        color=color.gray
    )
    world_blocks.append(wall_west)
    
    world_blocks.append(ground)

    print(f"Generando mundo de {width}x{height}")

    player_spawn = Vec3(0, 0, 0)

    # Crear matriz de muros para greedy meshing
    wall_data = [[False for _ in range(width)] for _ in range(height)]
    
    # Primera pasada: identificar muros y otros bloques
    for y in range(height):
        for x in range(width):
            pixel_value = image_data[y][x]
            
            if pixel_value == 3:  # Muro azul
                wall_data[y][x] = True
            elif pixel_value in color_map and color_map[pixel_value] is not None:
                block = None
                if pixel_value == 5:  # Spawn point
                    player_spawn = Vec3(x * block_size, 0, y * block_size)
                elif pixel_value == 2:  # Easter egg
                    block = Entity(
                        model='cube',
                        origin_y=-0.5,
                        texture='brick',
                        x=x * block_size,
                        z=y * block_size,
                        color=color_map[pixel_value],
                        collider='box',
                        scale=(block_size, 1, block_size),
                    )
                    easter_egg = block
                elif pixel_value == 1:  # Enemy spawn
                    block = Entity(
                        model='cube',
                        origin_y=-0.5,
                        texture='brick',
                        x=x * block_size,
                        z=y * block_size,
                        color=color_map[pixel_value],
                        collider='box',
                        scale=(block_size, 1, block_size),
                    )
                    enemy_spawn_points.append(block)
                
                if block:
                    world_blocks.append(block)
    
    # Aplicar greedy meshing a los muros
    wall_meshes = greedy_mesh_walls(wall_data, block_size)
    
    print(f"Creando {len(wall_meshes)} meshes optimizados para muros (antes: {sum(sum(row) for row in wall_data)} bloques individuales)")
    
    # Crear las entidades de muro optimizadas
    for mesh in wall_meshes:
        wall_block = Entity(
            model='cube',
            origin_y=-0.5,
            texture='brick',
            x=mesh['x'],
            z=mesh['z'],
            collider='box',
            scale=mesh['scale'],
            color=color.blue,
            # Ajustar escala de textura basada en el tamaño del mesh
            texture_scale=(mesh['width']/2, mesh['height']/2)
        )
        world_blocks.append(wall_block)
    
    print(f"Mundo generado con {len(world_blocks)} bloques (incluyendo meshes optimizados)")
    return player_spawn
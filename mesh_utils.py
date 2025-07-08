from ursina import *
import os
import re

def fix_obj_file(input_path, output_path):
    """
    Fix common OBJ file issues that cause mesh loading problems.
    
    Args:
        input_path: Path to the original OBJ file
        output_path: Path to save the fixed OBJ file
    
    Returns:
        True if fix was successful, False otherwise
    """
    try:
        with open(input_path, 'r') as f:
            lines = f.readlines()
        
        fixed_lines = []
        vertex_count = 0
        texture_count = 0
        normal_count = 0
        
        # First pass: count vertices and fix UV coordinates
        for line in lines:
            line = line.strip()
            if line.startswith('v '):
                vertex_count += 1
                fixed_lines.append(line)
            elif line.startswith('vt '):
                texture_count += 1
                # Fix UV coordinates that are outside 0-1 range
                parts = line.split()
                if len(parts) >= 3:
                    u = float(parts[1])
                    v = float(parts[2])
                    # Clamp UV coordinates to 0-1 range
                    u = max(0.0, min(1.0, u % 1.0))
                    v = max(0.0, min(1.0, v % 1.0))
                    fixed_lines.append(f"vt {u} {v} 0")
                else:
                    fixed_lines.append(line)
            elif line.startswith('vn '):
                normal_count += 1
                fixed_lines.append(line)
            elif line.startswith('f '):
                # Fix face indices that might be out of range
                parts = line.split()
                fixed_face = ['f']
                for i in range(1, len(parts)):
                    face_part = parts[i]
                    # Handle face format: v/vt/vn or v//vn or v/vt or v
                    if '/' in face_part:
                        indices = face_part.split('/')
                        vertex_idx = int(indices[0]) if indices[0] else 1
                        texture_idx = int(indices[1]) if len(indices) > 1 and indices[1] else 1
                        normal_idx = int(indices[2]) if len(indices) > 2 and indices[2] else 1
                        
                        # Clamp indices to valid ranges
                        vertex_idx = max(1, min(vertex_count, vertex_idx))
                        texture_idx = max(1, min(texture_count, texture_idx)) if texture_count > 0 else 1
                        normal_idx = max(1, min(normal_count, normal_idx)) if normal_count > 0 else 1
                        
                        if len(indices) == 3:
                            fixed_face.append(f"{vertex_idx}/{texture_idx}/{normal_idx}")
                        elif len(indices) == 2:
                            fixed_face.append(f"{vertex_idx}/{texture_idx}")
                        else:
                            fixed_face.append(f"{vertex_idx}")
                    else:
                        vertex_idx = int(face_part)
                        vertex_idx = max(1, min(vertex_count, vertex_idx))
                        fixed_face.append(str(vertex_idx))
                
                # Only add faces with at least 3 vertices
                if len(fixed_face) >= 4:
                    fixed_lines.append(' '.join(fixed_face))
            else:
                fixed_lines.append(line)
        
        # Write the fixed file
        with open(output_path, 'w') as f:
            for line in fixed_lines:
                f.write(line + '\n')
        
        print(f"🔧 Fixed OBJ file: {input_path} -> {output_path}")
        return True
        
    except Exception as e:
        print(f"✗ Error fixing OBJ file {input_path}: {e}")
        return False

def load_model_safe(model_path, fallback_model='cube'):
    """
    Safely load a model with fallback to a simple shape if loading fails.
    
    Args:
        model_path: Path to the model file
        fallback_model: Fallback model to use if loading fails
    
    Returns:
        Loaded model or fallback model
    """
    try:
        # Check if file exists
        if not os.path.exists(model_path):
            print(f"⚠️  Model file not found: {model_path}, using fallback: {fallback_model}")
            return fallback_model
            
        # Try to load the model
        model = load_model(model_path)
        print(f"✅ Successfully loaded model: {model_path}")
        return model
        
    except Exception as e:
        print(f"✗ Error loading model {model_path}: {e}")
        
        # Try to fix the OBJ file if it's an OBJ file
        if model_path.endswith('.obj'):
            fixed_path = model_path.replace('.obj', '_fixed.obj')
            print(f"🔧 Attempting to fix OBJ file...")
            
            if fix_obj_file(model_path, fixed_path):
                try:
                    model = load_model(fixed_path)
                    print(f"✅ Successfully loaded fixed model: {fixed_path}")
                    return model
                except Exception as e2:
                    print(f"✗ Fixed model still failed to load: {e2}")
        
        print(f"📦 Using fallback model: {fallback_model}")
        return fallback_model

def create_simple_bot_mesh():
    """
    Create a simple bot mesh as a fallback when the original OBJ fails to load.
    """
    # Create a simple humanoid-like mesh using basic shapes
    vertices = [
        # Head (cube)
        Vec3(-0.5, 1.5, -0.5), Vec3(0.5, 1.5, -0.5), Vec3(0.5, 2.5, -0.5), Vec3(-0.5, 2.5, -0.5),  # Front
        Vec3(-0.5, 1.5, 0.5), Vec3(0.5, 1.5, 0.5), Vec3(0.5, 2.5, 0.5), Vec3(-0.5, 2.5, 0.5),    # Back
        
        # Body (larger cube)
        Vec3(-0.7, 0, -0.4), Vec3(0.7, 0, -0.4), Vec3(0.7, 1.5, -0.4), Vec3(-0.7, 1.5, -0.4),     # Front
        Vec3(-0.7, 0, 0.4), Vec3(0.7, 0, 0.4), Vec3(0.7, 1.5, 0.4), Vec3(-0.7, 1.5, 0.4),        # Back
        
        # Arms (simple rectangles)
        Vec3(-1.2, 0.5, -0.2), Vec3(-0.7, 0.5, -0.2), Vec3(-0.7, 1.2, -0.2), Vec3(-1.2, 1.2, -0.2), # Left arm front
        Vec3(-1.2, 0.5, 0.2), Vec3(-0.7, 0.5, 0.2), Vec3(-0.7, 1.2, 0.2), Vec3(-1.2, 1.2, 0.2),   # Left arm back
        Vec3(0.7, 0.5, -0.2), Vec3(1.2, 0.5, -0.2), Vec3(1.2, 1.2, -0.2), Vec3(0.7, 1.2, -0.2),   # Right arm front
        Vec3(0.7, 0.5, 0.2), Vec3(1.2, 0.5, 0.2), Vec3(1.2, 1.2, 0.2), Vec3(0.7, 1.2, 0.2),       # Right arm back
        
        # Legs (simple rectangles)
        Vec3(-0.4, -1.5, -0.2), Vec3(0, -1.5, -0.2), Vec3(0, 0, -0.2), Vec3(-0.4, 0, -0.2),       # Left leg front
        Vec3(-0.4, -1.5, 0.2), Vec3(0, -1.5, 0.2), Vec3(0, 0, 0.2), Vec3(-0.4, 0, 0.2),           # Left leg back
        Vec3(0, -1.5, -0.2), Vec3(0.4, -1.5, -0.2), Vec3(0.4, 0, -0.2), Vec3(0, 0, -0.2),         # Right leg front
        Vec3(0, -1.5, 0.2), Vec3(0.4, -1.5, 0.2), Vec3(0.4, 0, 0.2), Vec3(0, 0, 0.2),             # Right leg back
    ]
    
    # Define triangles for the mesh
    triangles = [
        # Head
        0, 1, 2, 0, 2, 3,    # Front face
        4, 6, 5, 4, 7, 6,    # Back face
        0, 3, 7, 0, 7, 4,    # Left face
        1, 5, 6, 1, 6, 2,    # Right face
        3, 2, 6, 3, 6, 7,    # Top face
        0, 4, 5, 0, 5, 1,    # Bottom face
        
        # Body
        8, 9, 10, 8, 10, 11,    # Front face
        12, 14, 13, 12, 15, 14, # Back face
        8, 11, 15, 8, 15, 12,   # Left face
        9, 13, 14, 9, 14, 10,   # Right face
        11, 10, 14, 11, 14, 15, # Top face
        8, 12, 13, 8, 13, 9,    # Bottom face
        
        # Add similar triangles for arms and legs...
        # (Simplified - just adding a few key faces)
        16, 17, 18, 16, 18, 19, # Left arm front
        20, 22, 21, 20, 23, 22, # Left arm back
        24, 25, 26, 24, 26, 27, # Right arm front
        28, 30, 29, 28, 31, 30, # Right arm back
    ]
    
    # Create UVs
    uvs = [(0, 0) for _ in vertices]
    
    # Create the mesh
    mesh = Mesh(vertices=vertices, triangles=triangles, uvs=uvs)
    return mesh

def create_bot_entity_safe(**kwargs):
    """
    Create a bot entity with safe model loading.
    """
    # Try to load the original model first
    model = load_model_safe('assets/botsito/bot.obj', None)
    
    # If loading failed, create a simple fallback mesh
    if model is None:
        print("🔧 Creating simple bot mesh as fallback...")
        model = create_simple_bot_mesh()
    
    # Create and return the entity
    return Entity(model=model, **kwargs)

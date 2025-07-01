def get_chunk_coords(x, y, z, chunk_size):
    return (x // chunk_size, y // chunk_size, z // chunk_size)

def clamp(val, min_val, max_val):
    return max(min(val, max_val), min_val) 
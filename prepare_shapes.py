import random
import math
from noise import pnoise2

def write_to_obj(filename, vertices, indices):
    with open(filename, 'w') as f:
        # Write vertices to the file
        for vertex in vertices:
            f.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")
        # Write faces to the file (OBJ indices start from 1)
        for face in indices:
            f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

def make_pyramid(filename):
    # Define the tetrahedron vertices and indices
    vertices = [
        [-5, -5, 0],  # Base vertex 1
        [5, -5, 0],   # Base vertex 2
        [0, 5, 0],    # Base vertex 3
        [0, 0, 5]     # Apex vertex
    ]
    indices = [
        [0, 1, 2],    # Base triangle
        [0, 1, 3],    # Side triangle 1
        [1, 2, 3],    # Side triangle 2
        [2, 0, 3]     # Side triangle 3
    ]
    write_to_obj(filename, vertices, indices)

def make_rocky_moutain(filename):
    # Define the pyramid vertices and indices
    vertices = [
        [-5, -5, 0],  # Base vertex 1
        [5, -5, 0],   # Base vertex 2
        [5, 5, 0],    # Base vertex 3
        [-5, 5, 0],   # Base vertex 4
        [0, 0, 5]     # Apex vertex
    ]
    indices = [
        [0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4],  # Sides
        [0, 1, 2], [2, 3, 0]                         # Base
    ]

    # Add random cubes embedded in the pyramid
    num_cubes = 5
    for _ in range(num_cubes):
        size = random.uniform(0.5, 2)
        x = random.uniform(-4, 4)
        y = random.uniform(-4, 4)
        z = random.uniform(0.5, 4.5)
        
        cube_vertices = [
            [x-size/2, y-size/2, z-size/2], [x+size/2, y-size/2, z-size/2],
            [x+size/2, y+size/2, z-size/2], [x-size/2, y+size/2, z-size/2],
            [x-size/2, y-size/2, z+size/2], [x+size/2, y-size/2, z+size/2],
            [x+size/2, y+size/2, z+size/2], [x-size/2, y+size/2, z+size/2]
        ]
        
        cube_indices = [
            [0, 1, 2], [2, 3, 0],  # Bottom
            [4, 5, 6], [6, 7, 4],  # Top
            [0, 1, 5], [5, 4, 0],  # Front
            [1, 2, 6], [6, 5, 1],  # Right
            [2, 3, 7], [7, 6, 2],  # Back
            [3, 0, 4], [4, 7, 3]   # Left
        ]
        
        offset = len(vertices)
        cube_indices = [[i+offset for i in face] for face in cube_indices]
        vertices.extend(cube_vertices)
        indices.extend(cube_indices)

    write_to_obj(filename, vertices, indices)

def gaussian2(x, y, sigma, height):
    """Return the height using a Gaussian function."""
    return height * math.exp(-((x**2 + y**2) / (2 * sigma**2)))

def generate_gaussian_pyramid4(filename, size=10, resolution=0.5, sigma=3, height=5, noise_scale=0.5, noise_factor=1.0):
    vertices = []
    faces = []
    res_count = int(size / resolution)

    # Top surface with Noise
    for i in range(res_count):
        for j in range(res_count):
            x = -size/2 + i * resolution
            y = -size/2 + j * resolution
            z = gaussian2(x, y, sigma, height)
            z += pnoise2(x * noise_scale, y * noise_scale) * noise_factor
            vertices.append([x, y, z])

    # Flat Base
    for i in range(res_count):
        for j in range(res_count):
            x = -size/2 + i * resolution
            y = -size/2 + j * resolution
            vertices.append([x, y, 0])

    # Top faces
    for i in range(res_count - 1):
        for j in range(res_count - 1):
            bl = i * res_count + j
            br = i * res_count + j + 1
            tl = (i + 1) * res_count + j
            tr = (i + 1) * res_count + j + 1
            faces.append([bl, br, tl])
            faces.append([tl, br, tr])

    # Base faces
    base_offset = res_count * res_count
    for i in range(res_count - 1):
        for j in range(res_count - 1):
            blb = base_offset + i * res_count + j
            brb = base_offset + i * res_count + j + 1
            tlb = base_offset + (i + 1) * res_count + j
            trb = base_offset + (i + 1) * res_count + j + 1
            faces.append([blb, tlb, brb])
            faces.append([tlb, trb, brb])

    # Side faces
    for i in range(res_count - 1):
        for j in range(res_count):
            top = i * res_count + j
            bottom = base_offset + i * res_count + j
            top_next = (i + 1) * res_count + j
            bottom_next = base_offset + (i + 1) * res_count + j
            faces.append([top, bottom, top_next])
            faces.append([top_next, bottom, bottom_next])

    write_to_obj(filename, vertices, faces)

# --- Execution ---
if __name__ == "__main__":
    output_dir = "./shapes"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    generate_gaussian_pyramid4(f"{output_dir}/gaussian_pyramid.obj")
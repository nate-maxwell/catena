import math
from pathlib import Path

import OpenGL.GL as gl

SHADER_DIR = Path(__file__).parent


def load_obj(path: Path) -> tuple[list[float], list[int]]:
    """
    Load interleaved vertex data and triangle indices from an OBJ file.

    Parses positions, texture coordinates, and normals. If the file contains no
    normals, smooth per-vertex normals are computed from face geometry. Output
    vertices are interleaved as position (3), normal (3), texcoord (2) per vertex,
    with one unique vertex per distinct position/normal/texcoord combination.

    Args:
        path (Path): Path to the .obj file.
    Returns:
        tuple[list[float], list[int]]: Flat interleaved vertex data (8 floats
            per vertex) and flat triangle index array.
    """
    raw_positions: list[tuple[float, float, float]] = []
    raw_texcoords: list[tuple[float, float]] = []
    raw_normals: list[tuple[float, float, float]] = []
    raw_faces: list[list[tuple[int, int, int]]] = []

    with open(path, "r", encoding="utf-8") as obj_file:
        for line in obj_file:
            tokens = line.split()
            if not tokens:
                continue
            if tokens[0] == "v":
                raw_positions.append(
                    (float(tokens[1]), float(tokens[2]), float(tokens[3]))
                )
            elif tokens[0] == "vt":
                raw_texcoords.append((float(tokens[1]), float(tokens[2])))
            elif tokens[0] == "vn":
                raw_normals.append(
                    (float(tokens[1]), float(tokens[2]), float(tokens[3]))
                )
            elif tokens[0] == "f":
                face: list[tuple[int, int, int]] = []
                for token in tokens[1:]:
                    parts = token.split("/")
                    position_index = int(parts[0]) - 1
                    texcoord_index = (
                        int(parts[1]) - 1 if len(parts) > 1 and parts[1] else -1
                    )
                    normal_index = (
                        int(parts[2]) - 1 if len(parts) > 2 and parts[2] else -1
                    )
                    face.append((position_index, texcoord_index, normal_index))
                raw_faces.append(face)

    if not raw_normals:
        computed_normals = [[0.0, 0.0, 0.0] for _ in raw_positions]
        for face in raw_faces:
            for i in range(1, len(face) - 1):
                i0, i1, i2 = face[0][0], face[i][0], face[i + 1][0]
                v0, v1, v2 = raw_positions[i0], raw_positions[i1], raw_positions[i2]
                ux, uy, uz = v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]
                vx, vy, vz = v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2]
                nx = uy * vz - uz * vy
                ny = uz * vx - ux * vz
                nz = ux * vy - uy * vx
                for idx in (i0, i1, i2):
                    computed_normals[idx][0] += nx
                    computed_normals[idx][1] += ny
                    computed_normals[idx][2] += nz
        for normal in computed_normals:
            length = math.sqrt(normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2)
            if length > 0.0:
                normal[0] /= length
                normal[1] /= length
                normal[2] /= length
        raw_normals = [tuple(normal) for normal in computed_normals]
        use_position_index_as_normal = True
    else:
        use_position_index_as_normal = False

    vertex_cache: dict[tuple[int, int, int], int] = {}
    interleaved: list[float] = []
    indices: list[int] = []

    for face in raw_faces:
        resolved: list[int] = []
        for position_index, texcoord_index, normal_index in face:
            effective_normal_index = (
                position_index if use_position_index_as_normal else normal_index
            )
            key = (position_index, texcoord_index, effective_normal_index)
            if key not in vertex_cache:
                vertex_cache[key] = len(interleaved) // 8
                px, py, pz = raw_positions[position_index]
                if effective_normal_index >= 0:
                    nx, ny, nz = raw_normals[effective_normal_index]
                else:
                    nx, ny, nz = 0.0, 0.0, 1.0
                if texcoord_index >= 0:
                    tu, tv = raw_texcoords[texcoord_index]
                else:
                    tu, tv = 0.0, 0.0
                interleaved.extend((px, py, pz, nx, ny, nz, tu, tv))
            resolved.append(vertex_cache[key])

        for i in range(1, len(resolved) - 1):
            indices.append(resolved[0])
            indices.append(resolved[i])
            indices.append(resolved[i + 1])

    return interleaved, indices


def compute_tangents(interleaved: list[float], indices: list[int]) -> list[float]:
    """
    Compute per-vertex tangents and append them to interleaved vertex data.

    Args:
        interleaved (list[float]): Flat interleaved vertex data (8 floats per
            vertex: position, normal, texcoord).
        indices (list[int]): Flat triangle index array.
    Returns:
        list[float]: Flat interleaved vertex data with tangents appended (11
            floats per vertex: position, normal, texcoord, tangent).
    """
    vertex_count = len(interleaved) // 8
    tangents = [[0.0, 0.0, 0.0] for _ in range(vertex_count)]

    for i in range(0, len(indices), 3):
        i0, i1, i2 = indices[i], indices[i + 1], indices[i + 2]

        p0 = interleaved[i0 * 8 : i0 * 8 + 3]
        p1 = interleaved[i1 * 8 : i1 * 8 + 3]
        p2 = interleaved[i2 * 8 : i2 * 8 + 3]

        uv0 = interleaved[i0 * 8 + 6 : i0 * 8 + 8]
        uv1 = interleaved[i1 * 8 + 6 : i1 * 8 + 8]
        uv2 = interleaved[i2 * 8 + 6 : i2 * 8 + 8]

        edge1 = [p1[j] - p0[j] for j in range(3)]
        edge2 = [p2[j] - p0[j] for j in range(3)]
        delta_uv1 = [uv1[j] - uv0[j] for j in range(2)]
        delta_uv2 = [uv2[j] - uv0[j] for j in range(2)]

        denom = delta_uv1[0] * delta_uv2[1] - delta_uv2[0] * delta_uv1[1]
        if abs(denom) < 1e-12:
            continue
        inv_denom = 1.0 / denom

        tangent = [
            inv_denom * (delta_uv2[1] * edge1[j] - delta_uv1[1] * edge2[j])
            for j in range(3)
        ]

        for idx in (i0, i1, i2):
            tangents[idx][0] += tangent[0]
            tangents[idx][1] += tangent[1]
            tangents[idx][2] += tangent[2]

    extended: list[float] = []
    for vertex_index in range(vertex_count):
        vertex_data = interleaved[vertex_index * 8 : vertex_index * 8 + 8]
        tangent = tangents[vertex_index]
        length = math.sqrt(tangent[0] ** 2 + tangent[1] ** 2 + tangent[2] ** 2)
        if length > 0.0:
            tangent = [component / length for component in tangent]
        else:
            tangent = [1.0, 0.0, 0.0]
        extended.extend(vertex_data)
        extended.extend(tangent)

    return extended


def compile_shader_program(vertex_path: Path, fragment_path: Path) -> int:
    """
    Compile and link a GLSL shader program from vertex and fragment source files.

    Args:
        vertex_path (Path): Path to the vertex shader source file.
        fragment_path (Path): Path to the fragment shader source file.
    Returns:
        int: The linked shader program's OpenGL handle.
    """
    vertex_source = vertex_path.read_text(encoding="utf-8")
    fragment_source = fragment_path.read_text(encoding="utf-8")

    vertex_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    gl.glShaderSource(vertex_shader, vertex_source)
    gl.glCompileShader(vertex_shader)
    if not gl.glGetShaderiv(vertex_shader, gl.GL_COMPILE_STATUS):
        raise RuntimeError(gl.glGetShaderInfoLog(vertex_shader).decode("utf-8"))

    fragment_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
    gl.glShaderSource(fragment_shader, fragment_source)
    gl.glCompileShader(fragment_shader)
    if not gl.glGetShaderiv(fragment_shader, gl.GL_COMPILE_STATUS):
        raise RuntimeError(gl.glGetShaderInfoLog(fragment_shader).decode("utf-8"))

    program = gl.glCreateProgram()
    gl.glAttachShader(program, vertex_shader)
    gl.glAttachShader(program, fragment_shader)
    gl.glLinkProgram(program)
    if not gl.glGetProgramiv(program, gl.GL_LINK_STATUS):
        raise RuntimeError(gl.glGetProgramInfoLog(program).decode("utf-8"))

    gl.glDeleteShader(vertex_shader)
    gl.glDeleteShader(fragment_shader)
    return program


import json
import os
import sys

# The script uses Blender's Python API.
try:
    import bpy
    from mathutils import Vector, Euler
except Exception as e:
    raise RuntimeError("This script must be run inside Blender (bpy not found).")


def load_json(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"JSON file not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def ensure_collection(name, parent=None):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    if parent is None:
        bpy.context.scene.collection.children.link(col)
    else:
        parent.children.link(col)
    return col


def create_material(mat_def):
    """Create or reuse a material from a definition dict."""
    if not mat_def:
        return None
    name = mat_def.get('name', 'Material')
    if name in bpy.data.materials:
        mat = bpy.data.materials[name]
    else:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
    # Principled BSDF node
    bsdf = None
    if mat.node_tree:
        for n in mat.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED':
                bsdf = n
                break
    if bsdf is None:
        # create principled bsdf
        nodes = mat.node_tree.nodes
        nodes.clear()
        output = nodes.new(type='ShaderNodeOutputMaterial')
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    # Apply properties
    base = mat_def.get('base_color')
    if base:
        # allow 3 or 4-length lists
        if len(base) == 3:
            bsdf.inputs['Base Color'].default_value = (base[0], base[1], base[2], 1.0)
        else:
            bsdf.inputs['Base Color'].default_value = tuple(base[:4])
    metallic = mat_def.get('metallic')
    if metallic is not None:
        bsdf.inputs['Metallic'].default_value = float(metallic)
    roughness = mat_def.get('roughness')
    if roughness is not None:
        bsdf.inputs['Roughness'].default_value = float(roughness)
    # Image texture
    tex_path = mat_def.get('texture_image')
    if tex_path:
        tex_path = os.path.expanduser(tex_path)
        if os.path.isfile(tex_path):
            tex_image = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
            try:
                tex_image.image = bpy.data.images.load(tex_path)
            except Exception as e:
                print(f"Warning: could not load image {tex_path}: {e}")
            mat.node_tree.links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
        else:
            print(f"Warning: texture image not found: {tex_path}")
    return mat


def set_transform(obj, defn):
    loc = defn.get('location')
    if loc:
        obj.location = Vector(loc)
    rot = defn.get('rotation_euler')
    if rot:
        # rotation in radians
        obj.rotation_euler = Euler(rot, 'XYZ')
    scl = defn.get('scale')
    if scl:
        obj.scale = Vector(scl)


def create_primitive(defn):
    t = defn.get('type', 'cube').lower()
    name = defn.get('name', t)
    obj = None
    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')

    if t == 'cube':
        bpy.ops.mesh.primitive_cube_add()
    elif t == 'sphere' or t == 'uv_sphere':
        bpy.ops.mesh.primitive_uv_sphere_add()
    elif t == 'icosphere':
        bpy.ops.mesh.primitive_ico_sphere_add()
    elif t == 'cylinder':
        bpy.ops.mesh.primitive_cylinder_add()
    elif t == 'cone':
        bpy.ops.mesh.primitive_cone_add()
    elif t == 'torus':
        bpy.ops.mesh.primitive_torus_add()
    elif t == 'plane':
        bpy.ops.mesh.primitive_plane_add()
    else:
        raise ValueError(f"Unsupported primitive type: {t}")
    obj = bpy.context.active_object
    obj.name = name
    return obj


def create_mesh_from_def(defn):
    name = defn.get('name', 'Mesh')
    verts = defn.get('vertices', [])
    faces = defn.get('faces', [])
    if not verts or not faces:
        raise ValueError('Mesh type requires "vertices" and "faces" arrays')
    mesh = bpy.data.meshes.new(name + '_mesh')
    mesh.from_pydata([Vector(v) for v in verts], [], [tuple(f) for f in faces])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    return obj


def apply_material(obj, mat_def):
    mat = create_material(mat_def)
    if mat:
        if obj.data and hasattr(obj.data, 'materials'):
            if len(obj.data.materials) == 0:
                obj.data.materials.append(mat)
            else:
                obj.data.materials[0] = mat


def create_object(defn, created_objects, collections):
    """Create a single object from its definition and store it in created_objects by name."""
    name = defn.get('name')
    if not name:
        raise ValueError('Every object must have a "name"')
    obj_type = defn.get('type', 'cube')
    if obj_type == 'mesh':
        obj = create_mesh_from_def(defn)
    else:
        obj = create_primitive(defn)
    set_transform(obj, defn)
    # Assign to collection if requested
    col_name = defn.get('collection')
    if col_name:
        col = collections.setdefault(col_name, ensure_collection(col_name))
        # unlink from default and link to this collection
        for c in obj.users_collection:
            c.objects.unlink(obj)
        col.objects.link(obj)
    # apply material
    mat_def = defn.get('material')
    if mat_def:
        apply_material(obj, mat_def)
    created_objects[name] = obj
    return obj


def build_scene(data):
    scene_name = data.get('scene_name', 'JSON_Scene')
    # Optionally clear existing objects? (we'll not delete by default). If user sets clear_scene=true, clear.
    if data.get('clear_scene'):
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
    created_objects = {}
    collections = {}
    # First pass: create all objects (without parenting)
    for obj_def in data.get('objects', []):
        try:
            create_object(obj_def, created_objects, collections)
        except Exception as e:
            print(f"Error creating object {obj_def.get('name')}: {e}")
    # Second pass: parenting and constraints
    for obj_def in data.get('objects', []):
        name = obj_def.get('name')
        parent_name = obj_def.get('parent')
        if parent_name:
            obj = created_objects.get(name)
            parent = created_objects.get(parent_name)
            if obj and parent:
                obj.parent = parent
            else:
                print(f"Warning: cannot parent {name} to {parent_name} (not found)")
    # Optional camera and light creation
    cam_def = data.get('camera')
    if cam_def:
        cam_data = bpy.data.cameras.new(cam_def.get('name', 'Camera'))
        cam = bpy.data.objects.new(cam_def.get('name', 'Camera'), cam_data)
        bpy.context.collection.objects.link(cam)
        if 'location' in cam_def:
            cam.location = Vector(cam_def['location'])
        if 'rotation_euler' in cam_def:
            cam.rotation_euler = Euler(cam_def['rotation_euler'], 'XYZ')
    light_def = data.get('light')
    if light_def:
        light_data = bpy.data.lights.new(light_def.get('name', 'Light'), light_def.get('light_type','POINT'))
        light = bpy.data.objects.new(light_def.get('name','Light'), light_data)
        bpy.context.collection.objects.link(light)
        if 'location' in light_def:
            light.location = Vector(light_def['location'])
    print(f"Finished building scene: {scene_name}")

def prompt_for_json_path():
    try:
        # In Blender, there is a file browser, but for script simplicity ask user to edit variable below or
        # pass command-line parameter. We'll fallback to asking via input() if available.
        path = input('Enter path to scene JSON file: ')
        return path.strip()
    except Exception:
        return None


def main():
    # Accept json path from command line after "--" if using blender --python script.py -- /path/to/file.json
    argv = sys.argv
    if "--" in argv:
        idx = argv.index("--")
        cli_args = argv[idx+1:]
    else:
        cli_args = []
    json_path = None
    if len(cli_args) >= 1:
        json_path = cli_args[0]
    if not json_path:
        # try to prompt
        json_path = "C:/Users/ASUS/OneDrive/Desktop/blender_test/example.json"
    if not json_path:
        raise RuntimeError('No JSON path provided. Pass it after -- on the command-line or input when prompted.')
    json_path = os.path.expanduser(json_path)
    data = load_json(json_path)
    build_scene(data)


if __name__ == '__main__':
    main()


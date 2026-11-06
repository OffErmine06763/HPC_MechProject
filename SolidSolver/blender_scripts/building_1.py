import os
import bpy

# ============================================================
# 1. BUILDING PARAMETERS
# ============================================================

# Overall building dimensions
BUILDING_WIDTH = 20.0
BUILDING_DEPTH = 20.0
N_FLOORS = 16
FLOOR_HEIGHT = 3.0

# Structural dimensions
SLAB_THICKNESS = 0.20
COLUMN_WIDTH = 0.40
COLUMN_DEPTH = 0.40

CORE_WIDTH = 4.0
CORE_DEPTH = 4.0
CORE_WALL_THICKNESS = 0.25

FACADE_THICKNESS = 0.20
FOUNDATION_THICKNESS = 0.50

# Optional components
CREATE_COLUMNS = True
CREATE_CORE = True
CREATE_FACADE = True

# ============================================================
# 2. CLEAN SCENE
# ============================================================

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

for collection in list(bpy.data.collections):
    if collection.name != "Collection":
        bpy.data.collections.remove(collection)

# ============================================================
# 3. SCENE UNITS
# ============================================================

scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = 'METERS'

# ============================================================
# 4. CREATE COLLECTIONS
# ============================================================

def create_collection(name):
    collection = bpy.data.collections.new(name)
    scene.collection.children.link(collection)
    return collection

foundation_col = create_collection("01_Foundation")
slabs_col = create_collection("02_FloorSlabs")
columns_col = create_collection("03_Columns")
core_col = create_collection("04_Core")
facade_col = create_collection("05_Facade")

# ============================================================
# 5. CREATE VIEWPORT MATERIALS
# ============================================================

def create_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    return mat

concrete = create_material(
    "Concrete",
    (0.55, 0.55, 0.58)
)

slab_material = create_material(
    "Floor_Slabs",
    (0.35, 0.55, 0.75)
)

column_material = create_material(
    "Columns",
    (0.85, 0.65, 0.30)
)

core_material = create_material(
    "Shear_Core",
    (0.75, 0.35, 0.30)
)

facade_material = create_material(
    "Facade",
    (0.35, 0.70, 0.55)
)

# ============================================================
# 6. GENERIC CUBE CREATION FUNCTION
# ============================================================

def create_box(name, dimensions, location, collection, material):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)

    obj = bpy.context.object
    obj.name = name

    obj.dimensions = dimensions

    # Apply scale
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Move object to the appropriate collection
    for col in list(obj.users_collection):
        col.objects.unlink(obj)

    collection.objects.link(obj)

    # Assign material
    if material:
        obj.data.materials.append(material)

    return obj

# ============================================================
# 7. FOUNDATION
# ============================================================

create_box(
    "Foundation",
    (
        BUILDING_WIDTH,
        BUILDING_DEPTH,
        FOUNDATION_THICKNESS
    ),
    (
        0.0,
        0.0,
        -FOUNDATION_THICKNESS / 2
    ),
    foundation_col,
    concrete
)

# ============================================================
# 8. FLOOR SLABS
# ============================================================

for i in range(N_FLOORS):

    z = (i + 1) * FLOOR_HEIGHT - SLAB_THICKNESS / 2

    create_box(
        f"Slab_{i+1:02d}",
        (
            BUILDING_WIDTH,
            BUILDING_DEPTH,
            SLAB_THICKNESS
        ),
        (0.0, 0.0, z),
        slabs_col,
        slab_material
    )

# ============================================================
# 9. EXTERNAL COLUMNS
# ============================================================

if CREATE_COLUMNS:

    x_positions = [
        -BUILDING_WIDTH / 2 + COLUMN_WIDTH,
        0.0,
        BUILDING_WIDTH / 2 - COLUMN_WIDTH
    ]

    y_positions = [
        -BUILDING_DEPTH / 2 + COLUMN_DEPTH,
        BUILDING_DEPTH / 2 - COLUMN_DEPTH
    ]

    positions = []

    # Front and back rows
    for y in y_positions:
        for x in x_positions:
            positions.append((x, y))

    # Middle columns on left and right sides
    positions.append((
        -BUILDING_WIDTH / 2 + COLUMN_WIDTH,
        0.0
    ))

    positions.append((
        BUILDING_WIDTH / 2 - COLUMN_WIDTH,
        0.0
    ))

    for i, (x, y) in enumerate(positions):

        create_box(
            f"Column_{i+1:02d}",
            (
                COLUMN_WIDTH,
                COLUMN_DEPTH,
                N_FLOORS * FLOOR_HEIGHT
            ),
            (
                x,
                y,
                N_FLOORS * FLOOR_HEIGHT / 2
            ),
            columns_col,
            column_material
        )

# ============================================================
# 10. CENTRAL SHEAR CORE
# ============================================================

if CREATE_CORE:

    t = CORE_WALL_THICKNESS

    # Front wall
    create_box(
        "Core_Front",
        (CORE_WIDTH, t, N_FLOORS * FLOOR_HEIGHT),
        (0, -CORE_DEPTH / 2 + t / 2,
         N_FLOORS * FLOOR_HEIGHT / 2),
        core_col,
        core_material
    )

    # Back wall
    create_box(
        "Core_Back",
        (CORE_WIDTH, t, N_FLOORS * FLOOR_HEIGHT),
        (0, CORE_DEPTH / 2 - t / 2,
         N_FLOORS * FLOOR_HEIGHT / 2),
        core_col,
        core_material
    )

    # Left wall
    create_box(
        "Core_Left",
        (t, CORE_DEPTH - 2*t, N_FLOORS * FLOOR_HEIGHT),
        (-CORE_WIDTH / 2 + t / 2, 0,
         N_FLOORS * FLOOR_HEIGHT / 2),
        core_col,
        core_material
    )

    # Right wall
    create_box(
        "Core_Right",
        (t, CORE_DEPTH - 2*t, N_FLOORS * FLOOR_HEIGHT),
        (CORE_WIDTH / 2 - t / 2, 0,
         N_FLOORS * FLOOR_HEIGHT / 2),
        core_col,
        core_material
    )

# ============================================================
# 11. EXTERNAL FACADE WALLS
# ============================================================

if CREATE_FACADE:

    t = FACADE_THICKNESS

    # Front facade
    create_box(
        "Facade_Front",
        (BUILDING_WIDTH, t, N_FLOORS * FLOOR_HEIGHT),
        (0, -BUILDING_DEPTH / 2 + t / 2,
         N_FLOORS * FLOOR_HEIGHT / 2),
        facade_col,
        facade_material
    )

    # Back facade
    create_box(
        "Facade_Back",
        (BUILDING_WIDTH, t, N_FLOORS * FLOOR_HEIGHT),
        (0, BUILDING_DEPTH / 2 - t / 2,
         N_FLOORS * FLOOR_HEIGHT / 2),
        facade_col,
        facade_material
    )

    # Left facade
    create_box(
        "Facade_Left",
        (t, BUILDING_DEPTH - 2*t, N_FLOORS * FLOOR_HEIGHT),
        (-BUILDING_WIDTH / 2 + t / 2, 0,
         N_FLOORS * FLOOR_HEIGHT / 2),
        facade_col,
        facade_material
    )

    # Right facade
    create_box(
        "Facade_Right",
        (t, BUILDING_DEPTH - 2*t, N_FLOORS * FLOOR_HEIGHT),
        (BUILDING_WIDTH / 2 - t / 2, 0,
         N_FLOORS * FLOOR_HEIGHT / 2),
        facade_col,
        facade_material
    )

# ============================================================
# 12. FINISH
# ============================================================

# Select all objects
bpy.ops.object.select_all(action='SELECT')

# Set viewport shading to material color
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.color_type = 'MATERIAL'

# Print summary
print("====================================")
print("SKYSCRAPER GENERATED SUCCESSFULLY")
print("====================================")
print(f"Floors: {N_FLOORS}")
print(f"Height: {N_FLOORS * FLOOR_HEIGHT} m")
print(f"Width: {BUILDING_WIDTH} m")
print(f"Depth: {BUILDING_DEPTH} m")
print("====================================")


# --------------------------------------------------
# EXPORT STL FILES
# --------------------------------------------------


def export_collection_stl(collection, export_dir):
    """
    Export all mesh objects in a collection to one STL file.
    Each collection gets its own STL file.
    """

    # Get all mesh objects in the collection
    mesh_objects = [
        obj for obj in collection.objects
        if obj.type == 'MESH'
    ]

    if not mesh_objects:
        print(f"Skipping {collection.name}: no mesh objects")
        return

    # Deselect everything
    bpy.ops.object.select_all(action='DESELECT')

    # Select all mesh objects in this collection
    for obj in mesh_objects:
        obj.select_set(True)

    # Set an active object
    bpy.context.view_layer.objects.active = mesh_objects[0]

    # Create the output filename
    filename = f"{collection.name}.stl"
    filepath = os.path.join(export_dir, filename)

    # Export selected objects as one STL
    bpy.ops.wm.stl_export(
        filepath=filepath,
        export_selected_objects=True,
        global_scale=1.0,
        apply_modifiers=True
    )

    print(f"Exported: {filepath}")


def export_all_collections(export_dir):
    os.makedirs(export_dir, exist_ok=True)

    for collection in bpy.data.collections:
        # Ignore the master scene collection
        if collection == bpy.context.scene.collection:
            continue

        export_collection_stl(collection, export_dir)

    # Deselect everything when finished
    bpy.ops.object.select_all(action='DESELECT')

    print("STL export completed!")
    
    

EXPORT_DIR = bpy.path.abspath("//STL")

export_all_collections(EXPORT_DIR)
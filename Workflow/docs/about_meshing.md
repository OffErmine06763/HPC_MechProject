# Meshing

## Building Internal Geometry

The building internal structure is created in Blender via a python script. Blender outputs stl files for each different type of structural components.

**Usage in Blender**
1. open blender
2. click "scripting" in the menu above
3. create a new file and paste the script

When saving the building model, a directory /STL will be produced alongside the .blend file. It contains one .stl file per structural component type (column, facade, core...)

## Meshing the Geometry

AI explanation:  
`meshing_1.py` builds a three-dimensional quadratic tetrahedral mesh from the STL files in `geometry/meshing_input/`. It uses Trimesh to split disconnected solids within each file, reconstructs every closed shell with the Gmsh API, and writes `geometry/meshes/building.inp` - a CalculiX/Abaqus input mesh with C3D10 elements.
The stl filename becomes the CalculiX element-set name after its numeric prefix is removed. For example, `03_Columns.stl` produces `Columns`.

Every input component must be a closed, watertight STL shell; the script stops with an explicit error if one is open. Components are meshed independently: this intentionally preserves the overlapping building parts produced by the Blender script (for example, columns penetrating slabs). A tied/contact definition is needed in CalculiX if those intersections must transfer load.

### Requirements

Running the meshing requires gmsh (including the shared library it requires) the "meshing" optional dependencies:

    sudo apt install libgmsh-dev
    python -m pip install -e ".[meshing]"

### Execution

    workflow-meshing --geometry-dir <geometry dir>

This will mesh all the stl files under `geometry/for_meshing/<geometry dir>` and output `geometry/meshes/<geometry dir>.inp`

Mesh size can be specified from command line:

    workflow-meshing \
        --min-size 0.20 --max-size 0.75 \
        --geometry-name geo
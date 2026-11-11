# Gmsh Meshing Scripts

`meshing_1.py` builds a three-dimensional quadratic tetrahedral mesh from the
STL files in `geometry/`. It uses Trimesh to split disconnected solids within
each file, reconstructs every closed shell with the Gmsh API, and writes
`output/building.inp` — a CalculiX/Abaqus input mesh with C3D10 elements.

The STL filename becomes the CalculiX element-set name after its numeric
prefix is removed. For example, `03_Columns.stl` produces `Columns`.

## Requirements

Install Gmsh (including the shared library it requires) and the Python
packages in the same Python environment:

```bash
sudo apt install libgmsh-dev
python -m pip install gmsh trimesh networkx
```

On WSL might require a venv 

    python -m venv .venv
    source .venv/bin/activate

To exit

    deactivate

## Run

Run from any directory; paths default to the directories beside the script:

```bash
python src/gmsh_scripts/meshing_1.py
```

Mesh size and input/output paths can be changed without editing the script:

```bash
python src/gmsh_scripts/meshing_1.py \
  --min-size 0.20 --max-size 0.75 \
  --geometry-dir src/gmsh_scripts/geometry \
  --output-dir src/gmsh_scripts/output
```

Every input component must be a closed, watertight STL shell; the script stops
with an explicit error if one is open. Components are meshed independently:
this intentionally preserves the overlapping building parts produced by the
Blender script (for example, columns penetrating slabs). A tied/contact
definition is needed in CalculiX if those intersections must transfer load.

## Building Mesh

Move under `geometry/` the stl files produced by Blender
# Workflow

Code to automate execution of the simulation.

## Project Structure

    Workflow/
    ├── configs/                  # simulation control files
    ├── geometry/
    │   ├── for_fluid/            # building external structure
    │   ├── for_meshing/          # building internal structure
    │   └── meshes/               # meshed internal structure
    ├── runs/                     # output of simulations
    │
    └── src/workflow/             # workflow code
        ├── make_the_work_flow.py # entry-point
        ├── environment.py        # collection of global variables
        ├── pipeline.py           # core of the orchestration
        │
        ├── config/               # config loading and validation
        ├── fluid/
        │   ├── setup.py          # OpenFOAM case preparation
        │   └── runner.py         # OpenFOAM case execution
        ├── coupling/             # extract fluid sim results and convert to solid input
        ├── solid/
        ├── post/                 # postprocessing
        ├── geometry/             # code to generate building geometries
        │
        ├── utils/
        └── scripts/              # additional programs

## Setup

From Workflow directory run the following once

    python -m venv .venv
    source .venv/bin/activate
    python -m pip install -e .
    workflow-setup
    
## Execute

From Workflow directory (with venv activated)

    workflow-run <configuration path>

This will execute a simulation according to the parameters contained in the configuration files under `configs/<configuration path>/`

## Defining a Simulation

To define a simulation run

    workflow-create <configuration path> 

The given path will be the configuration path to use for the workflow execution. This will create a directory under `configs` with the specified name, filled with the `.yaml` files used to specify the parameters of the simulation.

TODO: detailed list of the parameters, default values, accepted values, optionality and so on...

## Inspecting the Output

The results of a simulation are located under `runs/<configuration path>/`. The exact content depends on the configuration options.

To inspect the results (maybe)

    workflow-inspect <configuration path>

## Cleaning the Output

To clean the output of previous runs and restore the project to a clean state use

    workflow-clean [configuration path]

If the configuration path is given, only the outputs associated to that run are erased (the contents of `runs/<configuration path>/`). If no argument is given then all the contents of `runs/` are erased and the simulations are restored to the initial condition.

## Meshes

### Building Internal Geometry

The building internal structure is created in Blender via a python script. Blender outputs stl files for each different type of structural components.

**Usage in Blender**
1. open blender
2. click "scripting" in the menu above
3. create a new file and paste the script

When saving the building model, a directory /STL will be produced alongside the .blend file. It contains one .stl file per structural component type (column, facade, core...)

### Meshing

Move under `geometry/meshing_input/` the stl files produced by Blender. Those are meshed **togheter** using gmsh and converted to a file format accepted by CalculiX.

AI explanation:  
`meshing_1.py` builds a three-dimensional quadratic tetrahedral mesh from the STL files in `geometry/meshing_input/`. It uses Trimesh to split disconnected solids within each file, reconstructs every closed shell with the Gmsh API, and writes `geometry/meshes/building.inp` - a CalculiX/Abaqus input mesh with C3D10 elements.
The stl filename becomes the CalculiX element-set name after its numeric prefix is removed. For example, `03_Columns.stl` produces `Columns`.

Every input component must be a closed, watertight STL shell; the script stops with an explicit error if one is open. Components are meshed independently: this intentionally preserves the overlapping building parts produced by the Blender script (for example, columns penetrating slabs). A tied/contact definition is needed in CalculiX if those intersections must transfer load.

**Requirements**

Running the meshing requires gmsh (including the shared library it requires) the "meshing" optional dependencies:

    sudo apt install libgmsh-dev
    python -m pip install -e ".[meshing]"

**Execution**

    workflow-meshing --geometry-dir <geometry dir>

This will mesh all the stl files under `geometry/for_meshing/<geometry dir>` and output `geometry/meshes/<geometry dir>.inp`

Mesh size can be specified from command line:

    workflow-meshing \
        --min-size 0.20 --max-size 0.75 \
        --geometry-name geo


## For Internal Use Only

Parameters to expose:
- Pre Simulation
    - Wave parameters
    - Domain size and discretization
    - Timestep and final time
- Fluid Simulation
    - Domain size and discretization
    - Timestep and final time
    - Output frequency
    - Building grid configuration (have a standard .stl file and move it where necessary, giving it also different patch names (only in the snappy, not in the stl))
    - Water initial condition (block vs result of pre-simulation vs nothing)
    - Water inlet flow
    - Building surface forces extraction parameters (patches, fields, write frequency)
- Solid Simulation
    - Mesh

Workflow Steps
- Run pre-simulation for water initial condition
    - move initial condition to fluid simulation
- Run fluid simulation
    - apply post-processing to the output timestamps
    - move the fluid-structure interaction files to the solid solver
- Run solid simulation

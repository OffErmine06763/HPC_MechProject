# Workflow

Code to automate execution of the simulation.

## Project Structure

- configs/: files containing all the parameters to run the simulations
- runs/: execution results
- src/fluid/: openfoam preparation, execution and result extraction
- src/coupling/: conversion and transfer from fluid simulation output to solid simulation input
- src/solid/: structural solver preparation, execution and result extraction
- src/post/: postprocessing of all the simulations results
- src/pipeline.py: uses the configuration to run the appropriate simulation
- src/config/: reads the config files
- meshes/: all the versions of the building mesh

## Setup

From Workflow directory

    python -m venv .venv
    source .venv/bin/activate
    python -m pip install -e .
    
## Execute

From Workflow directory (with venv activated)

    python -m workflow.make_the_work_flow <configuration name>

## AAA

The building internal structure is created in Blender via a python script (see [blender_scripts](blender_scripts/)). Blender outputs stl files for each different type of structural components. Those are meshed using gmsh and converted to a file format accepted by CalculiX (see [gmsh_scripts](gmsh_scripts/))

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

# Solid Solver

## Overview

The building internal structure is created in Blender via a python script (see [blender_scripts](blender_scripts/)). Blender outputs stl files for each different type of structural components. Those are meshed using gmsh and converted to a file format accepted by CalculiX (see [gmsh_scripts](gmsh_scripts/))
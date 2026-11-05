# HPSLME Project – Tsunami Simulation

## Execution

First compile the custom function object (see later)

    cd src/buildingLoadExtractor
    wmake libso
    cd ../..

Then run the simulation

    ./Allrun

## Current Simulation Setup

This section summarizes the current configuration of the OpenFOAM simulation, including the computational domain, mesh, boundary conditions, initial water distribution, and building geometry.

### 1. Computational Domain and Mesh

- **Domain** ([`blockMeshDict`](system/blockMeshDict?plain=1#L19-L30)):
  $[0,12] \times [0,2] \times [0,4]$
  where $x$, $y$, and $z$ represent the streamwise, spanwise, and vertical directions, respectively.

- **Mesh discretization** ([`blockMeshDict`](system/blockMeshDict?plain=1#L31-L35)):
  5 cells per unit length in each direction, with further refinement on the water-air interface, which is updated automatically at each simulation timestep.

### 2. Boundary Patches

The computational domain is bounded by the following patches ([`blockMeshDict`](system/blockMeshDict?plain=1#L40-L88)):

| Patch | Type | Location | Description |
|---|---|---|---|
| `inlet` | patch | $x=0$ | Inlet, located near the initial water region |
| `outlet` | patch | $x=12$ | Outlet, opposite to the inlet |
| `sideWalls` | wall | $y=0,2$ | Lateral boundaries, parallel to the flow direction |
| `bottom` | wall | $z=0$ | Bottom of the computational domain |
| `atmosphere` | patch | $z=4$ | Upper boundary, open to the atmosphere |

### 3. Initial Conditions

#### Water Phase

The initial water distribution is defined in [`setFieldsDict`](system/setFieldsDict?plain=1#L25-L34):

- **Initial water region:**
  $[0,4] \times [0,2] \times [0,1]$
  The water occupies the full domain width and is initially located near the inlet.

- **Initial velocity:**
  $\mathbf{U}_0 = (0.5,0,0)\ \mathrm{m/s}$

The initial water velocity is directed along the positive $x$-axis, generating the incoming wave.

### 4. Building Geometry

The building mesh is defined in [building_separated.stl](constant/triSurface): it is a rectangular volume at $[6.5,7.5] \times [0.5,1.5] \times [0,3]$.  
The domain mesh is updated using `snappyHexMesh`, for now simply removing the domain cells.  
The building faces are divided in 6 patches (`building_front`, `building_back`, `building_left`, `building_right`, `building_top`, `building_bottom`), grouped under `building`.  
No refinement is performed by snappy since the simulation already update the mesh refinement at each frame to follow the water-air interface.

### 5. Parallelization

The simulation is configured to run on **4 processors**, as specified in [`decomposeParDict`](system/decomposeParDict?plain=1#L17).

### 6. Boundary Conditions

The following boundary conditions are currently defined:

| Field | Patch / Region | Boundary Condition | Description |
|---|---|---|---|
| `alpha.water` | All boundaries | `zeroGradient` | No prescribed gradient of the water volume fraction at the boundaries |
| `U` | `sideWalls` | `slip` | Allows tangential flow without imposing a no-slip condition |
| `p_rgh` | - | - | See [`0.orig/p_rgh`](0.orig/p_rgh) |

**Note:** The `slip` condition on `sideWalls` is intended to approximate lateral symmetry, since the lateral walls are not physical walls but rather artificial boundaries of the computational domain.

### 7. Data Extraction

Simulation state against the building faces is extracted using OpenFOAM function objects, so that the data extraction can be performed independently from the output of the whole simulation state. See [`controlDict`](system/controlDict?plain=1#L56-L80).

We are using a custom function object (implemented [here](src/buildingLoadExtractor)) that takes a patch and for each mesh quad extracts the following fields: face id, center position, area, pressure and force acting on it.

---

## Notes

- **Water–air interface:** The two phases are distinguished using the volume fraction field `alpha.water`:
  - `alpha.water = 1`: pure water.
  - `alpha.water = 0`: pure air.
  - `0 < alpha.water < 1`: cells containing the interface between the two phases.

- **Initial field assignment:** `setFields` is an OpenFOAM utility used to initialize the simulation fields according to the regions and values specified in `setFieldsDict`.

- **Building representation:** The building is currently modeled as a fixed obstacle. No structural deformation or fluid–structure interaction (FSI) is currently considered.

## TODO

- [ ] Investigate replacing `slip` with `symmetry` for the `sideWalls` patch and update the corresponding boundary conditions in the initial field files.
- [ ] Tweak snappy to better model the edges of the building
# HPSLME Project – Tsunami Simulation

## Current Simulation Setup

This section summarizes the current configuration of the OpenFOAM simulation, including the computational domain, mesh, boundary conditions, initial water distribution, and building geometry.

### 1. Computational Domain and Mesh

- **Domain** ([`blockMeshDict`](system/blockMeshDict?plain=1#L19-L30)):
  $
  [0,12] \times [0,2] \times [0,4]
  $
  where $x$, $y$, and $z$ represent the streamwise, spanwise, and vertical directions, respectively.

- **Mesh discretization** ([`blockMeshDict`](system/blockMeshDict?plain=1#L31-L35)):
  5 cells per unit length in each direction, resulting in a mesh of:
  $
  60 \times 10 \times 20 = 12\,000 \text{ cells}
  $

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
  $
  [0,4] \times [0,2] \times [0,1]
  $
  The water occupies the full domain width and is initially located near the inlet.

- **Initial velocity:**
  $
  \mathbf{U}_0 = (5,0,0)\ \mathrm{m/s}
  $

The initial water velocity is directed along the positive $x$-axis, generating the incoming wave.

#### Building Geometry

The building is introduced by modifying the computational mesh:

1. [`topoSetDict`](system/topoSetDict?plain=1#L17-L37) defines a cell selection corresponding to the volume:
   $
   [6.5,7.5] \times [0.5,1.5] \times [0,3]
   $

2. [`Allrun`](Allrun#L10-L13) removes the selected cells from the mesh using `subsetMesh`.

This creates an obstacle representing a building positioned downstream of the initial water region.

### 4. Parallelization

The simulation is configured to run on **8 processors**, as specified in [`decomposeParDict`](system/decomposeParDict?plain=1#L17).

### 5. Boundary Conditions

The following boundary conditions are currently defined:

| Field | Patch / Region | Boundary Condition | Description |
|---|---|---|---|
| `alpha.water` | All boundaries | `zeroGradient` | No prescribed gradient of the water volume fraction at the boundaries |
| `U` | `sideWalls` | `slip` | Allows tangential flow without imposing a no-slip condition |
| `p_rgh` | - | - | See [`0.orig/p_rgh`](0.orig/p_rgh) |

**Note:** The `slip` condition on `sideWalls` is intended to approximate lateral symmetry, since the lateral walls are not physical walls but rather artificial boundaries of the computational domain.

---

## Notes

- **Water–air interface:** The two phases are distinguished using the volume fraction field `alpha.water`:
  - `alpha.water = 1`: pure water.
  - `alpha.water = 0`: pure air.
  - `0 < alpha.water < 1`: cells containing the interface between the two phases.

- **Initial field assignment:** `setFields` is an OpenFOAM utility used to initialize the simulation fields according to the regions and values specified in `setFieldsDict`.

- **Building representation:** The building is currently modeled as an obstacle by removing the corresponding cells from the fluid mesh. No structural deformation or fluid–structure interaction (FSI) is currently considered. Also the removal isn't working properly

## TODO

- [ ] Investigate replacing `slip` with `symmetry` for the `sideWalls` patch and update the corresponding boundary conditions in the initial field files.
- [ ] Fix the building geometry and verify that `topoSet` and `subsetMesh` generate the intended obstacle.
# HPSLME Project - Tsunami

## Current state of the simulation

Here follows the relevant information about the current state of the simulation

[Domain](system/blockMeshDict?plain=1#L19-L30): $[0, 12] \times [0, 2] \times [0, 4]$  
[Discretization](system/blockMeshDict?plain=1#L31-L35): 5 splits per unit in each direction ($60 \times 10 \times 20$)  
[Domain Boundary](system/blockMeshDict?plain=1#L40-L88): the walls are divided in

- inlet (patch) $x = 0$: near the water initial position
- outlet (patch) $x = 12$: opposite of inlet
- sideWalls (wall) $y = 0,2$: parallel to the water motion
- bottom (wall) $z = 0$
- atmosphere (patch) $z = 4$

[Parallelization](system/decomposeParDict?plain=1#L17): 8 processors  
[Water](system/setFieldsDict?plain=1#L25-L34): starts from the box $[0, 4] \times [0, 2] \times [0, 1]$ (near the inlet, full domain width), with initial velocity of $5 \, ms^{-1}$  
Building: [first](system/topoSetDict?plain=1#L17-L37) define the volume $[6.5, 7.5] \times [0.5, 1.5] \times [0, 3]$ from the domain, [then](Allrun#L10-L13) remove them from the mesh  
Boundary Conditions:

- [water](0.orig/alpha.water?plain=1#L23-L27): avoid water from crossing any boundary (`zeroGradient`)
- [pressure](0.orig/p_rgh): idk
- [velocity](0.orig/U?plain=1#L36-L40): `slip` condition on the side walls, cause they aren't actually there

---

### Notes

The distinction between water and air is given by the value of `alpha.water` (0 for air and 1 for water)

`setFields` is the OpenFOAM program that sets an initial value to the simulation

TODO: try type `symmetry` for `sideWall` and associated boundary conditions

TODO: the building is f***ed up

#!/usr/bin/env python3
"""Mesh Blender STL component files as C3D10 elements for CalculiX.

Each STL in ``geometry/`` represents one building-component type.  The files
can contain several disconnected closed shells; Trimesh splits those shells
and Gmsh reconstructs and meshes each as a separate 3-D volume.  The meshes
are assembled into one CalculiX ``.inp`` file with one element set per STL.
"""

from __future__ import annotations

import argparse
import math
import sys
import tempfile
from collections.abc import Iterable
from pathlib import Path

import gmsh
import trimesh


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_GEOMETRY_DIR = SCRIPT_DIR / "geometry"
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "output"
GMSH_C3D10 = 11  # Gmsh's complete 10-node second-order tetrahedron


def component_type(stl_path: Path) -> str:
    """Create a CalculiX-safe element-set name from a Blender STL file name."""
    stem = stl_path.stem
    if len(stem) > 3 and stem[:2].isdigit() and stem[2] == "_":
        stem = stem[3:]
    return stem.replace(" ", "_")


def load_components(stl_path: Path, minimum_volume: float) -> list[trimesh.Trimesh]:
    """Split an STL and return its usable, watertight solid components."""
    loaded = trimesh.load(stl_path, force="mesh", process=True)
    if not isinstance(loaded, trimesh.Trimesh) or loaded.is_empty:
        raise ValueError(f"{stl_path} did not contain a triangular mesh")

    components = loaded.split(only_watertight=False)
    accepted: list[trimesh.Trimesh] = []
    print(f"{stl_path.name}: {len(components)} disconnected component(s)")
    for index, mesh in enumerate(components, start=1):
        mesh.remove_unreferenced_vertices()
        mesh.merge_vertices()
        if mesh.is_empty or len(mesh.faces) == 0:
            print(f"  component {index}: skipped (no faces)")
            continue
        if not mesh.is_watertight:
            raise ValueError(
                f"{stl_path.name}, component {index} is not watertight; "
                "a closed shell is required to create a 3-D volume"
            )

        # Correct a valid but inward-oriented shell before sending it to Gmsh.
        mesh.fix_normals(multibody=False)
        volume = abs(mesh.volume)
        if volume < minimum_volume:
            print(
                f"  component {index}: skipped "
                f"(volume {volume:.6g} below threshold {minimum_volume:.6g})"
            )
            continue
        print(f"  component {index}: {len(mesh.faces)} faces, {volume:.6g} m^3")
        accepted.append(mesh)
    return accepted


def configure_gmsh(minimum_size: float, maximum_size: float) -> None:
    """Set options required for complete quadratic tetrahedral meshing."""
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.option.setNumber("Mesh.ElementOrder", 2)
    gmsh.option.setNumber("Mesh.SecondOrderIncomplete", 0)  # C3D10, not C3D10M
    gmsh.option.setNumber("Mesh.MeshSizeMin", minimum_size)
    gmsh.option.setNumber("Mesh.MeshSizeMax", maximum_size)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.Algorithm3D", 1)  # Delaunay tetrahedralization


def write_temp_stl(mesh: trimesh.Trimesh, output_path: Path) -> None:
    """Write ASCII STL, avoiding Gmsh binary-STL parsing edge cases."""
    output_path.write_text(
        trimesh.exchange.stl.export_stl_ascii(mesh), encoding="ascii", newline="\n"
    )


def mesh_component(
    stl_path: Path,
    minimum_size: float,
    maximum_size: float,
    classification_angle: float,
) -> tuple[list[tuple[float, float, float]], list[tuple[int, ...]]]:
    """Reconstruct, volume-mesh, and return one shell's C3D10 mesh.

    Gmsh is deliberately cleared between components.  The Blender building
    parts overlap (e.g. columns penetrate slabs), and importing those separate
    closed meshes into one Gmsh model can make its discrete-surface importer
    reject later STL files.  Meshing every disconnected solid independently
    preserves the input components and produces a valid CalculiX assembly.
    """
    gmsh.clear()
    gmsh.model.add("stl_component")
    configure_gmsh(minimum_size, maximum_size)
    gmsh.merge(str(stl_path))

    imported_surfaces = {tag for _, tag in gmsh.model.getEntities(2)}
    gmsh.model.mesh.classifySurfaces(
        classification_angle,
        boundary=True,
        forReparametrization=True,
        curveAngle=math.pi,
    )
    gmsh.model.mesh.createGeometry()
    surfaces = sorted(
        tag for _, tag in gmsh.model.getEntities(2) if tag not in imported_surfaces
    )
    if not surfaces:
        raise RuntimeError(f"Gmsh did not reconstruct surfaces for {stl_path.name}")

    surface_loop = gmsh.model.geo.addSurfaceLoop(surfaces)
    volume = gmsh.model.geo.addVolume([surface_loop])
    gmsh.model.geo.synchronize()
    gmsh.model.mesh.generate(3)
    # Netgen optimization operates on the linear tetrahedral mesh. Elevate it
    # afterwards, otherwise it may leave only first-order Tetrahedron 4 cells.
    gmsh.model.mesh.optimize("Netgen")
    gmsh.model.mesh.setOrder(2)

    element_types, _, connectivities = gmsh.model.mesh.getElements(3, volume)
    if element_types != [GMSH_C3D10]:
        names = ", ".join(gmsh.model.mesh.getElementProperties(kind)[0] for kind in element_types)
        raise RuntimeError(f"{stl_path.name} did not produce only C3D10 elements: {names}")

    node_tags, coordinates, _ = gmsh.model.mesh.getNodes()
    node_coordinates = {
        tag: (coordinates[3 * index], coordinates[3 * index + 1], coordinates[3 * index + 2])
        for index, tag in enumerate(node_tags)
    }
    connectivity = connectivities[0]
    if len(connectivity) % 10:
        raise RuntimeError(f"unexpected C3D10 connectivity from {stl_path.name}")
    used_tags = sorted(set(connectivity))
    nodes = [node_coordinates[tag] for tag in used_tags]
    local_tags = {tag: index + 1 for index, tag in enumerate(used_tags)}
    elements = [
        tuple(local_tags[tag] for tag in connectivity[index : index + 10])
        for index in range(0, len(connectivity), 10)
    ]
    return nodes, elements


def write_calculix_inp(
    output_path: Path,
    groups: Iterable[tuple[str, list[tuple[float, float, float]], list[tuple[int, ...]]]],
) -> tuple[int, int]:
    """Write mesh groups as one CalculiX deck and return node/element totals."""
    node_id = 1
    element_id = 1
    node_count = 0
    element_count = 0
    with output_path.open("w", encoding="ascii", newline="\n") as inp:
        inp.write("** Generated by src/gmsh_scripts/meshing_1.py\n")
        inp.write("*NODE\n")
        for _, nodes, _ in groups:
            for x, y, z in nodes:
                inp.write(f"{node_id}, {x:.16g}, {y:.16g}, {z:.16g}\n")
                node_id += 1
                node_count += 1

        node_offset = 0
        for name, nodes, elements in groups:
            inp.write(f"*ELEMENT, TYPE=C3D10, ELSET={name}\n")
            for element in elements:
                connectivity = ", ".join(str(node_offset + local_id) for local_id in element)
                inp.write(f"{element_id}, {connectivity}\n")
                element_id += 1
                element_count += 1
            node_offset += len(nodes)
    return node_count, element_count


def write_gmsh_msh(
    output_path: Path,
    groups: Iterable[tuple[str, list[tuple[float, float, float]], list[tuple[int, ...]]]],
) -> tuple[int, int]:
    """Write the assembled C3D10 mesh in Gmsh MSH 2.2 ASCII format.

    Each input group becomes a 3-D physical group, preserving the STL
    component-type names used for the CalculiX element sets.
    """
    groups = list(groups)
    node_id = 1
    element_id = 1
    node_count = sum(len(nodes) for _, nodes, _ in groups)
    element_count = sum(len(elements) for _, _, elements in groups)

    with output_path.open("w", encoding="ascii", newline="\n") as msh:
        msh.write("$MeshFormat\n2.2 0 8\n$EndMeshFormat\n")

        # Physical groups let Gmsh retain the original STL/component names.
        msh.write(f"$PhysicalNames\n{len(groups)}\n")
        for physical_tag, (name, _, _) in enumerate(groups, start=1):
            safe_name = name.replace('"', '\\\"')
            msh.write(f'3 {physical_tag} "{safe_name}"\n')
        msh.write("$EndPhysicalNames\n")

        msh.write(f"$Nodes\n{node_count}\n")
        for _, nodes, _ in groups:
            for x, y, z in nodes:
                msh.write(f"{node_id} {x:.16g} {y:.16g} {z:.16g}\n")
                node_id += 1
        msh.write("$EndNodes\n")

        msh.write(f"$Elements\n{element_count}\n")
        node_offset = 0
        for physical_tag, (_, nodes, elements) in enumerate(groups, start=1):
            for element in elements:
                # Gmsh element type 11 is a 10-node second-order tetrahedron.
                connectivity = " ".join(
                    str(node_offset + local_id) for local_id in element
                )
                # Two tags: physical group and geometrical entity.
                msh.write(
                    f"{element_id} 11 2 {physical_tag} {physical_tag} "
                    f"{connectivity}\n"
                )
                element_id += 1
            node_offset += len(nodes)
        msh.write("$EndElements\n")

    return node_count, element_count


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--geometry-dir", type=Path, default=DEFAULT_GEOMETRY_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--min-size", type=float, default=0.20, help="minimum mesh size in m")
    parser.add_argument("--max-size", type=float, default=2.00, help="maximum mesh size in m")
    parser.add_argument(
        "--classification-angle", type=float, default=40.0,
        help="surface classification angle in degrees (default: 40)",
    )
    parser.add_argument(
        "--minimum-volume", type=float, default=1e-8,
        help="ignore closed components smaller than this volume in m^3",
    )
    args = parser.parse_args()
    if args.min_size <= 0 or args.max_size <= 0 or args.min_size > args.max_size:
        parser.error("mesh sizes must be positive and --min-size must not exceed --max-size")
    if args.minimum_volume < 0:
        parser.error("--minimum-volume must be non-negative")
    return args


def main() -> int:
    args = parse_arguments()
    geometry_dir = args.geometry_dir.resolve()
    output_dir = args.output_dir.resolve()
    stl_files = sorted(geometry_dir.glob("*.stl"))
    if not stl_files:
        print(f"No STL files found in {geometry_dir}", file=sys.stderr)
        return 2

    output_dir.mkdir(parents=True, exist_ok=True)
    mesh_groups: list[tuple[str, list[tuple[float, float, float]], list[tuple[int, ...]]]] = []
    gmsh.initialize()
    try:
        with tempfile.TemporaryDirectory(prefix="building_stl_") as directory:
            temporary_directory = Path(directory)
            component_index = 0
            for stl_file in stl_files:
                group_name = component_type(stl_file)
                group_nodes: list[tuple[float, float, float]] = []
                group_elements: list[tuple[int, ...]] = []
                for component in load_components(stl_file, args.minimum_volume):
                    component_index += 1
                    component_path = temporary_directory / f"component_{component_index:05d}.stl"
                    write_temp_stl(component, component_path)
                    nodes, elements = mesh_component(
                        component_path,
                        args.min_size,
                        args.max_size,
                        math.radians(args.classification_angle),
                    )
                    offset = len(group_nodes)
                    group_nodes.extend(nodes)
                    group_elements.extend(
                        tuple(offset + local_id for local_id in element) for element in elements
                    )

                if group_elements:
                    mesh_groups.append((group_name, group_nodes, group_elements))
                    print(f"  -> {group_name}: {len(group_elements)} C3D10 element(s)")

        if not mesh_groups:
            raise RuntimeError("no valid closed solids were created from the STL files")
        inp_path = output_dir / "building.inp"
        nodes, elements = write_calculix_inp(inp_path, mesh_groups)
        print(f"Wrote {nodes} nodes and {elements} C3D10 elements to {inp_path}")

        msh_path = output_dir / "building.msh"
        msh_nodes, msh_elements = write_gmsh_msh(msh_path, mesh_groups)
        print(
            f"Wrote {msh_nodes} nodes and {msh_elements} C3D10 elements "
            f"to {msh_path}"
        )
        return 0
    finally:
        gmsh.finalize()


if __name__ == "__main__":
    raise SystemExit(main())

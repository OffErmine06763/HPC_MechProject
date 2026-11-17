import argparse

from workflow.geometry.mesher import *
from workflow.environment import environment


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--geometry-dir", type=Path)
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
    environment.initialize()
    args = parse_arguments()

    geometry_dir = environment.workflow_dir / "geometry/for_meshing" / args.geometry_dir
    output_dir = environment.workflow_dir / "geometry/meshes" / args.geometry_dir.parent
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
        
        inp_path = output_dir / f"{geometry_dir.name}.inp"
        nodes, elements = write_calculix_inp(inp_path, mesh_groups)
        print(f"Wrote {nodes} nodes and {elements} C3D10 elements to {inp_path}")

        msh_path = output_dir / f"{geometry_dir.name}.msh"
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

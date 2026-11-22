"""Clears the runs directory and restores the simulation to the initial state"""

import argparse
from pathlib import Path

from workflow.environment import environment
from workflow.fluid.runner import clean_fluid_simulation
from workflow.utils.utils import delete_dir_content, delete_path


def parse_arguments():
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description="Clean script")

    parser.add_argument(
        "simulation",
        type=Path,
        nargs="?",
        default=environment.workflow_dir / "runs",
        help="Simulation to clean."
    )

    return parser.parse_args()


def main():
    environment.initialize()
    args = parse_arguments()

    runs_dir = environment.workflow_dir / "runs"

    if str(args.simulation) == str(runs_dir):
        # clean all runs and simulations
        delete_dir_content(runs_dir)
        clean_fluid_simulation()
    else:
        # clean only one run
        dir = runs_dir / args.simulation
        delete_path(dir)

"""Clears the runs directory and restores the simulation to the initial state"""

import argparse
import shutil
from pathlib import Path

from workflow.environment import environment
from workflow.fluid.runner import clean_fluid_simulation


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
        if runs_dir.exists() and runs_dir.is_dir():
            for item in runs_dir.iterdir():
                if item.is_dir() and not item.is_symlink():
                    shutil.rmtree(item)
                else:
                    item.unlink()

        clean_fluid_simulation()
    else:
        # clean only one run
        dir = runs_dir / args.simulation
        if dir.exists() and dir.is_dir():
            shutil.rmtree(dir)

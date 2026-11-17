import os
from pathlib import Path


class Environment:
    """
    Collection of variables for use across the whole codebase.
    Mostly for paths, so that we have to validate them only once.
    """

    base_dir: Path
    workflow_dir: Path
    solid_dir: Path
    fluid_dir: Path
    output_dir: Path

    def initialize(self):
        self.workflow_dir = Path(os.getcwd())
        if self.workflow_dir.name != "Workflow":
            print("Run this script from the Workflow directory")
            exit(1)

        self.base_dir = self.workflow_dir.parent
        self.solid_dir = self.base_dir / "SolidSolver"
        self.fluid_dir = self.base_dir / "FluidSolver"

        if not self.solid_dir.is_dir():
            print("Cannot find SolidSolver directory")
            exit(1)
        if not self.fluid_dir.is_dir():
            print("Cannot find FluidSolver directory")
            exit(1)

environment = Environment()
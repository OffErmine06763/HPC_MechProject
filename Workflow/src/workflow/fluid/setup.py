"""Code to modify openfoam dictionaries according to the configuration files and prepare the case for execution."""

import logging
import subprocess
import shutil
from pathlib import Path

from workflow.config.config import ExecutionConfig, FluidConfig
from workflow.utils.commands import get_write_dictionary_command, run_command



def _fluid_case_directory() -> Path:
    """Return the repository's OpenFOAM fluid case directory."""
    # TODO: improve ts
    return Path(__file__).resolve().parents[4] / "FluidSolver"


def _write_dictionaries(fluid_config: FluidConfig, execution_config: ExecutionConfig):
    case_directory = _fluid_case_directory()
    if not case_directory.is_dir():
        raise FileNotFoundError(f"FluidSolver case directory does not exist: {case_directory}")

    command = get_write_dictionary_command("numberOfSubdomains", str(execution_config.effective_processors), "system/decomposeParDict")
    return_code = run_command(command, working_directory=case_directory)
    if return_code != 0:
        logger = logging.getLogger(__name__)
        logger.error("Command failed with exit code %d", return_code)
        raise subprocess.CalledProcessError(return_code, command)


def _move_files(fluid_config: FluidConfig, execution_config: ExecutionConfig):
    src = Path("meshes/building_separated.stl")
    dst = Path("../FluidSolver/constant/triSurface/building_separated.stl")
    shutil.copy(src, dst)


def _restore_initial_conditions() -> None:
    source = Path("../FluidSolver") / "0.orig"
    destination = Path("../FluidSolver") / "0"
    if not source.is_dir():
        raise FileNotFoundError(f"Initial-condition directory does not exist: {source}")

    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)
    

def prepare_case(fluid_config: FluidConfig, execution_config: ExecutionConfig):
    logger = logging.getLogger(__name__)

    _write_dictionaries(fluid_config, execution_config)
    _move_files(fluid_config, execution_config)
    _restore_initial_conditions()

    logger.info("OpenFOAM case ready")
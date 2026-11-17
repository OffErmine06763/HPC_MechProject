"""Code to modify openfoam dictionaries according to the configuration files and prepare the case for execution."""

import logging
import subprocess
from pathlib import Path

from workflow.config.config import ExecutionConfig, FluidConfig
from workflow.utils.commands import get_write_dictionary_command, run_command



def _fluid_case_directory() -> Path:
    """Return the repository's OpenFOAM fluid case directory."""
    # TODO: improve ts
    return Path(__file__).resolve().parents[4] / "FluidSolver"


def prepare_case(fluid_config: FluidConfig, execution_config: ExecutionConfig):
    logger = logging.getLogger(__name__)

    case_directory = _fluid_case_directory()
    if not case_directory.is_dir():
        raise FileNotFoundError(f"FluidSolver case directory does not exist: {case_directory}")

    command = get_write_dictionary_command("numberOfSubdomains", str(execution_config.effective_processors), "system/decomposeParDict")
    return_code = run_command(command, working_directory=case_directory)
    if return_code != 0:
        logger.error("Command failed with exit code %d", return_code)
        raise subprocess.CalledProcessError(return_code, command)

    logger.info("OpenFOAM case ready")
"""Code to modify OpenFOAM dictionaries according to the configuration files and prepare the case for execution."""

import logging
import subprocess
import shutil
import os
from pathlib import Path

from workflow.config.config import ExecutionConfig, FluidConfig
from workflow.utils.commands import get_write_dictionary_command, run_command
from workflow.environment import environment



def _write_dictionaries(fluid_config: FluidConfig, execution_config: ExecutionConfig):
    case_directory = environment.fluid_dir
    command = get_write_dictionary_command("numberOfSubdomains", str(execution_config.effective_processors), "system/decomposeParDict")
    return_code = run_command(command, working_directory=case_directory)
    if return_code != 0:
        logger = logging.getLogger(__name__)
        logger.error("Command failed with exit code %d", return_code)
        raise subprocess.CalledProcessError(return_code, command)


def _move_files(fluid_config: FluidConfig, execution_config: ExecutionConfig):
    src = environment.workflow_dir / "geometry/for_fluid/building_separated.stl"
    dst = environment.fluid_dir / "constant/triSurface/building_separated.stl"
    shutil.copy(src, dst)


def _restore_initial_conditions() -> None:
    source = environment.fluid_dir / "0.orig"
    destination = environment.fluid_dir / "0"
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
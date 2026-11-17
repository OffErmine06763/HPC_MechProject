"""Code to run an OpenFOAM simulation, almost equivalent to the Allrun script"""

import logging
import shutil
import subprocess
import re
from pathlib import Path

from workflow.config.config import ExecutionConfig
from workflow.utils.commands import get_read_dictionary_command, run_command



def _get_application(case_directory: Path, output_directory: Path) -> str:
    application_log = output_directory / "log.getApplication"
    _run_command(
        get_read_dictionary_command("application", "system/controlDict"),
        case_directory,
        application_log,
    )
    application = application_log.read_text(encoding="utf-8").strip()
    if not application:
        raise RuntimeError("OpenFOAM controlDict does not define an application")
    return application


def _run_simulation(config: ExecutionConfig, case_directory: Path, log_directory: Path):
    logger = logging.getLogger(__name__)
    application = _get_application(case_directory, log_directory)
    
    commands: list[tuple[str, str]] = [
        ("blockMesh"    , "blockMesh"),
        ("snappyHexMesh", "snappyHexMesh -overwrite"),
        ("setFields"    , "setFields"),
    ]
    if config.parallelization == "serial":
        commands.append((application, application))
    else:
        processors = config.effective_processors
        commands.extend(
            [
                ("decomposePar"      ,  "decomposePar"),
                ( application        , f"mpirun -np {processors} {application} -parallel"),
                ("reconstructParMesh",  "reconstructParMesh -constant"),
                ("reconstructPar"    ,  "reconstructPar"),
            ]
        )

    for command_name, command in commands:
        logger.info("Running %s (log: %s)", command_name, f"log.{command_name}")
        _run_command(command, case_directory, log_directory / f"log.{command_name}")


def _move_results(output_directory: Path):
    """Moves the simulation outputs to the runs directory"""

    states_src_dir = Path("../FluidSolver")
    states_dst_dir = output_directory / "state"
    states_dst_dir.mkdir(parents=True, exist_ok=True)

    pattern = re.compile(r"^\d+(?:\.\d+)?$")

    for path in states_src_dir.iterdir():
        if path.is_dir() and pattern.fullmatch(path.name):
            shutil.move(str(path), str(states_dst_dir / path.name))

    postproc_src_dir = Path("../FluidSolver/postProcessing")
    postproc_dst_dir = output_directory / "post_processing"
    postproc_dst_dir.mkdir(parents=True, exist_ok=True)

    for path in postproc_src_dir.iterdir():
        shutil.move(str(path), str(postproc_dst_dir / path.name))


def run_fluid_simulation(config: ExecutionConfig, output_directory: Path):
    """
    Runs all the steps of the fluid simulation.
    Outputs are redirected to log files in the output directory.

    Raises:
        FileNotFoundError: missing solver case or initial condition
        RuntimeError: invalid data in the dictionaries prevents starting the simulation
        CalledProcessError: non-zero exit code for any of the OpenFOAM commands
    """

    logger = logging.getLogger(__name__)
    case_directory = _fluid_case_directory()
    if not case_directory.is_dir():
        raise FileNotFoundError(f"FluidSolver case directory does not exist: {case_directory}")
    fluid_output_directory = output_directory / Path("fluid")
    fluid_output_directory.mkdir(parents=True, exist_ok=True)
    log_directory = output_directory / Path("fluid/logs")
    log_directory.mkdir(parents=True, exist_ok=True)

    _run_simulation(config, case_directory, log_directory)
    _move_results(fluid_output_directory)

    logger.info("Fluid simulation completed successfully")




def clean_fluid_simulation():
    """Performs the equivalent of Allclean and remove other files managed by the workflow"""
    # TODO: the fluid solver directory and Allclean path should be obtained in a better way

    command = "../FluidSolver/Allclean"
    return_code = run_command(command)
    if return_code != 0:
        logger = logging.getLogger(__name__)
        logger.error("Command failed with exit code %d", return_code)
        raise subprocess.CalledProcessError(return_code, command)

    # also remove the building geometry, since another simulation might use a different one
    directory = Path("../FluidSolver/constant/triSurface")
    for item in directory.iterdir():
        if item.is_dir() and not item.is_symlink():
            shutil.rmtree(item)
        else:
            item.unlink()



def _fluid_case_directory() -> Path:
    """Return the repository's OpenFOAM fluid case directory."""
    # TODO: improve ts
    return Path(__file__).resolve().parents[4] / "FluidSolver"


def _run_command(command: str, case_directory: Path, log_file: Path) -> None:
    """Run an OpenFOAM command and raise when it returns a non-zero status."""

    return_code = run_command(command, log_file, working_directory=case_directory)
    if return_code != 0:
        logger = logging.getLogger(__name__)
        logger.error("Command failed with exit code %d; see %s", return_code, log_file)
        raise subprocess.CalledProcessError(return_code, command)

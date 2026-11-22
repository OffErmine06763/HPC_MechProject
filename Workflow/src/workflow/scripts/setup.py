"""Initial setup of the project"""

import logging
from pathlib import Path

from workflow.environment import environment
from workflow.utils.commands import run_command
from workflow.utils.utils import setup_logging


def main():
    environment.initialize()
    log = Path("logs/setup")

    setup_logging(True)
    logger = logging.getLogger(__name__)

    # setup fluid sim
    command = environment.fluid_dir / "Allsetup"
    command = str(command)
    return_code = run_command(command, redirect=log, redirect_mode="append")
    if return_code != 0:
        logger.error(f"Fluid sim setup failed with exit code {return_code}, see {log}")
        exit(1)
    logger.info("Fluid simulation initialized!")

    logger.info("Setup completed!")

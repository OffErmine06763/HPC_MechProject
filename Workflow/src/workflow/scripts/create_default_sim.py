"""Creates a default simulation configuration with the mandatory parameters set to default values"""

import argparse
from pathlib import Path

from workflow.environment import environment
from workflow.utils.utils import delete_path
from workflow.config.config_creator import create_default_config


def parse_arguments():
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description="Crate config script")

    parser.add_argument("simulation", type=Path, help="Name of the simulation to create.")

    return parser.parse_args()


def main():
    environment.initialize()
    args = parse_arguments()

    configs_dir = environment.workflow_dir / "configs"
    new_config = configs_dir / args.simulation

    if new_config.exists():
        delete_path(new_config)

    create_default_config(new_config)



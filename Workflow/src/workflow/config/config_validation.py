"""Validate configuration files"""

import math
from typing import Any

from workflow.config.config_error import ConfigurationError
from workflow.config.config import ExecutionConfig, SolidConfig, FluidConfig


def validate_execution_config(config: ExecutionConfig) -> None:
    """
    Validate the execution settings.
    
    Raises:
        ConfigurationError: If the parameters are invalid.
    """

    # TODO: check that the bumber of processors is <= than the available processors
    if config.parallelization == "manual":
        if config.number_of_processors is None:
            raise ValueError("number_of_processors must be specified for manual parallelization")
    elif config.number_of_processors is not None:
        raise ValueError("number_of_processors can only be specified for manual parallelization")


def validate_fluid_config(config: FluidConfig) -> None:
    """
    Validate the fluid simulation settings.

    Raises:
        ConfigurationError: If the parameters are invalid.
    """


def validate_solid_config(config: SolidConfig) -> None:
    """
    Validate the solid simulation settings.

    Raises:
        ConfigurationError: If the parameters are invalid.
    """

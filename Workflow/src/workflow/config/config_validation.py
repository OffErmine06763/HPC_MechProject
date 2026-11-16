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
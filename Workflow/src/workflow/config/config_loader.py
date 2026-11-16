"""Loading workflow configuration files."""

from pathlib import Path
from typing import Any, Mapping
import yaml
from pydantic import ValidationError

from workflow.config.config_error import ConfigurationError
from workflow.config.config import WorkflowConfig

_CONFIG_FILES = ("sim.yaml", "fluid.yaml", "solid.yaml")


def _read_yaml(path: Path) -> dict[str, Any]:
    """Read a YAML mapping."""

    try:
        with path.open("r", encoding="utf-8") as config_file:
            data = yaml.safe_load(config_file)
    except OSError as error:
        raise ConfigurationError(f"Could not read configuration file '{path}': {error}") from error
    except yaml.YAMLError as error:
        raise ConfigurationError(f"Invalid YAML in configuration file '{path}': {error}") from error

    if data is None:
        return {}
    if not isinstance(data, Mapping):
        raise ConfigurationError(f"Configuration file '{path}' must contain a YAML mapping.")
    return dict(data)



def load_config(simulation_name: str | Path) -> WorkflowConfig:
    """
    Load and validate the configuration files under `configs/<simulation_name>`.

    Raises:
        ConfigurationError: If a required files are missing, YAML is malformed, or the parameters are invalid.
    """

    directory = (Path("configs") / Path(simulation_name)).expanduser()

    if not directory.exists():
        raise ConfigurationError(f"Configuration directory does not exist: '{directory}'.")
    if not directory.is_dir():
        raise ConfigurationError(f"Configuration path is not a directory: '{directory}'.")

    paths = {filename: directory / filename for filename in _CONFIG_FILES}
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise ConfigurationError("Missing required configuration file(s): " + ", ".join(missing))

    config = {
        "sim"  : _read_yaml(paths["sim.yaml"  ]),
        "fluid": _read_yaml(paths["fluid.yaml"]),
        "solid": _read_yaml(paths["solid.yaml"]),
    }
    try:
        config = WorkflowConfig.model_validate(config)
    except ValidationError as e:
        errors = e.errors()

        formatted_errors = "\n".join(
            f"  - Field: {'.'.join(str(loc) for loc in error['loc'])}\n"
            f"    Error: {error['msg']}"
            for error in errors
        )

        raise ConfigurationError(f"Configuration files did NOT pass validation:\n{formatted_errors}") from e

    return config

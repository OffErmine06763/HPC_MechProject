"""Creates the default yaml for defining simulation configuration"""

from __future__ import annotations

import types
from collections.abc import Mapping, Sequence
from enum import Enum
from pathlib import Path
from typing import Any, Literal, Union, get_args, get_origin, get_type_hints

import yaml
from pydantic import BaseModel

from workflow.config.config import SimulationConfig, FluidConfig, SolidConfig



def _normalize_value(value: Any) -> Any:
    """Convert Python values into YAML-compatible values."""

    if isinstance(value, BaseModel):
        return _normalize_value(value.model_dump(mode="python"))

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, dict):
        return {
            _normalize_value(k): _normalize_value(v)
            for k, v in value.items()
        }

    if isinstance(value, (list, tuple, set, frozenset)):
        return [_normalize_value(v) for v in value]

    return value


def _placeholder_for_type(
    annotation: Any,
    model_stack: frozenset[type[BaseModel]] = frozenset(),
    field_name: str = "",
) -> Any:
    """Generate a placeholder value for a Python type annotation."""

    origin = get_origin(annotation)
    args = get_args(annotation)

    # Annotated[T, ...] -> T
    if origin is not None and str(origin) == "<class 'typing.Annotated'>":
        return _placeholder_for_type(args[0], model_stack, field_name)

    # Literal values -> first allowed value
    if origin is Literal:
        return _normalize_value(args[0])

    # Union and Optional types
    if origin in (Union, types.UnionType):
        non_none_args = [arg for arg in args if arg is not type(None)]

        if not non_none_args:
            return None

        return _placeholder_for_type(
            non_none_args[0], model_stack, field_name
        )

    # Nested Pydantic models
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return _build_model_template(annotation, model_stack)

    # Enumerations
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        return _normalize_value(next(iter(annotation)))

    # Generic collections
    if origin in (list, set, frozenset, tuple, Sequence):
        return []

    if origin in (dict, Mapping):
        return {}

    # Primitive types
    if annotation is str:
        return "simulation_name" if field_name == "name" else "TODO"

    if annotation is int:
        return 1

    if annotation is float:
        return 1.0

    if annotation is bool:
        return False

    # Unknown types
    return None


def _build_model_template(
    model: type[BaseModel],
    model_stack: frozenset[type[BaseModel]] = frozenset(),
) -> dict[str, Any]:
    """Recursively build a configuration template from a Pydantic model."""

    if model in model_stack:
        return {}

    model_stack = model_stack | {model}

    result = {}

    # Resolve forward references where possible
    type_hints = get_type_hints(model, include_extras=True)

    for name, field in model.model_fields.items():
        if field.is_required():
            annotation = type_hints.get(name, field.annotation)

            result[name] = _placeholder_for_type(
                annotation,
                model_stack,
                name,
            )

        elif field.default_factory is not None:
            result[name] = _normalize_value(field.default_factory())

        else:
            result[name] = _normalize_value(field.default)

    return result


def _create_default_config_of(path: str | Path, model: type[BaseModel]):
    """Create a minimal YAML configuration file from a Pydantic model."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    config = _build_model_template(model)

    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            config,
            f,
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
        )


def create_default_config(directory: Path) -> None:
    _create_default_config_of(directory / "sim.yaml"  , SimulationConfig)
    _create_default_config_of(directory / "fluid.yaml", FluidConfig)
    _create_default_config_of(directory / "solid.yaml", SolidConfig)

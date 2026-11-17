
from __future__ import annotations
from pydantic import BaseModel, Field, model_validator
from typing import Self, Literal
import os


class WorkflowConfig(BaseModel):
    """Collection of all the parameters"""
    model_config = {"frozen": True}
    
    sim: SimulationConfig
    fluid: FluidConfig
    solid: SolidConfig


class SimulationConfig(BaseModel):
    """Collection of the general simulation parameters"""
    model_config = {"frozen": True}
    
    info: InfoConfig
    execution: ExecutionConfig


class InfoConfig(BaseModel):
    """Information about the simulation"""
    model_config = {"frozen": True}

    name: str
    description: str = ""


class ExecutionConfig(BaseModel):
    """Generic execution-related parameters"""
    model_config = {"frozen": True}
    
    parallelization: Literal[ "serial", "automatic", "manual"] = "automatic"
    number_of_processors: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate(self) -> Self:
        from workflow.config.config_validation import validate_execution_config
        validate_execution_config(self)
        return self

    @property
    def effective_processors(self) -> int:
        if self.parallelization == "serial":
            return 1
        if self.parallelization == "automatic":
            # TODO: this returns the logical cores, which makes mpi sad; we need the number of physical cores.
            return os.cpu_count() or 1
        return self.number_of_processors or 1


class FluidConfig(BaseModel):
    """Fluid simulation parameters"""
    model_config = {"frozen": True}
    
    end_time: float = Field(gt=0)
    delta_t : float = Field(gt=0)

    @model_validator(mode="after")
    def validate(self) -> Self:
        from workflow.config.config_validation import validate_fluid_config
        validate_fluid_config(self)
        return self


class SolidConfig(BaseModel):
    """Solid simulation parameters"""
    model_config = {"frozen": True}

    @model_validator(mode="after")
    def validate(self) -> Self:
        from workflow.config.config_validation import validate_solid_config
        validate_solid_config(self)
        return self    



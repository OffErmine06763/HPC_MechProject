from pathlib import Path
import logging
import shutil

from workflow.fluid.setup import prepare_case
from workflow.fluid.runner import run_fluid_simulation, clean_fluid_simulation
from workflow.solid.runner import run_solid_simulation
from workflow.config.config import WorkflowConfig, FluidConfig, SolidConfig, ExecutionConfig
from workflow.environment import environment




def fluid_pipeline(fluid_config: FluidConfig, execution_config: ExecutionConfig):
    clean_fluid_simulation()
    prepare_case(fluid_config, execution_config)
    run_fluid_simulation(execution_config)
    pass


def coupling_pipeline(fluid_config: FluidConfig, solid_config: SolidConfig):
    # extract data from the fluid sim
    # convert it to what the solid sim expects
    # move to solid sim directory
    pass


def solid_pipeline(config: SolidConfig):
    run_solid_simulation()
    pass


def postprocessing_pipeline():
    pass


def cleanup_pipeline():
    clean_fluid_simulation()


def run_pipeline(config: WorkflowConfig, stage="all"):
    """
    Execute the workflow stages (or only the requested one).
    """

    logger = logging.getLogger(__name__)

    logger.info("Fluid simulation...")
    fluid_pipeline(config.fluid, config.sim.execution)
    logger.info("Fluid simulation... done!")

    logger.info("Coupling...")
    coupling_pipeline(config.fluid, config.solid)
    logger.info("Coupling... done!")

    logger.info("Solid simulation...")
    solid_pipeline(config.solid)
    logger.info("Solid simulation... done!")

    logger.info("Postprocessing...")
    postprocessing_pipeline()
    logger.info("Postprocessing... done!")

    logger.info("Final cleanup...")
    cleanup_pipeline()
    logger.info("Final cleanup... done!")

    pass
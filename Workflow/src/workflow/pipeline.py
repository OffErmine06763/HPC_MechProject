from pathlib import Path
import logging
import shutil

from workflow.fluid.setup import prepare_case
from workflow.fluid.runner import run_fluid_simulation, clean_fluid_simulation
from workflow.solid.runner import run_solid_simulation
from workflow.config.config import WorkflowConfig, FluidConfig, SolidConfig, ExecutionConfig


class WorkflowInfo:
    output_directory: Path


def create_run_directory(simulation_name: Path) -> Path:
    directory = Path("runs") / simulation_name

    # Delete all existing contents if the directory exists
    if directory.exists():
        if directory.is_dir():
            for item in directory.iterdir():
                if item.is_dir() and not item.is_symlink():
                    shutil.rmtree(item)
                else:
                    item.unlink()
        else:
            raise NotADirectoryError(directory)

    # Create the directory
    directory.mkdir(parents=True, exist_ok=True)
    return directory



def fluid_pipeline(fluid_config: FluidConfig, execution_config: ExecutionConfig, workflow_info: WorkflowInfo):
    clean_fluid_simulation()
    prepare_case(fluid_config, execution_config)
    run_fluid_simulation(execution_config, workflow_info.output_directory)
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


def run_pipeline(simulation_name: Path, config: WorkflowConfig, stage="all"):
    """
    Execute the workflow stages (or only the requested one).
    """

    logger = logging.getLogger(__name__)
    workflow_info = WorkflowInfo()

    workflow_info.output_directory = create_run_directory(simulation_name)

    logger.info("Fluid simulation...")
    fluid_pipeline(config.fluid, config.sim.execution, workflow_info)
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
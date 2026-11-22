# python -m make_the_work_flow sim1
# this looks for configs in config/sim1/ and outputs to runs/sim1/
# python -m make_the_work_flow sim1 --stage solid
# this expects the runs/sim1 to contain the required data to run the solid simulation
# the configs to load depend on the stage to perform (e.g. fluid configs shouldn't influence solid execution)


import argparse
import logging
import sys
from pathlib import Path

from workflow.environment import environment
from workflow.config.config_loader import load_config
from workflow.pipeline import run_pipeline
from workflow.utils.utils import delete_path, setup_logging


def parse_arguments():
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description="Tsunami (Work)flow") # yes they do

    parser.add_argument(
        "simulation",
        type=Path,
        help="Simulation to execute (must have a corresponding set of configuration files)."
    )

    parser.add_argument(
        "--stage",
        type=str,
        choices=["all", "fluid", "solid", "postprocessing"],
        default="all",
        help="Workflow stage to execute."
    )

    return parser.parse_args()





def create_output_directory() -> Path:
    directory = environment.output_dir

    # Delete all existing contents if the directory exists
    delete_path(directory)

    # Create the directory
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def main():
    """Main application entry point."""

    environment.initialize()
    args = parse_arguments()

    setup_logging(True)
    logger = logging.getLogger(__name__)

    try:
        logger.info("Starting FSI workflow")

        # Load and validate configuration
        config = load_config(args.simulation)
        logger.info("Loaded and validated \"%s\" workflow configuration", args.simulation)
        if config.sim.execution.effective_processors != 1:
            logger.info(f"Parallel execution on {config.sim.execution.effective_processors} processors")

        # Execute pipeline
        environment.output_dir = environment.workflow_dir / Path("runs") / args.simulation
        create_output_directory()
        run_pipeline(config=config, stage=args.stage)

        logger.info("Workflow completed successfully!")

    except KeyboardInterrupt:
        logger.warning("Workflow interrupted by user")
        sys.exit(130)

    except Exception as e:
        logger.error("Workflow failed: %s", e, exc_info=e)
        # TODO: write to file the full trace
        sys.exit(1)


if __name__ == "__main__":
    main()

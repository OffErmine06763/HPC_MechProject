# python -m make_the_work_flow sim1
# this looks for configs in config/sim1/ and outputs to runs/sim1/
# python -m make_the_work_flow sim1 --stage solid
# this expects the runs/sim1 to contain the required data to run the solid simulation
# the configs to load depend on the stage to perform (e.g. fluid configs shouldn't influence solid execution)


import argparse
import logging
import sys
from pathlib import Path

from workflow.config.config_loader import load_config
from workflow.pipeline import run_pipeline


def parse_arguments():
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="OpenFOAM - Structural Solver Workflow"
    )

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


def setup_logging(verbose=False):
    """Configure application logging."""

    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        force=True
    )


def main():
    """Main application entry point."""

    args = parse_arguments()

    setup_logging(True)

    logger = logging.getLogger(__name__)

    try:
        logger.info("Starting FSI workflow")

        # Load and validate configuration
        config = load_config(args.simulation)
        logger.info("Loaded and validated \"%s\" workflow configuration", args.simulation)

        # Execute pipeline
        run_pipeline(config=config, stage=args.stage)

        logger.info("Workflow completed successfully")

    except KeyboardInterrupt:
        logger.warning("Workflow interrupted by user")
        sys.exit(130)

    except Exception as e:
        logger.error("Workflow failed: %s", e)
        # TODO: write to file the full trace
        sys.exit(1)


if __name__ == "__main__":
    main()

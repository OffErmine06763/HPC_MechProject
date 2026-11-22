import logging
import shutil
import sys
from pathlib import Path

def delete_dir_content(path: Path):
    if path.exists() and path.is_dir():
        for item in path.iterdir():
            if item.is_dir() and not item.is_symlink():
                shutil.rmtree(item)
            else:
                item.unlink()


def delete_path(path: Path):
    if path.exists():
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        else:
            path.unlink()

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
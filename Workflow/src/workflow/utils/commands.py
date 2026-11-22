"""Utils to create and execute commands"""

from pathlib import Path
import shlex
import subprocess
from typing import Literal


def run_command(command: str, redirect: Path | None | Literal["stdout"] = None, working_directory: Path | None = None, redirect_mode: Literal["overwrite", "append"] = "overwrite") -> int:
    if redirect is None:
        result = subprocess.run(
            command,
            shell=True,
            cwd=working_directory,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    elif isinstance(redirect, Path):
        redirect.parent.mkdir(parents=True, exist_ok=True)
        with redirect.open("w" if redirect_mode == "overwrite" else "a", encoding="utf-8") as output:
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_directory,
                stdout=output,
                stderr=subprocess.STDOUT,
                check=False,
            )
    else:
        result = subprocess.run(
            command,
            shell=True,
            cwd=working_directory,
            stderr=subprocess.STDOUT,
            check=False,
        )
    return result.returncode


def get_write_dictionary_command(field: str, value: str, file: str) -> str:
    return (
        f"foamDictionary {shlex.quote(file)} -entry {shlex.quote(field)} "
        f"-set {shlex.quote(value)}"
    )


def get_read_dictionary_command(field: str, file: str) -> str:
    return f"foamDictionary {shlex.quote(file)} -entry {shlex.quote(field)} -value"


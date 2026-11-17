"""Utils to create and execute commands"""

from pathlib import Path
import shlex
import subprocess


def run_command(command: str, redirect_file: Path | None = None, working_directory: Path | None = None) -> int:
    """Run *command*, redirecting stdout and stderr to ``redirect_file``.

    Commands are intentionally strings because the OpenFOAM command builders
    return shell-ready commands (including quoted dictionary values).  The
    caller owns deciding whether a non-zero return code is an error.
    """

    if redirect_file is None:
        result = subprocess.run(
            command,
            shell=True,
            cwd=working_directory,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    else:
        redirect_file.parent.mkdir(parents=True, exist_ok=True)
        with redirect_file.open("w", encoding="utf-8") as output:
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_directory,
                stdout=output,
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


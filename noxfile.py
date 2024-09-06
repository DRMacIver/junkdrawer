"""Nox sessions."""

import os
import shlex
import shutil
import sys
from glob import glob
from pathlib import Path

import nox
from nox import Session, session

nox.options.default_venv_backend = "uv"

package = "drmaciver-junkdrawer"
python_versions = ["3.12"]
nox.needs_version = ">= 2021.6.6"
nox.options.sessions = (
    "mypy",
    "tests",
)


PY_FILES = glob("src/**/*.py", recursive=True) + glob("test/**/*.py", recursive=True)
assert PY_FILES


@session(python=python_versions[0])
def format(session: Session) -> None:
    session.install(
        "shed==2024.3.1",
    )
    session.run("shed", "--refactor", *PY_FILES)


@session(python=python_versions)
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or ["src", "tests"]
    session.install(".")
    session.install("mypy", "pytest")
    session.run("mypy", *args)
    if not session.posargs:
        session.run("mypy", f"--python-executable={sys.executable}", "noxfile.py")


@session(python=python_versions, reuse_venv=True)
def tests(session: Session) -> None:
    """Run the test suite."""
    session.install("-e", ".")
    session.install("coverage[toml]", "pytest", "pygments", "hypothesis")
    try:
        session.run(
            "coverage",
            "run",
            "--branch",
            "--parallel",
            "-m",
            "pytest",
            *session.posargs,
        )
    finally:
        if session.interactive and not session.posargs:
            session.run("coverage", "combine")
            session.run("coverage", "report", "--show-missing", "--fail-under=100")

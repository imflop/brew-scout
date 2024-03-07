import toml

from functools import cache
from pathlib import Path


@cache
def _project_root() -> Path | None:
    current_path = Path(__file__)

    for parent_directory in current_path.parents:
        if (parent_directory / "pyproject.toml").is_file():
            return parent_directory

    return None


def _get_path_to_pyproject_toml() -> str | None:
    if project_root_path := _project_root():
        return f"{project_root_path}/pyproject.toml"

    return None


def _get_version() -> str | None:
    if path_to_pyproject_toml := _get_path_to_pyproject_toml():
        if pyproject_version := toml.load(path_to_pyproject_toml)["tool"]["poetry"]["version"]:
            return pyproject_version

    return None


def _get_name() -> str | None:
    if path_to_pyproject_toml := _get_path_to_pyproject_toml():
        if pyproject_name := toml.load(path_to_pyproject_toml)["tool"]["poetry"]["name"]:
            return pyproject_name

    return None


def _get_description() -> str | None:
    if path_to_pyproject_toml := _get_path_to_pyproject_toml():
        if pyproject_description := toml.load(path_to_pyproject_toml)["tool"]["poetry"]["description"]:
            return pyproject_description

    return None


VERSION = _get_version() or "DEFAULT-0.0.1"
MODULE_NAME = _get_name() or "DEFAULT NAME"
DESCRIPTION = _get_description() or "DEFAULT DESCRIPTION"

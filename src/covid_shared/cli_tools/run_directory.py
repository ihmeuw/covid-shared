import datetime
from pathlib import Path
import re
from typing import Optional, Union, Tuple
from warnings import warn

from loguru import logger

from covid_shared import paths
from covid_shared.cli_tools.metadata import Metadata
from covid_shared.shell_tools import mkdir


def make_run_directory(output_root: Union[str, Path]) -> Path:
    """Convenience function for making a new run directory and getting its path."""
    run_directory = get_run_directory(output_root)
    mkdir(run_directory)
    return run_directory


def get_run_directory(output_root: Union[str, Path]) -> Path:
    """Gets a path to a datetime directory for a new output.

    Parameters
    ----------
    output_root
        The root directory for all outputs.

    """
    output_root = Path(output_root).resolve()
    launch_time = datetime.datetime.now().strftime("%Y_%m_%d")
    today_runs = [int(run_dir.name.split('.')[1]) for run_dir in output_root.iterdir() if
                  run_dir.name.startswith(launch_time)]
    run_version = max(today_runs) + 1 if today_runs else 1
    datetime_dir = output_root / f'{launch_time}.{run_version:0>2}'
    return datetime_dir


def get_last_stage_directory(last_stage_version: Union[str, Path], last_stage_directory: Union[str, Path] = None,
                             last_stage_root: Path = None) -> Path:
    """Get the directory containing the results of the last pipeline stage.

    Parameters
    ----------
    last_stage_version
        The path to the version. Can either be an absolute path, or a path relative to the last_stage_root

    last_stage_directory
        Deprecated parameter. The path to the version. Should use last_stage_version instead

    last_stage_root
        The path to the root of the resource. Must be an absolute path.
    """
    if last_stage_directory:
        warn(f'Usage of the "last_stage_directory" argument is deprecated. Please use "last_stage_version instead.',
             Warning)
    last_stage_directory = last_stage_directory if last_stage_directory is not None else last_stage_version
    # If last_stage_directory is an absolute path, the last_stage_root will be ignored here
    last_stage_directory = (last_stage_root / last_stage_directory if last_stage_root is not None
                            else last_stage_directory)
    if not last_stage_directory.is_absolute():
        raise ValueError(f'Invalid version path: {last_stage_directory}')
    return last_stage_directory


def setup_directory_structure(output_root: Union[str, Path], with_production: bool = False) -> None:
    """Sets up a best and latest directory for results versioning.

    Parameters
    ----------
    output_root
        The root directory for all outputs.
    with_production
        If true, additionally sets up a `production-run` sub-directory within
        the primary output root.

    """
    mkdir(output_root, exists_ok=True, parents=True)
    output_root = Path(output_root).resolve()
    for link in [paths.BEST_LINK, paths.LATEST_LINK]:
        link_path = output_root / link
        if not link_path.is_symlink() and not link_path.exists():
            mkdir(link_path)

    if with_production:
        production_dir = output_root / paths.PRODUCTION_RUN
        mkdir(production_dir, exists_ok=True)


def make_links(app_metadata: Metadata, run_directory: Path,
               mark_as_best: bool, production_tag: Optional[str]) -> None:
    if app_metadata['success']:
        mark_latest(run_directory)

        if mark_as_best:
            mark_best(run_directory)

            if production_tag:
                try:
                    mark_production(run_directory, production_tag)
                except ValueError:
                    logger.warning(f'Invalid production tag {production_tag}. Run not marked for production.'
                                   f'Please provide production tag in format YYYY_MM_DD.')


def mark_best(run_directory: Union[str, Path]) -> None:
    """Marks an output directory as the best source of data."""
    run_directory = Path(run_directory).resolve()
    mark_best_explicit(run_directory, run_directory.parent)


def mark_latest(run_directory: Union[str, Path]) -> None:
    """Marks an output directory as the latest source of data."""
    run_directory = Path(run_directory).resolve()
    mark_latest_explicit(run_directory, run_directory.parent)


def mark_production(run_directory: Union[str, Path], date: str = None) -> None:
    """Marks a run as a production run.

    Raises
    ------
    ValueError
        If date is not in the format YYYY_MM_DD

    """
    run_directory = Path(run_directory).resolve()
    mark_production_explicit(run_directory, run_directory.parent / paths.PRODUCTION_RUN, date)


def mark_production_explicit(run_directory: Union[str, Path], version_root: Union[str, Path], date: str = None) -> None:
    """Marks a run as a production run within a specific version root.

    Raises
    ------
    ValueError
        If date is not in the format YYYY_MM_DD

    """
    if date is None:
        date = datetime.datetime.now().strftime('%Y_%m_%d')
    else:
        # Will raise a Value error if not the correct format.
        datetime.datetime.strptime(date, '%Y_%m_%d')
    mark_explicit(run_directory, version_root, date)


def mark_best_explicit(run_directory: Union[str, Path], version_root: Union[str, Path]) -> None:
    """Marks a directory best within a specific version root."""
    mark_explicit(run_directory, version_root, paths.BEST_LINK)


def mark_latest_explicit(run_directory: Union[str, Path], version_root: Union[str, Path]) -> None:
    """Marks a directory latest within a specific version root."""
    mark_explicit(run_directory, version_root, paths.LATEST_LINK)


def mark_explicit(run_directory: Union[str, Path], version_root: Union[str, Path], link_name: Union[str, Path]) -> None:
    """Makes or moves a link name to the run directory in a version root."""
    run_directory = Path(run_directory).resolve()
    version_root = Path(version_root).resolve()
    link_file = version_root / link_name
    move_link(link_file, run_directory)


def move_link(symlink_file: Path, link_target: Path) -> None:
    """Removes an old symlink and links it to something else."""
    if symlink_file.is_symlink():
        symlink_file.unlink()
    elif symlink_file.is_dir():  # We have set this up be a directory at the start.
        symlink_file.rmdir()
    elif symlink_file.exists():  # A file exists but isn't a symlink or a directory
        raise ValueError(f'{str(symlink_file)} is not a symlink or a directory')
    symlink_file.symlink_to(link_target, target_is_directory=True)


def get_current_previous_version(current_run_directory: Path, previous_run_directory: Path = None,
                                 resolved_name: bool = True) -> Tuple[str, str]:
    """
    Takes a full path to the current version, and returns the string name of the current and previous versions.

    Parameters
    ----------
    current_run_directory
        Path of the current version.
    previous_run_directory
        Path of a previous version. If unspecified, the previous version is taken to be the latest run from a date
        prior to the current run's date
    resolved_name
        If False, resolves a potential symlink to a canonical location

    """
    run_matcher = r'^\d{4}'

    parent_dir = current_run_directory.parent
    current_version = current_run_directory.name
    current_version_resolved = current_run_directory.resolve().name
    current_version_date = current_version_resolved.split('.')[0]
    previous_version = previous_run_directory.name if previous_run_directory else sorted([
        p.name for p in parent_dir.iterdir() if re.search(run_matcher, p.name) and current_version_date > p.name
    ])[-1]
    return current_version_resolved if resolved_name else current_version, previous_version

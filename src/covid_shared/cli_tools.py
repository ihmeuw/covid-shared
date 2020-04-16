from bdb import BdbQuit
from datetime import datetime
import functools
from pathlib import Path
from pprint import pformat
import sys
import time
import traceback
import types
import typing
from typing import Any, Callable, Dict, Mapping, Union

import click
from loguru import logger
import yaml

from covid_shared import paths


DEFAULT_LOG_MESSAGING_FORMAT = ('<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
                                '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> '
                                '- <level>{message}</level>')

LOG_FORMATS = {
    # Keys are verbosity.  Specify special log formats here.
    0: ("ERROR", DEFAULT_LOG_MESSAGING_FORMAT),
    1: ("INFO", DEFAULT_LOG_MESSAGING_FORMAT),
    2: ("DEBUG", DEFAULT_LOG_MESSAGING_FORMAT),
}


def add_logging_sink(sink: typing.TextIO, verbose: int, colorize: bool = False, serialize: bool = False):
    """Add a new output file handle for logging."""
    level, message_format = LOG_FORMATS.get(verbose, LOG_FORMATS[max(LOG_FORMATS.keys())])
    logger.add(sink, colorize=colorize, level=level, format=message_format, serialize=serialize)


def configure_logging_to_terminal(verbose: int):
    """Setup logging to sys.stdout."""
    logger.remove(0)  # Clear default configuration
    add_logging_sink(sys.stdout, verbose, colorize=True)


# Common click options
shared_options = [
    click.option('--pdb', 'with_debugger',
                 is_flag=True,
                 help='Drop into python debugger if an error occurs.'),
    click.option('-v', 'verbose',
                 count=True,
                 help='Configure logging verbosity.'),
]


def add_verbose_and_with_debugger(func):
    """Add all the shared options to the command."""
    for option in shared_options:
        func = option(func)
    return func


class YamlIOMixin:
    """Mixin class for reading and writing data from yaml files."""

    @staticmethod
    def _load(in_file: typing.TextIO) -> Dict:
        return yaml.load(in_file)

    @staticmethod
    def _write(data: Dict[str, Any], out_file: typing.TextIO):
        yaml.dump(data, out_file)


class Metadata:
    """Base metadata class.  Looks and feels like a dict with a limited API.

    This class is meant for recording metadata for applications and run
    environments and forwarding that information across pipeline stages.

    This class provides the interface for file I/O, but does not implement
    it.

    """

    def __init__(self, *args, **kwargs):
        self._metadata = {}

    def update(self, metadata_update: Mapping):
        """Dictionary style update of metadata."""
        # Inefficient, by centralizes error handling.
        for key, value in metadata_update.items():
            self[key] = value

    def update_from_file(self, metadata_key: str, metadata_file: typing.TextIO):
        """Loads a metadata file from disk and stores it in the key."""
        logger.warning('Base metadata information cannot be constructed from a file. Returning empty metadata.')

    def to_dict(self):
        """Give back a dict version of the metadata."""
        return self._metadata.copy()

    def __getitem__(self, metadata_key: str):
        return self._metadata[metadata_key]

    def __setitem__(self, metadata_key: str, value: Any):
        if metadata_key in self:
            # This feels like a weird use of KeyError.  AttributeError also
            # feels wrong.  Maybe write a custom error later.
            raise KeyError(f'Metadata key {metadata_key} has already been set.')
        self._metadata[metadata_key] = value

    def __contains__(self, metadata_key: str):
        return metadata_key in self._metadata

    def dump(self, metadata_file: typing.TextIO):
        """Interface to dump metadata to disk."""
        logger.warning('Base metadata class should not be used to dump information to a file.')
        pass

    def __repr__(self):
        return self.__class__.__name__


class RunMetadata(Metadata, YamlIOMixin):
    """Metadata class meant specifically for application runners.

    Silently records profiling and provenance information.

    """

    def __init__(self, *args, **kwargs):
        self._start = time.time()
        super().__init__(*args, **kwargs)
        self['start_time'] = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    def update_from_file(self, metadata_key: str, metadata_file: typing.TextIO):
        """Loads a metadata file from disk and stores it in the key."""
        self._metadata[metadata_key] = yaml.load(metadata_file)

    def dump(self, metadata_file_path: Union[str, Path]):
        self._metadata['run_time'] = f"{time.time() - self._start:.2f} seconds"
        try:
            with Path(metadata_file_path).open('w') as metadata_file:
                self._write(self._metadata, metadata_file)
        except FileNotFoundError as e:
            logger.warning(f'Output directory for {metadata_file.name} does not exist. Dumping metadata to console.')
            click.echo(pformat(self._metadata))


def pass_run_metadata(run_metadata=RunMetadata()):
    """Decorator for cli entry points to inject a run metadata object and
    record arguments.

    Parameters
    ----------
    run_metadata
        The metadata object to inject.

    """

    def _pass_run_metadata(app_entry_point: types.FunctionType):

        @functools.wraps(app_entry_point)
        def _wrapped(*args, **kwargs):
            # Record arguments for the run and inject the metadata.
            run_metadata['tool_name'] = f'{app_entry_point.__module__}:{app_entry_point.__name__}'
            run_metadata['run_arguments'] = get_function_full_argument_mapping(app_entry_point,
                                                                               run_metadata, *args, **kwargs)
            return app_entry_point(run_metadata, *args, **kwargs)

        return _wrapped

    return _pass_run_metadata


def monitor_application(func: types.FunctionType, logger_: Any, with_debugger: bool,
                        app_metadata: Metadata = Metadata()) -> Callable:
    """Monitors an application for errors and injects a metadata container.

    Catches records them if they occur. Can also be configured to drop
    a user into an interactive debugger on failure.

    Parameters
    ----------
    func
        The application function to monitor.
    logger_
        The application logger
    with_debugger
        Whether the monitor drops a user into a pdb session on application
        failure.
    app_metadata
        Record for application metadata.

    """

    @functools.wraps(func)
    def _wrapped(*args, **kwargs):
        result = None
        try:
            # Record arguments for the run and inject the metadata
            app_metadata['main_function'] = f'{func.__module__}:{func.__name__}'
            app_metadata['run_arguments'] = get_function_full_argument_mapping(func, app_metadata,
                                                                               *args, **kwargs)
            result = func(app_metadata, *args, **kwargs)
        except (BdbQuit, KeyboardInterrupt):
            app_metadata['success'] = False
            app_metadata['error_info'] = 'User interrupt.'
        except Exception as e:
            # For general errors, write exception info to the metadata.
            app_metadata['success'] = False
            logger_.exception("Uncaught exception {}".format(e))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            app_metadata['error_info'] = {
                'exception_type': exc_type,
                'exception_value': exc_value,
                'exc_traceback': traceback.format_tb(exc_traceback)
            }
            if with_debugger:
                import pdb
                traceback.print_exc()
                pdb.post_mortem()
        finally:
            return app_metadata, result
    return _wrapped


def get_function_full_argument_mapping(func: types.FunctionType, *args, **kwargs) -> Dict:
    """Get a dict representation of all args and kwargs for a function."""
    # Grab all variables in the enclosing namespace.  Args will be first.
    # Note: This may rely on the CPython implementation.  Not sure.
    arg_names = func.__code__.co_varnames
    arg_vals = [str(arg) for arg in args]
    # Zip ignores extra items in the second arg.  Use that property to catch
    # all positional args and ignore kwargs.
    run_args = dict(zip(arg_names, arg_vals))
    run_args.update({k: str(v) for k, v in kwargs.items()})
    return run_args


def get_run_directory(output_root: Union[str, Path]) -> Path:
    """Gets a path to a datetime directory for a new snapshot.

    Parameters
    ----------
    output_root
        The root directory for all snapshots.

    """
    output_root = Path(output_root).resolve()
    launch_time = datetime.now().strftime("%Y_%m_%d")
    today_runs = [int(run_dir.name.split('.')[1]) for run_dir in output_root.iterdir() if
                  run_dir.name.startswith(launch_time)]
    run_version = max(today_runs) + 1 if today_runs else 1
    datetime_dir = output_root / f'{launch_time}.{run_version}'
    return datetime_dir


def get_last_stage_directory(last_stage_version: str, last_stage_directory: Union[str, Path],
                             last_stage_root: Path = None) -> Path:
    """Get the directory containing the results of the last pipeline stage."""
    if last_stage_directory:
        return Path(last_stage_directory)
    elif last_stage_root is None:
        raise ValueError('No previous stage results found.')
    else:
        return last_stage_root / last_stage_version


def setup_directory_structure(output_root: Union[str, Path]):
    """Sets up a best and latest directory for results versioning.

    output_root
        The root directory for all snapshots.

    """
    output_root = Path(output_root).resolve()
    for link in [paths.BEST_LINK, paths.LATEST_LINK]:
        link_path = output_root / link
        if not link_path.is_symlink() and not link_path.exists():
            link_path.mkdir(paths.DIRECTORY_PERMISSIONS)


def mark_best(run_directory: Union[str, Path]):
    """Marks an output directory as the best source of raw input data."""
    run_directory = Path(run_directory).resolve()
    best_link = run_directory.parent / paths.BEST_LINK
    move_link(best_link, run_directory)


def mark_latest(run_directory: Union[str, Path]):
    """Marks an output directory as the best source of raw input data."""
    run_directory = Path(run_directory).resolve()
    latest_link = run_directory.parent / paths.LATEST_LINK
    move_link(latest_link, run_directory)


def move_link(symlink_file: Path, link_target: Path):
    """Removes an old symlink and links it to something else."""
    if symlink_file.is_symlink():
        symlink_file.unlink()
    else:  # We have set this up be a directory at the start.
        symlink_file.rmdir()
    symlink_file.symlink_to(link_target, target_is_directory=True)

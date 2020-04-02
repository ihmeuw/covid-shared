from bdb import BdbQuit
from datetime import datetime
import functools
from pathlib import Path
from pprint import pformat
import sys
import time
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


class _Metadata:
    """Base metadata class. Does not record anything by default."""

    def __init__(self, *args, **kwargs):
        self._metadata = {}
        pass

    def __setitem__(self, metadata_key: str, value: Any):
        pass

    def __contains__(self, metadata_key: str):
        return metadata_key in self._metadata

    def dump(self):
        """Dumps all metadata to disk."""
        pass


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

    def to_dict(self):
        """Give back a dict version of the metadata."""
        return self._metadata.copy()

    @classmethod
    def from_file(cls, metadata_file: typing.TextIO):
        """Loads metadata from disk."""
        logger.warning('Base metadata information cannot be constructed from a file. Returning empty metadata.')
        return cls()

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


class RunMetadata(Metadata, YamlIOMixin):
    """Metadata class meant specifically for application runners.

    Silently records profiling and provenance information.

    """

    def __init__(self, *args, **kwargs):
        self._start = time.time()
        super().__init__(*args, **kwargs)
        self['start_time'] = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    @classmethod
    def from_file(cls, metadata_file: typing.TextIO):
        metadata_dict = cls._load(metadata_file)
        metadata = cls()
        metadata.update(metadata_dict)
        return metadata

    def dump(self, metadata_file: typing.TextIO):
        self._metadata['run_time'] = f"{time.time() - self._start:.2f} seconds"
        try:
            self._write(self._metadata, metadata_file)
        except FileNotFoundError as e:
            logger.warning(f'Output directory for {metadata_file.name} does not exist. Dumping metadata to console.')
            click.echo()



def record_run_metadata(app_entry_point, metadata_class=RunMetadata):
    run_metadata = RunMetadata()




class RunMetadata(_Metadata):
    """Metadata about a tool run.

    By default, records the following
        path: the root of the output directory.
        start_time: The full datetime when the run was started.
        run_time: How long the tool took to run.
    """

    def __init__(self, output_root: str):
        super().__init__()
        self._start = time.time()
        run_dir = get_run_directory(output_root)
        self._path = run_dir / paths.METADATA_FILE_NAME
        self._metadata = {}
        self['path'] = str(run_dir)
        self['start_time'] = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

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

    def dump(self):
        """Dumps all metadata to disk."""
        self._metadata['run_time'] = f"{time.time() - self._start:.2f} seconds"
        with self._path.open('w') as metadata_file:
            yaml.dump(self._metadata, metadata_file)


def handle_exceptions(func: Callable, logger_: Any, with_debugger: bool,
                      output_metadata: _Metadata = _Metadata()) -> Callable:
    """Drops a user into an interactive debugger if func raises an error."""

    @functools.wraps(func)
    def _wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (BdbQuit, KeyboardInterrupt):
            output_metadata['success'] = False
            raise
        except Exception as e:
            output_metadata['success'] = False
            logger_.exception("Uncaught exception {}".format(e))
            if with_debugger:
                import pdb
                import traceback
                traceback.print_exc()
                pdb.post_mortem()
            else:
                raise
        finally:
            if 'success' not in output_metadata:
                output_metadata['success'] = True
            output_metadata.dump()

    return _wrapped


def get_run_directory(output_root: Union[str, Path]) -> Path:
    """Gets a path to a datetime directory for a new snapshot.

    Parameters
    ----------
    output_root
        The root directory for all snapshots.

    """
    output_root = Path(output_root)
    launch_time = datetime.now().strftime("%Y_%m_%d")
    today_runs = [int(run_dir.name.split('.')[1]) for run_dir in output_root.iterdir() if
                  run_dir.name.startswith(launch_time)]
    run_version = max(today_runs) + 1 if today_runs else 1
    datetime_dir = output_root / f'{launch_time}.{run_version}'
    return datetime_dir


def setup_directory_structure(output_root: Union[str, Path]):
    """Sets up a best and latest directory for results versioning.

    output_root
        The root directory for all snapshots.

    """
    output_root = Path(output_root)
    for link in [paths.BEST_LINK, paths.LATEST_LINK]:
        link_path = output_root / link
        if not link_path.is_symlink() and not link_path.exists():
            link_path.mkdir(paths.DIRECTORY_PERMISSIONS)


def mark_best(run_directory: Union[str, Path]):
    """Marks an output directory as the best source of raw input data."""
    run_directory = Path(run_directory)
    best_link = run_directory.parent / paths.BEST_LINK
    move_link(best_link, run_directory)


def mark_latest(run_directory: Union[str, Path]):
    """Marks an output directory as the best source of raw input data."""
    run_directory = Path(run_directory)
    latest_link = run_directory.parent / paths.LATEST_LINK
    move_link(latest_link, run_directory)


def move_link(symlink_file: Path, link_target: Path):
    """Removes an old symlink and links it to something else."""
    if symlink_file.is_symlink():
        symlink_file.unlink()
    else:  # We have set this up be a directory at the start.
        symlink_file.rmdir()
    symlink_file.symlink_to(link_target, target_is_directory=True)

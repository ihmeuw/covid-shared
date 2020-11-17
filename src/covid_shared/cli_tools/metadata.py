from bdb import BdbQuit
import datetime
import functools
from pathlib import Path
from pprint import pformat
import sys
import time
import traceback
import types
import typing
from typing import Any, Callable, Dict, Mapping, Optional, Union

import click
from loguru import logger
import yaml

from covid_shared import paths


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
        self['start_time'] = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    def update_from_path(self, metadata_key: str, metadata_path: Union[str, Path]):
        """Updates metadata from a metadata file path."""
        metadata_path = Path(metadata_path)
        if not metadata_path.name == paths.METADATA_FILE_NAME.name:
            raise ValueError('Can only update from `metadata.yaml` files.')
        with metadata_path.open() as metadata_file:
            self.update_from_file(metadata_key, metadata_file)

    def update_from_file(self, metadata_key: str, metadata_file: typing.TextIO):
        """Loads a metadata file from disk and stores it in the key."""
        self._metadata[metadata_key] = yaml.full_load(metadata_file)

    def dump(self, metadata_file_path: Union[str, Path]):
        self._metadata['run_time'] = f"{time.time() - self._start:.2f} seconds"
        try:
            with Path(metadata_file_path).open('w') as metadata_file:
                self._write(self._metadata, metadata_file)
        except FileNotFoundError:
            logger.warning(f'Output directory for {metadata_file.name} does not exist. Dumping metadata to console.')
            click.echo(pformat(self._metadata))


def monitor_application(func: types.FunctionType, logger_: Any, with_debugger: bool,
                        app_metadata: Optional[Metadata] = None) -> Callable:
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
    if app_metadata is None:
        app_metadata = Metadata()
    @functools.wraps(func)
    def _wrapped(*args, **kwargs):
        result = None
        try:
            # Record arguments for the run and inject the metadata
            app_metadata['main_function'] = f'{func.__module__}:{func.__name__}'
            app_metadata['run_arguments'] = get_function_full_argument_mapping(func, app_metadata,
                                                                               *args, **kwargs)
            result = func(app_metadata, *args, **kwargs)
            app_metadata['success'] = True
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


def update_with_previous_metadata(run_metadata: RunMetadata, input_root: Path) -> RunMetadata:
    """Convenience function for updating metadata from an input source."""
    key = str(input_root.resolve()).replace(' ', '_').replace('-', '_').lower() + '_metadata'
    with (input_root / paths.METADATA_FILE_NAME).open() as input_metadata_file:
        run_metadata.update_from_file(key, input_metadata_file)
    return run_metadata


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

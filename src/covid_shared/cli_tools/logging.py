from pathlib import Path
import sys
import typing
from typing import Union

from loguru import logger

from covid_shared import paths
from covid_shared.shell_tools import mkdir


DEFAULT_LOG_MESSAGING_FORMAT = ('<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
                                '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> '
                                '- <level>{message}</level> - {extra}')

LOG_FORMATS = {
    # Keys are verbosity.  Specify special log formats here.
    0: ("ERROR", DEFAULT_LOG_MESSAGING_FORMAT),
    1: ("INFO", DEFAULT_LOG_MESSAGING_FORMAT),
    2: ("DEBUG", DEFAULT_LOG_MESSAGING_FORMAT),
}


def add_logging_sink(sink: Union[typing.TextIO, Path], verbose: int, colorize: bool = False, serialize: bool = False):
    """Add a new output file handle for logging."""
    level, message_format = LOG_FORMATS.get(verbose, LOG_FORMATS[max(LOG_FORMATS.keys())])
    logger.add(sink, colorize=colorize, level=level, format=message_format, serialize=serialize)


def configure_logging_to_terminal(verbose: int):
    """Setup logging to sys.stdout."""
    logger.remove(0)  # Clear default configuration
    add_logging_sink(sys.stdout, verbose, colorize=True)


def configure_logging_to_files(output_path: Path) -> None:
    log_path = output_path / paths.LOG_DIR
    mkdir(log_path, exists_ok=True)
    add_logging_sink(output_path / paths.LOG_DIR / paths.DETAILED_LOG_FILE_NAME, verbose=2, serialize=True)
    add_logging_sink(output_path / paths.LOG_DIR / paths.LOG_FILE_NAME, verbose=1)

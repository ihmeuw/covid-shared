import logging
from pathlib import Path
import sys
from typing import TextIO, Tuple, Union

from loguru import logger

from covid_shared import paths
from covid_shared.shell_tools import mkdir


JOBMON_LOGGING_LEVEL = 5  # A lower level than logging.DEBUG.
DEFAULT_LOG_MESSAGING_FORMAT = (
    '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
    '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> '
    '- <level>{message}</level> - {extra}'
)
LOG_FORMATS = {
    # Keys are verbosity.  Specify special log formats here.
    0: ("WARNING", DEFAULT_LOG_MESSAGING_FORMAT),
    1: ("INFO", DEFAULT_LOG_MESSAGING_FORMAT),
    2: ("DEBUG", DEFAULT_LOG_MESSAGING_FORMAT),
    3: (JOBMON_LOGGING_LEVEL, DEFAULT_LOG_MESSAGING_FORMAT),
}


def configure_logging_to_terminal(verbose: int) -> None:
    """Setup logging to sys.stdout.

    This is presumed to be one of the first calls made in an
    application entry point. Any logging that occurs before this
    call won't be intercepted or handled with the standard
    logging configuration.

    """
    logger.remove(0)  # Clear default configuration
    level = LOG_FORMATS.get(verbose, LOG_FORMATS[max(LOG_FORMATS.keys())])[0]
    intercept_jobmon_logs(level)
    add_logging_sink(sys.stdout, verbose, colorize=True)


def configure_logging_to_files(output_path: Path) -> None:
    """Sets up logging to a file in an output directory.

    Logs to files are done with the highest verbosity to allow
    for debugging if necessary.

    """
    log_path = output_path / paths.LOG_DIR
    mkdir(log_path, exists_ok=True)
    add_logging_sink(
        output_path / paths.LOG_DIR / paths.DETAILED_LOG_FILE_NAME,
        verbose=3,
        serialize=True,
    )
    add_logging_sink(
        output_path / paths.LOG_DIR / paths.LOG_FILE_NAME,
        verbose=3,
    )


def add_logging_sink(sink: Union[TextIO, Path],
                     verbose: int,
                     colorize: bool = False,
                     serialize: bool = False) -> None:
    """Add a new output file handle for logging."""
    level, message_format = LOG_FORMATS.get(
        verbose, LOG_FORMATS[max(LOG_FORMATS.keys())]
    )
    logger.add(
        sink,
        colorize=colorize,
        level=level,
        format=message_format,
        serialize=serialize,
        filter={
            # Suppress logs up to the level provided.
            'urllib3': 'WARNING',  # Uselessly (for us) noisy.
        }
    )


class JobmonInterceptHandler(logging.Handler):
    """Intercepts and handles logging messages from jobmon.

    Jobmon logs a lot of information on its own set of loggers at
    sometimes unexpected priority levels. Many of these messages
    are not useful in an application as they generally deal with
    jobmon internals. This handler does both filtering and parsing
    of jobmon log messages in order to suppress uninteresting
    messages and to summarize status information.

    The original messages are still emitted at the
    JOBMON_LOGGING_LEVEL for debugging purposes.

    As the core loop of jobmon is multithreaded, there is technically
    a race condition here as we could be asked to process a second
    message before we've finished the first. In practice, the
    processing here is so fast and the core jobmon loop sleeps
    so long that we'll never have an issue.

    """
    # log handling strategies
    _FILTER = 0
    _LIFT = 1
    _RE_EMIT = 2

    def emit(self, record: logging.LogRecord) -> None:
        # Grab some metadata about the record.
        level, depth = self._get_level_and_depth(record)

        # Parse/filter the message. Filtered messages
        message, log_strategy = self._get_message_and_strategy(record)

        if log_strategy == self._FILTER:
            pass
        elif log_strategy == self._LIFT:
            logger.info(message)
        else:  # log_strategy == self._RE_EMIT
            logger.opt(depth=depth, exception=record.exc_info).log(level, message)

        # Finally, relog the original at the jobmon logging level.
        original_message = record.getMessage()
        logger.opt(depth=depth, exception=record.exc_info).log(
            JOBMON_LOGGING_LEVEL, original_message
        )

    def _get_message_and_strategy(self, record: logging.LogRecord) -> Tuple[str, int]:
        # If it's more important than an INFO message just re-emit.
        if record.levelno > logging.INFO:
            return record.getMessage(), self._RE_EMIT
        elif self._should_drop(record):
            return record.getMessage(), self._FILTER
        else:
            return self._parse_record(record)

    def _should_drop(self, record: logging.LogRecord) -> bool:
        # drop_list is tuples of (logger_name, [ignore_functions])
        # where logger_name is usually the name of the module
        # being logged from (though occasionally a module
        # higher in the call stack) and each ignore_function is
        # the function or method that is logging a message.
        drop_list = (
            (
                'jobmon.client.workflow',
                ['add_task', '_distributor_alive']
            ),
            (
                'jobmon.client.distributor.distributor_service',
                ['_create_task_instance', '_keep_distributing', 'heartbeat',
                 '_get_lost_task_instances', '_distribute_forever']
            ),
            # Finally, drop any messages from these functions
            # regardless of where they're called from.
            (record.name, ['_send_request', 'is_5XX'])
        )
        for logger_name, ignore_functions in drop_list:
            if record.name == logger_name and record.funcName in ignore_functions:
                return True
        return False

    def _parse_record(self, record: logging.LogRecord) -> Tuple[str, int]:
        msg = record.getMessage()
        strategy = self._RE_EMIT

        if record.name == 'jobmon.client.distributor.distributor_service':
            # Couldn't filter these before without looking in the message.
            strategy = self._FILTER
            # We don't want these messages, but we want what's in them.
            if 'active distributor_ids:' in msg:
                queued_or_running = str(len(msg.split(',')))
                # This updates every 30s, which is a reasonable
                # frequency to log the workflow status.
                msg = f'Queued or running: {queued_or_running}'
                strategy = self._LIFT

        return msg, strategy

    @staticmethod
    def _get_level_and_depth(record: logging.LogRecord) -> Tuple[Union[int, str], int]:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        return level, depth


def intercept_jobmon_logs(level: Union[str, int]) -> None:
    """Add a handler to all the jobmon loggers to intercept and filter/parse the messages."""
    handler = JobmonInterceptHandler(level)
    for name, logger_ in logging.Logger.manager.loggerDict.items():
        if 'jobmon' in name and not isinstance(logger_, logging.PlaceHolder):
            logger_.handlers = [handler]


def list_loggers():
    """Utility function for analyzing the logging environment."""
    root_logger = logging.getLogger()
    print("Root logger: ", root_logger)
    for h in root_logger.handlers:
        print(f'     %s' % h)

    print("Other loggers")
    print("=============")
    for name, logger_ in logging.Logger.manager.loggerDict.items():
        print('+ [%-20s] %s ' % (name, logger_))
        if not isinstance(logger_, logging.PlaceHolder):
            for h in logger_.handlers:
                print('     %s' % h)

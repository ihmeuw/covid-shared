import logging
from pathlib import Path
import sys
import typing
from typing import Union

from loguru import logger

from covid_shared import paths
from covid_shared.shell_tools import mkdir


class JobmonInterceptHandler(logging.Handler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._queued = 0
        self._running = 0

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        message, log_from_here = self.parse_record(record)
        if message is None:
            return
        elif log_from_here:
            logger.info(message)
        else:
            logger.opt(depth=depth, exception=record.exc_info).log(
                level, message,
            )

    def parse_record(self, record):
        log_from_here = False
        if record.levelno > logging.INFO:
            return record.getMessage(), log_from_here
        drop = (
            (
                record.funcName in ['_send_request', 'is_5XX']
            ) or (
                record.name == 'jobmon.client.workflow'
                and record.funcName in ['add_task', '_distributor_alive']
            ) or (
                record.name == 'jobmon.client.distributor.distributor_service'
                and record.funcName in ['_create_task_instance', '_keep_distributing', 'heartbeat', '_get_lost_task_instances', '_distribute_forever']
            )
        )
        if drop:
            msg = None
        elif record.name == 'jobmon.client.distributor.distributor_service':
            msg = record.getMessage()
            if 'active distributor_ids:' in msg:
                self._running = str(len(msg.split(',')) - 1)
                msg = f'Queued: {self._queued}, Running: {self._running}'
                log_from_here = True
            elif 'Queued' in msg:
                self._queued = msg.split(' ')[1]
                msg = f'Queued: {self._queued}, Running: {self._running}'
                log_from_here = True
            else:
                msg = None
        else:
            msg = record.getMessage()
        return msg, log_from_here


DEFAULT_LOG_MESSAGING_FORMAT = ('<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
                                '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> '
                                '- <level>{message}</level> - {extra}')

LOG_FORMATS = {
    # Keys are verbosity.  Specify special log formats here.
    0: ("WARNING", DEFAULT_LOG_MESSAGING_FORMAT),
    1: ("INFO", DEFAULT_LOG_MESSAGING_FORMAT),
    2: ("DEBUG", DEFAULT_LOG_MESSAGING_FORMAT),
}

def listloggers():
    rootlogger = logging.getLogger()
    print(rootlogger)
    for h in rootlogger.handlers:
        print('     %s' % h)

    import pdb; pdb.set_trace()
    for nm, lgr in logging.Logger.manager.loggerDict.items():
        print('+ [%-20s] %s ' % (nm, lgr))
        if not isinstance(lgr, logging.PlaceHolder):
            for h in lgr.handlers:
                print('     %s' % h)


def intercept_jobmon_logs(level):
    handler = JobmonInterceptHandler(level)
    for name, logger in logging.Logger.manager.loggerDict.items():
        if 'jobmon' in name and not isinstance(logger, logging.PlaceHolder):
            logger.handlers = [handler]


def add_logging_sink(sink: Union[typing.TextIO, Path], verbose: int, colorize: bool = False, serialize: bool = False):
    """Add a new output file handle for logging."""
    level, message_format = LOG_FORMATS.get(verbose, LOG_FORMATS[max(LOG_FORMATS.keys())])
    logger.add(sink, colorize=colorize, level=level, format=message_format, serialize=serialize, filter={'urllib3': 'WARNING'})


def configure_logging_to_terminal(verbose: int):
    """Setup logging to sys.stdout."""
    logger.remove()  # Clear default configuration
    level = LOG_FORMATS.get(verbose, LOG_FORMATS[max(LOG_FORMATS.keys())])[0]
    intercept_jobmon_logs(level)
    add_logging_sink(sys.stdout, verbose, colorize=True)


def configure_logging_to_files(output_path: Path) -> None:
    log_path = output_path / paths.LOG_DIR
    mkdir(log_path, exists_ok=True)
    add_logging_sink(output_path / paths.LOG_DIR / paths.DETAILED_LOG_FILE_NAME, verbose=2, serialize=True)
    add_logging_sink(output_path / paths.LOG_DIR / paths.LOG_FILE_NAME, verbose=1)

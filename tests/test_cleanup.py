from loguru import logger
import pytest

from covid_shared.cli_tools import monitor_application
from covid_shared.cli_tools.cleanup import _raise_if_exception


def function_without_exception(app_metadata):
    return


def function_interrupted(app_metadata):
    raise KeyboardInterrupt


def function_custom_exception(app_metadata):
    raise RuntimeError("custom error")


def test_do_not_raise():
    func = monitor_application(
        func=function_without_exception,
        logger_=logger,
        with_debugger=False)
    app_metadata, _result = func()
    _raise_if_exception(app_metadata)


def test_raise_interrupt():
    func = monitor_application(
        func=function_interrupted,
        logger_=logger,
        with_debugger=False)
    app_metadata, _result = func()
    with pytest.raises(KeyboardInterrupt):
        _raise_if_exception(app_metadata)


def test_raise_custom():
    func = monitor_application(
        func=function_custom_exception,
        logger_=logger,
        with_debugger=False)
    app_metadata, _result = func()
    with pytest.raises(RuntimeError, match='custom error'):
        _raise_if_exception(app_metadata)

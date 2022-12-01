"""Wrappers for IHME specific dependencies.

This module explicitly declares and wraps IHME specific code bases
to prevent CI failures at import time.

"""
import importlib
import sys
from pathlib import Path

import pandas as pd


def _lazy_import_callable(module_path: str, object_name: str):
    """Delays import errors for callables until called."""
    try:
        module = importlib.import_module(module_path)
        return getattr(module, object_name)
    except ModuleNotFoundError:

        def f(*args, **kwargs):
            raise ModuleNotFoundError(
                f"No module named '{module_path}' and so we cannot find '{object_name}'. "
                f"Ensure you have a file in your home directory at '~/.pip/pip.conf' with contents\n\n"
                f"[global]\n"
                f"extra-index-url = https://artifactory.ihme.washington.edu/artifactory/api/pypi/pypi-shared/simple\n"
                f"trusted-host = artifactory.ihme.washington.edu/artifactory/api/pypi/pypi-shared\n\n"
                f"and run 'pip install {module_path.split('.')[0]}'"
            )

        return f


try:
    from db_queries.api.internal import get_location_hierarchy_by_version
except ModuleNotFoundError:
    get_location_hierarchy_by_version = _lazy_import_callable(
        "db_queries.api.internal", "get_location_hierarchy_by_version"
    )


def load_location_hierarchy(location_set_version_id: int = None, location_file: Path = None):
    assert (location_set_version_id and not location_file) or (
        not location_set_version_id and location_file
    )

    if location_set_version_id:
        return get_location_hierarchy_by_version(
            location_set_version_id=location_set_version_id,
        )
    else:
        return pd.read_csv(location_file)


##############
# GROSS HACK #
##############
# jobmon_uge uses structlog, a library which does an endrun around
# python standard logging and then dumps a bunch of useless information
# to stdout. Before we import structlog (via jobmon_uge via jobmon),
# put the name in the system's list of imported modules as an alias
# to the python std library logging module.
sys.modules["structlog"] = sys.modules["logging"]

try:
    from jobmon.client.api import Tool
    from jobmon.client.task import Task
    from jobmon.client.workflow import WorkflowRunStatus
    from jobmon.exceptions import WorkflowAlreadyComplete
except ModuleNotFoundError:
    Tool = _lazy_import_callable("jobmon.client.api", "Tool")
    Task = _lazy_import_callable("jobmon.client.task", "Task")
    WorkflowRunStatus = _lazy_import_callable("jobmon.client.workflow", "WorkflowRunStatus")
    WorkflowAlreadyComplete = _lazy_import_callable(
        "jobmon.exceptions", "WorkflowAlreadyComplete"
    )

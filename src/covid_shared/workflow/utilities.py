import socket
from pathlib import Path
from typing import Tuple, Union

from covid_shared import shell_tools
from covid_shared.ihme_deps import Tool


class JobmonTool:
    """Lazy initialization of the jobmon Tool.

    The Task and Workflow templates both create a jobmon tool at import time.
    This has the unfortunate side effect of talking to external services
    before anything else happens. This wrapper class delays initialization
    of the tool (and therefore the service communication) until runtime.

    """

    def __init__(self, package):
        if not hasattr(package, "__jobmon_tool_version__"):
            raise AttributeError(
                f"Package {package.__name__} must define a __jobmon_tool_version__ attribute "
                f"in its package level namespace."
            )
        else:
            self._package_name = package.__name__
            self._active_tool_version_id = package.__jobmon_tool_version__
        self._tool = None

    def lazy_init_tool(self):
        if self._tool is None:
            self._tool = Tool(self._package_name)
            self._tool.active_tool_version_id = self._active_tool_version_id

    def create_workflow(self, *args, **kwargs):
        self.lazy_init_tool()
        return self._tool.create_workflow(*args, **kwargs)

    def get_task_template(self, *args, **kwargs):
        self.lazy_init_tool()
        return self._tool.get_task_template(*args, **kwargs)


def get_jobmon_tool(package) -> JobmonTool:
    return JobmonTool(package)


def make_log_dirs(log_dir: Union[str, Path]) -> Tuple[str, str]:
    """Create log directories in output root and return the paths."""
    log_dir = Path(log_dir)
    std_out = log_dir / "output"
    std_err = log_dir / "error"
    shell_tools.mkdir(std_out, exists_ok=True, parents=True)
    shell_tools.mkdir(std_err, exists_ok=True, parents=True)

    return str(std_out), str(std_err)


def get_cluster_name() -> "str":
    hostname = socket.gethostname()

    if "slurm" in hostname:
        cluster, submit_host_marker = "slurm", "slogin"
    elif "uge" in hostname:
        cluster, submit_host_marker = "buster", "submit"
    else:
        raise RuntimeError("This tool must be run from an IHME cluster.")

    if submit_host_marker in hostname:
        raise RuntimeError("This tool must not be run from a submit host.")
    return cluster

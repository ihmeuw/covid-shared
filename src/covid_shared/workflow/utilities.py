from pathlib import Path
from typing import Tuple, Union

from covid_shared import shell_tools
from covid_shared.ihme_deps import Tool


def get_jobmon_tool(package) -> Tool:
    tool = Tool.create_tool(package.__name__)
    if hasattr(package, '__jobmon_tool_version__'):
        tool.active_tool_version_id = package.__jobmon_tool_version__
    else:
        raise AttributeError(f"Package {package.__name__} must define a __jobmon_tool_version__ attribute "
                             f"in its package level namespace.")
    return tool


def make_log_dirs(log_dir: Union[str, Path]) -> Tuple[str, str]:
    """Create log directories in output root and return the paths."""
    log_dir = Path(log_dir)
    std_out = log_dir / 'output'
    std_err = log_dir / 'error'
    shell_tools.mkdir(std_out, exists_ok=True, parents=True)
    shell_tools.mkdir(std_err, exists_ok=True, parents=True)

    return str(std_out), str(std_err)

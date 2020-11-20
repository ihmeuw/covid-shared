from pathlib import Path
from typing import Optional

from covid_shared.cli_tools.metadata import Metadata, RunMetadata
from covid_shared.cli_tools.run_directory import make_links


def finish_application(
    run_metadata: RunMetadata,
    app_metadata: Metadata,
    run_directory: Path,
    mark_as_best: bool,
    production_tag: Optional[str]
) -> None:
    """
    Every cli tool should do the following:
        1. serialize metadata to disk
        2. update symlinks (if successful application)
        3. raise exception (if not sucessful)

    Parameters
    ------------
        run_metadata: metadata from cli invocation
        app_metadata: metadata from application getting monitored
        run_directory: output path of application
        mark_as_best: whether to update 'best' symlink
        production_tag: what string to tag prod run, if any
    """
    run_metadata['app_metadata'] = app_metadata.to_dict()
    run_metadata.dump(run_directory / 'metadata.yaml')

    # Configure latest or best symlink
    make_links(app_metadata, run_directory, mark_as_best, production_tag)

    _raise_if_exception(app_metadata)


def _raise_if_exception(app_metadata: Metadata) -> None:
    """
    CLI tools should return a non-zero error code in the case of an error.
    cli_tools.monitor_application catches exceptions so we need to look for
    and raise any exception in the app metadata if it exists.

    There are 3 cases:
        1. no exception. In that case metadata contains success=True
        2. user interrupt. In that case metadata contains success=False and
            error_info='User interrupt.'
        3. any other exception: metadata contains success=False and error_info
            is a dictionary with keys 'exception_type', 'exception_value',
            'exc_traceback'
    """
    if app_metadata['success']:
        return

    error_info = app_metadata['error_info']
    user_interrupt = 'interrupt' in error_info
    if user_interrupt:
        raise KeyboardInterrupt
    else:
        raise error_info['exception_value']

import functools
import types

import click

from covid_shared.cli_tools.metadata import RunMetadata, get_function_full_argument_mapping


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


def pass_run_metadata(run_metadata=RunMetadata()):
    """Decorator for cli entry points to inject a run metadata object and
    record arguments.

    Parameters
    ----------
    run_metadata
        The metadata object to inject.

    """

    def _pass_run_metadata(app_entry_point: types.FunctionType):

        @functools.wraps(app_entry_point)
        def _wrapped(*args, **kwargs):
            # Record arguments for the run and inject the metadata.
            run_metadata['tool_name'] = f'{app_entry_point.__module__}:{app_entry_point.__name__}'
            run_metadata['run_arguments'] = get_function_full_argument_mapping(app_entry_point,
                                                                               run_metadata, *args, **kwargs)
            return app_entry_point(run_metadata, *args, **kwargs)

        return _wrapped

    return _pass_run_metadata

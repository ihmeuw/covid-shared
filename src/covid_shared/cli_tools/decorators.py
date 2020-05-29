import functools
from pathlib import Path
import types

import click

from covid_shared.cli_tools.metadata import RunMetadata, get_function_full_argument_mapping
from covid_shared.paths import BEST_LINK, R_SINGULARITY_IMAGE_PATH


# Common click options
logging_options = [
    click.option('--pdb', 'with_debugger',
                 is_flag=True,
                 help='Drop into python debugger if an error occurs.'),
    click.option('-v', 'verbose',
                 count=True,
                 help='Configure logging verbosity.'),
]


def add_verbose_and_with_debugger(func: types.FunctionType):
    """Add all the shared options to the command."""
    for option in logging_options:
        func = option(func)
    return func


def pass_run_metadata(run_metadata: RunMetadata = RunMetadata()):
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


def add_r_singularity_option():
    """
    Decorator to set R environment to use in a CLI command.
    """
    def wrapper(entry_point: types.FunctionType):
        entry_point = click.option(
            '--r-singularity-image', 'r_singularity_image',
            type=click.Path(file_okay=True),
            default=R_SINGULARITY_IMAGE_PATH,
            help=(f"Path to a specific R singularity. Can pass 'None' to use active conda environment. "
                  f"By default uses {R_SINGULARITY_IMAGE_PATH}.")
        )(entry_point)

        return entry_point
    return wrapper


def add_output_options(default_output_root: Path):
    """
    Decorator to set CLI command options required when producing outputs.
    """
    def wrapper(entry_point: types.FunctionType):

        entry_point = click.option(
            "-o", "--output-root",
            type=click.Path(file_okay=False),
            default=default_output_root,
            help=(f"Directory to outputs. Defaults to {default_output_root}/YYYY_MM_DD.VV for today's date and the "
                  "newest uncreated version")
        )(entry_point)

        entry_point = click.option(
            '-p', '--production-tag',
            type=click.STRING,
            help='Tags this run as a production run.'
        )(entry_point)

        entry_point = click.option(
            '-b', '--mark-best',
            is_flag=True,
            help='Mark this run as "best"'
        )(entry_point)

        return entry_point
    return wrapper


def _create_dependency_option(data_source: str, default: Path = BEST_LINK):
    """
    Declares a dependency on a specific version of some data source, with a default option

    Parameters
    ----------
    data_source
        The name of the data source. Multiple words should be separated by '-'
    default
        The default location of the dependency. If None is provided, there is no default and the option is required.
    """
    def wrapper(entry_point: types.FunctionType):
        click_args = {
            'type': click.Path(file_okay=False),
            'help': f'Version of the {data_source.replace("-", " ")} to use. Defaults to "{default}"',
        }
        if default is not None:
            click_args['default'] = default
            click_args['help'] = f'Version of the {data_source.replace("-", " ")} to use. Defaults to "{default}"',
        else:
            click_args['required'] = True
            click_args['help'] = f'Version of the {data_source.replace("-", " ")} to use. Required."',

        entry_point = click.option(
            f"--{data_source}-version",
            **click_args
        )(entry_point)

        return entry_point
    return wrapper


def add_mobility_gpr_dependency_option():
    """
    Declares a dependency on a specific mobility gpr version. Has no default and is required if added.
    """
    return _create_dependency_option('mobility-gpr', None)


def add_model_inputs_dependency_option():
    """
    Declares a dependency on a specific model inputs version. Defaults to "best".
    """
    return _create_dependency_option('model-inputs')


def add_seir_covariates_dependency_option():
    """
    Declares a dependency on a specific seir covariates version. Defaults to "best".
    """
    return _create_dependency_option('seir-covariates')


def add_snapshot_dependency_option():
    """
    Declares a dependency on a specific snapshot version. Defaults to "best".
    """
    return _create_dependency_option('snapshot')

"""Manages all path metadata."""
from pathlib import Path
from datetime import datetime

##################
# Executor paths #
##################
EXEC_R_SCRIPT_PATH = Path('/share/singularity-images/lbd/shells/singR.sh')
R_SINGULARITY_IMAGE_PATH = Path('/ihme/singularity-images/lbd/releases/lbd_full_20200128.simg')

################
# Shared paths #
################
# Concrete share drive root
COVID_19_2 = Path('/ihme/covid-19-2')
ARCHIVE_ROOT = COVID_19_2 / 'archive'

# Main share drive root. This is a symlink farm for COVID_19_2.
# All paths should point here.
COVID_19 = Path('/ihme/covid-19')

# Shared config for running rclone on the IHME OneDrive
RCLONE_CONFIG_PATH = COVID_19 / '.config' / 'rclone' / 'rclone.conf'

# Top level directories.  These represent, mostly, outputs of pipeline stages.
# Keep them in alphabetical order.
# TODO: This should definitely be in a container.
AGE_SPECIFIC_RATES_ROOT = COVID_19 / 'age-specific-rates'
AIRLINE_DATA_ROOT = COVID_19 / 'airline-data'
DATA_FIXES_ROOT = COVID_19 / 'data-fixes'
DATA_INTAKE_ROOT = COVID_19 / 'data_intake'
DURATIONS_ROOT = COVID_19 / 'durations'
EXCESS_MORTALITY_ROOT = COVID_19 / 'excess-mortality'
GBD_ROOT = COVID_19 / 'gbd'
HISTORICAL_MODEL_ROOT = COVID_19 / 'historical-model'
MANDATES_ROOT = COVID_19 / 'mandates'
MASK_USE_OUTPUT_ROOT = COVID_19 / 'mask-use-outputs'
MOBILITY_COVARIATES_OUTPUT_ROOT = COVID_19 / 'mobility-covariate'
MOBILITY_COVARIATES_GPR_OUTPUT_ROOT = MOBILITY_COVARIATES_OUTPUT_ROOT / 'gpr_outputs'
MODEL_INPUTS_ROOT = COVID_19 / 'model-inputs'
MORTALITY_AGE_PATTERN_ROOT = COVID_19 / 'mortality-age-pattern'
PAST_INFECTIONS_ROOT = COVID_19 / 'past-infections'
PNEUMONIA_OUTPUT_ROOT = COVID_19 / 'pneumonia'
POPULATION_DENSITY_OUTPUT_ROOT = COVID_19 / 'population-density'
RESULTRON_ROOT = COVID_19 / 'resultron'
SEIR_COUNTERFACTUAL_INPUT_ROOT = COVID_19 / 'seir-counterfactual-input'
SEIR_COUNTERFACTUAL_ROOT = COVID_19 / 'seir-counterfactual'
SEIR_COVARIATE_PRIORS_ROOT = COVID_19 / 'seir-covariate-priors'
SEIR_COVARIATES_OUTPUT_ROOT = COVID_19 / 'seir-covariates'
SEIR_DIAGNOSTICS_OUTPUTS = COVID_19 / 'seir-diagnostics'
SEIR_FORECAST_OUTPUTS = COVID_19 / 'seir-forecast'
SEIR_FINAL_OUTPUTS = COVID_19 / 'seir-outputs'
SEIR_REGRESSION_OUTPUTS = COVID_19 / 'seir-regression'
SHAPEFILE_ROOT = COVID_19 / 'shapefiles'
SNAPSHOT_ROOT = COVID_19 / 'snapshot-data'
STATIC_DATA_INPUTS_ROOT = COVID_19 / 'static-data'
SYMPTOM_SURVEY_ROOT = COVID_19 / 'symptom-survey-data'
TESTING_OUTPUT_ROOT = COVID_19 / 'testing-outputs'
UNVERSIONED_INPUTS_ROOT = COVID_19 / 'unversioned-inputs'
VACCINE_COVERAGE_OUTPUT_ROOT = COVID_19 / 'vaccine-coverage'
VARIANT_OUTPUT_ROOT = COVID_19 / 'variant-scaleup'
VISIT_VOLUME_ROOT = COVID_19 / 'visit-volume/'
WEBSCRAPER_ROOT = COVID_19 / 'webscrape'


######################################
# Shared file and subdirectory names #
######################################
METADATA_FILE_NAME = Path('metadata.yaml')

LOG_DIR = Path("logs")
LOG_FILE_NAME = Path("master_log.txt")
DETAILED_LOG_FILE_NAME = Path("master_log.json")

BEST_LINK = Path('best')
LATEST_LINK = Path('latest')
PRODUCTION_RUN = Path('production-runs')


def latest_production_snapshot_path():
    return _latest_prod_path(SNAPSHOT_ROOT)


def latest_production_etl_path():
    return _latest_prod_path(MODEL_INPUTS_ROOT)


def _latest_prod_path(prefix: Path):
    prod_run_dir = prefix / PRODUCTION_RUN
    prod_runs = [d for d in prod_run_dir.iterdir()]
    sorted_runs = list(sorted(prod_runs, key=lambda p: datetime.strptime(p.stem, '%Y_%m_%d')))
    return sorted_runs[-1]


#################
# I/O utilities #
#################

# TODO: Set the ihme-covid user group.  Don't think I can do this without sudo.
DIRECTORY_PERMISSIONS = 0o775
FILE_PERMISSIONS = 0o664


def make_dir_tree(directory: Path):
    """Makes all directories and their parents with the correct permissions.

    Parameters
    ----------
    directory
        The directory to make.

    This skirts around the default behavior of :func:`Path.mkdir` which
    mimics `mkdir -p` which will create a dir with requested permissions,
    but all parent directories with default permissions.

    """
    to_create = []
    p = directory
    while not p.exists():
        to_create.append(p)
        p = p.parent
    while to_create:
        to_create.pop().mkdir(DIRECTORY_PERMISSIONS)


def recursive_set_permissions(path: Path):
    """Recursively set permissions to defaults."""
    if path.is_file():
        path.chmod(FILE_PERMISSIONS)
    else:
        path.chmod(DIRECTORY_PERMISSIONS)
        for p in path.iterdir():
            recursive_set_permissions(p)

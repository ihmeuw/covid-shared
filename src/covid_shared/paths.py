"""Manages all path metadata."""
from pathlib import Path
from datetime import datetime

# Input data paths
JOHNS_HOPKINS_REPO = 'https://github.com/CSSEGISandData/COVID-19/archive/master.zip'
ITALY_REPO = 'https://github.com/pcm-dpc/COVID-19/archive/master.zip'
DESCARTES_REPO = 'https://github.com/descarteslabs/DL-COVID-19/archive/master.zip'
NY_TIMES_REPO = 'https://github.com/nytimes/covid-19-data/archive/master.zip'
ONEDRIVE_PATH = "covid-onedrive:'COVID-19 Resource Hub'"
NOAA_PM_DATA = "ftp://ftp.cdc.noaa.gov/Datasets/ncep.reanalysis.dailyavgs/surface_gauss/air.2m.gauss.2020.nc"
CITYMAPPER_MOBILITY_TEMPLATE = "https://cdn.citymapper.com/data/cmi/Citymapper_Mobility_Index_{DATE}.csv"


# Shared paths
EXEC_R_SCRIPT_PATH = Path('/share/singularity-images/lbd/shells/singR.sh')
R_SINGULARITY_IMAGE_PATH = Path('/ihme/singularity-images/lbd/releases/lbd_full_20200128.simg')

RCLONE_CONFIG_PATH = Path('/ihme/covid-19/.config/rclone/rclone.conf')

UNVERSIONED_INPUTS_ROOT = Path('/ihme/covid-19/unversioned-inputs')
STATIC_DATA_INPUTS_ROOT = Path('/ihme/covid-19/static-data')
SNAPSHOT_ROOT = Path('/ihme/covid-19/snapshot-data/')
MODEL_INPUTS_ROOT = Path('/ihme/covid-19/model-inputs/')

DEATHS_OUTPUT_ROOT = Path('/ihme/covid-19/deaths-outputs/')
INFECTIONATOR_OUTPUTS = Path('/ihme/covid-19/seir-inputs')

TEMPERATURE_OUTPUT_ROOT = Path('/ihme/covid-19/temperature/')
POPULATION_DENSITY_OUTPUT_ROOT = Path('/ihme/covid-19/population-density')
MOBILITY_COVARIATES_OUTPUT_ROOT = Path('/ihme/covid-19/mobility-covariate')
TESTING_OUTPUT_ROOT = Path('/ihme/covid-19/testing-outputs')
SEIR_COVARIATES_RAW_OUTPUT_ROOT = Path('/ihme/covid-19/seir-covariates-raw')
SEIR_COVARIATES_OUTPUT_ROOT = Path('/ihme/covid-19/seir-covariates')

SEIR_FIT_OUTPUTS = Path('/ihme/covid-19/seir-fit')
SEIR_REGRESSION_OUTPUTS = Path('/ihme/covid-19/seir-regression')
SEIR_FORECAST_OUTPUTS = Path('/ihme/covid-19/seir-forecast')


# Shared file names
METADATA_FILE_NAME = Path('metadata.yaml')
BEST_LINK = Path('best')
LATEST_LINK = Path('latest')
PRODUCTION_RUN = Path('production-runs')

JOHNS_HOPKINS_OUTPUT_DIR_NAME = Path('johns_hopkins_repo')
ITALY_OUTPUT_DIR_NAME = Path('italy_repo')
NY_TIMES_OUTPUT_DIR_NAME = Path('ny_times_repo')
NOAA_OUTPUT_DIR_NAME = Path('noaa_data')
MOBILITY_OUTPUT_DIR_NAME = Path('mobility_data')
ONEDRIVE_OUTPUT_DIR_NAME = Path('covid_onedrive')

LOG_DIR = Path("logs")
LOG_FILE_NAME = Path("master_log.txt")
DETAILED_LOG_FILE_NAME = Path("master_log.json")


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

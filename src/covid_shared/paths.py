"""Manages all path metadata."""
from pathlib import Path
from datetime import datetime

# Input data paths
JOHNS_HOPKINS_REPO = 'https://github.com/CSSEGISandData/COVID-19/archive/master.zip'
ITALY_REPO = 'https://github.com/pcm-dpc/COVID-19/archive/master.zip'
DESCARTES_REPO = 'https://github.com/descarteslabs/DL-COVID-19/archive/master.zip'
ONEDRIVE_PATH = "covid-onedrive:'COVID-19 Resource Hub'"
CITYMAPPER_MOBILITY_TEMPLATE = "https://cdn.citymapper.com/data/cmi/Citymapper_Mobility_Index_{DATE}.csv"


# Shared paths
RCLONE_CONFIG_PATH = Path('/ihme/covid-19/.config/rclone/rclone.conf')
SNAPSHOT_ROOT = Path('/ihme/covid-19/snapshot-data/')
MODEL_INPUTS_ROOT = Path('/ihme/covid-19/model-inputs/')

# Shared file names
METADATA_FILE_NAME = 'metadata.yaml'
BEST_LINK = 'best'
LATEST_LINK = 'latest'
PRODUCTION_RUN = 'production-runs'

JOHNS_HOPKINS_OUTPUT_DIR_NAME = 'johns_hopkins_repo'
ITALY_OUTPUT_DIR_NAME = 'italy_repo'
MOBILITY_OUTPUT_DIR_NAME = 'mobility_data'
ONEDRIVE_OUTPUT_DIR_NAME = 'covid_onedrive'


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




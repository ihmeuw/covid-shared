"""Manages all path metadata."""
from pathlib import Path

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

JOHNS_HOPKINS_OUTPUT_DIR_NAME = 'johns_hopkins_repo'
ITALY_OUTPUT_DIR_NAME = 'italy_repo'
MOBILITY_OUTPUT_DIR_NAME = 'mobility_data'
ONEDRIVE_OUTPUT_DIR_NAME = 'covid_onedrive'



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




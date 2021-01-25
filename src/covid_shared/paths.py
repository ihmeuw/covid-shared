"""Manages all path metadata."""
from pathlib import Path
from datetime import datetime

# Input data paths
JOHNS_HOPKINS_REPO = 'https://github.com/CSSEGISandData/COVID-19/archive/master.zip'
ITALY_REPO = 'https://github.com/pcm-dpc/COVID-19/archive/master.zip'
DESCARTES_REPO = 'https://github.com/descarteslabs/DL-COVID-19/archive/master.zip'
NY_TIMES_REPO = 'https://github.com/nytimes/covid-19-data/archive/master.zip'
ONEDRIVE_PATH = "covid-onedrive:'COVID-19 Resource Hub'"
CITYMAPPER_MOBILITY_TEMPLATE = "https://cdn.citymapper.com/data/cmi/Citymapper_Mobility_Index_{DATE}.csv"
OPEN_COVID19_GROUP_REPO = "https://github.com/beoutbreakprepared/nCoV2019/archive/master.zip"
CDC_DEATHS_BY_RACE_ETHNICITY_AGE_STATE = "https://data.cdc.gov/api/views/ks3g-spdg/rows.csv?accessType=DOWNLOAD"
DATA_INTAKE_J_DIR = Path('/home/j/Project/covid/data_intake')
SEROSURVEY_SUPPLEMENTAL_DATA = DATA_INTAKE_J_DIR / 'serology/supplemental_serosurvey_metadata'
US_SYMPTOM_SURVEY_DATA = DATA_INTAKE_J_DIR / 'symptom_survey/us'
GLOBAL_SYMPTOM_SURVEY_DATA = DATA_INTAKE_J_DIR / 'symptom_survey/global'
PULSE_SURVEY_DATA = DATA_INTAKE_J_DIR / 'pulse_survey/US Census_pulse surveys'
SOCIAL_DISTANCING_DATA = DATA_INTAKE_J_DIR / 'social distancing'
CFR_AGE_MAX_PLANCK_DATA = DATA_INTAKE_J_DIR / 'CFR-age/MaxPlanck'
HHS_DATA = DATA_INTAKE_J_DIR / 'hhs'

# Shared paths
EXEC_R_SCRIPT_PATH = Path('/share/singularity-images/lbd/shells/singR.sh')
R_SINGULARITY_IMAGE_PATH = Path('/ihme/singularity-images/lbd/releases/lbd_full_20200128.simg')

RCLONE_CONFIG_PATH = Path('/ihme/covid-19/.config/rclone/rclone.conf')

UNVERSIONED_INPUTS_ROOT = Path('/ihme/covid-19/unversioned-inputs')
STATIC_DATA_INPUTS_ROOT = Path('/ihme/covid-19/static-data')
SNAPSHOT_ROOT = Path('/ihme/covid-19/snapshot-data/')
MODEL_INPUTS_ROOT = Path('/ihme/covid-19/model-inputs/')
VISIT_VOLUME_ROOT = Path('/ihme/covid-19/visit-volume/')
MORTALITY_RATIO_ROOT = Path('/ihme/covid-19/mortality-ratio')
INFECTION_FATALITY_RATIO_ROOT = Path('/ihme/covid-19/infection-fatality-ratio')
INFECTION_HOSPITALIZATION_RATIO_ROOT = Path('/ihme/covid-19/infection-hospitalization-ratio')
INFECTION_DETECTION_RATE_ROOT = Path('/ihme/covid-19/infection-detection-rate')
HOSPITAL_DEATH_RATIO_ROOT = Path('/ihme/covid-19/hospitalization-death-ratio')
DEATHS_SPLINE_OUTPUT_ROOT = Path('/ihme/covid-19/deaths-outputs/')
PAST_INFECTIONS_ROOT = Path('/ihme/covid-19/past-infections')
INFECTIONATOR_OUTPUTS = Path('/ihme/covid-19/seir-inputs')
SHAPEFILE_ROOT = Path('/ihme/covid-19/shapefiles')
WEBSCRAPER_ROOT = Path('/ihme/covid-19/webscrape')

MASK_USE_OUTPUT_ROOT = Path('/ihme/covid-19/mask-use-outputs')
PNEUMONIA_OUTPUT_ROOT = Path('/ihme/covid-19/pneumonia')
POPULATION_DENSITY_OUTPUT_ROOT = Path('/ihme/covid-19/population-density')
MOBILITY_COVARIATES_OUTPUT_ROOT = Path('/ihme/covid-19/mobility-covariate')
MOBILITY_COVARIATES_GPR_OUTPUT_ROOT = MOBILITY_COVARIATES_OUTPUT_ROOT / 'gpr_outputs'
TESTING_OUTPUT_ROOT = Path('/ihme/covid-19/testing-outputs')
VACCINE_COVERAGE_OUTPUT_ROOT = Path('/ihme/covid-19/vaccine-coverage')
SEIR_COVARIATES_OUTPUT_ROOT = Path('/ihme/covid-19/seir-covariates')

SEIR_REGRESSION_OUTPUTS = Path('/ihme/covid-19/seir-regression')
SEIR_FORECAST_OUTPUTS = Path('/ihme/covid-19/seir-forecast')
SEIR_FINAL_OUTPUTS = Path('/ihme/covid-19/seir-outputs')
SEIR_DIAGNOSTICS_OUTPUTS = Path('/ihme/covid-19/seir-diagnostics')


# Shared file names
METADATA_FILE_NAME = Path('metadata.yaml')
BEST_LINK = Path('best')
LATEST_LINK = Path('latest')
PRODUCTION_RUN = Path('production-runs')

JOHNS_HOPKINS_OUTPUT_DIR_NAME = Path('johns_hopkins_repo')
ITALY_OUTPUT_DIR_NAME = Path('italy_repo')
NY_TIMES_OUTPUT_DIR_NAME = Path('ny_times_repo')
CDC_OUTPUT_DIR_NAME = Path('cdc_data')
MOBILITY_OUTPUT_DIR_NAME = Path('mobility_data')
ONEDRIVE_OUTPUT_DIR_NAME = Path('covid_onedrive')
OPEN_COVID19_OUTPUT_DIR_NAME = Path('open_covid19_working_group')
SEROSURVEY_OUTPUT_DIR_NAME = Path('serosurvey_data')
SEROSURVEY_SUPPLEMENTAL_OUTPUT_DIR_NAME = Path('supplemental_serosurvey_metadata')
SYMPTOM_SURVEY_OUTPUT_DIR_NAME = Path('symptom_survey')
US_SYMPTOM_SURVEY_OUTPUT_DIR_NAME = Path('us')
GLOBAL_SYMPTOM_SURVEY_OUTPUT_DIR_NAME = Path('global')
PULSE_SURVEY_OUTPUT_DIR_NAME = Path('pulse_survey')
PULSE_SURVEY_US_CENSUS_OUTPUT_DIR_NAME = Path('US Census_pulse surveys')
SOCIAL_DISTANCING_DIR_NAME = Path('social distancing')
CFR_AGE_DIR_NAME = Path('cfr_age')
CFR_AGE_MAX_PLANCK_DIR_NAME = Path('MaxPlanck')
HHS_DIR_NAME = Path('hhs_data')

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

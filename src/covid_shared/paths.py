"""Manages all path metadata."""
from pathlib import Path
from datetime import datetime

# Input data paths
JOHNS_HOPKINS_REPO = 'https://github.com/CSSEGISandData/COVID-19/archive/master.zip'
DESCARTES_REPO = 'https://github.com/descarteslabs/DL-COVID-19/archive/master.zip'
NY_TIMES_REPO = 'https://github.com/nytimes/covid-19-data/archive/master.zip'
ONEDRIVE_PATH = "covid-onedrive:'COVID-19 Resource Hub'"
OPEN_COVID19_GROUP_REPO = "https://github.com/beoutbreakprepared/nCoV2019/archive/master.zip"
CDC_DEATHS_BY_RACE_ETHNICITY_AGE_STATE = "https://data.cdc.gov/api/views/ks3g-spdg/rows.csv?accessType=DOWNLOAD"

# J: drive paths
DATA_INTAKE_J_DIR = Path('/home/j/Project/covid/data_intake')
SEROLOGY_DATA = DATA_INTAKE_J_DIR / 'serology'
SEROSURVEY_SUPPLEMENTAL_DATA = SEROLOGY_DATA / 'supplemental_serosurvey_metadata'
WANING_IMMUNITY_DATA = SEROLOGY_DATA / 'waning_immunity'
PULSE_SURVEY_DATA = DATA_INTAKE_J_DIR / 'pulse_survey/US Census_pulse surveys'
SOCIAL_DISTANCING_DATA = DATA_INTAKE_J_DIR / 'social distancing'
CFR_AGE_MAX_PLANCK_DATA = DATA_INTAKE_J_DIR / 'CFR-age/MaxPlanck'
HHS_DATA = DATA_INTAKE_J_DIR / 'hhs'
VACCINE_DATA = DATA_INTAKE_J_DIR / 'vaccine'
MEXICO_CFR_AGE = DATA_INTAKE_J_DIR / 'data' / 'out' / 'cfr-age' / 'mexico' / 'latest'
MEXICO_HFR_AGE = DATA_INTAKE_J_DIR / 'data' / 'out' / 'hospitalization-age' / 'mexico' / 'latest'
VARIANTS_DATA_GISAID = DATA_INTAKE_J_DIR / 'GISAID'
VARIANTS_DATA = DATA_INTAKE_J_DIR / 'variants'

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
MORTALITY_RATIO_ROOT = COVID_19 / 'mortality-ratio'
PAST_INFECTIONS_ROOT = COVID_19 / 'past-infections'
PNEUMONIA_OUTPUT_ROOT = COVID_19 / 'pneumonia'
POPULATION_DENSITY_OUTPUT_ROOT = COVID_19 / 'population-density'
RESULTRON_ROOT = COVID_19 / 'resultron'
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

# ???
JOHNS_HOPKINS_OUTPUT_DIR_NAME = Path('johns_hopkins_repo')
NY_TIMES_OUTPUT_DIR_NAME = Path('ny_times_repo')
CDC_OUTPUT_DIR_NAME = Path('cdc_data')
MOBILITY_OUTPUT_DIR_NAME = Path('mobility_data')
ONEDRIVE_OUTPUT_DIR_NAME = Path('covid_onedrive')
OPEN_COVID19_OUTPUT_DIR_NAME = Path('open_covid19_working_group')
SEROSURVEY_OUTPUT_DIR_NAME = Path('serosurvey_data')
SEROSURVEY_SUPPLEMENTAL_OUTPUT_DIR_NAME = Path('supplemental_serosurvey_metadata')
SYMPTOM_SURVEY_OUTPUT_DIR_NAME = Path('symptom_survey')
PULSE_SURVEY_OUTPUT_DIR_NAME = Path('pulse_survey')
PULSE_SURVEY_US_CENSUS_OUTPUT_DIR_NAME = Path('US Census_pulse surveys')
SOCIAL_DISTANCING_DIR_NAME = Path('social distancing')
CFR_AGE_DIR_NAME = Path('cfr_age')
CFR_AGE_MAX_PLANCK_DIR_NAME = Path('MaxPlanck')
HHS_DIR_NAME = Path('hhs_data')
VACCINE_DIR_NAME = Path('vaccine')
MEXICO_CFR_AGE_DIR_NAME = Path('mexico_cfr_age')
MEXICO_HFR_AGE_DIR_NAME = Path('mexico_hfr_age')
VARIANTS_DIR_NAME = Path('Variants')
SEROLOGY_DIR_NAME = Path('serology')
WANING_IMMUNITY_DIR_NAME = Path('waning_immunity')


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

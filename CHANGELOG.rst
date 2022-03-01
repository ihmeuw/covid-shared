**2.0.0 - 03/01/2022**
 - Update jobmon tools and paths for slurm transition

**1.15.5 - 01/20/2022**
 - Add oos path.

**1.15.4 - 11/17/2021**
 - Add several paths for waning model.

**1.15.3 - 11/01/2021**
 - Remove vaccine-efficacy path, add waning-immunity path.

**1.15.2 - 11/01/2021**
 - Add model-comparison-inputs path.

**1.15.1 - 11/01/2021**
 - Add vaccine-efficacy path.

**1.15.0 - 09/20/2021**
 - Unpin db-queries version.
 - Make 'best' and production run validation more generic.

**1.14.0 - 07/27/2021**
 - Remove snapshot-only paths.

**1.13.0 - 07/27/2021**
 - Add counterfactual paths.

**1.12.0 - 07/14/2021**
 - Change data intake J: paths to /ihme/data_intake/
 
**1.11.0 - 06/11/2021**
 - Remove mortality ratio root.

**1.10.0 - 06/04/2021**
 - Added J:drive path for Google mobility data 

**1.9.0 - 06/01/2021**
 - Add exception handler utility to metadata tools.
 - Add wrapper functions for IHME internal dependencies.
 - Drop several internal and external paths that were no longer being used.
 - Add tools for building jobmon workflows and a tutorial for use.

**1.8.0 - 04/26/2021**
 - Add new symptom survey data path
 - Remove old symptom survey data paths

**1.7.0 - 04/16/2021**
 - Add /Variants/ path
 - Remove paths to /Variants/ subfolders

**1.6.0 - 04/15/2021**
 - Add age specific rates path
 - Add historical model path
 
**1.5.0 - 04/15/2021**
 - Add Denmark variants path

**1.4.0 - 04/09/2021**
 - Add modify existing and add new variants data path
 
**1.3.0 - 03/19/2021**
 - Add waning immunity path

**1.2.0 - 03/12/2021**
 - Prevent quick runs from being marked as "latest".

**1.1.3 - 03/11/2021**
 - v1.1.2 did not properly deploy. Added wheel to build depenencies.

**1.1.2 - 03/11/2021**
 - v1.1.1 did not properly deploy.

**1.1.1 - 03/11/2021**
 - Updated Variants data path.

**1.1.0 - 03/08/2021**
 - Add validation module with check that quick runs are not marked best or for production

**1.0.59 - 03/02/2021**

 - Add Mexico CFR-age paths.

**1.0.58 - 02/17/2021**

 - Add Vaccine path

**1.0.57 - 02/01/2021**

 - Metadata fix.

**1.0.56 - 02/01/2021**

 - Add variant path.

**1.0.55 - 01/25/2021**

 - Add new ratio paths.

**1.0.54 - 01/23/2021**

 - Update HHS path.

**1.0.53 - 01/21/2021**

 - Remove NOAA paths

**1.0.52 - 01/18/2021**

 - Add new infections path.

**1.0.51 - 01/16/2021**

 - Separate verbose, with_debugger, and output root, cleanup imports.

**1.0.50 - 01/16/2021**

 - Separate mark best and production tag decorators for independent use.

**1.0.49 - 01/09/2021**

 - Add ratio paths.

**1.0.48 - 01/04/2021**

 - Add SEIR diagnostics path.

**1.0.47 - 12/17/2020**

 - Add visit-volume directory to paths.

**1.0.46 - 12/14/2020**

 - More CI bugfixes.

**1.0.45 - 12/14/2020**

 - Only deploy on successful test pass.

**1.0.44 - 12/14/2020**

 - CI bugfixes.

**1.0.43 - 12/14/2020**

 - Switch to github actions for ci workflow.

**1.0.42 - 12/11/2020**

 - Add path for HHS data on J drive

**1.0.41 - 12/09/2020**

 - Add path for CFR-age MaxPlanck data on J drive

**1.0.40 - 11/19/2020**

 - Add path for survey data on J drive
 - Remove old paths
 - Return non-zero exit codes on application failure

**1.0.39 - 10/21/2020**

 - Add path for survey data on J drive

**1.0.38 - 10/21/2020**

 - Add path for new vaccine-coverage covariate.

**1.0.37 - 10/20/2020**

 - Add path for serosurvey supplemental metadata.

 **1.0.36 - 10/19/2020**

 - Change CDC race/ethnicity data path (old path had truncated data).

**1.0.35 - 09/24/2020**

 - Add path for SEIR final outputs.

**1.0.34 - 08/21/2020**

 - Add path for CDC race/ethnicity data.

**1.0.33 - 07/14/2020**

 - Add path for webscraper outputs.

**1.0.32 - 06/12/2020**

 - Expand cli tools interface.

**1.0.31 - 06/12/2020**

 - Add path for shapefiles.

**1.0.30 - 06/11/2020**

 - Add path for mask/contact interaction covariate.

**1.0.29 - 06/08/2020**

 - Add path for contact covariate.

**1.0.28 - 05/31/2020**

 - Add path for pneumonia covariate.

**1.0.27 - 05/29/2020**

 - Hotfix for bug in decorator method

**1.0.26 - 05/29/2020**

 - Create common click option decorators for CLI methods

**1.0.25 - 05/28/2020**

 - Hotfix in import paths to preserve backwards compatibility.

**1.0.24 - 05/28/2020**

 - Refactor cli_tools as a subpackage
 - Add mobility gpr path

**1.0.23 - 05/25/2020**

 - Redirect deaths outputs.

**1.0.22 - 05/24/2020**

 - New outputs root for deaths

**1.0.21 - 05/21/2020**

 - Mask use paths.
 - shared repo path.

**1.0.20 - 05/21/2020**

 - Fix yaml warning.

**1.0.19 - 05/21/2020**

 - Update singularity paths for executing R scripts.

**1.0.18 - 05/20/2020**

 - Add more seiir paths.

**1.0.17 - 05/19/2020**

 - Fix default R singularity image path

**1.0.16 - 05/18/2020**

 - Bugfix in metadata file comparison.

**1.0.15 - 05/16/2020**

 - Add shared paths used in testing covariate.
 - Change lots of stuff to path objects.
 - Add update from path method to run metadata.
 - Add paths for seiir inputs and outputs.

**1.0.14 - 05/12/2020**

 - Add static data root.

**1.0.13 - 05/12/2020**

 - Add unversioned inputs root.

**1.0.12 - 05/12/2020**

 - Refactor of get_last_stage_directory to be a bit smarter.
 - Add NOAA data.

**1.0.11 - 05/01/2020**

 - Add a path for raw covariates.

**1.0.10 - 04/30/2020**

 - Add new paths for covariate gathering
 - Update cli tools to support QC functions.

**1.0.9 - 04/28/2020**

 - Adjust update with previous metadata.

**1.0.8 - 04/28/2020**

 - Error on bad production dir name.
 - Add output root for deaths model.
 - Extract some convenience functions to reduce cli boilerplate.

**1.0.7 - 04/26/2020**

 - Additional logging utilities
 - Better mkdir support
 - Expanded marking functions.

**1.0.6 - 04/22/2020**

 - Bugfix in symlink handling.
 - Add general method to create dirs with reasonable permissions.

**1.0.5 - 04/18/2020**

 - Add NY times output directory name.

**1.0.4 - 04/18/2020**

 - Add NY times repo path.
 - Add success flag to metadata when successful.

**1.0.3 - 04/16/2020**

 - Add tool tracking to metadata.

**1.0.2 - 04/14/2020**

 - Add authors, code of conduct, contributing guide.

**1.0.1 - 04/14/2020**

 - Deployment updates.

**1.0.0 - 04/14/2020**

 - Initial release.

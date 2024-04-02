#!/bin/bash
############################################################
#              CREATE AND EXPORT IMDIFFS
############################################################

###
# RESOURCES
##
# Script dir is required to resolve the location of the topdir of the repo
# otherwise it's relative to the caller's dir and we can't resolve path to other scripts
# if we need them
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Number of processes to use, by default matched to widest part of the graph
J=20

# Creates the trimmedRefcats import files with correct paths to the shards
# i.e. the gaia..._fixed.ecsv and ps1..._fixed.ecsv files.
$SCRIPT_DIR/../trimmedRefcats/fix_relative_paths.py
$SCRIPT_DIR/../trimmedRawData/fakes/fix_relative_paths.py

# Add our tasks directory to PYTHONPATH
__saved_path=$PYTHONPATH
export PYTHONPATH="$SCRIPT_DIR/../python:$PYTHONPATH"

# a directory to store logs for later review
mkdir -p processing_logs


####
## CREATE REPO, REGISTER INSTRUMENT
###

# Create a butler repo containing only calibs, then create master calibrations and export them
butler create dataRepo

# Tell it we're working with DECam
butler register-instrument dataRepo "lsst.obs.decam.DarkEnergyCamera"


###
# IMPORT DATA
##

# Import pre-created trimmed master calibration files
# See: https://github.com/dirac-institute/kbmod_mastercals_recipe
butler import dataRepo calibs_20210318 --export-file calibs_20210318/export.yaml

# Then we have to ingest the reference catalog objects we exported, first Gaia
# DR3 for astrometry# and then PanSTARSS for photometry.
butler register-dataset-type dataRepo gaia_dr3_20230707 SimpleCatalog htm7
butler ingest-files dataRepo gaia_dr3_20230707 refcats/gaia_dr3_20230707 trimmedRefcats/gaia_dr3_20230707_fixed.ecsv

butler register-dataset-type dataRepo ps1_pv3_3pi_20170110 SimpleCatalog htm7
butler ingest-files dataRepo ps1_pv3_3pi_20170110 refcats/ps1_pv3_3pi_20170110 trimmedRefcats/ps1_pv3_3pi_20170110_fixed.ecsv


# DIFFERENT!!!
# We register our data-table as a new dataset type and ingest the file into the repository
butler register-dataset-type dataRepo raw_fakes Catalog
butler ingest-files dataRepo raw_fakes fakes/raw trimmedRawData/fakes/fakes_fakeSrcCat_fixed.csv


# put them in a common collection so it's easy to target later
butler collection-chain dataRepo refcats refcats/gaia_dr3_20230707,refcats/ps1_pv3_3pi_20170110

# Ingest curated calibrations
# this will also create the base collections like "DECam" "Decam/calib"
butler write-curated-calibrations dataRepo "DECam"

# import the trimmed raw science exposures we have
butler ingest-raws dataRepo trimmedRawData/210318/science/ --transfer link --output-run "DECam/raw/20210318" -j $J


###
# PROCESS DATA
##

# Then we define visits based on pointing data, there are two targets
# in our dataset: cosmos 1 and 2
butler define-visits dataRepo "DECam" --collections "DECam/raw/20210318"

# First we correct the raw data for the cross-talk. Note that this task is not
# explicitly defined in simple.yaml, yet it exists - via inheritance.
pipetask run \
    -b dataRepo \
    -d "detector=35" \
    -i "DECam/raw/20210318,DECam/calib" \
    -o "DECam/raw/crosstalk/20210318" \
    -p pipelines/simple.yaml#step0 \
    --register-dataset-types \
    -j $J 2>&1 | tee processing_logs/crosstalk.log

# Then we calibrate and characterize images, i.e. make calexps.
pipetask --long-log run \
         -b dataRepo \
         -d "detector=35" \
         -i "DECam/raw/crosstalk/20210318,DECam/calib/20210318,DECam/calib,refcats" \
         -o "DECam/calexp/20210318" \
         -p pipelines/simple.yaml#calexp \
         --register-dataset-types \
         -j $J 2>&1 | tee processing_logs/raw_to_calexp.log


# To create coadds, templates and imdiffs we need to know how to locate data on
# the sky so we must create a skymap
butler make-discrete-skymap dataRepo lsst.obs.decam.DarkEnergyCamera --collections "DECam/calexp/20210318" --skymap-id "skymap_20210318"


# DIFFERENT!!!
# The ProcessCcdWithFakes uses skymap and tract names to match fakes with images
# so we need to link each ingested fake data with its tract ID. This is just:
# > tracts = skyMap.findTractIdArray(fakes['ra'], fakes['dec'], degrees=True)
# really. This task is shipped by us - see python/tasks/partitionFakes.py
pipetask --long-log run \
         -b dataRepo \
         -i "fakes/raw,skymaps" \
         -o "DECam/fakes/partitioned" \
         -p pipelines/fakes.yaml#partitionFakes \
         --register-dataset-types \
         -j $J 2>&1 | tee processing_logs/raw_to_calexp.log


# DIFFERENT!!!
# Then we can reprocess the calexps to add the fakes in it
pipetask --long-log --log-level verbose run \
         -b dataRepo \
         -i "DECam/fakes/partitioned,DECam/calexp/20210318,skymaps" \
         -o "DECam/withFakes/20210318" \
         -p pipelines/fakes.yaml#insertFakes \
         --register-dataset-types \
         -j $J 2>&1 | tee processing_logs/raw_to_calexp.log


# Finally it's the same step to prodice imdiffs, we just target the different
# input collection
pipetask run \
         -b dataRepo \
         -i "DECam/withFakes/20210318,skymaps" \
         -o "DECam/imdiffs/20210318" \
         -p pipelines/simple.yaml#imdiff \
         --register-dataset-types \
         -j $J 2>&1 | tee processing_logs/calexp_to_imdiff.log

# Admittedly this will only run when everything runs successfully, which isn't
# guaranteed - but if-else everywhere hide the simplicity
export PYTHONPATH=$__saved_path

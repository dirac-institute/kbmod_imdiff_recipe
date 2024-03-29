#!/bin/bash
############################################################
#              CREATE AND EXPORT IMDIFFS
############################################################

###
# RESOURCES
##
# Number of processes to use
J=8


###
# CREATE REPO, REGISTER INSTRUMENT
##

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

## Then we have to ingest the reference catalog objects we exported
butler import dataRepo trimmedRefcats --export-file trimmedRefcats/ps1_export_gen3.yaml
butler import dataRepo trimmedRefcats --export-file trimmedRefcats/gaia_export_gen3.yaml

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

mkdir -p processing_logs
# First we correct the raw data for the cross-talk
# TODO: why is it critical that only detector=35 is provided?
# if "instrument='DECam' and detector=35" is given it fails?
pipetask run \
    -b dataRepo \
    -d "detector=35" \
    -i "DECam/raw/20210318,DECam/calib" \
    -o "DECam/raw/crosstalk/20210318" \
    -p ${AP_PIPE_DIR}/pipelines/DarkEnergyCamera/RunIsrForCrosstalkSources.yaml \
    --register-dataset-types \
    -j $J 2>&1 | tee processing_logs/crosstalk.log

# Then we calibrate and characterize images (make calexps)
# Use AP PIPE workflows because of all the config overrides:
# https://github.com/lsst/ap_pipe/blob/main/config/DECam/characterizeImage.py
pipetask --long-log run \
    -b dataRepo \
    -d "detector=35" \
    -i "DECam/raw/crosstalk/20210318,DECam/calib/20210318,DECam/calib,refcats/gen2" \
    -o "DECam/calexp/20210318" \
    -p ${AP_PIPE_DIR}/pipelines/DarkEnergyCamera/ProcessCcd.yaml \
    --register-dataset-types \
    -j $J 2>&1 | tee processing_logs/process_ccd.log

# then we can create a skymap
butler make-discrete-skymap dataRepo lsst.obs.decam.DarkEnergyCamera --collections "DECam/calexp/20210318" --skymap-id "skymap/20210318"

# Now we build the coadds, we build imdiff templates
# out of these, these also build the warps
pipetask run \
    -b dataRepo \
    -d "detector=35" \
    -i "DECam/calexp/20210318,skymaps" \
    -o "DECam/coadd/20210318" \
    -p pipelines/coadd.yaml \
    --register-dataset-types \
    -j $J 2>&1 | tee processing_logs/coadd.log


# Finally we build imdiffs and imdiffed warps
pipetask run \
    -b dataRepo \
    -d "detector=35" \
    -i "DECam/calexp/20210318,DECam/coadd/20210318,skymaps" \
    -o "DECam/imdiff/20210318" \
    -p pipelines/imdiff.yaml \
    --register-dataset-types \
    -j $J 2>&1 | tee processing_logs/imdiff.log


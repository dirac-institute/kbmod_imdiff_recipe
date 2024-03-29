#!/bin/bash

# Script dir is required to resolve the location of the topdir of the repo
# otherwise it's relative to the caller's dir
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Cleanup existing directories and create a fresh one
rm -rf $SCRIPT_DIR/../trimmedRefcats


python %SCRIPT_DIR/refcat_shard_resolver.py $SCRIPT_DIR/../trimmedRawData/210318/science/ \
       --refcat ps1_pv3_3pi_20170110 \
       --refcat-path /epyc/data/lsst_refcats/ps1/ps1_pv3_3pi_20170110 \
       --copy \
       --import-file

python $SCRIPT_DIR/refcat_shard_resolver.py $SCRIPT_DIR/../trimmedRawData/210318/science/ \
       --refcat gaia_dr3_20230707 \
       --refcat-path /epyc/data/lsst_refcats/GAIA_DR3/gaia_dr3 \
       --copy \
       --import-file

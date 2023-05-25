#!/bin/bash

# Script dir is required to resolve the location of the topdir of the repo
# otherwise it's relative to the caller's dir
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Cleanup existing directories and create a fresh one
rm -rf $SCRIPT_DIR/../trimmedRefcats
mkdir -p $SCRIPT_DIR/../trimmedRefcats/refcats/gen2/ps1_pv3_3pi_20170110
mkdir -p $SCRIPT_DIR/../trimmedRefcats/refcats/gen2/gaia_dr2_20200414

python $SCRIPT_DIR/refcat_shard_resolver.py  $SCRIPT_DIR/../trimmedRawData/210318/science/ \
--refcat             ps1_pv3_3pi_20170110 \
--refcat-path        /gscratch/dirac/shared/lsst_refcats/gen3/refcats/gen2/ps1_pv3_3pi_20170110 \
--copy               $SCRIPT_DIR/../trimmedRefcats/refcats/gen2/ps1_pv3_3pi_20170110 \
--trim-exported-yaml /gscratch/dirac/shared/lsst_refcats/ps1_export_gen3.yaml \
--to-trimmed-yaml    $SCRIPT_DIR/../trimmedRefcats/ps1_export_gen3.yaml \
#--detector 35

 
python $SCRIPT_DIR/refcat_shard_resolver.py $SCRIPT_DIR/../trimmedRawData/210318/science/ \
--refcat             gaia_dr2_20200414 \
--refcat-path        /gscratch/dirac/shared/lsst_refcats/gen3/refcats/gen2/gaia_dr2_20200414 \
--copy               $SCRIPT_DIR/../trimmedRefcats/refcats/gen2/gaia_dr2_20200414 \
--trim-exported-yaml /gscratch/dirac/shared/lsst_refcats/gaia_export_gen3.yaml \
--to-trimmed-yaml    $SCRIPT_DIR/../trimmedRefcats/gaia_export_gen3.yaml \
#--detector 35

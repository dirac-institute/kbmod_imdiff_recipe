#!/bin/bash

# Download calibs and science data to rawData dir
python scripts/download_data.py \
    --download-science rawData/210318/science/ \
    --filters i

cp -r rawData trimmedRawData
scripts/trim_ccds.py trimmedRawData/210318/science 35 --verbose --overwrite
scripts/trim_ccds.py trimmedRawData/210318/calib/bias 35 --verbose --overwrite

# Summary

This repository serves as a recipe describing how to process
DECam raw data and create calibrated exposures, coadds and 
image differences using Vera C. Rubin Science Pipelines. 

Raw science data, master calibration and reference catalog
files are provided with the repository for ease of use.
The provided data has been modified, trimmed, in order to
reduce the data volume required. To see full details of 
this procedure refer to the content section. Briefly, 
it contains only the raw, calibration and reference 
catalog data necessary to process the `N4` detector of
DECam `i` filter data taken on the night of 18.03.2021
for the DDDF survey.

The repository uses Git LFS to provide the data.

To run the processing execute 

```bash
git clone https://github.com/dirac-institute/kbmod_imdiff_recipe.git
cd kbmod_imdiff_recipe
scripts/create_imdiffs.sh
```

The processing will produce the calibrated exposures, calexp,
good seeing coadds, and good seeing image differenced 
exposures of sufficient quality to test the KBMOD 
functionality.

# Content

## Science data

The data was taken for the cosmos 1, 2, and 3 targets of the
DECam Deep Drilling Field (DDF) survey on the night of 
18.03.2021 for DECam `i` filter only. The provided science 
data has been trimmed, i.e. modified to reduce the total 
data volume required to store it. Trimming the dataset 
involves setting all the image data to 0, except for the 
detector of interest. The trimmed data zeroes out all the
images except for detector `N4`, near the center of the 
focal plane. The detector ID is 35 and its AstroPy HDUList
index is 37. To create the trimmed data, download the raw 
data, and execute:

To identify and download the original untrimmed raw science
data run:

```bash
scripts/download_data.py \
    --download-science rawData/210318/science \
    --filters i
```

To then trim and reproduce the data provided with the repository
run:

```bash
cp -r rawData trimmedRawData
scripts/trim_ccds.py trimmedRawData/210318/science N4 --verbose --overwrite
```

For convenience the `scripts/download_and_trim_data.sh` 
should preform the same action. The directories should
contain the following data:

                         SCIENCE RAW

i  |  md5sum                          |  ifilter                         |  proposal  |  caldat    |  archive_filename
---|----------------------------------|----------------------------------|------------|------------|------------------------------------------------------------------------
 0 | 020c85f7e80ca26821aed1f6c0902127 | i DECam SDSS c0003 7835.0 1470.0 | 2021A-0113 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2021A-0113/c4d_210319_024912_ori.fits.fz
 1 | 35330f682b64d4b6ccd8bc402b408888 | i DECam SDSS c0003 7835.0 1470.0 | 2021A-0113 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2021A-0113/c4d_210319_024310_ori.fits.fz
 2 | e126aab419d1b5a7503b36d0b31d3e05 | i DECam SDSS c0003 7835.0 1470.0 | 2021A-0113 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2021A-0113/c4d_210319_023704_ori.fits.fz
 3 | f8290547a6124d65a63f75897087af04 | i DECam SDSS c0003 7835.0 1470.0 | 2021A-0113 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2021A-0113/c4d_210319_023059_ori.fits.fz
 4 | e33ae2af4f5f52d147dfd878dd958b2e | i DECam SDSS c0003 7835.0 1470.0 | 2021A-0113 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2021A-0113/c4d_210319_022455_ori.fits.fz
 5 | fa80fd7530560622e450a30174d9a2b7 | i DECam SDSS c0003 7835.0 1470.0 | 2021A-0113 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2021A-0113/c4d_210319_005134_ori.fits.fz
 6 | 56d81414ab12a448b8ac5fce2181b339 | i DECam SDSS c0003 7835.0 1470.0 | 2021A-0113 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2021A-0113/c4d_210319_004532_ori.fits.fz
 7 | fea13cc71be5302de7e9f63e4109f26f | i DECam SDSS c0003 7835.0 1470.0 | 2021A-0113 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2021A-0113/c4d_210319_003928_ori.fits.fz
 8 | c74f675c59185dfee2cd8fd661806e7f | i DECam SDSS c0003 7835.0 1470.0 | 2021A-0113 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2021A-0113/c4d_210319_003322_ori.fits.fz
 9 | 202f4137d1f7571054e9f0539ff9bc3d | i DECam SDSS c0003 7835.0 1470.0 | 2021A-0113 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2021A-0113/c4d_210319_002721_ori.fits.fz

The provided science exposures target three different 
pointings on the sky in the same night named cosmos 1, 2 and
3. The following table lays out which FITS files belong
to which.

        Filename              |  Target
------------------------------|---------
c4d_210319_003928_ori.fits.fz | cosmos_1
c4d_210319_024310_ori.fits.fz | cosmos_1
c4d_210319_022455_ori.fits.fz | cosmos_1
c4d_210319_024912_ori.fits.fz | cosmos_2
c4d_210319_023059_ori.fits.fz | cosmos_2
c4d_210319_004532_ori.fits.fz | cosmos_2
c4d_210319_002721_ori.fits.fz | cosmos_2
c4d_210319_023704_ori.fits.fz | cosmos_3
c4d_210319_005134_ori.fits.fz | cosmos_3
c4d_210319_003322_ori.fits.fz | cosmos_3

The script 

## Reference Catalogs

Included are the reference catalogs, as formatted and 
sharded into HTM shards for use with the Vera C. Rubin 
Science Pipelines. Included are the Gaia DR2 and 
Processing Version 3 of the Pan-STARRS1 3pi survey catalog
shards, used for astrometry and photometry respectively,
relevant for processing the included science data 
only. 

To find out more about how the survey catalogs are formatted
and sharded refer to the example of a trimmed Rubin refcat
found in the `ci_hsc_gen3` repository [here](https://github.com/lsst/testdata_ci_hsc/tree/main/gaia_dr2_20200414)
and [here](https://github.com/lsst/testdata_ci_hsc/tree/main/ps1_pv3_3pi_20170110).

To re-create the provided reference catalogs, access to full
catalogs, already formatted and sharded for use with Rubin 
Science Pipelines, will be required. The `scripts/refcat_shard_resolver.py` 
contains the functionality required to identify and copy the
appropriate catalog shards that overlap given exposures and
to trim down the catalog YAML file intended to be used with
the Rubin Data Butler to only contain those copied catalog 
shards. This reduces the catalog size and the time required
to ingest it into a new Rubin Data Butler Data Repository. 

To see the shard IDs, shard filenames and shard file 
locations of reference catalog shards that overlap a given
set of exposures on your system invoke the script with the
name of the catalog and the location of the catalog shard 
files:

```bash
scripts/refcat_shard_resolver.py trimmedRawData/210318/science/ \
    --refcat ps1_pv3_3pi_20170110 \
    --refcat-path <path_to_lsst_refcats>/gen3/refcats/gen2/ps1_pv3_3pi_20170110/
```

Refer to `scripts/trim_refcats.sh` script to see how more
full usage of the script, including copying the shards and
trimming of the Gen 3 Rubin Data Butler exported data YAML
file. The file assumes paths appropriate for use with DiRAC
computing resources, namely `mox.hyak`.

Following are the identified shard IDs and shard names as
retrieved from the reference catalog made for Gen 2 Rubin
Data Butler, and then exported for Gen 3 Rubin Data Butler
use. Because the reference catalogs in question use the same
HTM order the shard IDS for the catalogs are identical.

                          Shard IDs that overlap the exposures

| ID       |
| ---------|
| 231812   |
| 231813   | 
| 231815   | 
| 231816   | 
| 231818   | 
| 231819   | 
| 231820   | 
| 231825   | 
| 231826   | 
| 231827   | 
| 231828   | 
| 231829   | 
| 231830   | 
| 231831   | 
| 231832   | 
| 231833   | 
| 231834   | 
| 231835   | 
| 231836   | 
| 231837   | 
| 231838   | 
| 231839   | 
| 232344   | 
| 232345   | 
| 232347   | 
| 231844   | 
| 231845   | 
| 231846   | 
| 231847   | 
| 231848   | 
| 231849   | 
| 231850   | 
| 231851   | 
| 231852   | 
| 231853   | 
| 231854   | 
| 231855   | 
| 231856   | 
| 231857   | 
| 231858   | 
| 231859   | 
| 231860   | 
| 231861   | 
| 231862   | 
| 231863   | 
| 231864   | 
| 231865   | 
| 231866   | 
| 231867   | 
| 231868   | 
| 231869   | 
| 231870   | 
| 231871   | 
| 231890   | 
| 231896   | 
| 231897   | 
| 231899   | 
| 231901   |


## Master calibration files

The certified master, flat and bias, calibration files are
the crosstalk and ISR corrected flat and bias files combined
into a master calibration product appropriate for calibration
of the included science data. 

To see how these were created refer to the
[kbmod_mastercals_recipe](https://github.com/dirac-institute/kbmod_mastercals_recipe)
and the instructions therein. 
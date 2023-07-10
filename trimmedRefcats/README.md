# Reference Catalogs

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

####                          Shard IDs that overlap the exposures

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

#!/usr/bin/env python

import os
import glob
import shutil
import argparse
import itertools
import importlib
import subprocess


############################################################
#                         Utils
############################################################
def deferred_import(module, name=None):
    """Defer the import of the stack untill we actually need it to be able to
    print help message before the heat death of the universe.
    """
    if name is None:
        name = module
    if globals().get(name, False):
        return
    try:
        globals()[name] = importlib.import_module(module)
    except ImportError as e:
        raise ImportError("No Rubin Stack found. Please activate Rubin stack.") from e


def get_exp_metadata(exposure):
    """Return exposure's bounding box, wcs and, if existant, filter
    and calibration data.

    Parameters
    ----------
    exposure : `afw.image.ExposureF`
        Exposure
    """
    expInfo = exposure.getInfo()

    #filterName = expInfo.getFilter().getName() or None
    filterName = expInfo.getFilter().physicalLabel or None
    if filterName == "_unknown_":
        filterName = None

    return pipeBase.Struct(
        bbox  = exposure.getBBox(),
        wcs   = expInfo.getWcs(),
        filterName = filterName,
    )


def get_shard_filename(refcatConf, shardId):
    """Returns the name of the shard file."""
    return f"{shardId}.fits"


def get_shard_filepath(refcatConf, refcatLocation, shardId):
    """Return the filepath to the shard file."""
    return os.path.join(refcatLocation, get_shard_filename(refcatConf, shardId))


def resolve_input_meaning(input_val, default_val):
    """Resolves the meaning of given input value to the given default value,
    the input value or to ``None``.

    When the given input value is ``None`` returns the default value.
    When the input value is truthy returns the given input value.
    When the input value is falsy returns ``None``

    Parameters
    ----------
    input_val : any
        Input value.
    default_val : any
        Output value when input_value is None.

    Returns
    -------
    interpreted_val : any
        Given value, default value or None - depending on the input.
    """
    if input_val is None:
        return default_val
    elif input_val:
        return input_val
    else:
        return None


def build_table(ids, names, paths, padding=1):
    """Pretty print the results in a tabular format."""
    header = ""
    if len(ids)>0:
        maxlen1 = max([len(str(i)) for i in ids])+padding
        header += f"ID{'':<{maxlen1}}"
    else:
        maxlen1 = padding
    if len(names)>0:
        maxlen2 = max([len(n) for n in names])+padding
        header += f"NAME{'':<{maxlen2}}"
    else:
        maxlenpadding = padding
    if len(paths)>0:
        maxlen3 = max([len(p) for p in paths])+padding
        header += f"PATH{'':<{maxlen3}}"
    else:
        maxlen3=padding
    header+="\n"

    tmpltstr = "{id:{align}{width1}}{name:{align}{width2}}{path:{align}{width3}}\n"

    prtstr = header
    for i, n, p in itertools.zip_longest(ids, names, paths, fillvalue=""):
        prtstr += tmpltstr.format(id=i, name=n, path=p, align="<",
                                  width1=maxlen1, width2=maxlen2, width3=maxlen3)

    return prtstr


############################################################
#                         Resolvers
############################################################
def calculate_circle(bbox, wcs, pixelMargin):
    """Computes on-sky center and radius of search region

    Parameters
    ----------
    bbox : `lsst.geom.Box2DI` or `lsst.geom.Box2D`
        Bounding box
    wcs : `lsst.afw.geom.SkyWcs`
        WCS
    pixelMargin : `int` or `float`
        padding in pixels by which the bbox will be expanded

    Returns
    ----------
    coord : `lsst.geom.SpherePoint`
        ICRS center of the search region
    radius : `lsst.geom.Angle`
        Radius of the search region
    bbox : `lsst.geom.Box2D`
        Bounding box used to compute the circumscribed circle
    """
    bbox = geom.Box2D(bbox)
    bbox.grow(pixelMargin)
    coord  = wcs.pixelToSky(bbox.getCenter())
    radius = max(coord.separation(wcs.pixelToSky(pp)) for pp in bbox.getCorners())
    return pipeBase.Struct(coord=coord, radius=radius, bbox=bbox)


def resolve_circle2shard_ids(refCatConf, circle):
    """Resolves IDs of shards overlapping an on-sky circular region.

    Parameters
    ----------
    refCatConf : `lsst.meas.algorithms.DatasetConfig`
        Configuration of the reference catalog
    circle : `lsst.pipe.base.Struct`
        Struct containing ICRS center of the search region
        (`lsst.geom.SpherePoint`) and radius of the search region
        (`lsst.geom.Angle`).

    Returns
    ----------
    shard_ids : `list`
        List of integer IDs of reference catalog shards overlapping the region.
    """
    ref_dataset_name = refCatConf.ref_dataset_name
    indexer = measAlgs.IndexerRegistry[refCatConf.indexer.name](refCatConf.indexer.active)
    shard_ids, boundary_mask = indexer.getShardIds(circle.coord, circle.radius)
    return shard_ids


def resolve_bbox2shard_ids(refCatConf, bbox, wcs, pixelMargin=300):
    """Resolves IDs of shards overlapping an on-sky bounding box.

    Parameters
    ----------
    refCatConf : `lsst.meas.algorithms.DatasetConfig object`
        Reference catalog configuration
    bbox : `lsst.geom.Box2D`
        bounding box of the region of interest
    wcs : `lsst.afw.geom.SkyWcs`
        WCS defining the bbox coordinate system
    pixelMargin: `int`
        Bounding box padding, in pixels. Default: 300.

    Returns
    ----------
    shard_ids : `list`
        IDs of reference catalog shards overlapping the region.
    """
    circle = calculate_circle(bbox, wcs, pixelMargin)
    shard_ids = resolve_circle2shard_ids(refCatConf, circle)
    return shard_ids


def resolve_calexp_shard_ids(refCatConf, exposure, pixelMargin=300, **kwargs):
    """Resolves IDs of shards overlapping an Exposure.

    This functions is tailored to resolving the shard IDs
    from a calexp-like data products.

    Parameters
    ----------
    refCatConf : `lsst.meas.algorithms.DatasetConfig object`
        Reference catalog configuration
    exposure : `lsst.afw.ExposureF`
        Image
    pixelMargin: `int`
        Bounding box padding, in pixels. Default: 300.

    Returns
    ----------
    shard_ids : `list`
        IDs of reference catalog shards overlapping the region.
    """
    # remove "detectors" kwargs to maintain compatibility
    # with DECam func
    _ = kwargs.pop("detectors", None)
    meta = get_exp_metadata(exposure)
    return resolve_bbox2shard_ids(
        refCatConf, bbox=meta.bbox,
        wcs=meta.wcs, pixelMargin=pixelMargin,
        **kwargs
    )


def resolve_decamraw_shard_ids(refCatConf, fitsPath, detectors=None, pixelMargin=300, **kwargs):
    """Resolves IDs of shards overlapping an fits file.

    This functions is specifically tailored to handle
    DECam raw FITS files, if you have FITS files with
    only 1 image look at `resolve_calexp_shard_ids`.

    Parameters
    ----------
    refCatConf : `lsst.meas.algorithms.DatasetConfig object`
        Reference catalog configuration
    exposure : `lsst.afw.ExposureF`
        Image
    detectors : `list` or `None`
        List of integer IDs of the detectors for which
        overlapping shards will be found. When `None`
        uses all of the image-like detectors.
    pixelMargin: `int`
        Bounding box padding, in pixels. Default: 300.

    Returns
    ----------
    shard_ids : `list`
        IDs of reference catalog shards overlapping the region.
    """
    hdul = fitsio.open(fitsPath)

    shardIds = []
    bbox = geom.Box2D(geom.Point2D(0, 0), geom.Extent2D(hdul[1].header["NAXIS1"], hdul[1].header["NAXIS2"]))

    if isinstance(detectors, list) or isinstance(detectors, tuple):
        usehdus = [hdul[i] for i in detectors]
    else:
        usehdus = hdul[1:]

    for hdu in usehdus:
        wcs = awcs.WCS(hdu.header)
        crpix = geom.Point2D(wcs.wcs.crpix)
        crval = geom.SpherePoint(longitude=wcs.wcs.crval[0], latitude=wcs.wcs.crval[1], units=geom.degrees)
        skyWcs = afwGeom.makeSkyWcs(crpix=crpix, crval=crval, cdMatrix=wcs.wcs.cd, projection="TAN")
        shards = resolve_bbox2shard_ids(refCatConf, bbox=bbox, wcs=skyWcs, pixelMargin=pixelMargin, **kwargs)
        shardIds.extend(shards)

    return list(set(shardIds))


############################################################
#                         Main
############################################################
def trim_gen3_exported_refcat_yaml(yamlpath, shard_ids):
    """Extract the header and the entry for each of the given shard IDs from
    the Data Butler Gen 3 exported reference catalog YAML file.

    Parameters
    ----------
    yamlpath : `str`
        Path to the exported reference catalog YAML file.
    shard_ids : `str`
        A list of shard IDs.

    Returns
    -------
    trimmed_yaml : `str`
        A valid YAML string, trimmed down version of the given YAML.
    """
    metadata_match = subprocess.run(["head", "-19", yamlpath],
                                    capture_output=True)
    newyaml = metadata_match.stdout.decode()

    for shard_id in shard_ids:
        # this could be a bit problematic because it
        # assumes htm - but no other refcats exist
        # anyhow, so whatever
        match = subprocess.run(
            ["grep", f"\- htm7: {shard_id}", "-B", "3", "-A", "2", yamlpath],
            capture_output=True
        )
        newyaml += match.stdout.decode()

    return newyaml

def main(files, ref_dataset_name, indexer, refcatLoc, detectors):
    """Identify IDs of reference catalog shards that overlap the given image.

    Convenience wrapper for the program's purpose so it can be called from the
    REPL or in an another script.

    Parameters
    ----------
    img : `str`
        Path to image file.
    ref_dataset_name : `str`
        Reference catalog name.
    indexer : `str`
        Indexer scheme to use.
    refcatLoc : `str` or  `None`
        Path to the reference catalog top-level directory
    detectors : `list` or `None`
        List of detectors for which the shard IDs
        will be resolved for. If `None` uses all of the
        image-like HDUs.

    Returns
    -------
    shard_ids : `list`
        List of shard IDs
    shard_names : `list`
        List of shard would-be file names, constructed from ref_dataset_name
        and shard id.
    shard_paths : `list`
        An absolute path to the shard files.
    """
    deferred_import("lsst.meas.algorithms", "measAlgs")
    deferred_import("lsst.afw.image", "afwImage")
    deferred_import("lsst.afw.geom", "afwGeom")
    deferred_import("lsst.pipe.base", "pipeBase")
    deferred_import("lsst.geom", "geom")
    deferred_import("astropy.io.fits", "fitsio")
    deferred_import("astropy.wcs", "awcs")

    refCatConf = measAlgs.DatasetConfig()
    refCatConf.ref_dataset_name  = ref_dataset_name
    refCatConf.indexer = indexer

    #calexp = afwImage.ExposureF(aargs.img)
    #shard_ids = resolve_calexp_shard_ids(refCatConf, calexp)
    shard_ids = []
    for f in files:
        shard_ids.extend(resolve_decamraw_shard_ids(refCatConf, f, detectors=detectors))
    # each shard_id list for each file is de-duplicated itself
    # we need to deduplicate the total set too however.
    shard_ids = list(set(shard_ids))

    shard_names = []
    for sid in shard_ids:
        shard_names.append(get_shard_filename(refCatConf, sid))

    shard_paths = []
    if refcatLoc:
        for sid in shard_ids:
            shard_path = get_shard_filepath(refCatConf, refcatLoc, sid)
            shard_paths.append(shard_path)

    return shard_ids, shard_names, shard_paths


if __name__=="__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Extract reference catalog shard IDs, filenames or full file path "
            "to the reference catalogs that cover the given image."
        )
    )

    ##########
    # Required arguments
    ##########
    parser.add_argument(
        "path",
        help="Path to an image or a directory of images."
    )

    ##########
    # Data Source configuration arguments
    ##########
    parser.add_argument(
        "--refcat",
        help="Reference catalog name. Default: ps1_pv3_3pi_20170110",
        nargs="?", default="ps1_pv3_3pi_20170110", dest="ref_dataset_name"
    )
    parser.add_argument(
        "--refcat-path",
        help="Path to the top-level directory of the reference catalog, assumed $PWD",
        nargs="?", default=False, dest="refcatLoc"
    )
    parser.add_argument(
        "--indexer",
        help="Indexer scheme to use. Default: HTM",
        nargs="?", default="HTM", dest="indexer"
    )
    parser.add_argument(
        "--detectors",
        help=(
            "List of integer detector IDs to use. Not supported by all ",
            "resolvers. Default: use all of the image-like HDUs for shard ",
            "resolution"
        ),
        nargs="?", default=None, dest="detectors"
    )

    ##########
    # Data extraction arguments
    ##########
    parser.add_argument(
        "--copy",
        help="Copy the shards to the given destination, assumed $PWD",
        nargs="?", default=False, dest="copy"
    )
    parser.add_argument(
        "--import-file",
        help=(
            "Create an ECSV file that can be ingested into the butler."
        ),
        nargs="?", default=True, dest="import_file"
    )

    ##########
    # Logic
    ##########
    aargs = parser.parse_args()

    copyLoc = resolve_input_meaning(aargs.copy, os.path.join(os.getcwd(), aargs.ref_dataset_name))
    refcatLoc = resolve_input_meaning(aargs.refcatLoc, os.getcwd())
    importFile = resolve_input_meaning(aargs.import_file, os.getcwd())
    if aargs.detectors is not None:
        detectors = [int(i) for i in aargs.detectors.split()]

    if os.path.isfile(aargs.path):
        files = [aargs.path, ]
    elif os.path.isdir(aargs.path):
        files = glob.glob(f"{aargs.path}/*.fits*")
    else:
        raise ValueError("Expected path to file or a directory, got {aargs.path} instead.")

    ids, names, paths = main(
        files=files,
        ref_dataset_name=aargs.ref_dataset_name,
        indexer=aargs.indexer,
        refcatLoc=aargs.refcatLoc,
        detectors=aargs.detectors
    )
    print(build_table(ids, names, paths))

    # main() returns empty list when no shards were identified or not enough
    # information was provided (f.e. no refcatloc means no shard paths). When
    # copying is requested empty list constitutes an error and not just an
    # empty match.
    if copyLoc and not aargs.refcatLoc:
        raise ValueError(
            "Unable to resolve shard filepath without a valid path to the "
            "reference catalog directory. Provide --refcat-path."
        )
    elif copyLoc and refcatLoc:
        if not os.path.exists(copyLoc):
            os.makedirs(copyLoc, exist_ok=True)
        [shutil.copy(shard, os.path.abspath(copyLoc)) for shard in paths]
    else:
        # no copying was requested
        pass

    if importFile:
        from astropy.table import Table
        tbl = Table({"filename": paths, "htm7": ids})
        relpath = "{ROOT}" + os.path.basename(copyLoc) if copyLoc else "/"
        for row in tbl:
            row["filename"] = row["filename"].replace(refcatLoc, f"{{ROOT}}/{aargs.ref_dataset_name}")
        tbl.write(os.path.join(importFile, f"{aargs.ref_dataset_name}.ecsv"))


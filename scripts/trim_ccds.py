#!/usr/bin/env python
import os
import glob
import argparse
from collections import OrderedDict

from astropy.io import fits
import yaml


############################################################
#                         Utilities
############################################################
class HDULookup:
    """A map between the ``detector`` number and ``full_name``
    values and provides easy(ier) translation between the two.
    
    Powers the functionality where the detector IDs can be suplied
    as an integer detector ID or as a string name ID.
    Ideally this would also be used to track filters, and be a full ID
    resolver, but it's too nuanced and hard to do for a simple script
    so I gave up. 

    Usage is simple - use the brackets operator ``[]`` in combination
    with either index or the name of the detector in question to
    retrieve the opposite. 

    Parameters
    ----------
    idx_name_map : `dict` or `list`
        A map (dict or otherwise) or a list of lists or tuples that
        pair ``detector`` and ``full_name`` values. On the example of
        DECam:
        ``[(1, 'S1'), (2, 'S2') ...]``
    hdutypes : `list`
        List of Astropy class names for the header type. Used to
        determine if the HDU is image-like or not. 
    """    
    def __init__(self, idx_name_map, hdutypes):
        if isinstance(idx_name_map, dict):
            self.idx_name = idx_name_map
        else:
            self.idx_name = {i:n for i,n in idx_name_map}

        self.name_idx = {n: i for i,n in self.idx_name.items()}
        self.types = hdutypes

    @classmethod
    def fromHDUList(cls, hdul):
        """Create an HDULookup instance from an
        `~astropy.io.fits.HDUList`. 


        Astropy's HDUList summary determines the indices names and
        detector names. 

        Note this is not the same as the Rubin's abstraction of
        detector designations.
        
        Returns
        -------
        hdumap : `HDULookup`
            Map of logical detector indices and their full names.
        """
        idx_name_map, hdutypes = [], []
        for hdu in hdul:
            name, idx, hdutype, _, _, _ = hdu._summary()
            idx_name_map.append((idx, name))
            hdutypes.append(hdutype)
        
        return cls(idx_name_map, hdutypes)

    @classmethod
    def fromDECamHDUList(cls, hdul):
        """Create an HDULookup instance from an DECam
        `~astropy.io.fits.HDUList`.

        The difference between generic fromHDUList 
        method is that the detector full name is 
        extracted via the headers instead of 
        automatic naming scheme used by Astropy. 
        This is so that the names actually match
        the detector designations when trimming
        the exported YAMLs. 

        Returns
        -------
        hdumap : `HDULookup`
            Map of logical detector indices and their full names.
        """
        idx_name_map, hdutypes = [], []
        unparsable_counter = len(hdul)
        for hdu in hdul:
            hdutype = hdu.__class__.__name__
            try:
                idx = hdu.header["CCDNUM"]
                name = hdu.header["DETPOS"]
            except KeyError as e:
                if hdutype == "PrimaryHDU":
                    category = (0, "PrimaryHDU")
                else:
                    unparsable_counter += 1
                    name, _, _, _, _, _ = hdu._summary()
                    category = (unparsable_counter, name)
            else:
                category = (idx, name)

            idx_name_map.append(category)
            hdutypes.append(hdutype)
        return cls(idx_name_map, hdutypes)

    def __getitem__(self, val):
        try:
            return self.idx_name[val]
        except KeyError:
            return self.name_idx[val]

    def to_names(self, ids):
        """Convert iterable of IDs into the detector name."""
        names = []
        for i in ids:
            # assume it's an logical id, if it isn't it must be a name
            # else, translate and append
            is_name = False
            try:
                tmpi = int(i)
            except ValueError:
                is_name = True
            else:
                # id is logical indexm, translate to name
                names.append(self[i])

            # id is a name already, if exists in the map store it
            # else raise Key Error
            if is_name and i in self.name_idx:
                names.append(i)
            else:
                raise KeyError(f"No ID {i} in the detector ID-name map.")

        return names

    def to_ids(self, ids):
        """Convert iterable of IDs into logical detector index."""
        idxs = []
        for i in ids:
            # assume it's an logical id, check it exists in the map and append
            # otherwise it's a name, so translate and append 
            try:
                tmpi = int(i)
            except ValueError:
                idxs.append(self[i])
            else:
                if i in self.idx_name:
                    idxs.append(i)
        return idxs

    def get_imagelike_idxs(self):
        """Return all image-like logical detector indices."""
        idxs = []
        for hdutype, (name, idx) in zip(self.types, self.name_idx.items()):
            if "ImageHDU" in hdutype:
                idxs.append(idx)
        return idxs

    def get_imagelike_names(self):
        """Return all image-lige detector full names."""
        idxs = self.get_imagelike_idxs()
        return [self.idx_name[i] for i in idxs]


############################################################
#                         Trimmers
############################################################
def trim_exported_yaml(path, idxs, fullnames, filters=None, writeto=None):
    """Trim the targeted export.yaml file creted by 
    butler export-calibs, keeping only the targeted 
    CCD names and filter(s).
    
    Parameters
    ----------
    path : `str`
        Path to the ``export.yaml`` file to trim.
    idxs : `list`
        List of ``detector`` names which will be exported. 
        On the example of DECam, these are integer detector
        indices 1-62, for other instruments these indices 
        could be string names.
    fullnames : `list`
        List of ``full_names`` of the detectors. On the 
        example of DECam, these are ``S`` and ``N`` strings
        in combination with 1-31 numbers. For other
        instruments these could be completely different
        or matching strings to the idxs. Check the original
        ``export.yaml`` to see the set of values you should
        use.
    filters : `list` or `None`
        List of ``physical_filter`` names to preserve.
        These can be simple ugriz characters or longer
        strings with passband values.
    writeto : `str` or `None`
        If provided, path to file where the trimmed YAML will 
        be written.

    Note
    ----
    Don't even try to refactor this function, it's not worth 
    it. Better to figure out how to do the same 
    using `~lsst.daf.butler.Butler.export`.
    """
    with open(path) as f:
        export = yaml.load(f, Loader=yaml.BaseLoader)
        
    trimmed = {} #OrderedDict()
    # copy header by hand to preserve key-order and datatypes
    trimmed["description"] = export["description"]
    trimmed["version"] = export["version"]
    trimmed["universe_version"] = int(export["universe_version"])
    trimmed["universe_namespace"] = export["universe_namespace"]
    trimmed["data"] = []

    #for key in export.keys():
    #    if key != "data":
    #        trimmed[key] = export[key]

    tmpassociations, tmpfilters = [], None
    uuids, fpaths, existing_filters = [], [], []

    # this for loop occurs over Rubin registry types. There 
    # are several types: dimension, collection, dataset_type
    # dataset and associations. 
    for entry in export["data"]:

        # `dimension` are Rubin abstractions of the physical
        # characteristic of the observing instrumentation.
        # Several `dimension`s exist: instrument, detector or 
        # physical_filter and they list out all of the availible
        # instruments, detectors or filters that exist at that 
        # telescope. We skip trimming most of them here because
        # they don't repeat, are hard to solve, and I don't
        # think they harm if they exist
        if entry["type"] == "dimension":
            elem = entry["element"]
            if elem == "instrument":
                trimmed["data"].append(entry)

            if elem == "physical_filter":
                tmpfilters = entry
                trimmed["data"].append(entry)

            if elem == "detector":
                tmprows = []
                for row in entry["records"]:
                    if row["full_name"] in fullnames:
                        tmprows.append(row)
                trimmed["data"].append(entry)
                trimmed["data"][-1]["records"] = tmprows

        # Collections and dataset_types are Rubin abstractions
        # of data collections of data and of different "kinds"
        # of images (raw, bias, flat, calexp etc.) and other
        # datasets (defects etc.). We want to keep this in 
        # its entirety, doing otherwise leaves the data repo
        # in an inconsistent state.
        if entry["type"] in ["collection", "dataset_type"]:
            trimmed["data"].append(entry)

        # Associations basically list which dataids belong to
        # which collection, but we don't know the order of 
        # items in the export["data"] list, so we have to
        # skip rewriting the associations until we find all
        # dataids that we're actually keeping. Unlike
        # dimensions, associations can repeat for any N 
        # collections we have.
        if entry["type"] == "associations":
            tmpassociations.append(entry)
            trimmed["data"].append(entry)

        # Finally, dataset type is the one we want to trim
        # datasets oddly can have multiple instrument-detector-filter
        # pairs at the same time?
        if entry["type"] == "dataset":
            tmprows = []
            for row in entry["records"]:
                tmpr = []
                for r in row["data_id"]:
                    # flats recognize no filtrs, biases do but they're both datasets
                    rHasFilter = r.get("physical_filter",  False)
                    if rHasFilter and int(r["detector"]) in idxs and r["physical_filter"] in filters:
                        add = True
                    elif rHasFilter and int(r["detector"]) in idxs and r["physical_filter"] not in filters:
                        add = False
                    elif not rHasFilter and int(r["detector"]) in idxs:
                        add=True
                    else:
                        add = False

                    #datType = entry.get("dataset_type", False)
                    #if datType == "bias":
                        #breakpoint()
                    if add:
                        tmpr.append(row)
                        uuids.extend(row["dataset_id"])
                        existing_filters.extend([di["physical_filter"] for di in row["data_id"] if "physical_filter" in di])
                if tmpr:
                    tmprows.extend(tmpr)
            trimmed["data"].append(entry)
            trimmed["data"][-1]["records"] = tmprows

    # we added things to the trimmed copy even when we
    # couldn't trim them at the time to preserve the 
    # ordering in the YAML. Time to revisit these.
    uuids = set(uuids)
    filters = set(filters)
    keep_filters = filters if filters is not None else existing_filters
    for i, entry in enumerate(trimmed["data"]):
        if entry["type"] == "dimension" and entry["element"] == "physical_filter":
            newrecords = []
            for row in entry["records"]:
                if row["name"] in keep_filters:
                    newrecords.append(row)
            trimmed["data"][i]["records"] = newrecords

        if entry["type"] == "associations":
            matching_assoc, j = None, 0
            for assoc in tmpassociations:
                if assoc == entry:
                    matching_assoc = assoc
                    j += 1
            
            if j>1:
                raise ValueError("Identified multiple associations as matching!")
            
            keepvalrange = []
            for valrange in matching_assoc["validity_ranges"]:
                keepvalrange.append({"timespan": valrange["timespan"]})
                keepvalrange[-1]["dataset_ids"] = []
                for did in valrange["dataset_ids"]:
                    if did in uuids:
                        keepvalrange[-1]["dataset_ids"].append(did)
            if keepvalrange:
                trimmed["data"][i]["validity_ranges"] = keepvalrange
            else:
                trimmed["data"][i]["validity_ranges"] = None

    trimmedYaml = yaml.dump(trimmed, default_flow_style=False, sort_keys=False)
    trimmedYaml = trimmedYaml.replace("'", "")
    # important to include newline char in case one timespan passed with the class
    # descriptor
    trimmedYaml = trimmedYaml.replace("timespan:\n", "timespan: !lsst.daf.butler.Timespan\n")
    for did in uuids:
        trimmedYaml = trimmedYaml.replace(did, f"!uuid '{did}'")

    if writeto is not None:
        with open(writeto, "w") as f:
            f.write(trimmedYaml)
    else:
        return trimmed


def compress_image(path, protected, **kwargs):
    """Zeroes out all but the selected HDU(s) and compresses
    the files using fpack or Astropy's CompHDU.

    Inspired by the approach used in:
    https://github.com/lsst/testdata_decam
    in order to reduce the size of the test data repository.

    Parameters
    ----------
    path : `str`
        Path to the directory, or the file to process.
    protected : `int` or `list`
        ID(s) of the HDU to leave unchanged.
    kwargs : `dict`
        Optional `fits.CompImageHDU` init parameters that will be
        passed on, if the selected compression strategy is ``astropy``. 

    Returns
    -------
    hdul : `fits.HDUList`
        The same HDUList, but with unprotected images zeroed and 
        compressed.
    """
    if not os.path.isfile(path):
        raise ValueError("Expected path to file, got {path} instead.")
        #files = path

    hdul = fits.open(path)

    # be careful about discerning the name of the detectors from its 
    # associated logical id and its index in the HDUList object
    hdumap = HDULookup.fromDECamHDUList(hdul)
    protected_names = hdumap.to_names(protected)
    protected_idxs = [hdul.index_of(idx) for idx in protected_names]

    imagelike_idxs = [hdul.index_of(n) for n in hdumap.get_imagelike_names()]
    for idx in imagelike_idxs:
        if idx not in protected_idxs:
            hdul[idx].data[:] = 0

        # this compresses the protected data too, it 
        # just doesn't set them identically to 0
        hdul[idx] = fits.CompImageHDU(
            header=fits.Header(hdul[idx].header),
            data=hdul[idx].data,
            **kwargs
        )

    return hdul


def compress_images(loadfrom, writeto, protectHDUs, verbose=False, overwrite=False, **kwargs):
    """Zeroes out all but the selected HDU(s) and compresses
    the files using fpack or Astropy's CompHDU for all found
    FITS files and saves them in the given location.

    Parameters
    ----------
    loadfrom : `str`
        Path to the directory, or the file to process.
    writeto : `str`
        Path to the directory in which the files will be saved.
    protectHDUs : `int` or `list`
        ID(s) of the HDU to leave unchanged.
    kwargs : `dict`
        Optional `fits.CompImageHDU` init parameters that will be
        passed on, if the selected compression strategy is ``astropy``. 
    """
    if os.path.isfile(loadfrom):
        files = [loadfrom, ]
    elif os.path.isdir(loadfrom):
        files = glob.glob(f"{loadfrom}/*.fits*")
    else:
        raise ValueError("Expected path to file or a directory, got {loadfrom} instead.")

    if os.path.isdir(writeto) and not os.path.exists(writeto):
        os.makedirs(writeto, exist_ok=True)

    totn = len(files)
    for i, f in enumerate(files):
        newimg = compress_image(f, protectHDUs, **kwargs)
        if os.path.isdir(writeto):
            dn = newimg.filename()
            fn = os.path.basename(dn) if os.sep in dn else dn
            fpath = os.path.join(writeto, fn)
        else:
            # likely a single exposure only
            fpath = writeto
        newimg.writeto(fpath, overwrite=overwrite)
        if verbose:
            print(f"[{i}/{totn}] Writing {fpath} succesfull.")


############################################################
#                         Main
############################################################
def main(path, hdus, writeto=False, verbose=False, overwrite=False, **kwargs):
    """Zeroes out all but the selected HDU(s) and, optionally,
    compresses the files using fpack or Astropy's CompHDU.

    Inspired by the approach used in:
    https://github.com/lsst/testdata_decam

    Parameters
    ----------
    img : `str`
        Path to the directory, or the file to process.
    hdus : `int` or `list`
        ID(s) of the HDU to leave unchanged.
    writeto : `bool` or `str`
        If a path is given, writes the compressed files to that
        location. Otherwise the compressed fits are returned as
        a list of `fits.HDUList` objects.
    kwargs : `dict`
        Optional `fits.CompImageHDU` init parameters that will be
        passed on, if the selected compression strategy is ``astropy``. 
    """
    res = compress_images(
        loadfrom=path,
        writeto=writeto,
        protectHDUs=hdus,
        verbose=verbose,
        overwrite=overwrite,
        **kwargs
    )

    if res is not None:
        return new_fits
                      

if __name__=="__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Zero all but protected HDUs, compress and write the new FITS files to disk. "
            "When path to related exported DECam calibration directory is given, trims the "
            "calibration data, leaving only the flats and biases of the protected HDUs."
        )
    )

    ##########
    # Required arguments
    ##########
    parser.add_argument(
        "path",
        help="FITS file or directory containing FITS files that will be compressed."
    )
    parser.add_argument(
        "hdus",
        help="Comma separated list of detector IDs (their numerical or string ID) to preserve."
    )

    ##########
    # Optional arguments
    ##########
    parser.add_argument(
        "--writeto",
        help="Write new FITS files at the given destination, assumed $PWD",
        nargs="?", default=None, dest="writeto"
    )
    parser.add_argument(
        "--trim-exported-calibs",
        help="Path to a directory containing the YAML with exported DECam calibrations.",
        nargs="?", default=False, dest="writeto"
    )
    parser.add_argument(
        "--strategy",
        help=(
            "Optional keyword arguments passed to the constructor of CompImageHDU. "
            "Comma separated list of key=val values, f.e. key1=val1,key2=val2 etc."
        ),
        nargs="?", default=None, dest="strategy"
    )
    parser.add_argument(
        "--verbose",
        help="Print processing progress.",
        action="store_true", dest="verbose"
    )
    parser.add_argument(
        "--overwrite",
        help="Overwrite files at the destination, if they exist..",
        action="store_true", dest="overwrite"
    )

    ##########
    # Logic
    ##########
    aargs = parser.parse_args()

    if not os.path.exists(aargs.path):
        raise ValueError(f"File or directory does not exist: {aargs.path}")

    if aargs.writeto is None:
        aargs.writeto = aargs.path

    kwargs = {}
    if aargs.strategy:
        pairs = aargs.strategy.split(",")
        for pair in pairs:
            key, v = pair.split("=")
            # all CompHDU kwargs are float-compatible or
            # strings, so we make the guess here
            try:
                val = float(v)
            except TypeError:
                val = v
            kwargs[key] = val

    hdus = [i for i in aargs.hdus.split(",")]

    main(
        path=aargs.path,
        hdus=hdus,
        writeto=aargs.writeto,
        verbose=aargs.verbose,
        overwrite=aargs.overwrite,
        **kwargs
    )

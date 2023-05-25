#!/usr/bin/env python3
import os
import argparse
import requests
try:
    # this makes sense because mostly the script would
    # be used with an activate lsst env.
    import tabulate
except ImportError:
    tabulate = None


class Downloader:
    # See https://github.com/NOAO/nat-nb/blob/master/advanced-search.ipynb
    # for all field details, this Factory only creates minimum required for
    # actual usage, and debugging.
    outfields_v2 = [
        "md5sum",
        "archive_filename",
        "caldat", # obstime
        "ifilter",
        "proc_type",
        "obs_type",
        "ra_min", # approximate position on sky
        "dec_min", 
        "proposal"
    ]
    outfields_v1 = [
        "md5sum",
        "archive_filename",
        "proposal",
        "caldat",
        "ifilter",
    ]
    outfields_v0 = [outfields_v2[:2], ]
    query_url = "https://astroarchive.noirlab.edu/api/adv_search/find/?"
    download_url = "https://astroarchive.noirlab.edu/api/retrieve/{}"

    def __init__(self, response):
        self.response = [response,]
        jdat = response.json()

        if not response.ok:
            if "errorMessage" in jdat.keys():
                raise ValueError(
                    "Can not instantiate Downloader, bad query.\n"
                    f"{jdat['errorMessage']}"
                )
            raise ValueError(
                "Can not instantiate Downloader, bad response:\n"
                f"{response.status_code} {response.reason}"
            )

        self.query_params = [jdat[0], ]
        self.jdat = jdat[1:]
        
        # empty list, no matched results
        if not self.jdat:
            self.header = []
            self.data = []
        else:
            self.header = self.jdat[0].keys()
            self.data = []
            for row in self.jdat:
                self.data.append([row[key] for key in self.header])

    @classmethod
    def getPayload(cls, archivefilename, obstype, additionalArgs=None, verbosity=0):
        outfields = getattr(cls, f"outfields_v{verbosity}")
        base_search = [
            ["instrument", "decam"],            
            ["proc_type", "raw"],
            ["archive_filename", archivefilename, "contains"],
            ["obs_type", obstype],
        ]
        
        if additionalArgs is not None:
            if isinstance(additionalArgs[0], list):
                base_search.extend(additionalArgs)
            else:
                base_search.append(additionalArgs)

        base_yaml = {
            "outfields" : outfields,
            "search": base_search
        }
        return base_yaml

    @classmethod
    def get(cls, archivefilename, obstype, additionalArgs=None, verbosity=0):
        payload = cls.getPayload(archivefilename, obstype, additionalArgs, verbosity)
        results = requests.post(cls.query_url, json=payload)
        return cls(results)

    def __str__(self):
        if tabulate is not None:
            return tabulate.tabulate(self.data, self.header, showindex=True)
        else:
            padding = [len(str(val)) for val in self.data[0]]
            tmplt = "".join(["{{:{0}}}".format(pad+2) for pad in padding]) + "\n"
            retr = tmplt.format(*self.header)
            for row in self.data:
                retr += tmplt.format(*row)
            return retr

    def extend(self, other):
        # header check prevents `self` from being empty 
        if not self.header and other.header:
            self.header = other.header 

        if not self.header and self.header != other.header:
            raise ValueError("Unable to extend Downloaders with unmatched headers.")

        self.response.extend(other.response)
        self.query_params.append(other.query_params)
        self.jdat.extend(other.jdat)
        self.data.extend(other.data)
        
    def get_column(self, name):
        if not self.header:
            return []

        if name not in self.header:
            raise ValueError(f"Key '{name}' not availible in the data. Are you sure it's spelled right?")
            
        idx = list(self.header).index(name)
        res = []
        for row in self.data:
            res.append(row[idx])
        return res

    def downloadTo(self, dirpath):
        ids = self.get_column("md5sum")
        names = [os.path.basename(aname) for aname in self.get_column("archive_filename")]
        i, tot = 0, len(ids)
        for md5, name in zip(ids, names):
            print(f"[{i:3}/{tot:3}] Downloading {name}")
            response = requests.get(self.download_url.format(md5))
            if response.ok:
                with open(os.path.join(dirpath, name), "wb") as f:
                    f.write(response.content)
                print("    Success.")
            else:
                print("    FAILED.")
            i += 1


if __name__=="__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Extract reference catalog shard IDs, filenames or full file path "
            "to the reference catalogs that cover the given image."
        )
    )

    ##########
    # Data Source configuration arguments
    ##########
    parser.add_argument(
        "--verbosity",
        help="Verobosity of output, 0-2. Default: 1",
        nargs="?", default="1", dest="verbosity"
    )
    parser.add_argument(
        "--download",
        help="Download selected files?",
        nargs="?", default=False, dest="downloadAll"
    )
    parser.add_argument(
        "--download-bias",
        help="Download selected biases?",
        nargs="?", default=False, dest="downloadBias"
    )
    parser.add_argument(
        "--download-flats",
        help="Download selected flats?",
        nargs="?", default=False, dest="downloadFlats"
    )
    parser.add_argument(
        "--download-science",
        help="Download selected science exposuress?",
        nargs="?", default=False, dest="downloadScience"
    )
    parser.add_argument(
        "--filters",
        help="Download selected filters only [gri].",
        nargs="+", default=("g", "r", "i"), dest="filters"
    )
    

    ##########
    # Logic
    ##########
    aargs = parser.parse_args()

    filters =[]
    if "i" in aargs.filters:
        filters.append("i DECam SDSS c0003 7835.0 1470.0")
    if "g" in aargs.filters:
        filters.append("g DECam SDSS c0001 4720.0 1520.0")
    if "r" in aargs.filters:
        filters.append("r DECam SDSS c0002 6415.0 1480.0")

    if not filters:
        raise ValueError("No filters were given, nothing to download.")

    print(" "*26+"BIAS RAW")
    print("#"*60)
    bias = Downloader.get("c4d_210318", "zero", verbosity=aargs.verbosity)
    print(bias)

    print()
    print(" "*26+"FLAT RAW")
    print("#"*60)
    flat = Downloader.get("c4d_210318", "dome flat", ["ifilter", filters[0]], verbosity=aargs.verbosity)
    for filter_name in filters[1:]:
        flat.extend(Downloader.get("c4d_210318", "dome flat", ["ifilter", filter_name], verbosity=aargs.verbosity))
    print(flat)

    print()
    print(" "*25+"SCIENCE RAW")
    print("#"*60)
    addedArgs = [
        ["ifilter", filters[0]],
        ["proposal", "2021A-0113", "contains"],
    ]
    science = Downloader.get("c4d_210319", "object", addedArgs, verbosity=aargs.verbosity)

    for filter_name in filters[1:]:
        addedArgs[0][1] = filter_name
        science.extend(Downloader.get("c4d_210319", "object", addedArgs, verbosity=aargs.verbosity))
    print(science)

    if aargs.downloadAll:
        aargs.downloadBias = True
        aargs.downloadFlats = True
        aargs.downloadScience = True

    def create_save_dirs(arg, default):
        if isinstance(arg, bool) or arg is None:
            pth = default
        else:
            pth = arg
        os.makedirs(pth, exist_ok=True)
        return pth

    if aargs.downloadBias or aargs.downloadBias is None:
        biasDir = create_save_dirs(aargs.downloadBias, "../rawData/210318/calib/bias")
        bias.downloadTo(biasDir)
        
    if aargs.downloadFlats or aargs.downloadFlats is None:
        flatDir = create_save_dirs(aargs.downloadFlats, "../rawData/210318/calib/flat")
        flat.downloadTo(flatDir)

    if aargs.downloadScience or aargs.downloadScience is None:
        sciDir = create_save_dirs(aargs.downloadScience, "../rawData/210318/science")
        science.downloadTo(sciDir)

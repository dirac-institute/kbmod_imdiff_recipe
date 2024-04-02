import lsst.pipe.base as pipeBase
from lsst.pipe.base import PipelineTask, PipelineTaskConfig, PipelineTaskConnections
import lsst.pipe.base.connectionTypes as cT
from lsst.skymap import BaseSkyMap
import pandas as pd
from astropy.table import vstack, Table
import numpy as np

class PartitionFakesConnections(PipelineTaskConnections, dimensions=("skymap",)):
    skyMap = cT.Input(
        doc="Skymap that defines tracts",
        name=BaseSkyMap.SKYMAP_DATASET_TYPE_NAME,
        dimensions=("skymap",),
        storageClass="SkyMap",
    )

    fakeCat = cT.Input(
        doc="Unpartitioned fake catalogs.",
        name="raw_fakes",
        storageClass="Catalog",
        dimensions=(),
        deferLoad=True,
        multiple=True,
    )

    partitionedFakes = cT.Output(
        doc="Fakes partitioned by tract",
        name="partitioned_fakes",
        storageClass="DataFrame",
        dimensions=("skymap", "tract"),
        multiple=True,
    )

class PartitionFakesConfig(PipelineTaskConfig, pipelineConnections=PartitionFakesConnections):
    pass

class PartitionFakesTask(PipelineTask):
    _DefaultName = "partitionFakes"
    ConfigClass = PartitionFakesConfig

    def run(self, skyMap, fakeCat):
        print(skyMap)
        print(fakeCat)
        # determine the tract assignment of each fake based on ra/dec

        fakes = Table()
        for deferred in fakeCat:
            print(dir(deferred))
            catalog = deferred.butler.get(deferred.ref)
            fakes = vstack([fakes, catalog.asAstropy()])

        tracts = skyMap.findTractIdArray(fakes['ra'], fakes['dec'], degrees=True)

        outputCats = {}
        for tract in set(tracts):
            print("subsetting tract", tract)
            subset = fakes[tracts == tract]
            _none = [None] * len(subset)
            _true = [True] * len(subset)
            # ProcessCcdWithFakesTask uses the galsim img sim models
            # http://galsim-developers.github.io/GalSim/_build/html/sb.html
            # I guess it defaults to galaxy model.
            outputCats[tract] = pd.DataFrame(
                dict(
                    ra=subset['ra'] * np.pi/180,
                    dec=subset['dec'] * np.pi/180,
                    bulge_semimajor=_none,
                    bulge_axis_ratio=_none,
                    bulge_pa=_none,
                    bulge_n=_none,
                    disk_semimajor=_none,
                    disk_axis_ratio=_none,
                    disk_pa=_none,
                    disk_n=_none,
                    bulge_disk_flux_ratio=_none,
                    trail_length=_none,
                    trail_angle=_none,
                    select=_true,
                    i_mag=subset['mag'],
                    sourceType=["star"] * len(subset),
                    visit=subset['visits'], # convert to visit?
                )
            )

        return outputCats

    def runQuantum(self, butlerQC, inputRefs, outputRefs):
        inputs = butlerQC.get(inputRefs)

        print("inputs=", inputs)
        print("outputRefs")
        print(outputRefs) # all of the tracts in the skymap

        runOutputs = self.run(**inputs)
        if runOutputs:
            tracts = [ref.dataId['tract'] for ref in outputRefs.partitionedFakes]
            outputs = [runOutputs.get(tract, pd.DataFrame()) for tract in tracts] # trim outputs to just those
            butlerQC.put(pipeBase.Struct(partitionedFakes=outputs), outputRefs)

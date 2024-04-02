import os

import astropy.io.fits as fitsio
from astropy.wcs import WCS
from astropy.table import Table

# we trimmed everything except detector 35 for
# 3 different targets, so we need to do some bookkeeping
# start position, move distance, pix a day
pos_in_field = {
    "COSMOS-1": [100, 100, 0],
    "COSMOS-2": [100, 100, 0],
    "COSMOS-3": [100, 100, 0]
}
dx, dy = 100, 100

ras, decs, visits = [], [], []
for f in os.listdir("../210318/science"):
    hdul = fitsio.open(f"../210318/science/{f}")

    primhdr = hdul["PRIMARY"].header
    visits.append(primhdr["EXPNUM"])

    # add the object
    obj = primhdr["OBJECT"]
    x0, y0, idx = pos_in_field[obj]
    x, y = idx*x0, idx*y0
    pos_in_field[obj][-1] += 1

    wcs = WCS(hdul[35].header)
    coord = wcs.pixel_to_world(x, y)
    ras.append(coord.ra.radian)
    decs.append(coord.dec.radian)

# src cat matches the galsim catalog format
srcCatData = Table(dict(
    ra        = ras,
    dec       = decs,
    visits    = visits,
    mag    = [17]*len(ras),
    sourceTye = ["stars"]*len(ras),
))

srcCat = fitsio.BinTableHDU(srcCatData)
srcCat.writeto("fakes_fakeSrcCat.fits", overwrite=True)
with open("fakes_fakeSrcCat.csv", "w") as f:
    f.write("file\n")
    f.write("{ROOT}/fakes_fakeSrcCat.fits\n")

#!/usr/bin/env python3
"""Expand the relative path in the exported trimmed reference catalogs.

Writes the gaia and ps1 ``_fixed`` files with full paths expanded relative to
the root of this directory.
"""
import os.path

from astropy.io import ascii
from astropy.table import Table


DATA_ROOT = os.path.abspath((os.path.dirname(__file__)))

pth = os.path.join(DATA_ROOT, "fakes_fakeSrcCat.csv")
with open(pth, "r") as f:
    content = f.read()

newpth = pth.replace(".csv", "_fixed.csv")
with open(newpth, "w") as f:
    f.write(content.format(ROOT=DATA_ROOT))

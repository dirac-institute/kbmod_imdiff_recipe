#!/usr/bin/env python3
"""Expand the relative path in the exported trimmed reference catalogs.

Writes the gaia and ps1 ``_fixed`` files with full paths expanded relative to
the root of this directory.
"""
import os.path

from astropy.io import ascii
from astropy.table import Table


REFCAT_ROOT = os.path.abspath(os.path.dirname(__file__))

# apparently we can't set the row directly to itself due to size truncation
# - we're adding a long string to something ascii declared a shorter string
# so we have to put them in a list, and then assign.

gaia = ascii.read(os.path.join(REFCAT_ROOT, "gaia_dr3_20230707.ecsv"))
tmp = []
for row in gaia:
    tmp.append(row["filename"].format(ROOT=REFCAT_ROOT))
gaia["filename"] = tmp

ps1 = ascii.read(os.path.join(REFCAT_ROOT, "ps1_pv3_3pi_20170110.ecsv"))
tmp = []
for row in ps1:
    tmp.append(row["filename"].format(ROOT=REFCAT_ROOT))
ps1["filename"] = tmp

gaia.write(os.path.join(REFCAT_ROOT, "gaia_dr3_20230707_fixed.ecsv"), overwrite=True)
ps1.write(os.path.join(REFCAT_ROOT, "ps1_pv3_3pi_20170110_fixed.ecsv"), overwrite=True)

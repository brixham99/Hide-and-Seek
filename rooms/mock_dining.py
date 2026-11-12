#!/usr/bin/env python3
"""Static isometric mock-up of the DINING HALF of the Anderson house
Kitchen + Dining Room for 'Hide and Seek', in the house-wide camera
convention (house_common.HOUSE_CAMERA).

This view is world x 0 .. KD_SPLIT (local x = world x). The whole room is
described once in kd_room and drawn for this x range; the kitchen shows
beyond the open beam side from that same description. Nothing here depends
on which way the camera looks.

    python mock_dining.py [out.png]
"""
import sys

import house_common as hc
hc.init_room(hc.KD_SPLIT, hc.KD_DEP, ox=570)
from house_common import *  # noqa: E402,F401,F403
import kd_room  # noqa: E402

X0 = KD_VIEWS["dining"]                 # 0: local x = world x
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "shots/hs_dining_mock.png"


def main():
    kd_room.render(sys.modules[__name__], X0, "Hide and Seek - Dining Room (mock-up)",
                   "Ground Floor - dining half of the Kitchen + Dining Room", OUT,
                   sprite=("archie", 5.3, 3.0))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Static isometric mock-up of the KITCHEN HALF of the Anderson house
Kitchen + Dining Room for 'Hide and Seek', in the house-wide camera
convention (house_common.HOUSE_CAMERA).

This view is world x KD_SPLIT .. KD_LEN (local x = world x - KD_SPLIT). The
whole room - walls, openings and furniture - is described once in kd_room
and drawn for this x range; the dining half shows beyond the open beam side
from that same description. Nothing here depends on which way the camera
looks.

    python mock_kitchen.py [out.png]
"""
import sys

import house_common as hc
hc.init_room(hc.KD_LEN - hc.KD_SPLIT, hc.KD_DEP, ox=700)
from house_common import *  # noqa: E402,F401,F403
import kd_room  # noqa: E402

X0 = KD_VIEWS["kitchen"]                # world x of this view's local x = 0 (the beam)

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "shots/hs_kitchen_mock_v3.png"
COPIES = () if ARGS else ("shots/hs_kitchen_mock.png",)


def main():
    kd_room.render(sys.modules[__name__], X0, "Hide and Seek - Kitchen (mock-up)",
                   "Ground Floor - kitchen half of the Kitchen + Dining Room", OUT, COPIES,
                   sprite=("archie", 6.7, 2.7))


if __name__ == "__main__":
    main()

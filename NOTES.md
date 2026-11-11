# Notes

## Camera labels versus internal names

The default on-screen camera (internally the “SE camera”, `HOUSE_CAMERA`,
`flipped = False`) looks **north**. The opposite view (internally the flip /
“NW” camera, `V` / `flipped = True`) looks **south**.

On-screen copy now says “looking north” / “looking south”. Internal
identifiers and wall names (`N`, `S`, `E`, `W`, `drawing_r`, comments about
the south-east camera, and so on) keep the old labels so layouts, ghosting
and depth sorting stay untouched.

## Door frames and the upstairs corridor (white-frames)
- Near-wall doorways in both cameras now carry the Haunted Mansion ghost
  frame (`door_frame_polys`, translucent, white with a slight cold tint) so the
  exits read; nothing of the next room shows through them. Looking south, the
  frames come from `house.PORTALS` on the old back walls (`_near_ghost_frames`
  in build_rooms.py). Far-wall doorways keep the solid white architrave.
- The landing <-> corridor arch is a slim curved arch (`arch_z`,
  `arch_frame_polys` in house_common.py) with a white moulding on both sides.
- Upstairs Corridor shortened to 7.75 tiles: its west dead end (house X =
  11.75) now stops at the Dressing Room's east wall, as on the first-floor
  plate (~1.3 m of blank wall west of the arch). The recessed niche on the
  passage's south wall by the clothes basket read as a door, so it is gone;
  that stretch is plain wall (the plate shows no opening there). Looking
  south, the corridor's near walls are ghosts (no solid pillar).

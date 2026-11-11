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

## Myrtle (the black Labrador)
- Sprites: `tools/make_myrtle.py` paints them from one signed-distance model
  of a Labrador (round cones and ellipsoids with smooth unions: deep chest,
  tucked waist, rounded skull, drop ears, otter tail, shaped legs and paws),
  ray-marched through the house's 2:1 camera at 3x with the rooms' light, a
  blue-grey sheen and rim, a warm floor bounce and streaky fur, then
  downsampled with a soft dark edge. Output in `assets/myrtle/`: standing,
  an 8-frame walk, sitting and lying (curled a little to fit her bed), in
  Archie's four facings (se, sw, nw, ne). Glossy black coat, brown eyes,
  narrow red collar with a small brass tag. `tools/myrtle_sheet.py` makes a
  contact sheet. A full build takes about 2.5 minutes.
- Bed: the existing teal dog bed in the Drawing Room (room-local 1.35-2.55 x
  4.55-5.65, on the rug by the TV); she lies on its top (z = 16).
- Behaviour (`dog.py`, basic for now): lies on her bed; when the player walks
  about downstairs she gets up and trails ~1.35 tiles behind and to one side,
  room to room through the doorways (8-way grid path on the room's own
  collision, never upstairs, no collision with the player). She sits when they
  stop (not in a doorway), and goes back to bed after 25 s idle or when nobody
  is downstairs. In the Kitchen / Dining Room she keeps closer (0.9 tiles),
  trots, and hangs about for 50 s, sitting and looking up hopefully.
  Simulated off-screen; drawn only in the room on screen, depth-sorted with
  Archie, under the ghost walls, both cameras. `dog_test.py` checks the states.

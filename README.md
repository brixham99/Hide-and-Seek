# Hide and Seek

**Anderson Family - Gaming Creations**

A walkable prototype of the downstairs of our house, built with pygame on the
isometric engine from [Haunted Mansion](https://github.com/brixham99/Haunted-Mansion).

## Install and run

```
git clone https://github.com/brixham99/Hide-and-Seek.git
cd Hide-and-Seek
pip install -r requirements.txt
python3 game.py
```

`requirements.txt` installs pygame-ce, NumPy and Pillow (the room builder uses
Pillow to paint the furniture faces). The first run builds the room images into `cache/` (a few seconds). You can also
build them yourself with `python3 build_rooms.py`.

## Controls

The game opens on a title screen: **Enter** (or **A** / **Cross**) starts.

| Action | Keyboard | Xbox | PlayStation |
|--------|----------|------|-------------|
| Turn a quarter turn | Left / Right (A / D) | Left stick / D-pad left, right | the same |
| Walk forwards / back | Up / Down (W / S) | Left stick / D-pad up, down; RT walks forwards | the same; R2 |
| Look from the other side | V | Y (or X) | Triangle (or Square) |
| Back to the title | Esc | B (or Start) | Circle (or Options) |
| Quit | Esc on the title | hold Back for a second | hold Share |

## Zen Station (Raspberry Pi)

Listed on [Zen Station](https://github.com/brixham99/Zen-Station) as
**Hide and Seek (Beta)**. With `ZENSTATION=1` (set by the launcher) or
`--fullscreen` it fills the TV; holding Back / Share returns to the launcher.
The room images are built by `zenbuild.py`, split across the Pi's cores; Zen
Station runs it in the background after each clone or update, and if the game
is started first it shows a progress screen until they are ready. They live in
`cache/` (not in git), so a `git pull` keeps them, and a `CACHE_REV` bump in
`build_rooms.py` rebuilds them once.

Files for this: `zen.py` (title, pads, full screen), `title.py` and
`assets/title/` (the title screen, painted by `tools/make_title.py`),
`zenbuild.py`, and `pads.py` / `screenfit.py` from Haunted Mansion. Checks:
`SDL_VIDEODRIVER=dummy python3 tools/zen_test.py`.

## What's in so far

- The whole ground floor: Hall, Sitting Room, Drawing Room, Kitchen and Dining
  Room (one room, the view slides across at the beam), Boot Room, Utility,
  Office and the Dragon Toilet. The garage isn't in yet.
- One camera direction for the whole house; the near walls of the room you are
  in are see-through, as in Haunted Mansion.
- No internal doors: every doorway is open. The front door, the Boot Room door
  and the French doors stay shut.
- Walls and the main furniture are solid.
- A headless test walk that goes through every doorway both ways:
  `SDL_VIDEODRIVER=dummy python3 walk_test.py` (screenshots in `shots/`).

On the title screen, Left / Right (keys, D-pad or stick) chooses who you
play, Archie or Holly; the choice is kept until you quit. The other child
wanders the whole house on their own (`npc.py`, `npc_test.py`). The player is
blocked by the walls and the furniture, and drawn behind anything closer to
the camera. Still to come: hiding and seeking,
the stairs and upstairs, and the garage.

## Files

- `game.py` - the game
- `house.py` - room layout on the house grid, doorways and furniture footprints
- `build_rooms.py` - renders each room view from the drawing code in `rooms/`
- `rooms/` - the room drawing code (one script per room, shared kit in
  `house_common.py`, Haunted Mansion engine pieces in `hm_engine.py`)
- `assets/characters/` - Archie's and Holly's sprites (copied unchanged from
  Haunted Mansion's `assets/characters/`)
- `npc.py` - the child you are not playing, wandering the house

© 2026 - Made in England

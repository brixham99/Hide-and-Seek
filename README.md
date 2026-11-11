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

- **Left / Right** (or A / D): turn a quarter turn
- **Up / Down** (or W / S): walk forwards / backwards
- A gamepad stick or d-pad works too
- **Esc**: quit

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

Archie is blocked by the walls and the furniture, and he is drawn behind
anything closer to the camera than he is. Still to come: hiding and seeking,
the stairs and upstairs, and the garage.

## Files

- `game.py` - the game
- `house.py` - room layout on the house grid, doorways and furniture footprints
- `build_rooms.py` - renders each room view from the drawing code in `rooms/`
- `rooms/` - the room drawing code (one script per room, shared kit in
  `house_common.py`, Haunted Mansion engine pieces in `hm_engine.py`)
- `assets/characters/` - Archie's sprites (from Haunted Mansion)

© 2026 - Made in England

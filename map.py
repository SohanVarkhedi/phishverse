"""
PHISHVERSE – map.py  (fixed 2D office, 40×28 tiles, all rooms connected)
"""

import pygame
from tiles import (TileRenderer,
    TILE_FLOOR as _F, TILE_WALL as _W, TILE_DESK as _K, TILE_DOOR as _D,
    TILE_WINDOW as _O, TILE_CARPET as _Z, TILE_COMPUTER as _C,
    TILE_PLANT as _P, TILE_POSTER as _S, TILE_USB as _U, TILE_PHONE as _H,
    TILE_CHAIR as _N, TILE_TABLE as _T, TILE_GRASS as _G,
    TILE_RECEPTION as _R, TILE_BOOKSHELF as _B, TILE_CABINET as _A,
    TILE_ENTRY_FLOOR as _E, SOLID_TILES)
from constants import TILE_SIZE

OFFICE_GRID = [
    # Row 0 – top border
    [_W]*40,
    # Rows 1-2 – outside grass
    [_W]+[_G]*38+[_W],
    [_W]+[_G]*38+[_W],
    # Row 3 – building entrance wall (doors at 18-21)
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_D,_D,_D,_D,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    # Row 4 – windows along top wall, RECEPTION starts
    [_W,_O,_O,_O,_O,_W,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_W,_O,_O,_O,_O,_W],
    # Row 5 – reception desk both sides
    [_W,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_W],
    # Row 6 – counters
    [_W,_F,_R,_R,_R,_R,_R,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_R,_R,_R,_R,_R,_F,_F,_W],
    # Row 7 – lobby with plants
    [_W,_F,_F,_F,_F,_F,_F,_F,_P,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_P,_F,_F,_F,_F,_F,_F,_F,_F,_W],
    # Row 8 – open lobby
    [_W,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_W],
    # Row 9 – SEPARATOR (single wall + doors at 9,10 and 29,30)
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_D,_D,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_D,_D,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    # Row 10 – WORK AREA | HR ROOM corridor row
    [_W,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_W,_W,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_W],
    # Row 11 – desks row 1 + bookshelves HR
    [_W,_K,_C,_F,_K,_C,_F,_K,_C,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_W,_W,_F,_F,_F,_F,_F,_F,_B,_F,_F,_F,_F,_B,_F,_F,_F,_F,_F,_F,_W],
    # Row 12 – chairs row 1
    [_W,_N,_F,_F,_N,_F,_F,_N,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_W,_W,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_W],
    # Row 13 – USB on floor (col 10) + HR phone (col 24)
    [_W,_F,_F,_F,_F,_F,_F,_F,_F,_F,_U,_F,_F,_F,_F,_F,_F,_F,_F,_W,_W,_F,_F,_F,_H,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_W],
    # Row 14 – desks row 2 + HR computer (col 35)
    [_W,_K,_C,_F,_K,_C,_F,_K,_C,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_W,_W,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_C,_F,_F,_F,_W],
    # Row 15 – chairs + plant
    [_W,_N,_F,_F,_N,_F,_F,_N,_F,_F,_F,_F,_F,_F,_P,_F,_F,_F,_F,_W,_W,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_W],
    # Row 16 – open floor
    [_W,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_W,_W,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_W],
    # Row 17 – SEPARATOR (single wall + doors at 9,10 and 29,30)
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_D,_D,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_D,_D,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    # Row 18 – CAFETERIA | MEETING carpet/floor
    [_W,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_W,_W,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_W],
    # Row 19 – cafeteria tables + poster (col 14) + meeting table
    [_W,_Z,_T,_T,_T,_Z,_T,_T,_T,_Z,_T,_T,_T,_Z,_S,_Z,_Z,_Z,_Z,_W,_W,_F,_T,_T,_T,_T,_T,_T,_T,_T,_T,_T,_T,_T,_T,_T,_T,_F,_F,_W],
    # Row 20 – chairs
    [_W,_Z,_N,_F,_N,_Z,_N,_F,_N,_Z,_N,_F,_N,_Z,_Z,_Z,_Z,_Z,_Z,_W,_W,_F,_N,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_N,_F,_F,_W],
    # Row 21 – open cafeteria
    [_W,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_W,_W,_F,_N,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_N,_F,_F,_W],
    # Row 22 – cabinets + CEO computer (col 23, meeting room)
    [_W,_A,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_A,_W,_W,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_W],
    # Row 23 – CEO computer at col 23
    [_W,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_Z,_W,_W,_F,_F,_C,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_W],
    # Row 24 – SEPARATOR (single wall + doors at 9,10 and 29,30)
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_D,_D,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_D,_D,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    # Row 25 – IT SUPPORT floor
    [_W,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_F,_W],
    # Row 26 – IT counter
    [_W,_F,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_R,_F,_W],
    # Row 27 – bottom border
    [_W]*40,
]

ROOM_LABELS = [
    {"name": "OUTSIDE",      "rows": range(0,  4),  "cols": range(0, 40)},
    {"name": "RECEPTION",    "rows": range(4,  9),  "cols": range(0, 40)},
    {"name": "WORK AREA",    "rows": range(10, 17), "cols": range(0, 20)},
    {"name": "HR ROOM",      "rows": range(10, 17), "cols": range(20, 40)},
    {"name": "CAFETERIA",    "rows": range(18, 24), "cols": range(0, 20)},
    {"name": "MEETING ROOM", "rows": range(18, 24), "cols": range(20, 40)},
    {"name": "IT SUPPORT",   "rows": range(25, 28), "cols": range(0, 40)},
]


class GameMap:
    def __init__(self):
        self.grid    = OFFICE_GRID
        self.height  = len(self.grid)
        self.width   = len(self.grid[0])
        self.renderer = TileRenderer(TILE_SIZE)
        self._surface = None
        # Pre-compute door positions once; avoids scanning all 1120 tiles every frame
        self._door_tiles = [
            (tx, ty)
            for ty in range(self.height)
            for tx in range(self.width)
            if self.grid[ty][tx] == _D
        ]

    def tile_at(self, tx, ty):
        if 0 <= ty < self.height and 0 <= tx < self.width:
            return self.grid[ty][tx]
        return 1   # wall

    def is_walkable(self, tx, ty):
        return self.tile_at(tx, ty) not in SOLID_TILES

    def get_room(self, tx, ty):
        for r in ROOM_LABELS:
            if ty in r["rows"] and tx in r["cols"]:
                return r["name"]
        return "OFFICE"

    def render_full(self):
        s = pygame.Surface((self.width * TILE_SIZE, self.height * TILE_SIZE))
        for ty in range(self.height):
            for tx in range(self.width):
                s.blit(self.renderer.get(self.tile_at(tx, ty)),
                       (tx * TILE_SIZE, ty * TILE_SIZE))
        return s

    def draw(self, screen, cam_x, cam_y, sw, sh):
        if self._surface is None:
            self._surface = self.render_full()
        screen.blit(self._surface, (0, 0), (cam_x, cam_y, sw, sh))

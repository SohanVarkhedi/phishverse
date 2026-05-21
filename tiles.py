"""
PHISHVERSE – tiles.py
Clean, readable pixel-art tiles at 40×40.
Every tile type is drawn with highlights and shadows for depth.
"""

import pygame
from constants import TILE_SIZE, ROOM_TINTS

# ── Tile IDs ─────────────────────────────────────────────────────────────────
TILE_FLOOR       = 0
TILE_WALL        = 1
TILE_DESK        = 2
TILE_DOOR        = 3
TILE_WINDOW      = 4
TILE_CARPET      = 5
TILE_COMPUTER    = 6
TILE_PLANT       = 7
TILE_POSTER      = 8
TILE_USB         = 9
TILE_PHONE       = 10
TILE_CHAIR       = 11
TILE_TABLE       = 12
TILE_GRASS       = 13
TILE_RECEPTION   = 14
TILE_BOOKSHELF   = 15
TILE_CABINET     = 16
TILE_ENTRY_FLOOR = 17

# Non-walkable tiles
SOLID_TILES = {
    TILE_WALL, TILE_DESK, TILE_WINDOW,
    TILE_PLANT, TILE_BOOKSHELF, TILE_CABINET,
    TILE_TABLE, TILE_RECEPTION,
}

# Tiles with interactive events
INTERACTIVE_TILES = {TILE_COMPUTER, TILE_POSTER, TILE_USB, TILE_PHONE}


def _bevel(surf, color, size=TILE_SIZE):
    """Add highlight on top-left and shadow on bottom-right edges."""
    hl = tuple(min(255, c + 30) for c in color)
    sh = tuple(max(0, c - 40)  for c in color)
    pygame.draw.line(surf, hl, (0, 0),      (size - 1, 0),      1)
    pygame.draw.line(surf, hl, (0, 0),      (0, size - 1),      1)
    pygame.draw.line(surf, sh, (0, size-1), (size-1, size-1),   1)
    pygame.draw.line(surf, sh, (size-1, 0), (size-1, size-1),   1)


class TileRenderer:
    def __init__(self, size: int = TILE_SIZE):
        self.s = size
        self._cache: dict[int, pygame.Surface] = {}

    def get(self, tile_id: int) -> pygame.Surface:
        if tile_id not in self._cache:
            self._cache[tile_id] = self._draw(tile_id)
        return self._cache[tile_id]

    def _surf(self, color) -> pygame.Surface:
        s = pygame.Surface((self.s, self.s))
        s.fill(color)
        return s

    def _draw(self, tid: int) -> pygame.Surface:
        fn = getattr(self, f"_t{tid}", None)
        return fn() if fn else self._surf((60, 60, 80))

    # ── Tile 0 – FLOOR ────────────────────────────────────────────────────────
    def _t0(self):
        col = (215, 208, 194)
        s = self._surf(col)
        h, t = self.s // 2, self.s
        # Grid lines for tile pattern
        pygame.draw.line(s, (200, 193, 180), (0, h), (t, h), 1)
        pygame.draw.line(s, (200, 193, 180), (h, 0), (h, t), 1)
        _bevel(s, col)
        return s

    # ── Tile 1 – WALL ─────────────────────────────────────────────────────────
    def _t1(self):
        col = (80, 70, 62)
        s = self._surf(col)
        t = self.s
        # Brick pattern
        for row in range(2):
            y1, y2 = row * (t//2), row * (t//2) + t//2 - 1
            offset = (t//4) if row % 2 == 1 else 0
            pygame.draw.rect(s, (95, 83, 72), (offset, y1 + 2, t//2 - 3, y2 - y1 - 4))
            pygame.draw.rect(s, (95, 83, 72), (offset + t//2, y1 + 2, t//2 - 3, y2 - y1 - 4))
            pygame.draw.line(s, (60, 52, 45), (0, y2), (t, y2), 1)
        _bevel(s, col)
        return s

    # ── Tile 2 – DESK ─────────────────────────────────────────────────────────
    def _t2(self):
        col = (175, 130, 75)
        s = self._surf((215, 208, 194))   # floor behind
        t = self.s
        # Desk surface
        pygame.draw.rect(s, col, (2, 5, t - 4, t - 10))
        pygame.draw.rect(s, (195, 150, 90), (2, 5, t - 4, 5))   # top highlight
        pygame.draw.rect(s, (140, 100, 55), (2, 5, t - 4, t - 10), 2)  # border
        # Drawer
        pygame.draw.rect(s, (155, 112, 62), (6, t//2, t - 12, t//2 - 8))
        pygame.draw.circle(s, (210, 180, 80), (t//2, t*3//4), 3)
        _bevel(s, col)
        return s

    # ── Tile 3 – DOOR ─────────────────────────────────────────────────────────
    def _t3(self):
        s = self._surf((215, 208, 194))
        t = self.s
        # Door frame + panel
        pygame.draw.rect(s, (165, 120, 55), (5, 0, t - 10, t - 3))
        pygame.draw.rect(s, (190, 145, 75), (5, 0, t - 10, t - 3), 2)
        # Panel lines
        pygame.draw.rect(s, (145, 104, 42), (9, 4, t-18, t//2 - 4))
        pygame.draw.rect(s, (145, 104, 42), (9, t//2 + 2, t-18, t//2 - 8))
        # Handle
        pygame.draw.circle(s, (220, 185, 80), (t - 10, t//2), 4)
        pygame.draw.circle(s, (200, 160, 60), (t - 10, t//2), 4, 1)
        return s

    # ── Tile 4 – WINDOW ──────────────────────────────────────────────────────
    def _t4(self):
        col = (80, 70, 62)
        s = self._surf(col)
        t = self.s
        pygame.draw.rect(s, (145, 200, 235), (4, 4, t-8, t-8))
        pygame.draw.line(s, (175, 220, 250), (t//2, 4), (t//2, t-4), 1)
        pygame.draw.line(s, (175, 220, 250), (4, t//2), (t-4, t//2), 1)
        pygame.draw.rect(s, (130, 95, 55), (4, 4, t-8, t-8), 2)
        # Reflection
        pygame.draw.rect(s, (200, 230, 255), (6, 6, 8, 8))
        return s

    # ── Tile 5 – CARPET ──────────────────────────────────────────────────────
    def _t5(self):
        col = (115, 95, 135)
        s = self._surf(col)
        t = self.s
        # Subtle weave pattern
        for i in range(0, t, 5):
            pygame.draw.line(s, (100, 82, 120), (i, 0), (i, t), 1)
        for i in range(0, t, 5):
            pygame.draw.line(s, (125, 105, 148), (0, i), (t, i), 1)
        _bevel(s, col)
        return s

    # ── Tile 6 – COMPUTER ────────────────────────────────────────────────────
    def _t6(self):
        s = self._surf((175, 130, 75))
        t = self.s
        # Monitor body
        pygame.draw.rect(s, (28, 28, 45), (5, 3, t-10, t-15))
        # Screen with glow
        pygame.draw.rect(s, (0, 40, 120), (8, 6, t-16, t-22))
        pygame.draw.rect(s, (0, 80, 200), (8, 6, t-16, t-22), 1)
        # Screen content (code lines)
        for i, line_col in enumerate([(0,255,100),(0,200,255),(0,255,100)]):
            pygame.draw.rect(s, line_col, (10, 9+i*4, (t-22)//2 + (i%2)*4, 2))
        # Stand
        pygame.draw.rect(s, (50, 50, 65), (t//2-4, t-12, 8, 5))
        pygame.draw.rect(s, (50, 50, 65), (t//2-8, t-8, 16, 3))
        return s

    # ── Tile 7 – PLANT ───────────────────────────────────────────────────────
    def _t7(self):
        s = self._surf((215, 208, 194))
        t = self.s
        # Pot
        pygame.draw.rect(s, (140, 100, 70), (t//2-6, t-13, 12, 10))
        pygame.draw.rect(s, (160, 120, 85), (t//2-6, t-13, 12, 3))
        # Leaves
        pygame.draw.circle(s, (50, 140, 60), (t//2, t//2-2), 11)
        pygame.draw.circle(s, (65, 160, 70), (t//2-7, t//2+3), 8)
        pygame.draw.circle(s, (65, 160, 70), (t//2+7, t//2+3), 8)
        pygame.draw.circle(s, (80, 180, 80), (t//2, t//2-6), 6)
        return s

    # ── Tile 8 – POSTER ──────────────────────────────────────────────────────
    def _t8(self):
        col = (80, 70, 62)
        s = self._surf(col)
        t = self.s
        # Poster paper
        pygame.draw.rect(s, (245, 242, 220), (4, 4, t-8, t-8))
        # Red header bar
        pygame.draw.rect(s, (210, 50, 50), (4, 4, t-8, 10))
        pygame.draw.rect(s, (235, 70, 70), (4, 4, t-8, 5))
        # Text lines
        for i in range(3):
            pygame.draw.rect(s, (160, 155, 140), (7, 18+i*6, t-18, 3))
        # QR code hint
        pygame.draw.rect(s, (30, 30, 30), (t-18, t-18, 10, 10))
        for qi in range(2):
            for qj in range(2):
                pygame.draw.rect(s, (255,255,255), (t-17+qi*4, t-17+qj*4, 3, 3))
        pygame.draw.rect(s, (150, 100, 40), (4, 4, t-8, t-8), 2)
        return s

    # ── Tile 9 – USB ─────────────────────────────────────────────────────────
    def _t9(self):
        s = self._surf((215, 208, 194))
        t = self.s
        cx, cy = t//2, t//2
        # USB body
        pygame.draw.rect(s, (210, 195, 50), (cx-8, cy-4, 16, 8))
        pygame.draw.rect(s, (235, 220, 70), (cx-8, cy-4, 16, 3))
        pygame.draw.rect(s, (180, 165, 30), (cx-8, cy-4, 16, 8), 1)
        # Plug end
        pygame.draw.rect(s, (70, 70, 85), (cx-4, cy-7, 8, 3))
        pygame.draw.rect(s, (50, 50, 65), (cx-4, cy-7, 8, 3), 1)
        # Label text dots
        for i in range(3):
            pygame.draw.rect(s, (100, 85, 0), (cx-5+i*4, cy, 3, 2))
        return s

    # ── Tile 10 – PHONE ──────────────────────────────────────────────────────
    def _t10(self):
        s = self._surf((175, 130, 75))
        t = self.s
        # Phone base
        pygame.draw.rect(s, (40, 40, 55), (5, 6, t-10, t-12))
        pygame.draw.rect(s, (55, 55, 70), (5, 6, t-10, 4))
        # Handset cradle
        pygame.draw.rect(s, (25, 25, 40), (7, 8, t-14, t-18))
        # Buttons grid
        for r in range(3):
            for c in range(3):
                pygame.draw.rect(s, (80, 80, 100), (9+c*6, 16+r*5, 4, 3))
        pygame.draw.rect(s, (40, 40, 55), (5, 6, t-10, t-12), 1)
        return s

    # ── Tile 11 – CHAIR ──────────────────────────────────────────────────────
    def _t11(self):
        s = self._surf((215, 208, 194))
        t = self.s
        # Back
        pygame.draw.rect(s, (70, 70, 80), (5, 4, t-10, 7))
        pygame.draw.rect(s, (85, 85, 95), (5, 4, t-10, 3))
        # Seat
        pygame.draw.rect(s, (80, 80, 92), (7, 11, t-14, t-20))
        # Legs
        for lx in [6, t-8]:
            pygame.draw.rect(s, (50, 50, 60), (lx, t-10, 4, 8))
        return s

    # ── Tile 12 – TABLE ──────────────────────────────────────────────────────
    def _t12(self):
        col = (155, 118, 70)
        s = self._surf((215, 208, 194))
        t = self.s
        pygame.draw.rect(s, col, (2, 8, t-4, t-16))
        pygame.draw.rect(s, (175, 138, 88), (2, 8, t-4, 5))
        pygame.draw.rect(s, (125, 92, 50), (2, 8, t-4, t-16), 2)
        return s

    # ── Tile 13 – GRASS ──────────────────────────────────────────────────────
    def _t13(self):
        col = (105, 155, 90)
        import random
        s = self._surf(col)
        t = self.s
        rng = random.Random(7)
        for _ in range(10):
            x, y = rng.randint(2, t-4), rng.randint(4, t-2)
            pygame.draw.line(s, (80, 130, 65), (x, y), (x+rng.randint(-2,2), y-5), 1)
        _bevel(s, col)
        return s

    # ── Tile 14 – RECEPTION DESK ─────────────────────────────────────────────
    def _t14(self):
        col = (195, 140, 80)
        s = self._surf((215, 208, 194))
        t = self.s
        pygame.draw.rect(s, col, (0, t//3, t, t*2//3))
        pygame.draw.rect(s, (215, 162, 100), (0, t//3, t, 5))
        pygame.draw.rect(s, (155, 108, 55), (0, t//3, t, t*2//3), 2)
        return s

    # ── Tile 15 – BOOKSHELF ──────────────────────────────────────────────────
    def _t15(self):
        col = (140, 100, 60)
        s = self._surf(col)
        t = self.s
        pygame.draw.rect(s, col, (2, 2, t-4, t-4), 3)
        book_colors = [(200,55,55),(55,55,200),(55,180,55),(220,180,40),(180,55,180)]
        bw = (t - 8) // len(book_colors)
        for i, bc in enumerate(book_colors):
            pygame.draw.rect(s, bc, (4 + i*bw, 4, bw-1, t-10))
            pygame.draw.rect(s, tuple(max(0,c-30) for c in bc), (4+i*bw, 4, bw-1, t-10), 1)
        return s

    # ── Tile 16 – CABINET ────────────────────────────────────────────────────
    def _t16(self):
        col = (120, 125, 140)
        s = self._surf(col)
        t = self.s
        pygame.draw.rect(s, (140, 145, 160), (3, 2, t-6, t-4))
        pygame.draw.line(s, (90, 95, 110), (t//2, 2), (t//2, t-3), 2)
        pygame.draw.circle(s, (215, 190, 75), (t//4, t//2), 4)
        pygame.draw.circle(s, (195, 168, 55), (t//4, t//2), 4, 1)
        pygame.draw.circle(s, (215, 190, 75), (3*t//4, t//2), 4)
        pygame.draw.circle(s, (195, 168, 55), (3*t//4, t//2), 4, 1)
        pygame.draw.rect(s, (90, 95, 110), (3, 2, t-6, t-4), 2)
        return s

    # ── Tile 17 – ENTRY FLOOR ────────────────────────────────────────────────
    def _t17(self):
        col = (155, 170, 145)
        s = self._surf(col)
        t = self.s
        pygame.draw.rect(s, (135, 150, 125), (2, 2, t-4, t-4), 1)
        pygame.draw.line(s, (140, 155, 130), (0, t//2), (t, t//2), 1)
        pygame.draw.line(s, (140, 155, 130), (t//2, 0), (t//2, t), 1)
        _bevel(s, col)
        return s

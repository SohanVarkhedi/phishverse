"""
PHISHVERSE 3D – raycaster.py
DDA raycasting engine. Renders:
 - Ceiling gradient
 - Floor gradient (distance-shaded)
 - Walls (per-room colour + fog + pseudo-texture via hash noise)
 - Billboard sprites for objects and NPCs
Renders at RAY_W × RAY_H then scales to SCREEN_WIDTH × SCREEN_HEIGHT.
"""

import pygame
import math
from constants import (
    RAY_W, RAY_H, SCREEN_WIDTH, SCREEN_HEIGHT,
    MAX_DEPTH, FOG_START, FOG_END,
    WALL_COLORS, CEILING_COLOR, FLOOR_TOP, FLOOR_FAR,
)


def _fog(color: tuple, dist: float) -> tuple:
    """Blend colour toward near-black based on distance."""
    t = max(0.0, min(1.0, (dist - FOG_START) / (FOG_END - FOG_START)))
    return tuple(int(c * (1 - t)) for c in color)


def _noise(tx: int, ty: int, tex_x: int, tex_y: int) -> int:
    """Cheap deterministic hash → subtle wall texture variation (±12)."""
    h = (tx * 374761393 + ty * 668265263 + tex_x * 2246822519 + tex_y * 3266489917)
    return ((h >> 13) ^ h) % 25 - 12


class Raycaster:
    def __init__(self):
        self._buf   = pygame.Surface((RAY_W, RAY_H))
        self._zbuf  = [0.0] * RAY_W   # depth buffer for sprites
        self._out   = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    def render(self, player, game_map) -> pygame.Surface:
        self._draw_floor_ceiling()
        self._cast_walls(player, game_map)
        # Scale up
        pygame.transform.scale(self._buf, (SCREEN_WIDTH, SCREEN_HEIGHT), self._out)
        return self._out

    def z_buffer(self) -> list:
        return self._zbuf

    # ── Floor & Ceiling ──────────────────────────────────────────────────────

    def _draw_floor_ceiling(self):
        buf = self._buf
        half = RAY_H // 2

        # Ceiling – solid dark
        buf.fill(CEILING_COLOR, (0, 0, RAY_W, half))

        # Floor – gradient strips (near=lighter, far=darker)
        for y in range(half, RAY_H):
            t = (y - half) / half          # 0=horizon, 1=feet
            r = int(FLOOR_TOP[0] + (FLOOR_FAR[0] - FLOOR_TOP[0]) * (1 - t))
            g = int(FLOOR_TOP[1] + (FLOOR_FAR[1] - FLOOR_TOP[1]) * (1 - t))
            b = int(FLOOR_TOP[2] + (FLOOR_FAR[2] - FLOOR_TOP[2]) * (1 - t))
            buf.fill((r, g, b), (0, y, RAY_W, 1))

    # ── Wall casting ─────────────────────────────────────────────────────────

    def _cast_walls(self, player, game_map):
        buf  = self._buf
        half = RAY_H // 2
        px, py   = player.x, player.y
        dx, dy   = player.dir_x, player.dir_y
        plx, ply = player.plane_x, player.plane_y
        bob      = int(player.bob_offset)

        for col in range(RAY_W):
            cam     = 2 * col / RAY_W - 1          # -1 … 1
            rdx     = dx + plx * cam
            rdy     = dy + ply * cam

            mx, my  = int(px), int(py)

            dsx = abs(1 / rdx) if rdx != 0 else 1e30
            dsy = abs(1 / rdy) if rdy != 0 else 1e30

            if rdx < 0:
                sx = -1; sdx = (px - mx) * dsx
            else:
                sx = 1;  sdx = (mx + 1 - px) * dsx
            if rdy < 0:
                sy = -1; sdy = (py - my) * dsy
            else:
                sy = 1;  sdy = (my + 1 - py) * dsy

            hit  = False
            side = 0
            for _ in range(MAX_DEPTH):
                if sdx < sdy:
                    sdx += dsx; mx += sx; side = 0
                else:
                    sdy += dsy; my += sy; side = 1
                if game_map.is_solid(mx, my):
                    hit = True
                    break

            if not hit:
                self._zbuf[col] = 1e30
                continue

            dist = (sdx - dsx) if side == 0 else (sdy - dsy)
            dist = max(dist, 0.001)
            self._zbuf[col] = dist

            wall_h    = int(RAY_H / dist)
            top       = max(0, half - wall_h // 2 + bob)
            bot       = min(RAY_H - 1, half + wall_h // 2 + bob)
            draw_h    = max(1, bot - top)

            # Wall hit position → texture x coordinate (0-63)
            if side == 0:
                wall_hit = py + dist * rdy
            else:
                wall_hit = px + dist * rdx
            wall_hit -= int(wall_hit)
            tex_x = int(wall_hit * 64)

            # Base color from wall type
            wtype   = game_map.get_wall(mx, my)
            colors  = WALL_COLORS.get(wtype, ((120, 120, 120), (80, 80, 80)))
            base    = colors[1] if side == 1 else colors[0]

            # Fog
            base = _fog(base, dist)

            # Draw wall strip with vertical texture noise
            step  = 64 / draw_h
            tex_y = 0.0
            for row in range(top, bot):
                n    = _noise(mx, my, tex_x, int(tex_y))
                c    = tuple(max(0, min(255, v + n)) for v in base)
                buf.set_at((col, row), c)
                tex_y += step


# ── Sprite / billboard renderer ───────────────────────────────────────────────

SPRITE_COLORS = {
    "💻": (60,  120, 200),
    "📋": (200, 180,  60),
    "💾": (200, 160,  40),
    "📞": (80,  160, 100),
    "🚨": (220,  50,  50),
    "NPC": (180,  80,  80),
}


def render_sprites(screen: pygame.Surface, player, objects: list,
                   zbuf: list, font: pygame.font.Font,
                   seen_events: set, small_font: pygame.font.Font):
    """
    Render billboard sprites for objects and NPCs.
    objects = [(wx, wy, event_id_or_'NPC', icon, label), ...]
    """
    px, py   = player.x, player.y
    dx, dy   = player.dir_x, player.dir_y
    plx, ply = player.plane_x, player.plane_y

    # Sort back-to-front
    sprites  = sorted(objects, key=lambda o: -(o[0]-px)**2 - (o[1]-py)**2)

    sw, sh   = SCREEN_WIDTH, SCREEN_HEIGHT
    scale_x  = sw / RAY_W
    scale_y  = sh / RAY_H

    for (wx, wy, ev_id, icon, label) in sprites:
        # Hide completed events (keep NPCs always)
        if ev_id != "NPC" and ev_id in seen_events:
            continue

        # Transform to camera space
        rel_x   = wx - px
        rel_y   = wy - py
        inv_det = 1.0 / (plx * dy - dx * ply)
        tx      =  inv_det * (dy  * rel_x - dx  * rel_y)
        ty_     =  inv_det * (-ply * rel_x + plx * rel_y)

        if ty_ <= 0.1:
            continue   # behind player

        # Screen X centre
        sx_ctr  = int((sw / 2) * (1 + tx / ty_))
        dist    = ty_

        # Sprite height / width on screen
        spr_h   = abs(int(sh / dist))
        spr_w   = spr_h
        spr_h   = min(spr_h, sh)
        spr_w   = min(spr_w, sw)

        draw_top  = sh // 2 - spr_h // 2
        left_col  = sx_ctr - spr_w // 2
        right_col = sx_ctr + spr_w // 2

        if right_col < 0 or left_col > sw:
            continue

        # Colour
        color = SPRITE_COLORS.get(icon, (160, 160, 160))
        fog_t = max(0.0, min(1.0, (dist - FOG_START) / (FOG_END - FOG_START)))
        color = tuple(int(c * (1 - fog_t)) for c in color)
        dark  = tuple(max(0, c - 30) for c in color)

        # Draw visible columns
        for scol in range(max(0, left_col), min(sw, right_col)):
            ray_col = int(scol / scale_x)
            if ray_col >= RAY_W or zbuf[ray_col] < dist:
                continue
            # Simple sprite body
            stripe_x = (scol - left_col) / max(spr_w, 1)
            c = color if stripe_x < 0.5 else dark
            pygame.draw.line(screen, c,
                             (scol, max(0, draw_top)),
                             (scol, min(sh, draw_top + spr_h)))

        # Label / icon above sprite (only when close)
        if dist < 4.0:
            alpha = int(255 * max(0, 1 - dist / 4))
            lbl = small_font.render(f"{icon} {label}", True, (255, 240, 100))
            lx  = sx_ctr - lbl.get_width() // 2
            ly  = max(5, draw_top - 20)
            # pulse on unseen events
            if ev_id != "NPC" and ev_id not in seen_events:
                t = pygame.time.get_ticks()
                pulse = abs(math.sin(t / 300)) * 50
                bg = pygame.Surface((lbl.get_width() + 10, lbl.get_height() + 4), pygame.SRCALPHA)
                bg.fill((30, 20, 0, int(180 + pulse)))
                screen.blit(bg, (lx - 5, ly - 2))
            screen.blit(lbl, (lx, ly))

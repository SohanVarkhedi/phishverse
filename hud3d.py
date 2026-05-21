"""
PHISHVERSE 3D – hud3d.py
Cyberpunk / Deus-Ex inspired HUD overlay drawn on top of 3D view.
Includes: score bar, room label, crosshair, minimap, objective ticker,
threat counter, interaction prompt, and screen-flash effects.
"""

import pygame
import math
from constants import *
from map3d import GRID, MAP_W, MAP_H, get_wall


class HUD3D:
    def __init__(self, sw: int, sh: int):
        self.sw = sw
        self.sh = sh
        self.objective = "Find your desk in the Work Area."
        self._font  = None
        self._big   = None
        self._small = None

    def set_fonts(self, font, big, small):
        self._font  = font
        self._big   = big
        self._small = small

    def set_objective(self, text: str):
        self.objective = text

    # ── Main draw ────────────────────────────────────────────────────────────

    def draw(self, screen: pygame.Surface, score: int,
             completed: int, total: int, room: str,
             player_x: float, player_y: float, player_angle: float,
             interact_hint: str = ""):

        self._draw_top_bar(screen, score, completed, total, room)
        self._draw_crosshair(screen)
        self._draw_minimap(screen, player_x, player_y, player_angle)
        self._draw_objective(screen)
        if interact_hint:
            self._draw_interact_prompt(screen, interact_hint)

    # ── Top bar ──────────────────────────────────────────────────────────────

    def _draw_top_bar(self, screen, score, completed, total, room):
        h = 44
        bar = pygame.Surface((self.sw, h), pygame.SRCALPHA)
        bar.fill((5, 5, 20, 200))
        screen.blit(bar, (0, 0))

        # Left: score
        sc_col = UI_HIGHLIGHT if score >= 70 else (UI_WARNING if score < 50 else UI_GOLD)
        pygame.draw.rect(screen, (20, 20, 50), (8, 6, 180, 32), border_radius=4)
        pygame.draw.rect(screen, sc_col,       (8, 6, 180, 32), 1, border_radius=4)
        sl = self._small.render("CYBER SCORE", True, LIGHT_GREY)
        sv = self._big.render(str(score), True, sc_col)
        screen.blit(sl, (14, 8))
        screen.blit(sv, (14, 20))

        # Score bar
        bx, by, bw, bh = 80, 20, 100, 10
        pygame.draw.rect(screen, (40, 40, 60), (bx, by, bw, bh), border_radius=5)
        fw = max(0, int(bw * score / 100))
        pygame.draw.rect(screen, sc_col,       (bx, by, fw, bh), border_radius=5)
        pygame.draw.rect(screen, UI_BORDER,    (bx, by, bw, bh), 1, border_radius=5)

        # Centre: room
        t = pygame.time.get_ticks()
        pulse = int(180 + 60 * math.sin(t / 800))
        rl = self._font.render(f"📍  {room}", True, (pulse, 210, 255))
        screen.blit(rl, (self.sw // 2 - rl.get_width() // 2, 12))

        # Right: threats
        pygame.draw.rect(screen, (20, 20, 50), (self.sw - 148, 6, 140, 32), border_radius=4)
        pygame.draw.rect(screen, UI_WARNING,   (self.sw - 148, 6, 140, 32), 1, border_radius=4)
        tl = self._small.render("THREATS", True, LIGHT_GREY)
        tv = self._big.render(f"{completed}/{total}", True,
                              UI_HIGHLIGHT if completed == total else UI_WARNING)
        screen.blit(tl, (self.sw - 142, 8))
        screen.blit(tv, (self.sw - 80, 18))

    # ── Crosshair ────────────────────────────────────────────────────────────

    def _draw_crosshair(self, screen):
        cx, cy = self.sw // 2, self.sh // 2
        size, gap, thick = 10, 4, 2
        col = (200, 220, 255, 180)
        # Draw with alpha
        ch = pygame.Surface((50, 50), pygame.SRCALPHA)
        m = 25
        pygame.draw.line(ch, col, (m - size, m), (m - gap, m), thick)
        pygame.draw.line(ch, col, (m + gap,  m), (m + size, m), thick)
        pygame.draw.line(ch, col, (m, m - size), (m, m - gap), thick)
        pygame.draw.line(ch, col, (m, m + gap),  (m, m + size), thick)
        pygame.draw.circle(ch, col, (m, m), 2)
        screen.blit(ch, (cx - 25, cy - 25))

    # ── Minimap ──────────────────────────────────────────────────────────────

    def _draw_minimap(self, screen, px: float, py: float, angle: float):
        CELL  = 6
        cols  = min(MAP_W, 20)
        rows  = min(MAP_H, 20)
        mw    = cols * CELL
        mh    = rows * CELL
        ox    = self.sw - mw - 10
        oy    = self.sh - mh - 10

        # Background
        bg = pygame.Surface((mw, mh), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        screen.blit(bg, (ox, oy))
        pygame.draw.rect(screen, UI_BORDER, (ox, oy, mw, mh), 1)

        # Tiles
        wall_colors_mini = {
            1: (80, 78, 72), 2: (40, 60, 90), 3: (80, 60, 40),
            4: (35, 80, 50), 5: (80, 35, 35), 6: (35, 55, 90),
            7: (120, 110, 40),
        }
        for ty in range(rows):
            for tx in range(cols):
                w = get_wall(tx, ty)
                if w != 0:
                    c = wall_colors_mini.get(w, (60, 60, 60))
                    pygame.draw.rect(screen, c,
                                     (ox + tx * CELL, oy + ty * CELL, CELL, CELL))

        # Player dot + direction line
        pdx = int((px) * CELL)
        pdy = int((py) * CELL)
        pygame.draw.circle(screen, UI_GOLD, (ox + pdx, oy + pdy), 3)
        edx = int(px * CELL + math.cos(angle) * 8)
        edy = int(py * CELL + math.sin(angle) * 8)
        pygame.draw.line(screen, UI_GOLD,
                         (ox + pdx, oy + pdy),
                         (ox + edx, oy + edy), 1)

    # ── Objective ────────────────────────────────────────────────────────────

    def _draw_objective(self, screen):
        h = 26
        bg = pygame.Surface((self.sw, h), pygame.SRCALPHA)
        bg.fill((5, 5, 20, 190))
        screen.blit(bg, (0, self.sh - h))
        pygame.draw.line(screen, UI_BORDER,
                         (0, self.sh - h), (self.sw, self.sh - h), 1)
        ol = self._small.render(f"▶  OBJECTIVE: {self.objective}", True, UI_TEXT)
        screen.blit(ol, (10, self.sh - h + 5))

    # ── Interact prompt ──────────────────────────────────────────────────────

    def _draw_interact_prompt(self, screen, hint: str):
        t = pygame.time.get_ticks()
        pulse = int(160 + 80 * abs(math.sin(t / 400)))
        lbl   = self._font.render(hint, True, WHITE)
        w, h  = lbl.get_width() + 24, lbl.get_height() + 12
        px    = self.sw // 2 - w // 2
        py    = self.sh // 2 + 60

        bg = pygame.Surface((w, h), pygame.SRCALPHA)
        bg.fill((10, 10, 35, pulse))
        pygame.draw.rect(bg, (*UI_GOLD, pulse), (0, 0, w, h), 2, border_radius=6)
        screen.blit(bg,  (px, py))
        screen.blit(lbl, (px + 12, py + 6))


class PauseMenu3D:
    OPTIONS = ["RESUME", "CONTROLS", "QUIT"]

    def __init__(self, sw, sh):
        self.sw = sw
        self.sh = sh
        self.sel = 0
        self._font = self._big = self._small = None

    def set_fonts(self, f, b, s):
        self._font = f; self._big = b; self._small = s

    def handle_key(self, key) -> str | None:
        if key == pygame.K_UP:
            self.sel = (self.sel - 1) % len(self.OPTIONS)
        elif key == pygame.K_DOWN:
            self.sel = (self.sel + 1) % len(self.OPTIONS)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            return self.OPTIONS[self.sel]
        elif key == pygame.K_ESCAPE:
            return "RESUME"
        return None

    def draw(self, screen):
        dim = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 170))
        screen.blit(dim, (0, 0))

        pw, ph = 320, 260
        px = self.sw // 2 - pw // 2
        py = self.sh // 2 - ph // 2
        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((8, 8, 25, 230))
        screen.blit(panel, (px, py))
        pygame.draw.rect(screen, UI_BORDER, (px, py, pw, ph), 2, border_radius=8)

        title = self._big.render("PHISHVERSE 3D", True, UI_GOLD)
        sub   = self._small.render("— PAUSED —", True, LIGHT_GREY)
        screen.blit(title, (px + pw//2 - title.get_width()//2, py + 14))
        screen.blit(sub,   (px + pw//2 - sub.get_width()//2,   py + 42))
        pygame.draw.line(screen, UI_BORDER, (px+16, py+60), (px+pw-16, py+60), 1)

        controls_text = [
            "W/S  – Move forward/back",
            "A/D  – Strafe left/right",
            "Q/E or ←/→ – Rotate",
            "F / Enter – Interact",
            "ESC  – Pause",
        ]

        for i, opt in enumerate(self.OPTIONS):
            y = py + 80 + i * 46
            issel = (i == self.sel)
            if issel:
                pygame.draw.rect(screen, CHOICE_HL,
                                 (px+18, y-5, pw-36, 34), border_radius=5)
            lbl = self._font.render(opt, True, WHITE if issel else LIGHT_GREY)
            screen.blit(lbl, (px + pw//2 - lbl.get_width()//2, y))

        if self.sel == 1:
            for j, line in enumerate(controls_text):
                cl = self._small.render(line, True, UI_TEXT)
                screen.blit(cl, (px + pw//2 - cl.get_width()//2,
                                 py + ph - 95 + j * 16))

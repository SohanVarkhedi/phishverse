"""
PHISHVERSE – ui.py
HUD overlay: score bar, threat counter, objective strip,
room label, mini-map indicator, and pause menu.
"""

import pygame
import math
from constants import *


class HUD:
    """Top-screen HUD displaying score, threats and current objective."""

    def __init__(self, screen_w: int, screen_h: int):
        self.sw = screen_w
        self.sh = screen_h
        self._font      = None
        self._big_font  = None
        self._small     = None
        self.objective  = "Head to Reception and begin your workday."

    def set_fonts(self, font, big_font, small_font):
        self._font     = font
        self._big_font = big_font
        self._small    = small_font
        # Pre-allocate fixed-size background surfaces — avoids SRCALPHA construction every frame
        self._top_bg = pygame.Surface((self.sw, 38), pygame.SRCALPHA)
        self._top_bg.fill((10, 10, 28, 210))
        self._obj_bg = pygame.Surface((self.sw, 28), pygame.SRCALPHA)
        self._obj_bg.fill((10, 10, 28, 180))

    # ── Update ───────────────────────────────────────────────────────────────

    def set_objective(self, text: str):
        self.objective = text

    # ── Draw ─────────────────────────────────────────────────────────────────

    def draw(self, screen: pygame.Surface, score: int, completed: int,
             total: int, room: str):
        self._draw_top_bar(screen, score, completed, total, room)
        self._draw_objective(screen)

    def _draw_top_bar(self, screen, score, completed, total, room):
        bar_h = 38
        screen.blit(self._top_bg, (0, 0))
        pygame.draw.line(screen, UI_BORDER, (0, bar_h), (self.sw, bar_h), 2)

        # Score badge
        score_color = UI_HIGHLIGHT if score >= 70 else (UI_WARNING if score < 50 else UI_GOLD)
        score_text  = self._font.render(f"CYBER SCORE", True, LIGHT_GREY)
        score_val   = self._big_font.render(f"{score}", True, score_color)
        screen.blit(score_text, (12, 4))
        screen.blit(score_val,  (12, 18))

        # Score bar
        bar_x, bar_y = 120, 14
        bar_w, bar_h2 = 160, 12
        pygame.draw.rect(screen, (40, 40, 60), (bar_x, bar_y, bar_w, bar_h2), border_radius=6)
        fill_w = int(bar_w * (score / 100))
        if fill_w > 0:
            pygame.draw.rect(screen, score_color, (bar_x, bar_y, fill_w, bar_h2), border_radius=6)
        pygame.draw.rect(screen, UI_BORDER, (bar_x, bar_y, bar_w, bar_h2), 1, border_radius=6)

        # Room label (centre)
        room_surf = self._font.render(f"📍 {room}", True, UI_GOLD)
        screen.blit(room_surf, (self.sw // 2 - room_surf.get_width() // 2, 10))

        # Threats counter (right)
        threat_txt = self._font.render("THREATS", True, LIGHT_GREY)
        threat_val = self._big_font.render(f"{completed}/{total}", True, UI_WARNING if completed < total else UI_HIGHLIGHT)
        screen.blit(threat_txt, (self.sw - 100, 4))
        screen.blit(threat_val, (self.sw - 80,  18))

    def _draw_objective(self, screen):
        h = 28
        screen.blit(self._obj_bg, (0, self.sh - h))
        pygame.draw.line(screen, UI_BORDER, (0, self.sh - h), (self.sw, self.sh - h), 1)
        label = self._small.render(f"▶ OBJECTIVE: {self.objective}", True, UI_TEXT)
        screen.blit(label, (10, self.sh - h + 6))


class PauseMenu:
    """ESC menu shown during exploration."""

    OPTIONS = ["RESUME", "CONTROLS", "QUIT"]

    def __init__(self, screen_w: int, screen_h: int):
        self.sw = screen_w
        self.sh = screen_h
        self.selected = 0
        self._font  = None
        self._big   = None
        self._small = None

    def set_fonts(self, font, big, small):
        self._font  = font
        self._big   = big
        self._small = small

    def handle_key(self, key: int) -> str | None:
        """Returns 'RESUME', 'QUIT', or None."""
        if key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(self.OPTIONS)
        elif key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(self.OPTIONS)
        elif key in (pygame.K_RETURN, pygame.K_e):
            return self.OPTIONS[self.selected]
        elif key == pygame.K_ESCAPE:
            return "RESUME"
        return None

    def draw(self, screen: pygame.Surface):
        # Dim background
        dim = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 160))
        screen.blit(dim, (0, 0))

        # Panel
        pw, ph = 300, 280
        px = self.sw // 2 - pw // 2
        py = self.sh // 2 - ph // 2
        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((*UI_BG, 230))
        screen.blit(panel, (px, py))
        pygame.draw.rect(screen, UI_BORDER, (px, py, pw, ph), 3, border_radius=8)

        # Title
        title = self._big.render("PHISHVERSE", True, UI_GOLD)
        screen.blit(title, (px + pw // 2 - title.get_width() // 2, py + 16))
        subtitle = self._small.render("PAUSED", True, LIGHT_GREY)
        screen.blit(subtitle, (px + pw // 2 - subtitle.get_width() // 2, py + 44))
        pygame.draw.line(screen, UI_BORDER, (px + 16, py + 62), (px + pw - 16, py + 62), 1)

        # Options
        for i, opt in enumerate(self.OPTIONS):
            is_sel = (i == self.selected)
            y = py + 86 + i * 52
            if is_sel:
                pygame.draw.rect(screen, CHOICE_HL, (px + 20, y - 6, pw - 40, 36), border_radius=6)
            color = WHITE if is_sel else LIGHT_GREY
            lbl = self._font.render(opt, True, color)
            screen.blit(lbl, (px + pw // 2 - lbl.get_width() // 2, y))

        # Controls hint
        if self.selected == 1:
            controls = [
                "WASD / Arrow Keys – Move",
                "E / Enter        – Interact",
                "ESC              – Pause",
            ]
            for j, line in enumerate(controls):
                surf = self._small.render(line, True, UI_TEXT)
                screen.blit(surf, (px + pw // 2 - surf.get_width() // 2, py + ph - 80 + j * 20))


class TitleScreen:
    """Animated splash / title screen."""

    def __init__(self, screen_w: int, screen_h: int):
        self.sw = screen_w
        self.sh = screen_h
        self._font  = None
        self._big   = None
        self._small = None
        self._timer = 0

    def set_fonts(self, font, big, small):
        self._font  = font
        self._big   = big
        self._small = small

    def update(self):
        self._timer += 1

    def handle_key(self, key) -> bool:
        """Returns True when player presses Enter to start."""
        return key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e)

    def draw(self, screen: pygame.Surface):
        # Animated gradient background
        t = self._timer
        for y in range(self.sh):
            r = int(10 + 10 * math.sin(t / 60 + y / 80))
            g = int(15 + 10 * math.sin(t / 80 + y / 60))
            b = int(40 + 20 * math.sin(t / 40 + y / 40))
            pygame.draw.line(screen, (r, g, b), (0, y), (self.sw, y))

        # Scanline overlay (retro effect)
        for y in range(0, self.sh, 3):
            pygame.draw.line(screen, (0, 0, 0, 40), (0, y), (self.sw, y))

        # Logo
        pulse = int(3 * math.sin(t / 20))
        cx = self.sw // 2

        # Glow
        for r in range(80, 20, -10):
            alpha = max(0, 40 - (80 - r))
            glow = pygame.Surface((r * 4, r * 2), pygame.SRCALPHA)
            glow.fill((0, 80, 255, alpha))
            screen.blit(glow, (cx - r * 2, 120 - r))

        title1 = self._big.render("PHISHVERSE", True, UI_GOLD)
        title2 = self._big.render("PHISHVERSE", True, (255, 200, 0))
        screen.blit(title1, (cx - title1.get_width() // 2 + 2, 122 + pulse + 2))
        screen.blit(title2, (cx - title2.get_width() // 2, 120 + pulse))

        sub = self._font.render("CYBERSECURITY AWARENESS RPG", True, UI_BORDER)
        screen.blit(sub, (cx - sub.get_width() // 2, 185))

        desc_lines = [
            "Navigate the office. Avoid phishing attacks.",
            "Every choice shapes your Cyber Resilience Score.",
        ]
        for i, line in enumerate(desc_lines):
            s = self._small.render(line, True, LIGHT_GREY)
            screen.blit(s, (cx - s.get_width() // 2, 230 + i * 22))

        # Blinking prompt
        if (t // 30) % 2 == 0:
            prompt = self._font.render("▶  PRESS ENTER TO START  ◀", True, UI_HIGHLIGHT)
            screen.blit(prompt, (cx - prompt.get_width() // 2, 310))

        # Controls strip at bottom
        controls = [
            "WASD / Arrows: Move",
            "E / Enter: Interact",
            "ESC: Pause",
        ]
        strip_y = self.sh - 50
        bg = pygame.Surface((self.sw, 45), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 140))
        screen.blit(bg, (0, strip_y))
        gap = self.sw // (len(controls) + 1)
        for i, ctrl in enumerate(controls):
            s = self._small.render(ctrl, True, UI_TEXT)
            screen.blit(s, ((i + 1) * gap - s.get_width() // 2, strip_y + 12))

        # Version tag
        ver = self._small.render("v1.0  —  Cybersecurity Hackathon Edition", True, MID_GREY)
        screen.blit(ver, (cx - ver.get_width() // 2, self.sh - 18))

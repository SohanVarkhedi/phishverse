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


# ── Campaign Select Screen ────────────────────────────────────────────────────

class CampaignSelectScreen:
    """
    Full-screen campaign picker shown between the title screen and gameplay.

    Displays each campaign as an animated card:
        • Name  (large, gold)
        • Department badge  (coloured pill)
        • Description  (word-wrapped)
        • Event count  |  Pass score  |  Duration

    Controls:
        UP / W      — previous campaign
        DOWN / S    — next campaign
        ENTER / E   — confirm and start selected campaign
        F           — free-play (all events, no result saved)
        ESC         — back to title screen

    handle_key() returns:
        None          — no action yet
        Campaign obj  — player confirmed a campaign
        "FREE_PLAY"   — player chose free play
        "BACK"        — player pressed ESC
    """

    # Department badge colours
    DEPT_COLORS = {
        "HR":      (100, 180, 255),
        "Finance": (255, 170,  50),
        "ALL":     ( 80, 210, 130),
    }

    # Card dimensions
    CARD_H   = 148
    CARD_PAD =  18
    CARD_GAP =  16

    def __init__(self, screen_w: int, screen_h: int):
        self.sw = screen_w
        self.sh = screen_h
        self._font  = None
        self._big   = None
        self._small = None
        self._timer = 0
        self._sel   = 0           # currently highlighted card index
        self._campaigns: list = []   # populated by set_campaigns()
        self._slide_in  = 0.0    # 0.0 → 1.0 ease-in animation

    def set_fonts(self, font, big, small):
        self._font  = font
        self._big   = big
        self._small = small

    def set_campaigns(self, campaigns: list):
        """Pass the list of Campaign objects to display."""
        self._campaigns = campaigns
        self._sel = 0

    def update(self):
        self._timer += 1
        self._slide_in = min(1.0, self._slide_in + 0.06)   # ~17 frames to full

    def handle_key(self, key: int):
        """Returns None, a Campaign object, 'FREE_PLAY', or 'BACK'."""
        if not self._campaigns:
            return None
        n = len(self._campaigns)
        if key in (pygame.K_UP, pygame.K_w):
            self._sel = (self._sel - 1) % n
        elif key in (pygame.K_DOWN, pygame.K_s):
            self._sel = (self._sel + 1) % n
        elif key in (pygame.K_RETURN, pygame.K_e):
            return self._campaigns[self._sel]
        elif key == pygame.K_f:
            return "FREE_PLAY"
        elif key == pygame.K_ESCAPE:
            return "BACK"
        return None

    # ── Draw ─────────────────────────────────────────────────────────────────

    def draw(self, screen: pygame.Surface):
        t = self._timer
        sw, sh = self.sw, self.sh

        # ── Animated gradient background ──────────────────────────────────────
        for y in range(sh):
            r = int(8  + 6  * math.sin(t / 70 + y / 90))
            g = int(10 + 8  * math.sin(t / 90 + y / 70))
            b = int(35 + 18 * math.sin(t / 50 + y / 50))
            pygame.draw.line(screen, (r, g, b), (0, y), (sw, y))

        # Scanline overlay
        for y in range(0, sh, 3):
            pygame.draw.line(screen, (0, 0, 0, 30), (0, y), (sw, y))

        # ── Header ───────────────────────────────────────────────────────────
        hdr_h = 72
        hdr = pygame.Surface((sw, hdr_h), pygame.SRCALPHA)
        hdr.fill((10, 10, 30, 220))
        screen.blit(hdr, (0, 0))
        pygame.draw.line(screen, UI_BORDER, (0, hdr_h), (sw, hdr_h), 2)

        pulse = int(2 * math.sin(t / 22))
        title = self._big.render("SELECT TRAINING CAMPAIGN", True, UI_GOLD)
        screen.blit(title, (sw // 2 - title.get_width() // 2, 14 + pulse))

        sub = self._small.render(
            "Choose a scenario set to begin your session", True, (140, 160, 220))
        screen.blit(sub, (sw // 2 - sub.get_width() // 2, 44))

        # ── Campaign cards ────────────────────────────────────────────────────
        n          = len(self._campaigns)
        total_h    = n * self.CARD_H + (n - 1) * self.CARD_GAP
        start_y    = hdr_h + (sh - hdr_h - 80 - total_h) // 2  # vertically centred

        ease = self._ease(self._slide_in)

        for i, camp in enumerate(self._campaigns):
            card_y = start_y + i * (self.CARD_H + self.CARD_GAP)
            # Slide in from left
            offset_x = int((1.0 - ease) * (-sw - i * 60))
            self._draw_card(screen, camp, i, offset_x, card_y, t)

        # ── Bottom controls strip ─────────────────────────────────────────────
        strip_h = 44
        strip_y = sh - strip_h
        strip = pygame.Surface((sw, strip_h), pygame.SRCALPHA)
        strip.fill((0, 0, 0, 160))
        screen.blit(strip, (0, strip_y))
        pygame.draw.line(screen, UI_BORDER, (0, strip_y), (sw, strip_y), 1)

        controls = [
            ("W/S or ↑↓",  "Navigate"),
            ("ENTER / E",   "Start Campaign"),
            ("F",           "Free Play (all events)"),
            ("ESC",         "Back to Title"),
        ]
        gap = sw // (len(controls) + 1)
        for j, (key_lbl, desc) in enumerate(controls):
            kw = self._small.render(key_lbl, True, UI_GOLD)
            dw = self._small.render(f"  {desc}", True, (160, 170, 200))
            cx_pos = (j + 1) * gap
            combined_w = kw.get_width() + dw.get_width()
            screen.blit(kw, (cx_pos - combined_w // 2, strip_y + 8))
            screen.blit(dw, (cx_pos - combined_w // 2 + kw.get_width(), strip_y + 8))

    # ── Card renderer ─────────────────────────────────────────────────────────

    def _draw_card(self, screen, camp, idx, ox, oy, t):
        sw   = self.sw
        is_sel = (idx == self._sel)
        pad  = self.CARD_PAD
        cw   = sw - 80          # card width
        cx   = 40 + ox          # card left edge (with slide offset)

        # ── Shadow ──
        shd = pygame.Surface((cw + 6, self.CARD_H + 6), pygame.SRCALPHA)
        shd.fill((0, 0, 0, 80))
        screen.blit(shd, (cx + 4, oy + 4))

        # ── Background ──
        if is_sel:
            # Animated selection glow background
            glow_a = int(35 + 20 * math.sin(t / 18))
            bg_col = (20, 40, 80, 200 + glow_a)
        else:
            bg_col = (14, 16, 36, 190)
        bg = pygame.Surface((cw, self.CARD_H), pygame.SRCALPHA)
        bg.fill(bg_col)
        screen.blit(bg, (cx, oy))

        # ── Border ──
        border_col = UI_BORDER if is_sel else (40, 50, 80)
        border_w   = 2 if is_sel else 1
        pygame.draw.rect(screen, border_col, (cx, oy, cw, self.CARD_H),
                         border_w, border_radius=8)

        # Selected: outer glow rect
        if is_sel:
            glow_alpha = int(60 + 40 * math.sin(t / 18))
            pygame.draw.rect(screen, (*UI_BORDER, glow_alpha),
                             (cx - 3, oy - 3, cw + 6, self.CARD_H + 6),
                             2, border_radius=10)

        # ── Selection cursor arrow ──
        if is_sel:
            bob = int(3 * math.sin(t / 14))
            arr = self._font.render("▶", True, UI_GOLD)
            screen.blit(arr, (cx - 22, oy + self.CARD_H // 2 - arr.get_height() // 2 + bob))

        # ── Department badge (coloured pill, right side) ──
        dept       = camp.department
        dept_col   = self.DEPT_COLORS.get(dept, (160, 160, 160))
        dept_lbl   = self._small.render(dept, True, (10, 10, 30))
        badge_w    = dept_lbl.get_width() + 16
        badge_h    = dept_lbl.get_height() + 6
        badge_x    = cx + cw - badge_w - pad
        badge_y    = oy + pad - 2
        pygame.draw.rect(screen, dept_col,
                         (badge_x, badge_y, badge_w, badge_h), border_radius=12)
        screen.blit(dept_lbl, (badge_x + 8, badge_y + 3))

        # ── Campaign name ──
        name_col = UI_GOLD if is_sel else WHITE
        name_lbl = self._font.render(camp.name, True, name_col)
        screen.blit(name_lbl, (cx + pad, oy + pad))

        # ── Description (word-wrapped, 2 lines max) ──
        desc_lines = self._wrap(camp.description, (cw - pad * 2) // 7)
        desc_col   = (210, 215, 240) if is_sel else (140, 145, 170)
        for k, line in enumerate(desc_lines[:2]):
            dl = self._small.render(line, True, desc_col)
            screen.blit(dl, (cx + pad, oy + pad + 22 + k * 16))

        # ── Divider ──
        div_y = oy + self.CARD_H - 42
        pygame.draw.line(screen, (*border_col, 80),
                         (cx + pad, div_y), (cx + cw - pad, div_y), 1)

        # ── Stats row ──
        stats = [
            (f"{len(camp.enabled_events)} events",   UI_GOLD),
            (f"Pass: {camp.pass_score}%",             (80, 210, 130) if is_sel else (120, 180, 130)),
            (f"{camp.duration_days}-day programme",   (160, 170, 200)),
        ]
        stat_x = cx + pad
        for text, col in stats:
            sv = self._small.render(text, True, col)
            screen.blit(sv, (stat_x, div_y + 10))
            stat_x += sv.get_width() + 24
            # Dot separator
            if stat_x < cx + cw - 60:
                dot = self._small.render("·", True, (60, 70, 100))
                screen.blit(dot, (stat_x - 16, div_y + 10))

    # ── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _ease(t: float) -> float:
        """Cubic ease-out: fast start, smooth landing."""
        t = max(0.0, min(1.0, t))
        return 1.0 - (1.0 - t) ** 3

    @staticmethod
    def _wrap(text: str, max_chars: int) -> list[str]:
        if not text:
            return []
        words  = text.split()
        lines, cur = [], ""
        for w in words:
            if len(cur) + len(w) + 1 <= max_chars:
                cur = (cur + " " + w).strip()
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines


# ── Employee Registration Screen ───────────────────────────────────────────────

class RegistrationScreen:
    """
    Pre-game employee registration form.

    Fields (TAB / UP / DOWN to navigate):
        0  Employee Name   — text, required
        1  Employee ID     — text, required
        2  Department      — select: HR / Finance / IT / General  (LEFT/RIGHT)
        3  Role (optional) — text
        4  CONFIRM button

    handle_key(key, unicode_char) returns:
        None     — no action
        dict     — employee data on confirm
        "BACK"   — ESC pressed
    """

    DEPARTMENTS = ["HR", "Finance", "IT", "General"]
    MAX_LEN     = 32
    DEPT_COLORS = {
        "HR":      (100, 180, 255),
        "Finance": (255, 170,  50),
        "IT":      (160, 110, 230),
        "General": ( 80, 210, 130),
    }

    def __init__(self, screen_w: int, screen_h: int):
        self.sw = screen_w
        self.sh = screen_h
        self._font  = None
        self._big   = None
        self._small = None
        self._timer    = 0
        self._blink    = 0
        self._active   = 0          # 0=name,1=emp_id,2=dept,3=role,4=confirm
        self._dept_i   = 3          # default "General"
        self._dept_open = False     # dropdown open/closed state
        self._dept_box_pos = None   # (fx, fy, fw, fh) — set each draw frame
        self._error  = ""
        self._vals   = {"name": "", "emp_id": "", "role": ""}

    def set_fonts(self, font, big, small):
        self._font = font; self._big = big; self._small = small

    def reset(self):
        self._vals      = {"name": "", "emp_id": "", "role": ""}
        self._dept_i    = 3
        self._dept_open = False
        self._active    = 0
        self._error     = ""

    # ── Input ─────────────────────────────────────────────────────────────────

    def handle_key(self, key: int, unicode_char: str = ""):
        # When dropdown is open absorb all navigation — don't let it bleed out
        if self._dept_open:
            n = len(self.DEPARTMENTS)
            if key in (pygame.K_UP, pygame.K_w):
                self._dept_i = (self._dept_i - 1) % n
            elif key in (pygame.K_DOWN, pygame.K_s):
                self._dept_i = (self._dept_i + 1) % n
            elif key in (pygame.K_RETURN, pygame.K_e):
                self._dept_open = False
            elif key == pygame.K_ESCAPE:
                self._dept_open = False
            return None

        if key == pygame.K_ESCAPE:
            return "BACK"
        if key in (pygame.K_TAB, pygame.K_DOWN):
            self._active = (self._active + 1) % 5
            self._error  = ""
            return None
        if key == pygame.K_UP:
            self._active = (self._active - 1) % 5
            self._error  = ""
            return None
        if key == pygame.K_RETURN:
            if self._active == 2:
                self._dept_open = True
                return None
            elif self._active < 4:
                self._active = min(self._active + 1, 4)
            else:
                return self._try_confirm()
            return None

        if   self._active == 0: self._text_input("name",   key, unicode_char)
        elif self._active == 1: self._text_input("emp_id", key, unicode_char)
        elif self._active == 3: self._text_input("role",   key, unicode_char)
        return None

    def _text_input(self, field: str, key: int, uc: str):
        if key == pygame.K_BACKSPACE:
            self._vals[field] = self._vals[field][:-1]
        elif uc and uc.isprintable() and len(self._vals[field]) < self.MAX_LEN:
            self._vals[field] += uc

    def _try_confirm(self):
        if not self._vals["name"].strip():
            self._error = "Employee Name is required."; self._active = 0; return None
        if not self._vals["emp_id"].strip():
            self._error = "Employee ID is required.";   self._active = 1; return None
        self._error = ""
        return {
            "employee_name": self._vals["name"].strip(),
            "employee_id":   self._vals["emp_id"].strip(),
            "department":    self.DEPARTMENTS[self._dept_i],
            "role":          self._vals["role"].strip(),
        }

    # ── Tick ──────────────────────────────────────────────────────────────────

    def update(self):
        self._timer += 1
        self._blink  = (self._timer // 25) % 2   # cursor blinks every 25 frames

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, screen: pygame.Surface):
        t      = self._timer
        sw, sh = self.sw, self.sh

        # Animated background
        for y in range(sh):
            r = int(10 + 5  * math.sin(t / 80  + y / 110))
            g = int(12 + 6  * math.sin(t / 100 + y / 90))
            b = int(42 + 22 * math.sin(t / 60  + y / 60))
            pygame.draw.line(screen, (r, g, b), (0, y), (sw, y))

        # Header
        hdr_h = 84
        hdr   = pygame.Surface((sw, hdr_h), pygame.SRCALPHA)
        hdr.fill((8, 10, 28, 230))
        screen.blit(hdr, (0, 0))
        pygame.draw.line(screen, UI_BORDER, (0, hdr_h), (sw, hdr_h), 2)

        pulse = int(2 * math.sin(t / 20))
        title = self._big.render("PHISHVERSE  EMPLOYEE  REGISTRATION", True, UI_GOLD)
        screen.blit(title, (sw // 2 - title.get_width() // 2, 14 + pulse))
        sub = self._small.render(
            "Identify yourself before beginning your training session",
            True, (130, 150, 210))
        screen.blit(sub, (sw // 2 - sub.get_width() // 2, 52))

        # Form layout
        fw      = 600
        fx      = sw // 2 - fw // 2
        label_h = 18
        field_h = 46
        gap     = 16
        unit_h  = label_h + 4 + field_h + gap
        fy      = hdr_h + 22

        field_defs = [
            ("Employee Name",    "name",   "text"),
            ("Employee ID",      "emp_id", "text"),
            ("Department",       "",       "select"),
            ("Role  (optional)", "role",   "text"),
        ]

        for i, (label, fkey, ftype) in enumerate(field_defs):
            is_active = (self._active == i)
            lc = UI_GOLD if is_active else (140, 150, 190)
            screen.blit(self._small.render(label, True, lc), (fx, fy))
            fy += label_h + 4

            if ftype == "text":
                bc  = UI_BORDER if is_active else (40, 55, 90)
                box = pygame.Surface((fw, field_h), pygame.SRCALPHA)
                box.fill((18, 22, 50, 215) if is_active else (10, 12, 32, 180))
                screen.blit(box, (fx, fy))
                pygame.draw.rect(screen, bc, (fx, fy, fw, field_h), 2, border_radius=6)
                val    = self._vals.get(fkey, "")
                cursor = "|" if (is_active and self._blink == 0) else ""
                ts     = self._font.render(val + cursor, True,
                                           WHITE if is_active else LIGHT_GREY)
                screen.blit(ts, (fx + 14, fy + (field_h - ts.get_height()) // 2))

            elif ftype == "select":
                self._draw_dept(screen, fx, fy, fw, field_h, is_active, t)
                self._dept_box_pos = (fx, fy, fw, field_h)

            fy += field_h + gap

        # Confirm button
        fy += 8
        btn_is_active = (self._active == 4)
        btn_w, btn_h  = 300, 52
        btn_x         = sw // 2 - btn_w // 2
        form_ok       = bool(self._vals["name"].strip() and self._vals["emp_id"].strip())

        if btn_is_active:
            ga = int(80 + 40 * math.sin(t / 15))
            pygame.draw.rect(screen, (*UI_GOLD, ga),
                             (btn_x - 5, fy - 5, btn_w + 10, btn_h + 10),
                             3, border_radius=14)

        btn_bg = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        btn_bg.fill((35, 45, 12, 220) if form_ok else (20, 22, 40, 200))
        screen.blit(btn_bg, (btn_x, fy))
        pygame.draw.rect(screen, UI_GOLD if form_ok else (55, 65, 90),
                         (btn_x, fy, btn_w, btn_h), 2, border_radius=8)
        bl = self._font.render("CONFIRM  &  BEGIN", True,
                               UI_GOLD if form_ok else (90, 100, 130))
        screen.blit(bl, (btn_x + btn_w // 2 - bl.get_width() // 2,
                         fy + btn_h // 2 - bl.get_height() // 2))

        # Error message
        if self._error:
            el = self._small.render(self._error, True, UI_WARNING)
            screen.blit(el, (sw // 2 - el.get_width() // 2, fy + btn_h + 14))

        # Controls strip
        strip_h = 36
        strip_y = sh - strip_h
        strip   = pygame.Surface((sw, strip_h), pygame.SRCALPHA)
        strip.fill((0, 0, 0, 150))
        screen.blit(strip, (0, strip_y))
        pygame.draw.line(screen, UI_BORDER, (0, strip_y), (sw, strip_y), 1)

        # Dropdown overlay — drawn last so it sits above all other fields
        if self._dept_open and self._dept_box_pos:
            self._draw_dept_dropdown(screen, *self._dept_box_pos)

        hints = [
            ("TAB / ↓",  "Next field"),  ("↑",        "Prev field"),
            ("Type",     "Enter text"),  ("ENTER",     "Open dept list"),
            ("↑↓ in list", "Navigate"),  ("ESC",       "Back / close"),
        ]
        gw = sw // (len(hints) + 1)
        for j, (k, d) in enumerate(hints):
            kl = self._small.render(k, True, UI_GOLD)
            dl = self._small.render(f"  {d}", True, (140, 150, 180))
            cx = (j + 1) * gw
            tw = kl.get_width() + dl.get_width()
            screen.blit(kl, (cx - tw // 2, strip_y + 10))
            screen.blit(dl, (cx - tw // 2 + kl.get_width(), strip_y + 10))

    # ── Department dropdown ────────────────────────────────────────────────────

    def _draw_dept(self, screen, fx, fy, fw, fh, is_active, t):
        """Closed dropdown — shows selected value + ▼ arrow."""
        bc  = UI_BORDER if is_active else (40, 55, 90)
        box = pygame.Surface((fw, fh), pygame.SRCALPHA)
        box.fill((18, 22, 50, 215) if is_active else (10, 12, 32, 180))
        screen.blit(box, (fx, fy))
        pygame.draw.rect(screen, bc, (fx, fy, fw, fh), 2, border_radius=6)

        dept     = self.DEPARTMENTS[self._dept_i]
        dept_col = self.DEPT_COLORS.get(dept, WHITE)

        # Coloured dot
        pygame.draw.circle(screen, dept_col,
                           (fx + 22, fy + fh // 2), 7)

        # Selected department name
        dl = self._font.render(dept, True, dept_col if is_active else LIGHT_GREY)
        screen.blit(dl, (fx + 38, fy + (fh - dl.get_height()) // 2))

        # ▼ arrow (right side)
        arrow_col = UI_GOLD if is_active else (80, 90, 120)
        arr = self._font.render("▼", True, arrow_col)
        screen.blit(arr, (fx + fw - arr.get_width() - 16,
                          fy + (fh - arr.get_height()) // 2))

    def _draw_dept_dropdown(self, screen, fx, fy, fw, fh):
        """Open dropdown overlay — drawn on top of subsequent form fields."""
        item_h = 44
        n      = len(self.DEPARTMENTS)
        panel_h = n * item_h + 6

        drop_y = fy + fh + 2
        panel  = pygame.Surface((fw, panel_h), pygame.SRCALPHA)
        panel.fill((16, 18, 46, 248))
        screen.blit(panel, (fx, drop_y))
        pygame.draw.rect(screen, UI_BORDER, (fx, drop_y, fw, panel_h), 2, border_radius=8)

        for i, dept in enumerate(self.DEPARTMENTS):
            item_y   = drop_y + 3 + i * item_h
            is_sel   = (i == self._dept_i)
            dept_col = self.DEPT_COLORS.get(dept, LIGHT_GREY)

            if is_sel:
                sel_bg = pygame.Surface((fw - 6, item_h - 2), pygame.SRCALPHA)
                sel_bg.fill((*CHOICE_HL, 200))
                screen.blit(sel_bg, (fx + 3, item_y))

            # Coloured dot
            pygame.draw.circle(screen, dept_col,
                               (fx + 24, item_y + item_h // 2), 8)

            # Department name
            lbl = self._font.render(dept, True, dept_col if is_sel else LIGHT_GREY)
            screen.blit(lbl, (fx + 44, item_y + (item_h - lbl.get_height()) // 2))

            # ◀ selection indicator
            if is_sel:
                ind = self._small.render("◀  selected", True, UI_GOLD)
                screen.blit(ind, (fx + fw - ind.get_width() - 14,
                                  item_y + (item_h - ind.get_height()) // 2))


# ── Analytics Dashboard Screen ────────────────────────────────────────────────

class DashboardScreen:
    """
    Post-report analytics dashboard.
    Reads all results from analytics/results/*.json and displays aggregate stats.

    handle_key() returns True to quit the application.
    """

    DEPT_COLORS = {
        "HR":      (100, 180, 255),
        "Finance": (255, 170,  50),
        "IT":      (160, 110, 230),
        "General": ( 80, 210, 130),
    }
    BIAS_COLORS = {
        "Urgency":   (230,  80,  80),
        "Authority": (200, 120,  50),
        "Reward":    ( 60, 160, 220),
        "Fear":      (180,  60, 200),
    }

    def __init__(self, screen_w: int, screen_h: int):
        self.sw = screen_w
        self.sh = screen_h
        self._font  = None
        self._big   = None
        self._small = None
        self._timer   = 0
        self._stats: dict = {}
        self._results: list = []

    def set_fonts(self, font, big, small):
        self._font  = font
        self._big   = big
        self._small = small

    def load_data(self):
        from analytics.result_store import ResultStore
        self._results = ResultStore.load_all()
        self._stats   = self._aggregate(self._results)
        self._timer   = 0

    def _aggregate(self, results: list) -> dict:
        if not results:
            return {}
        n = len(results)

        avg_score  = sum(r.get("score", 0) for r in results) / n
        pass_count = sum(1 for r in results if r.get("passed", False))

        # Per-department
        dept_map: dict = {}
        for r in results:
            d = r.get("department", "General")
            dept_map.setdefault(d, []).append(r.get("score", 0))
        dept_stats = {
            d: {"count": len(sc), "avg": round(sum(sc) / len(sc), 1)}
            for d, sc in dept_map.items()
        }

        # Per-campaign
        camp_map: dict = {}
        for r in results:
            c = r.get("campaign", "Unknown")
            camp_map.setdefault(c, {"scores": [], "passed": 0})
            camp_map[c]["scores"].append(r.get("score", 0))
            if r.get("passed", False):
                camp_map[c]["passed"] += 1
        camp_stats = {
            c: {
                "count":    len(d["scores"]),
                "avg":      round(sum(d["scores"]) / len(d["scores"]), 1),
                "pass_pct": round(d["passed"] / len(d["scores"]) * 100),
            }
            for c, d in camp_map.items()
        }

        # Behaviour biases
        avg_u = sum(r.get("urgency",   0) for r in results) / n
        avg_a = sum(r.get("authority", 0) for r in results) / n
        avg_r = sum(r.get("reward",    0) for r in results) / n
        avg_f = sum(r.get("fear",      0) for r in results) / n
        biases = {
            "Urgency":   round(avg_u, 1),
            "Authority": round(avg_a, 1),
            "Reward":    round(avg_r, 1),
            "Fear":      round(avg_f, 1),
        }

        most_vulnerable = min(dept_stats, key=lambda d: dept_stats[d]["avg"]) if dept_stats else "N/A"
        most_failed     = max(biases, key=biases.get)

        return {
            "total":           n,
            "avg_score":       round(avg_score, 1),
            "pass_rate":       round(pass_count / n * 100, 1),
            "dept_stats":      dept_stats,
            "camp_stats":      camp_stats,
            "biases":          biases,
            "most_vulnerable": most_vulnerable,
            "most_failed":     most_failed,
        }

    def handle_key(self, key: int) -> bool:
        """Returns True to quit the game."""
        return key in (pygame.K_ESCAPE, pygame.K_q, pygame.K_RETURN)

    def update(self):
        self._timer += 1

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, screen: pygame.Surface):
        t      = self._timer
        sw, sh = self.sw, self.sh
        s      = self._stats

        # Animated background
        for y in range(sh):
            b = int(22 + 12 * math.sin(t / 90 + y / 120))
            pygame.draw.line(screen, (8, b // 3, b), (0, y), (sw, y))

        # Header
        hdr_h = 72
        hdr = pygame.Surface((sw, hdr_h), pygame.SRCALPHA)
        hdr.fill((10, 14, 40, 235))
        screen.blit(hdr, (0, 0))
        pygame.draw.line(screen, UI_BORDER, (0, hdr_h), (sw, hdr_h), 2)

        pulse = int(2 * math.sin(t / 20))
        title = self._big.render("ANALYTICS  DASHBOARD", True, UI_GOLD)
        screen.blit(title, (sw // 2 - title.get_width() // 2, 12 + pulse))
        sub = self._small.render(
            "Aggregate results  ·  analytics/results/", True, (130, 150, 210))
        screen.blit(sub, (sw // 2 - sub.get_width() // 2, 46))

        # No-data fallback
        if not s:
            msg = self._font.render(
                "No results found — complete a campaign to generate data.",
                True, UI_WARNING)
            screen.blit(msg, (sw // 2 - msg.get_width() // 2, sh // 2 - 16))
            self._dismiss_hint(screen, t)
            return

        # ── Column layout ─────────────────────────────────────────────────────
        col_top   = hdr_h + 20
        C1X, C1W  = 24,  240
        C2X, C2W  = 284, 356
        C3X, C3W  = 660, 276

        # ── Col 1: Overview + Campaign stats ──────────────────────────────────
        y = col_top
        y = self._section(screen, C1X, y, C1W, "OVERVIEW")
        y = self._row(screen, C1X, y, C1W, "Employees",  str(s["total"]))
        y = self._row(screen, C1X, y, C1W, "Avg Score",  f"{s['avg_score']} / 100")
        y = self._row(screen, C1X, y, C1W, "Pass Rate",  f"{s['pass_rate']}%")

        y += 14
        y = self._section(screen, C1X, y, C1W, "CAMPAIGNS")
        for name, cd in list(s["camp_stats"].items())[:5]:
            y = self._row(screen, C1X, y, C1W,
                          name[:20], f"{cd['count']} · {cd['pass_pct']:.0f}% pass")

        # ── Col 2: Department risk bars ────────────────────────────────────────
        y = col_top
        y = self._section(screen, C2X, y, C2W, "DEPARTMENT RISK")
        bar_w = C2W - 90
        for dept, dd in sorted(s["dept_stats"].items(), key=lambda x: -x[1]["avg"]):
            avg      = dd["avg"]
            risk_col = (80, 220, 120) if avg >= 80 else ((255, 190, 50) if avg >= 55 else (230, 70, 70))
            dept_col = self.DEPT_COLORS.get(dept, LIGHT_GREY)

            dl = self._small.render(dept, True, dept_col)
            screen.blit(dl, (C2X, y))

            by = y + 16
            fill  = int(bar_w * avg / 100)
            anim  = min(fill, int(bar_w * min(t / 80, 1.0)))
            pygame.draw.rect(screen, (28, 30, 52), (C2X, by, bar_w, 14), border_radius=7)
            if anim > 0:
                pygame.draw.rect(screen, risk_col, (C2X, by, anim, 14), border_radius=7)
            pygame.draw.rect(screen, (50, 60, 90), (C2X, by, bar_w, 14), 1, border_radius=7)

            info = self._small.render(f"{avg}  ({dd['count']})", True, risk_col)
            screen.blit(info, (C2X + bar_w + 6, by - 1))
            y += 48

        # ── Col 3: Behaviour bias bars ─────────────────────────────────────────
        y = col_top
        y = self._section(screen, C3X, y, C3W, "BEHAVIOUR METRICS")
        bbar_w = C3W - 56
        for bias_name, avg_val in s["biases"].items():
            col = self.BIAS_COLORS.get(bias_name, LIGHT_GREY)
            bl = self._small.render(bias_name, True, col)
            screen.blit(bl, (C3X, y))

            by = y + 16
            fill  = int(bbar_w * min(avg_val / 30.0, 1.0))
            anim  = min(fill, int(bbar_w * min(t / 80, 1.0)))
            pygame.draw.rect(screen, (28, 30, 52), (C3X, by, bbar_w, 14), border_radius=7)
            if anim > 0:
                pygame.draw.rect(screen, col, (C3X, by, anim, 14), border_radius=7)
            pygame.draw.rect(screen, (50, 60, 90), (C3X, by, bbar_w, 14), 1, border_radius=7)

            vl = self._small.render(str(avg_val), True, col)
            screen.blit(vl, (C3X + bbar_w + 6, by - 1))
            y += 48

        # ── Bottom insight strip ───────────────────────────────────────────────
        strip_y = sh - 110
        pygame.draw.line(screen, UI_BORDER, (20, strip_y), (sw - 20, strip_y), 1)

        vuln_dept = s["most_vulnerable"]
        vuln_avg  = s["dept_stats"].get(vuln_dept, {}).get("avg", 0)
        most_fail = s["most_failed"]

        # Most vulnerable dept card
        bx, by, bw, bh = 20, strip_y + 10, 440, 68
        bg1 = pygame.Surface((bw, bh), pygame.SRCALPHA)
        bg1.fill((40, 12, 12, 210))
        screen.blit(bg1, (bx, by))
        pygame.draw.rect(screen, UI_WARNING, (bx, by, bw, bh), 2, border_radius=8)
        screen.blit(self._small.render("MOST VULNERABLE DEPARTMENT", True, UI_WARNING),
                    (bx + 12, by + 8))
        dept_col = self.DEPT_COLORS.get(vuln_dept, WHITE)
        screen.blit(self._font.render(f"{vuln_dept}  —  avg score: {vuln_avg}", True, dept_col),
                    (bx + 12, by + 30))

        # Most exploited attack card
        bx2, bw2 = 480, 460
        bg2 = pygame.Surface((bw2, bh), pygame.SRCALPHA)
        bg2.fill((12, 12, 40, 210))
        screen.blit(bg2, (bx2, by))
        pygame.draw.rect(screen, UI_BORDER, (bx2, by, bw2, bh), 2, border_radius=8)
        screen.blit(self._small.render("MOST EXPLOITED ATTACK TYPE", True, UI_BORDER),
                    (bx2 + 12, by + 8))
        fail_col = self.BIAS_COLORS.get(most_fail, WHITE)
        screen.blit(self._font.render(f"{most_fail} Manipulation", True, fail_col),
                    (bx2 + 12, by + 30))

        self._dismiss_hint(screen, t)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _section(self, screen, x, y, w, text) -> int:
        lbl = self._small.render(text, True, UI_GOLD)
        screen.blit(lbl, (x, y))
        pygame.draw.line(screen, (*UI_BORDER, 70), (x, y + 16), (x + w, y + 16), 1)
        return y + 26

    def _row(self, screen, x, y, w, label, value) -> int:
        pygame.draw.rect(screen, (18, 20, 44), (x, y, w, 26), border_radius=4)
        ll = self._small.render(label, True, LIGHT_GREY)
        vl = self._small.render(value, True, UI_HIGHLIGHT)
        screen.blit(ll, (x + 8,  y + 5))
        screen.blit(vl, (x + w - vl.get_width() - 8, y + 5))
        return y + 32

    def _dismiss_hint(self, screen, t):
        if (t // 30) % 2 == 0:
            hint = self._small.render("Press ENTER or ESC to quit", True, MID_GREY)
            screen.blit(hint, (self.sw // 2 - hint.get_width() // 2, self.sh - 18))


# ── Lecture Screen ─────────────────────────────────────────────────────────────

class LectureScreen:
    """
    Post-exam training module screen.

    List mode   — shows all assigned lecture cards with completion status.
    Detail mode — shows scrollable content for the selected lecture.

    handle_key() returns 'CONTINUE' when all lectures are done and player continues.
    """

    BIAS_COLORS = {
        "urgency":   (230,  80,  80),
        "authority": (200, 120,  50),
        "reward":    ( 60, 160, 220),
        "fear":      (180,  60, 200),
    }
    # Pixel offsets for content scroll
    _LINE_H = {"heading": 26, "bullet": 20, "gap": 10}

    def __init__(self, screen_w: int, screen_h: int):
        self.sw = screen_w
        self.sh = screen_h
        self._font  = None
        self._big   = None
        self._small = None
        self._timer         = 0
        self._mode          = "list"    # "list" | "detail"
        self._sel           = 0
        self._scroll        = 0         # pixel scroll offset in detail mode
        self._employee_id   = ""
        self._training: dict = {}
        self._lectures: list = []
        self._content_lines: list = []  # list of (type, text)

    def set_fonts(self, font, big, small):
        self._font  = font
        self._big   = big
        self._small = small

    def set_employee(self, employee_id: str):
        """Load training record and lecture content for this employee."""
        from training.lecture_engine import LectureEngine
        self._employee_id = employee_id
        self._training    = LectureEngine.load_training(employee_id) or {}

        if self._training:
            assigned = self._training.get("assigned_lectures", [])
            self._lectures = LectureEngine.load_lectures(assigned)
        else:
            # Free play / no record — load all lectures for browsing
            from training.lecture_engine import LectureEngine, LECTURES_FILE
            import json
            if LECTURES_FILE.exists():
                with open(LECTURES_FILE, "r", encoding="utf-8") as f:
                    self._lectures = json.load(f).get("lectures", [])

        self._sel    = 0
        self._mode   = "list"
        self._scroll = 0
        self._content_lines = []
        self._timer  = 0

    # ── Queries ───────────────────────────────────────────────────────────────

    def _is_complete(self, idx: int) -> bool:
        if idx >= len(self._lectures):
            return False
        lec_id = self._lectures[idx]["lecture_id"]
        return lec_id in self._training.get("completed_lectures", [])

    def _all_done(self) -> bool:
        if not self._lectures:
            return True
        return all(self._is_complete(i) for i in range(len(self._lectures)))

    # ── Content builder ───────────────────────────────────────────────────────

    def _build_content(self, idx: int):
        lec = self._lectures[idx]
        lines = []
        for sec in lec.get("sections", []):
            lines.append(("heading", sec["heading"]))
            for pt in sec.get("points", []):
                lines.append(("bullet", pt))
            lines.append(("gap", ""))
        self._content_lines = lines

    def _content_total_h(self) -> int:
        return sum(self._LINE_H.get(lt, 20) for lt, _ in self._content_lines)

    def _visible_h(self) -> int:
        return self.sh - 72 - 14 - 80   # header + padding + footer

    def _max_scroll(self) -> int:
        return max(0, self._content_total_h() - self._visible_h())

    # ── Input ─────────────────────────────────────────────────────────────────

    def handle_key(self, key: int) -> str | None:
        if self._mode == "detail":
            if key in (pygame.K_UP, pygame.K_w):
                self._scroll = max(0, self._scroll - 22)
            elif key in (pygame.K_DOWN, pygame.K_s):
                self._scroll = min(self._max_scroll(), self._scroll + 22)
            elif key in (pygame.K_m, pygame.K_RETURN, pygame.K_e):
                if self._employee_id and not self._is_complete(self._sel):
                    from training.lecture_engine import LectureEngine
                    lec_id = self._lectures[self._sel]["lecture_id"]
                    self._training = LectureEngine.mark_complete(
                        self._employee_id, lec_id)
                self._mode   = "list"
                self._scroll = 0
            elif key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self._mode   = "list"
                self._scroll = 0
            return None

        # List mode
        n     = len(self._lectures)
        extra = 1 if self._all_done() else 0
        total = n + extra

        if total == 0:
            if key in (pygame.K_RETURN, pygame.K_e):
                return "CONTINUE"
            return None

        if key in (pygame.K_UP, pygame.K_w):
            self._sel = (self._sel - 1) % total
        elif key in (pygame.K_DOWN, pygame.K_s):
            self._sel = (self._sel + 1) % total
        elif key in (pygame.K_RETURN, pygame.K_e):
            if self._sel < n:
                self._mode   = "detail"
                self._scroll = 0
                self._build_content(self._sel)
            elif self._sel == n:
                return "CONTINUE"
        return None

    # ── Tick ──────────────────────────────────────────────────────────────────

    def update(self):
        self._timer += 1

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, screen: pygame.Surface):
        if self._mode == "detail":
            self._draw_detail(screen)
        else:
            self._draw_list(screen)

    def _draw_list(self, screen: pygame.Surface):
        t      = self._timer
        sw, sh = self.sw, self.sh

        # Background
        for y in range(sh):
            b = int(22 + 10 * math.sin(t / 90 + y / 100))
            pygame.draw.line(screen, (8, b // 3, b), (0, y), (sw, y))

        # Header
        hdr_h = 72
        hdr = pygame.Surface((sw, hdr_h), pygame.SRCALPHA)
        hdr.fill((10, 14, 40, 235))
        screen.blit(hdr, (0, 0))
        pygame.draw.line(screen, UI_BORDER, (0, hdr_h), (sw, hdr_h), 2)

        pulse = int(2 * math.sin(t / 20))
        title = self._big.render("TRAINING MODULES", True, UI_GOLD)
        screen.blit(title, (sw // 2 - title.get_width() // 2, 12 + pulse))

        done_n = sum(1 for i in range(len(self._lectures)) if self._is_complete(i))
        pc = UI_HIGHLIGHT if self._all_done() else LIGHT_GREY
        prog = self._small.render(f"{done_n} / {len(self._lectures)} completed", True, pc)
        screen.blit(prog, (sw - prog.get_width() - 20, 50))

        # No lectures fallback
        if not self._lectures:
            msg = self._font.render("No training modules assigned for this session.", True, LIGHT_GREY)
            screen.blit(msg, (sw // 2 - msg.get_width() // 2, sh // 2 - 30))
            bl = self._font.render("▶  CONTINUE TO DASHBOARD", True, UI_GOLD)
            screen.blit(bl, (sw // 2 - bl.get_width() // 2, sh // 2 + 20))
            hint = self._small.render("ENTER  Continue", True, MID_GREY)
            screen.blit(hint, (sw // 2 - hint.get_width() // 2, sh - 20))
            return

        # Lecture cards
        cw      = sw - 80
        cx      = 40
        ch      = 88
        gap     = 10
        start_y = hdr_h + 18

        for i, lec in enumerate(self._lectures):
            card_y = start_y + i * (ch + gap)
            self._draw_card(screen, lec, i, cx, card_y, cw, ch, t)

        # CONTINUE button — only when all done
        btn_y = start_y + len(self._lectures) * (ch + gap) + 10
        if self._all_done():
            is_sel = (self._sel == len(self._lectures))
            bw, bh = 380, 50
            bx = sw // 2 - bw // 2
            if is_sel:
                ga = int(80 + 40 * math.sin(t / 15))
                pygame.draw.rect(screen, (*UI_GOLD, ga),
                                 (bx - 5, btn_y - 5, bw + 10, bh + 10), 3, border_radius=12)
            bg = pygame.Surface((bw, bh), pygame.SRCALPHA)
            bg.fill((30, 50, 14, 225) if is_sel else (18, 24, 40, 200))
            screen.blit(bg, (bx, btn_y))
            bc = UI_HIGHLIGHT if is_sel else (55, 80, 55)
            pygame.draw.rect(screen, bc, (bx, btn_y, bw, bh), 2, border_radius=8)
            lbl_col = UI_HIGHLIGHT if is_sel else (80, 120, 80)
            lbl = self._font.render("▶  CONTINUE TO DASHBOARD", True, lbl_col)
            screen.blit(lbl, (bx + bw // 2 - lbl.get_width() // 2,
                               btn_y + bh // 2 - lbl.get_height() // 2))

        # Controls strip
        strip_h, strip_y = 34, sh - 34
        strip = pygame.Surface((sw, strip_h), pygame.SRCALPHA)
        strip.fill((0, 0, 0, 155))
        screen.blit(strip, (0, strip_y))
        pygame.draw.line(screen, UI_BORDER, (0, strip_y), (sw, strip_y), 1)
        hints = [
            ("↑↓ / W S",  "Navigate"),
            ("ENTER",      "Read lecture"),
            ("M (in lecture)", "Mark complete"),
            ("All done",   "ENTER on Continue"),
        ]
        gw = sw // (len(hints) + 1)
        for j, (k, d) in enumerate(hints):
            kl = self._small.render(k, True, UI_GOLD)
            dl = self._small.render(f"  {d}", True, (140, 150, 180))
            cx_pos = (j + 1) * gw
            tw = kl.get_width() + dl.get_width()
            screen.blit(kl, (cx_pos - tw // 2, strip_y + 10))
            screen.blit(dl, (cx_pos - tw // 2 + kl.get_width(), strip_y + 10))

    def _draw_card(self, screen, lec, idx, cx, cy, cw, ch, t):
        is_sel    = (self._sel == idx)
        completed = self._is_complete(idx)
        bias      = lec.get("bias_target", "urgency")
        col       = self.BIAS_COLORS.get(bias, LIGHT_GREY)

        # Shadow
        shd = pygame.Surface((cw + 4, ch + 4), pygame.SRCALPHA)
        shd.fill((0, 0, 0, 60))
        screen.blit(shd, (cx + 3, cy + 3))

        # Background + border
        bg = pygame.Surface((cw, ch), pygame.SRCALPHA)
        bg.fill((20, 40, 80, 200) if is_sel else (14, 16, 36, 190))
        screen.blit(bg, (cx, cy))
        pygame.draw.rect(screen, UI_BORDER if is_sel else (40, 50, 80),
                         (cx, cy, cw, ch), 2 if is_sel else 1, border_radius=8)

        # Selection arrow
        if is_sel:
            bob = int(3 * math.sin(t / 14))
            arr = self._font.render("▶", True, UI_GOLD)
            screen.blit(arr, (cx - 22,
                               cy + ch // 2 - arr.get_height() // 2 + bob))

        # Status circle (left)
        sx = cx + 20
        sy = cy + ch // 2
        if completed:
            pygame.draw.circle(screen, UI_HIGHLIGHT, (sx, sy), 11)
            ck = self._small.render("✓", True, (8, 20, 8))
            screen.blit(ck, (sx - ck.get_width() // 2, sy - ck.get_height() // 2))
        else:
            pygame.draw.circle(screen, (50, 60, 90), (sx, sy), 11, 2)

        # Title, topic, section count
        title_col = UI_GOLD if is_sel else WHITE
        screen.blit(self._font.render(lec.get("title", ""), True, title_col),
                    (cx + 44, cy + 12))
        screen.blit(self._small.render(lec.get("topic", ""), True,
                                       (180, 190, 225) if is_sel else (110, 120, 155)),
                    (cx + 44, cy + 34))
        sc = len(lec.get("sections", []))
        screen.blit(self._small.render(f"{sc} sections  ·  ENTER to read",
                                       True, (70, 80, 110)),
                    (cx + 44, cy + 54))

        # Bias tag
        bl = self._small.render(bias.upper(), True, (10, 10, 20))
        tw = bl.get_width() + 14
        th = bl.get_height() + 6
        tx = cx + cw - tw - 14
        ty = cy + 10
        pygame.draw.rect(screen, col, (tx, ty, tw, th), border_radius=10)
        screen.blit(bl, (tx + 7, ty + 3))

        # Status label
        st = "COMPLETE" if completed else "PENDING"
        sc_col = UI_HIGHLIGHT if completed else UI_WARNING
        sl = self._small.render(st, True, sc_col)
        screen.blit(sl, (cx + cw - sl.get_width() - 14, cy + ch - sl.get_height() - 10))

    def _draw_detail(self, screen: pygame.Surface):
        t      = self._timer
        sw, sh = self.sw, self.sh
        lec       = self._lectures[self._sel]
        bias      = lec.get("bias_target", "urgency")
        col       = self.BIAS_COLORS.get(bias, LIGHT_GREY)
        completed = self._is_complete(self._sel)

        # Background
        for y in range(sh):
            b = int(22 + 8 * math.sin(t / 90 + y / 100))
            pygame.draw.line(screen, (8, b // 3, b), (0, y), (sw, y))

        # Header
        hdr_h = 72
        hdr = pygame.Surface((sw, hdr_h), pygame.SRCALPHA)
        hdr.fill((10, 14, 40, 235))
        screen.blit(hdr, (0, 0))
        pygame.draw.line(screen, UI_BORDER, (0, hdr_h), (sw, hdr_h), 2)

        title = self._big.render(lec.get("title", ""), True, UI_GOLD)
        screen.blit(title, (sw // 2 - title.get_width() // 2, 10))
        tag = self._small.render(
            f"BIAS: {bias.upper()}  ·  {lec.get('topic', '')}", True, col)
        screen.blit(tag, (sw // 2 - tag.get_width() // 2, 46))

        # Scrollable content
        content_x = 52
        content_y = hdr_h + 14
        vis_h     = self._visible_h()
        clip_rect = pygame.Rect(0, content_y, sw, vis_h)
        screen.set_clip(clip_rect)

        y = content_y - self._scroll
        for lt, text in self._content_lines:
            if y > content_y + vis_h:
                break
            lh = self._LINE_H.get(lt, 20)
            if y + lh > content_y:
                if lt == "heading":
                    hl = self._font.render(text, True, col)
                    screen.blit(hl, (content_x, y))
                elif lt == "bullet":
                    bl = self._small.render(f"  •  {text}", True, LIGHT_GREY)
                    screen.blit(bl, (content_x + 10, y))
            y += lh

        screen.set_clip(None)

        # Scroll indicators
        if self._scroll > 0:
            screen.blit(self._small.render("▲  scroll up", True, MID_GREY),
                        (sw - 120, content_y + 4))
        if self._scroll < self._max_scroll():
            screen.blit(self._small.render("▼  more below", True, MID_GREY),
                        (sw - 128, content_y + vis_h - 16))

        # Footer
        footer_y = sh - 76
        pygame.draw.line(screen, UI_BORDER, (20, footer_y), (sw - 20, footer_y), 1)

        if not completed:
            bw, bh = 380, 48
            bx = sw // 2 - bw // 2
            by = footer_y + 8
            ga = int(55 + 30 * math.sin(t / 15))
            pygame.draw.rect(screen, (*UI_HIGHLIGHT, ga),
                             (bx - 4, by - 4, bw + 8, bh + 8), 2, border_radius=12)
            bg = pygame.Surface((bw, bh), pygame.SRCALPHA)
            bg.fill((18, 38, 18, 225))
            screen.blit(bg, (bx, by))
            pygame.draw.rect(screen, UI_HIGHLIGHT, (bx, by, bw, bh), 2, border_radius=8)
            lbl = self._font.render("ENTER / M  —  Mark as Complete", True, UI_HIGHLIGHT)
            screen.blit(lbl, (bx + bw // 2 - lbl.get_width() // 2,
                               by + bh // 2 - lbl.get_height() // 2))
        else:
            done_lbl = self._font.render("✓  LECTURE COMPLETE", True, UI_HIGHLIGHT)
            screen.blit(done_lbl,
                        (sw // 2 - done_lbl.get_width() // 2, footer_y + 18))

        hint = self._small.render(
            "ESC  Back to list    ↑↓  Scroll content", True, MID_GREY)
        screen.blit(hint, (sw // 2 - hint.get_width() // 2, sh - 18))


# ── Semester Report Screen (Phase 8) ──────────────────────────────────────────

class SemesterReportScreen:
    """
    Comprehensive post-game semester report card.

    Displays 8 sections in a two-column layout:
    LEFT  — Entrance Exam Result · Cyber Maturity · Training Progress · Exam Status
    RIGHT — Behaviour Analysis · Weakness Detection · Recommendations · Learning Progress

    handle_key() returns:
        True  — user dismissed (Q / ESC)
        False — no action
    """

    MATURITY_COLORS = {
        "Beginner":       (235,  75,  75),
        "Aware":          (255, 200,  50),
        "Secure":         ( 80, 200, 130),
        "Cyber Guardian": ( 80, 160, 255),
    }
    RISK_COLORS = {
        "LOW":    ( 80, 210, 130),
        "MEDIUM": (255, 180,  50),
        "HIGH":   (235,  75,  75),
    }

    def __init__(self, screen_w: int, screen_h: int):
        self.sw = screen_w
        self.sh = screen_h
        self._font  = None
        self._big   = None
        self._small = None
        self._timer  = 0
        self._report: dict = {}

    def set_fonts(self, font, big, small):
        self._font = font; self._big = big; self._small = small

    def set_report(self, report: dict):
        """Load a semester report dict (from SemesterReport.generate())."""
        self._report = report or {}
        self._timer  = 0

    def handle_key(self, key: int) -> bool:
        """Return True to dismiss screen."""
        return key in (pygame.K_q, pygame.K_ESCAPE, pygame.K_RETURN)

    def update(self):
        self._timer += 1

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, screen: pygame.Surface):
        t       = self._timer
        sw, sh  = self.sw, self.sh
        r       = self._report

        if not r:
            screen.fill((10, 10, 30))
            return

        emp      = r.get("employee", {})
        maturity = r.get("maturity", {})
        biases   = r.get("biases", {})
        weakness = r.get("weakness", {})
        progress = r.get("training_progress", {})
        rec      = r.get("recommendation", {})
        lectures = r.get("lectures", {})
        score    = r.get("score",  0)
        risk     = r.get("risk",   "MEDIUM")
        exam_st  = r.get("exam_status", "LOCKED")

        # Score count-up animation (60 frames)
        disp_score = min(score, int(score * min(t, 60) / 60))

        # Animated background
        for y in range(sh):
            shade = int(6 + 4 * math.sin(t / 90 + y / 120))
            pygame.draw.line(screen, (shade, shade, shade + 18), (0, y), (sw, y))

        # ── HEADER ────────────────────────────────────────────────────────────
        hdr_h = 60
        hdr   = pygame.Surface((sw, hdr_h), pygame.SRCALPHA)
        hdr.fill((12, 14, 35, 235))
        screen.blit(hdr, (0, 0))
        pygame.draw.line(screen, UI_BORDER, (0, hdr_h), (sw, hdr_h), 2)

        title = self._big.render("PHISHVERSE  SEMESTER  REPORT", True, UI_GOLD)
        screen.blit(title, (sw // 2 - title.get_width() // 2, 12))

        date_str = r.get("date", "")
        if date_str:
            dl = self._small.render(date_str, True, (100, 120, 180))
            screen.blit(dl, (sw - dl.get_width() - 16, 4))

        # ── EMPLOYEE INFO BAR ──────────────────────────────────────────────────
        bar_y = hdr_h
        bar_h = 28
        bar   = pygame.Surface((sw, bar_h), pygame.SRCALPHA)
        bar.fill((8, 10, 28, 200))
        screen.blit(bar, (0, bar_y))
        pygame.draw.line(screen, (*UI_BORDER, 70), (0, bar_y + bar_h),
                         (sw, bar_y + bar_h), 1)

        parts = []
        if emp.get("employee_name"): parts.append(emp["employee_name"])
        if emp.get("employee_id"):   parts.append(f"ID: {emp['employee_id']}")
        if emp.get("department"):    parts.append(emp["department"])
        if emp.get("role"):          parts.append(emp["role"])
        camp_name = r.get("campaign_name", "")
        if camp_name:                parts.append(f"Campaign: {camp_name}")

        ix = 20
        for k, part in enumerate(parts):
            if k > 0:
                sep = self._small.render("  |  ", True, (50, 65, 110))
                screen.blit(sep, (ix, bar_y + 6)); ix += sep.get_width()
            pl = self._small.render(part, True, (180, 200, 240))
            screen.blit(pl, (ix, bar_y + 6)); ix += pl.get_width()

        # ── CONTENT AREA ──────────────────────────────────────────────────────
        content_y = bar_y + bar_h + 5
        gap       = 7           # vertical gap between cards
        col_gap   = 8           # horizontal gap between columns
        col_w     = (sw - 40 - col_gap) // 2
        lcx       = 20          # left column x
        rcx       = 20 + col_w + col_gap

        cy_l = content_y
        cy_r = content_y

        # ── LEFT COLUMN ───────────────────────────────────────────────────────

        # ① Entrance Exam Result
        card_h = 130
        self._card(screen, lcx, cy_l, col_w, card_h, "ENTRANCE EXAM RESULT")
        risk_col   = self.RISK_COLORS.get(risk, WHITE)
        score_lbl  = self._big.render(str(disp_score), True, risk_col)
        screen.blit(score_lbl, (lcx + 18, cy_l + 24))
        slash_lbl  = self._small.render("/100", True, (100, 110, 140))
        screen.blit(slash_lbl, (lcx + 18 + score_lbl.get_width() + 4, cy_l + 38))

        rbt  = self._small.render(f"  {risk} RISK  ", True, (10, 10, 30))
        rbw  = rbt.get_width(); rbh = rbt.get_height() + 6
        pygame.draw.rect(screen, risk_col,
                         (lcx + 110, cy_l + 26, rbw, rbh), border_radius=8)
        screen.blit(rbt, (lcx + 110, cy_l + 29))

        passed     = r.get("passed", False)
        stat_col   = (80, 210, 130) if passed else (235, 75, 75)
        stat_str   = "PASSED" if passed else "FAILED"
        stat_lbl   = self._small.render(stat_str, True, stat_col)
        screen.blit(stat_lbl, (lcx + col_w - stat_lbl.get_width() - 14, cy_l + 26))

        camp_l = self._small.render(camp_name, True, (140, 150, 200))
        screen.blit(camp_l, (lcx + 18, cy_l + 72))
        ev_l   = self._small.render(
            f"Events: {progress.get('events_completed',0)}"
            f"/{progress.get('events_total',0)} completed",
            True, (120, 135, 185))
        screen.blit(ev_l, (lcx + 18, cy_l + 90))
        cy_l += card_h + gap

        # ② Cyber Maturity Index
        card_h    = 108
        self._card(screen, lcx, cy_l, col_w, card_h, "CYBER MATURITY INDEX")
        mat_level = maturity.get("level", "Beginner")
        mat_col   = self.MATURITY_COLORS.get(mat_level, WHITE)
        mat_desc  = maturity.get("description", "")

        ml = self._font.render(mat_level.upper(), True, mat_col)
        screen.blit(ml, (lcx + 18, cy_l + 26))
        dl = self._small.render(mat_desc, True, (130, 145, 185))
        screen.blit(dl, (lcx + 18, cy_l + 48))

        self._bar(screen, lcx + 18, cy_l + 70, col_w - 40, 14,
                  disp_score / 100, mat_col)
        sl2 = self._small.render(f"{score}%", True, mat_col)
        screen.blit(sl2, (lcx + col_w - sl2.get_width() - 14, cy_l + 68))
        cy_l += card_h + gap

        # ③ Training Progress
        card_h    = 86
        self._card(screen, lcx, cy_l, col_w, card_h, "TRAINING PROGRESS")
        prog_pct  = progress.get("progress_pct", 0)
        ev_done   = progress.get("events_completed", 0)
        ev_total  = progress.get("events_total", 0)
        self._bar(screen, lcx + 18, cy_l + 36, col_w - 40, 16,
                  prog_pct / 100, (80, 160, 255))
        pstr = self._small.render(
            f"{ev_done}/{ev_total} events  ·  {prog_pct}% complete",
            True, (150, 170, 220))
        screen.blit(pstr, (lcx + 18, cy_l + 60))
        cy_l += card_h + gap

        # ④ Exam Status
        card_h     = 74
        self._card(screen, lcx, cy_l, col_w, card_h, "FINAL EXAM STATUS")
        exam_color = (80, 210, 130) if exam_st == "UNLOCKED" else (235, 75, 75)
        if exam_st == "LOCKED":
            pulse_a  = int(200 + 40 * math.sin(t / 18))
            ec_p     = (min(255, exam_color[0] + pulse_a // 8),
                        exam_color[1], exam_color[2])
        else:
            ec_p     = exam_color

        et   = self._font.render(f"  {exam_st}  ", True, (10, 10, 30))
        ew   = et.get_width(); eh = et.get_height() + 8
        pygame.draw.rect(screen, ec_p,
                         (lcx + 18, cy_l + 24, ew, eh), border_radius=8)
        screen.blit(et, (lcx + 18, cy_l + 28))
        cond = ("All events completed" if exam_st == "UNLOCKED"
                else "Complete all events to unlock")
        cl   = self._small.render(cond, True, (130, 145, 185))
        screen.blit(cl, (lcx + 26 + ew, cy_l + 32))
        cy_l += card_h + gap

        # ── RIGHT COLUMN ──────────────────────────────────────────────────────

        # ⑤ Behaviour Analysis
        card_h = 158
        self._card(screen, rcx, cy_r, col_w, card_h, "BEHAVIOUR ANALYSIS")
        bias_rows = [
            ("Urgency",   biases.get("urgency",   0), (255, 180,  50)),
            ("Authority", biases.get("authority", 0), (235,  75,  75)),
            ("Reward",    biases.get("reward",    0), ( 80, 160, 255)),
            ("Fear",      biases.get("fear",      0), (200,  80, 200)),
        ]
        by = cy_r + 28
        for name, val, col in bias_rows:
            nl = self._small.render(name, True, (140, 155, 200))
            screen.blit(nl, (rcx + 18, by))
            bar_x = rcx + 100; bar_w = col_w - 150
            self._bar(screen, bar_x, by + 2, bar_w, 10, min(val, 20) / 20, col)
            vl = self._small.render(str(val), True, col)
            screen.blit(vl, (rcx + col_w - 30, by))
            by += 30
        cy_r += card_h + gap

        # ⑥ Weakness Detection
        card_h    = 90
        self._card(screen, rcx, cy_r, col_w, card_h, "WEAKNESS DETECTION")
        primary   = weakness.get("primary",   "None")
        secondary = weakness.get("secondary", "None")
        pl_lbl  = self._small.render("Primary:",   True, (130, 145, 185))
        pv_lbl  = self._font.render( primary,      True, (235,  75,  75))
        sl_lbl  = self._small.render("Secondary:", True, (130, 145, 185))
        sv_lbl  = self._small.render( secondary,   True, (255, 180,  50))
        screen.blit(pl_lbl, (rcx + 18, cy_r + 26))
        screen.blit(pv_lbl, (rcx + 18, cy_r + 42))
        screen.blit(sl_lbl, (rcx + col_w // 2, cy_r + 26))
        screen.blit(sv_lbl, (rcx + col_w // 2, cy_r + 44))
        cy_r += card_h + gap

        # ⑦ Recommendations
        card_h    = 108
        self._card(screen, rcx, cy_r, col_w, card_h, "RECOMMENDATIONS")
        recs = [
            ("Next Lecture:", rec.get("next_lecture",    "TBD"),         ( 80, 200, 130)),
            ("Focus Area:",   rec.get("suggested_topic", "TBD"),         (255, 200,  50)),
            ("Exam Ready:",   "Yes" if rec.get("exam_ready") else "No",
             (80, 210, 130) if rec.get("exam_ready") else (235, 75, 75)),
        ]
        ry = cy_r + 26
        for label, val, col in recs:
            ll = self._small.render(label, True, (130, 145, 185))
            vl = self._small.render(val,   True, col)
            screen.blit(ll, (rcx + 18, ry))
            screen.blit(vl, (rcx + 130, ry))
            ry += 24
        cy_r += card_h + gap

        # ⑧ Learning Progress
        card_h  = 70
        self._card(screen, rcx, cy_r, col_w, card_h, "LEARNING PROGRESS")
        lec_done  = lectures.get("completed", 0)
        lec_total = lectures.get("assigned",  0)
        lec_pct   = lectures.get("progress_pct", 0)
        lstr = (f"{lec_done}/{lec_total} lectures completed"
                if lec_total > 0 else "No lectures assigned yet")
        ll = self._small.render(lstr, True, (140, 155, 200))
        screen.blit(ll, (rcx + 18, cy_r + 28))
        if lec_total > 0:
            self._bar(screen, rcx + 18, cy_r + 48, col_w - 40, 10,
                      lec_pct / 100, (80, 160, 255))

        # ── FOOTER ────────────────────────────────────────────────────────────
        footer_y = sh - 36
        footer   = pygame.Surface((sw, 36), pygame.SRCALPHA)
        footer.fill((0, 0, 0, 180))
        screen.blit(footer, (0, footer_y))
        pygame.draw.line(screen, UI_BORDER, (0, footer_y), (sw, footer_y), 1)

        emp_id   = emp.get("employee_id", "UNKNOWN").upper()
        save_str = f"Report: employee_reports/{emp_id}_report.json"
        sal = self._small.render(save_str, True, (80, 100, 140))
        screen.blit(sal, (20, footer_y + 10))

        ql = self._small.render("Q / ESC — Exit   |   ENTER — Continue",
                                True, (140, 150, 185))
        screen.blit(ql, (sw - ql.get_width() - 20, footer_y + 10))

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _card(self, screen, x, y, w, h, title):
        """Draw a dark titled card panel."""
        bg = pygame.Surface((w, h), pygame.SRCALPHA)
        bg.fill((10, 14, 36, 200))
        screen.blit(bg, (x, y))
        pygame.draw.rect(screen, (38, 50, 88), (x, y, w, h), 1, border_radius=5)
        # Title bar
        tb = pygame.Surface((w, 20), pygame.SRCALPHA)
        tb.fill((18, 26, 62, 225))
        screen.blit(tb, (x, y))
        pygame.draw.line(screen, (*UI_BORDER, 90), (x, y + 20), (x + w, y + 20), 1)
        tl = self._small.render(title, True, UI_GOLD)
        screen.blit(tl, (x + 10, y + 3))

    def _bar(self, screen, x, y, w, h, frac, col):
        """Draw a horizontal progress bar."""
        frac = max(0.0, min(1.0, frac))
        pygame.draw.rect(screen, (28, 34, 58), (x, y, w, h), border_radius=3)
        pygame.draw.rect(screen, (48, 58, 95), (x, y, w, h), 1, border_radius=3)
        fw = int(w * frac)
        if fw > 0:
            pygame.draw.rect(screen, col, (x, y, fw, h), border_radius=3)


# ── Final Exam Screen (Phase 9) ───────────────────────────────────────────────

class FinalExamScreen:
    """
    Adaptive MCQ final exam — 10 questions drawn from question_bank.json,
    weighted toward the employee's primary weakness category.

    Phases:
      IDLE      — waiting for start()
      QUIZ      — employee selects A/B/C/D, presses ENTER to confirm
      REVEALING — shows correct/wrong for ~1.5 s then auto-advances
      RESULTS   — final score display (PASS / FAIL)

    handle_key() returns:
      "PASS"  — exam finished, score >= 70
      "FAIL"  — exam finished, score < 70
      "QUIT"  — ESC pressed during exam (treated as quit)
      None    — no terminal action yet
    """

    CAT_COLORS = {
        "urgency":   (255, 180,  50),
        "authority": (235,  75,  75),
        "reward":    ( 80, 160, 255),
        "fear":      (200,  80, 200),
    }
    OPTION_KEYS = {
        pygame.K_a: 0, pygame.K_1: 0,
        pygame.K_b: 1, pygame.K_2: 1,
        pygame.K_c: 2, pygame.K_3: 2,
        pygame.K_d: 3, pygame.K_4: 3,
    }
    OPTION_LABELS = ["A", "B", "C", "D"]
    REVEAL_FRAMES  = 90      # 1.5 s at 60 fps

    def __init__(self, screen_w: int, screen_h: int):
        self.sw = screen_w
        self.sh = screen_h
        self._font  = None
        self._big   = None
        self._small = None
        self._reset()

    def _reset(self):
        self._phase      = "IDLE"
        self._questions  = []
        self._current    = 0
        self._selected   = None     # 0-3
        self._answers    = []       # list of chosen indices
        self._reveal_t   = 0
        self._score_data = {}
        self._attempt    = 1

    def set_fonts(self, font, big, small):
        self._font = font; self._big = big; self._small = small

    def start(self, questions: list, attempt: int = 1):
        """Begin a new exam session with the given question list."""
        self._reset()
        self._questions = questions
        self._attempt   = attempt
        self._phase     = "QUIZ"

    @property
    def score_data(self) -> dict:
        return self._score_data

    # ── Input ─────────────────────────────────────────────────────────────────

    def handle_key(self, key: int):
        """Returns "PASS"/"FAIL"/"QUIT"/None."""
        if self._phase == "IDLE":
            return None

        if self._phase == "REVEALING":
            return None   # keys ignored — auto-advance via update()

        if self._phase == "QUIZ":
            if key == pygame.K_ESCAPE:
                return "QUIT"
            if key in self.OPTION_KEYS:
                self._selected = self.OPTION_KEYS[key]
            elif key == pygame.K_RETURN and self._selected is not None:
                self._confirm_answer()
            return None

        if self._phase == "RESULTS":
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                return "PASS" if self._score_data.get("passed") else "FAIL"
            if key == pygame.K_ESCAPE:
                return "QUIT"
            return None

        return None

    def _confirm_answer(self):
        self._answers.append(self._selected)
        self._phase    = "REVEALING"
        self._reveal_t = 0

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self):
        if self._phase == "REVEALING":
            self._reveal_t += 1
            if self._reveal_t >= self.REVEAL_FRAMES:
                self._next_question()

    def _next_question(self):
        self._current  += 1
        self._selected  = None
        self._reveal_t  = 0
        if self._current >= len(self._questions):
            # Exam complete — compute score
            from exam.question_engine import QuestionEngine
            self._score_data = QuestionEngine.score(self._questions, self._answers)
            self._phase = "RESULTS"
        else:
            self._phase = "QUIZ"

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, screen: pygame.Surface):
        sw, sh = self.sw, self.sh

        # Background
        for y in range(sh):
            shade = int(6 + 3 * math.sin(self._current / 5 + y / 110))
            pygame.draw.line(screen, (shade, shade, shade + 22), (0, y), (sw, y))

        if self._phase == "IDLE":
            return

        if self._phase in ("QUIZ", "REVEALING"):
            self._draw_quiz(screen)
        elif self._phase == "RESULTS":
            self._draw_results(screen)

    def _draw_quiz(self, screen: pygame.Surface):
        sw, sh = self.sw, self.sh
        q = self._questions[self._current] if self._current < len(self._questions) else {}
        cat   = q.get("category", "urgency")
        text  = q.get("question", "")
        opts  = q.get("options", [])
        cor   = ord(q.get("answer", "A").upper()) - ord("A")
        phase = self._phase
        cat_col = self.CAT_COLORS.get(cat, WHITE)

        # ── HEADER ────────────────────────────────────────────────────────────
        hdr = pygame.Surface((sw, 58), pygame.SRCALPHA)
        hdr.fill((12, 14, 35, 240))
        screen.blit(hdr, (0, 0))
        pygame.draw.line(screen, UI_BORDER, (0, 58), (sw, 58), 2)

        title_lbl = self._big.render("PHISHVERSE  FINAL  EXAM", True, UI_GOLD)
        screen.blit(title_lbl, (sw // 2 - title_lbl.get_width() // 2, 12))

        # Q counter (right)
        qc = self._small.render(
            f"Q {self._current + 1} / {len(self._questions)}",
            True, (180, 200, 240))
        screen.blit(qc, (sw - qc.get_width() - 20, 4))

        # Category badge (left)
        cat_txt = self._small.render(f"  {cat.upper()}  ", True, (10, 10, 30))
        cw = cat_txt.get_width(); ch = cat_txt.get_height() + 6
        pygame.draw.rect(screen, cat_col, (16, 4, cw, ch), border_radius=8)
        screen.blit(cat_txt, (16, 7))

        # ── PROGRESS BAR ──────────────────────────────────────────────────────
        prog_y = 58
        prog_h = 10
        pygame.draw.rect(screen, (24, 28, 54), (0, prog_y, sw, prog_h))
        fill_w = int(sw * (self._current / max(len(self._questions), 1)))
        pygame.draw.rect(screen, cat_col, (0, prog_y, fill_w, prog_h))

        # ── QUESTION CARD ─────────────────────────────────────────────────────
        q_y  = 78;  q_x = 30; q_w = sw - 60; q_h = 130
        qbg  = pygame.Surface((q_w, q_h), pygame.SRCALPHA)
        qbg.fill((10, 14, 38, 210))
        screen.blit(qbg, (q_x, q_y))
        pygame.draw.rect(screen, cat_col, (q_x, q_y, q_w, q_h), 1, border_radius=6)

        # Word-wrap question text
        words   = text.split()
        lines   = []
        cur     = ""
        for w in words:
            test = (cur + " " + w).strip()
            tw   = self._font.size(test)[0]
            if tw > q_w - 24:
                lines.append(cur)
                cur = w
            else:
                cur = test
        if cur:
            lines.append(cur)

        ty = q_y + 14
        for ln in lines[:5]:
            ll = self._font.render(ln, True, (210, 220, 240))
            screen.blit(ll, (q_x + 12, ty))
            ty += 22

        # ── OPTIONS ───────────────────────────────────────────────────────────
        opt_y  = q_y + q_h + 12
        opt_h  = 46
        opt_gap = 8

        for i, opt_text in enumerate(opts):
            oy = opt_y + i * (opt_h + opt_gap)
            is_selected = (self._selected == i)
            is_correct  = (i == cor)

            # Colors
            if phase == "REVEALING":
                if is_correct:
                    bg_col  = (30, 80, 40, 200)
                    bd_col  = (80, 210, 130)
                elif is_selected and not is_correct:
                    bg_col  = (80, 20, 20, 200)
                    bd_col  = (235, 75, 75)
                else:
                    bg_col  = (10, 14, 38, 160)
                    bd_col  = (40, 50, 80)
            elif is_selected:
                bg_col  = (20, 30, 70, 220)
                bd_col  = UI_GOLD
            else:
                bg_col  = (10, 14, 38, 180)
                bd_col  = (40, 50, 80)

            obg = pygame.Surface((sw - 60, opt_h), pygame.SRCALPHA)
            obg.fill(bg_col)
            screen.blit(obg, (30, oy))
            pygame.draw.rect(screen, bd_col, (30, oy, sw - 60, opt_h), 1,
                             border_radius=5)

            # Option key badge
            key_lbl  = self._font.render(self.OPTION_LABELS[i], True, bd_col)
            kw, kh   = key_lbl.get_width() + 12, key_lbl.get_height() + 6
            pygame.draw.rect(screen, bd_col, (42, oy + opt_h // 2 - kh // 2, kw, kh),
                             border_radius=4)
            key_dark = self._font.render(self.OPTION_LABELS[i], True, (8, 8, 20))
            screen.blit(key_dark, (48, oy + opt_h // 2 - key_dark.get_height() // 2))

            # Option text
            # Truncate to fit
            opt_disp = opt_text
            while self._font.size(opt_disp)[0] > sw - 120 and len(opt_disp) > 10:
                opt_disp = opt_disp[:-4] + "..."
            ol = self._font.render(opt_disp, True, (210, 220, 240))
            screen.blit(ol, (42 + kw + 8, oy + opt_h // 2 - ol.get_height() // 2))

            # Reveal icons
            if phase == "REVEALING":
                icon = "OK" if is_correct else ("X" if (is_selected and not is_correct) else "")
                if icon:
                    ic_col = (80, 210, 130) if icon == "OK" else (235, 75, 75)
                    il = self._font.render(icon, True, ic_col)
                    screen.blit(il, (sw - 60, oy + opt_h // 2 - il.get_height() // 2))

        # ── FOOTER HINT ───────────────────────────────────────────────────────
        footer_y = sh - 30
        if phase == "QUIZ":
            hint = "A / B / C / D   to select     ENTER   to confirm     ESC   quit"
        else:
            rev_pct = int(self._reveal_t / self.REVEAL_FRAMES * 100)
            hint    = f"Next question in... {100 - rev_pct}%"

        hl = self._small.render(hint, True, (100, 115, 160))
        screen.blit(hl, (sw // 2 - hl.get_width() // 2, footer_y))

    def _draw_results(self, screen: pygame.Surface):
        sw, sh   = self.sw, self.sh
        sd       = self._score_data
        score    = sd.get("score",   0)
        correct  = sd.get("correct", 0)
        total    = sd.get("total",   10)
        passed   = sd.get("passed",  False)
        by_cat   = sd.get("by_category", {})

        pass_col = (80, 210, 130) if passed else (235, 75, 75)

        # ── HEADER ────────────────────────────────────────────────────────────
        hdr = pygame.Surface((sw, 58), pygame.SRCALPHA)
        hdr.fill((12, 14, 35, 240))
        screen.blit(hdr, (0, 0))
        pygame.draw.line(screen, UI_BORDER, (0, 58), (sw, 58), 2)
        tl = self._big.render("EXAM  COMPLETE", True, UI_GOLD)
        screen.blit(tl, (sw // 2 - tl.get_width() // 2, 12))

        # ── SCORE CIRCLE ──────────────────────────────────────────────────────
        cx = sw // 2; cy = 160; r = 70
        pygame.draw.circle(screen, (16, 20, 50), (cx, cy), r)
        pygame.draw.circle(screen, pass_col, (cx, cy), r, 3)
        sc_lbl = self._big.render(str(score), True, pass_col)
        screen.blit(sc_lbl, (cx - sc_lbl.get_width() // 2, cy - sc_lbl.get_height() // 2))
        pct_l  = self._small.render("%", True, pass_col)
        screen.blit(pct_l,  (cx + sc_lbl.get_width() // 2, cy - 6))

        # ── PASS / FAIL BANNER ────────────────────────────────────────────────
        banner_y = cy + r + 14
        bl = self._big.render(
            "PASSED  — Generating Certificate..." if passed else "FAILED  — Return to Lectures",
            True, pass_col)
        screen.blit(bl, (sw // 2 - bl.get_width() // 2, banner_y))

        # ── CATEGORY BREAKDOWN ────────────────────────────────────────────────
        bd_y = banner_y + 48
        for cat, data in by_cat.items():
            c_cor   = data.get("correct", 0)
            c_tot   = data.get("total",   0)
            c_pct   = round(c_cor / c_tot * 100) if c_tot else 0
            c_col   = self.CAT_COLORS.get(cat, WHITE)
            row_lbl = self._small.render(
                f"{cat.capitalize():<12}  {c_cor}/{c_tot}  ({c_pct}%)", True, c_col)
            screen.blit(row_lbl, (sw // 2 - row_lbl.get_width() // 2, bd_y))
            bd_y += 26

        # ── SCORE DETAIL ──────────────────────────────────────────────────────
        det = self._small.render(
            f"{correct} / {total} correct   |   Pass mark: 70%",
            True, (140, 155, 200))
        screen.blit(det, (sw // 2 - det.get_width() // 2, bd_y + 14))

        # ── CONTINUE BUTTON ───────────────────────────────────────────────────
        btn_y = bd_y + 56; btn_w = 280; btn_h = 44
        btn_x = sw // 2 - btn_w // 2
        btn_bg = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        btn_bg.fill((20, 26, 60, 220))
        screen.blit(btn_bg, (btn_x, btn_y))
        pygame.draw.rect(screen, pass_col, (btn_x, btn_y, btn_w, btn_h), 2, border_radius=8)
        btn_lbl = self._font.render("ENTER — Continue", True, pass_col)
        screen.blit(btn_lbl,
                    (sw // 2 - btn_lbl.get_width() // 2,
                     btn_y + btn_h // 2 - btn_lbl.get_height() // 2))


# ── Certificate Screen (Phase 9) ──────────────────────────────────────────────

class CertificateScreen:
    """
    Animated PHISHVERSE Cyber Awareness Certificate display.

    handle_key() returns True to dismiss.
    """

    MATURITY_COLORS = {
        "Beginner":       (235,  75,  75),
        "Aware":          (255, 200,  50),
        "Secure":         ( 80, 200, 130),
        "Cyber Guardian": ( 80, 160, 255),
    }

    def __init__(self, screen_w: int, screen_h: int):
        self.sw = screen_w
        self.sh = screen_h
        self._font  = None
        self._big   = None
        self._small = None
        self._cert  = {}
        self._timer  = 0

    def set_fonts(self, font, big, small):
        self._font = font; self._big = big; self._small = small

    def set_cert(self, cert: dict):
        self._cert  = cert or {}
        self._timer = 0

    def handle_key(self, key: int) -> bool:
        return key in (pygame.K_q, pygame.K_ESCAPE, pygame.K_RETURN)

    def update(self):
        self._timer += 1

    def draw(self, screen: pygame.Surface):
        t       = self._timer
        sw, sh  = self.sw, self.sh
        c       = self._cert

        # Animated dark-navy background
        for y in range(sh):
            shade = int(8 + 5 * math.sin(t / 80 + y / 90))
            pygame.draw.line(screen, (shade, shade, shade + 28), (0, y), (sw, y))

        if not c:
            return

        # Reveal animation — slide down from top (first 40 frames)
        offset_y = max(0, int((40 - t) * 16)) if t < 40 else 0

        # ── CERTIFICATE PANEL ─────────────────────────────────────────────────
        pad_x   = 60;  pad_y = 40
        cert_x  = pad_x
        cert_y  = pad_y + offset_y
        cert_w  = sw - 2 * pad_x
        cert_h  = sh - 2 * pad_y

        # Background
        cbg = pygame.Surface((cert_w, cert_h), pygame.SRCALPHA)
        cbg.fill((10, 12, 34, 230))
        screen.blit(cbg, (cert_x, cert_y))

        # Outer gold border (double)
        pulse_a = int(200 + 55 * math.sin(t / 40))
        border_col = (min(255, 220), min(255, pulse_a), 30)
        pygame.draw.rect(screen, border_col,
                         (cert_x, cert_y, cert_w, cert_h), 3, border_radius=8)
        pygame.draw.rect(screen, (*border_col, 80),
                         (cert_x + 7, cert_y + 7, cert_w - 14, cert_h - 14), 1,
                         border_radius=6)

        # Corner decorations
        for dx, dy in [(0, 0), (cert_w - 20, 0), (0, cert_h - 20), (cert_w - 20, cert_h - 20)]:
            pygame.draw.rect(screen, border_col,
                             (cert_x + dx, cert_y + dy, 20, 20), 2, border_radius=3)

        # ── ISSUER ────────────────────────────────────────────────────────────
        iss_y = cert_y + 18
        iss_l = self._small.render("PHISHVERSE  TRAINING  PLATFORM", True, border_col)
        screen.blit(iss_l, (cert_x + cert_w // 2 - iss_l.get_width() // 2, iss_y))

        # Divider
        pygame.draw.line(screen, border_col,
                         (cert_x + 30, iss_y + 18), (cert_x + cert_w - 30, iss_y + 18), 1)

        # ── TITLE ─────────────────────────────────────────────────────────────
        title_y = iss_y + 28
        tl1     = self._big.render("CERTIFICATE OF", True, UI_GOLD)
        tl2     = self._big.render("CYBER AWARENESS", True, UI_GOLD)
        screen.blit(tl1, (cert_x + cert_w // 2 - tl1.get_width() // 2, title_y))
        screen.blit(tl2, (cert_x + cert_w // 2 - tl2.get_width() // 2, title_y + 30))

        # ── THIS CERTIFIES THAT ───────────────────────────────────────────────
        cert_y2 = title_y + 76
        cl = self._small.render("This certifies that", True, (160, 175, 215))
        screen.blit(cl, (cert_x + cert_w // 2 - cl.get_width() // 2, cert_y2))

        # Employee name (large)
        emp_name = c.get("employee_name", "").upper() or "EMPLOYEE"
        nl = self._big.render(emp_name, True, WHITE)
        screen.blit(nl, (cert_x + cert_w // 2 - nl.get_width() // 2, cert_y2 + 22))

        # Sub-info: ID | Department | Role
        sub_parts = []
        if c.get("employee_id"):   sub_parts.append(f"ID: {c['employee_id']}")
        if c.get("department"):    sub_parts.append(c["department"])
        if c.get("role"):          sub_parts.append(c["role"])
        sl = self._small.render("  ·  ".join(sub_parts), True, (140, 155, 200))
        screen.blit(sl, (cert_x + cert_w // 2 - sl.get_width() // 2, cert_y2 + 56))

        # ── ACHIEVEMENT TEXT ──────────────────────────────────────────────────
        ach_y = cert_y2 + 80
        al = self._small.render(
            "has successfully completed the PHISHVERSE Cyber Awareness Programme",
            True, (160, 175, 215))
        screen.blit(al, (cert_x + cert_w // 2 - al.get_width() // 2, ach_y))

        camp = c.get("campaign", "")
        if camp:
            cl2 = self._small.render(f"Campaign: {camp}", True, (120, 140, 185))
            screen.blit(cl2, (cert_x + cert_w // 2 - cl2.get_width() // 2, ach_y + 20))

        # ── SCORE + MATURITY ──────────────────────────────────────────────────
        metric_y = ach_y + 54

        # Final score badge
        fs      = c.get("final_score", 0)
        fs_col  = (80, 210, 130)
        fs_bg   = pygame.Surface((130, 60), pygame.SRCALPHA)
        fs_bg.fill((20, 60, 28, 200))
        sc_x    = cert_x + cert_w // 4 - 65
        screen.blit(fs_bg, (sc_x, metric_y))
        pygame.draw.rect(screen, fs_col, (sc_x, metric_y, 130, 60), 1, border_radius=6)
        scl1 = self._small.render("FINAL SCORE", True, (100, 180, 120))
        scl2 = self._big.render(f"{fs}%", True, fs_col)
        screen.blit(scl1, (sc_x + 65 - scl1.get_width() // 2, metric_y + 6))
        screen.blit(scl2, (sc_x + 65 - scl2.get_width() // 2, metric_y + 24))

        # Maturity badge
        mat     = c.get("cyber_maturity", "Aware")
        mat_col = self.MATURITY_COLORS.get(mat, WHITE)
        mat_bg  = pygame.Surface((160, 60), pygame.SRCALPHA)
        mat_bg.fill((16, 22, 60, 200))
        mat_x   = cert_x + 3 * cert_w // 4 - 80
        screen.blit(mat_bg, (mat_x, metric_y))
        pygame.draw.rect(screen, mat_col, (mat_x, metric_y, 160, 60), 1, border_radius=6)
        ml1 = self._small.render("CYBER MATURITY", True, (100, 120, 180))
        ml2 = self._font.render(mat.upper(), True, mat_col)
        screen.blit(ml1, (mat_x + 80 - ml1.get_width() // 2, metric_y + 6))
        screen.blit(ml2, (mat_x + 80 - ml2.get_width() // 2, metric_y + 28))

        # ── CERT ID + DATE ────────────────────────────────────────────────────
        meta_y  = metric_y + 76
        pygame.draw.line(screen, (*UI_BORDER, 80),
                         (cert_x + 30, meta_y), (cert_x + cert_w - 30, meta_y), 1)
        meta_y += 10

        cert_id   = c.get("certificate_id", "PV-XXXXXXXX")
        issued    = c.get("issued_date",    "")
        id_lbl    = self._small.render(f"Cert ID: {cert_id}", True, (100, 115, 160))
        date_lbl  = self._small.render(f"Issued: {issued}",   True, (100, 115, 160))
        screen.blit(id_lbl,   (cert_x + 30, meta_y))
        screen.blit(date_lbl, (cert_x + cert_w - date_lbl.get_width() - 30, meta_y))

        # ── SEAL ──────────────────────────────────────────────────────────────
        seal_x = cert_x + cert_w // 2
        seal_y = meta_y + 30
        seal_r = 26
        pulse  = int(220 + 35 * math.sin(t / 25))
        seal_col = (min(255, pulse), min(255, pulse // 2), 20)
        pygame.draw.circle(screen, (16, 20, 50), (seal_x, seal_y), seal_r)
        pygame.draw.circle(screen, seal_col, (seal_x, seal_y), seal_r, 2)
        sl_txt = self._small.render("PV", True, seal_col)
        screen.blit(sl_txt, (seal_x - sl_txt.get_width() // 2,
                              seal_y - sl_txt.get_height() // 2))

        # ── FOOTER ────────────────────────────────────────────────────────────
        footer_y = sh - 26
        footer   = pygame.Surface((sw, 26), pygame.SRCALPHA)
        footer.fill((0, 0, 0, 160))
        screen.blit(footer, (0, footer_y))
        pygame.draw.line(screen, UI_BORDER, (0, footer_y), (sw, footer_y), 1)

        emp_id    = c.get("employee_id", "UNKNOWN").upper()
        save_str  = f"Saved: certificates/{emp_id}_certificate.json"
        sal = self._small.render(save_str, True, (80, 100, 140))
        screen.blit(sal, (20, footer_y + 6))

        ql = self._small.render("Q / ESC / ENTER — Exit PHISHVERSE",
                                True, (140, 150, 185))
        screen.blit(ql, (sw - ql.get_width() - 20, footer_y + 6))

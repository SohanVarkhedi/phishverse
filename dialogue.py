"""
PHISHVERSE – dialogue.py
Enhanced Pokémon-style dialog box:
- Animated typewriter text reveal
- Choice menu with highlighted cursor and border
- Speaker portrait icon strip
- Scanline retro overlay
- Auto word-wrap
"""

import pygame
import math
from constants import *

# Map speaker prefixes to accent colors
SPEAKER_COLORS = {
    "✓": (80, 220, 100),
    "⚠": (220, 80,  80),
    "📧": (100, 180, 255),
    "📋": (255, 200,  60),
    "💾": (255, 140,  50),
    "📞": (200, 100, 220),
    "💻": (100, 200, 255),
    "🚨": (255, 60,  60),
}


class DialogBox:
    BOX_HEIGHT     = 148   # minimum box height; grows dynamically
    PAD            = 14
    BORDER_W       = 3
    TEXT_SPEED     = 1.8   # chars per frame
    MSG_MARGIN_BOT = 25    # guaranteed gap between last text line and choices

    def __init__(self, screen_w: int, screen_h: int):
        self.sw = screen_w
        self.sh = screen_h
        self.active      = False
        self.lines: list[str] = []
        self.choices: list[str] = []
        self.choice_idx  = 0
        self.speaker     = ""
        self._revealed   = 0.0
        self._all_shown  = False
        self._font       = None
        self._small      = None
        self._on_choice  = None
        self._on_done    = None
        self._tick       = 0

    def set_fonts(self, font, small):
        self._font  = font
        self._small = small

    # ── Public ───────────────────────────────────────────────────────────────

    def show(self, speaker: str, lines: list[str], choices=None,
             on_choice=None, on_done=None):
        self.speaker     = speaker
        self.lines       = [l for line in lines for l in self._wrap(line, 68)]
        self.choices     = choices or []
        self.choice_idx  = 0
        self._revealed   = 0.0
        self._all_shown  = False
        self._on_choice  = on_choice
        self._on_done    = on_done
        self.active      = True
        self._tick       = 0

    def close(self):
        self.active  = False
        self.choices = []

    # ── Input ────────────────────────────────────────────────────────────────

    def handle_key(self, key: int) -> bool:
        if not self.active:
            return False
        if not self._all_shown:
            total = sum(len(l) + 1 for l in self.lines)
            self._revealed  = float(total)
            self._all_shown = True
            return True
        if self.choices:
            if key in (pygame.K_UP, pygame.K_w):
                self.choice_idx = (self.choice_idx - 1) % len(self.choices)
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.choice_idx = (self.choice_idx + 1) % len(self.choices)
            elif key in (pygame.K_RETURN, pygame.K_e):
                choice = self.choices[self.choice_idx]
                self.close()
                if self._on_choice:
                    self._on_choice(choice)
            return True
        else:
            if key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                self.close()
                if self._on_done:
                    self._on_done()
            return True

    # ── Update ───────────────────────────────────────────────────────────────

    def update(self):
        if not self.active or self._all_shown:
            return
        self._tick    += 1
        total          = sum(len(l) + 1 for l in self.lines)
        self._revealed = min(self._revealed + self.TEXT_SPEED, float(total))
        if self._revealed >= total:
            self._all_shown = True

    # ── Draw ─────────────────────────────────────────────────────────────────

    def draw(self, screen: pygame.Surface):
        if not self.active:
            return

        t  = pygame.time.get_ticks()
        bx = 8
        bw = self.sw - 16

        line_h = self._font.get_height() + 3   # height of one text row

        # ── Pre-compute region heights ────────────────────────────────────────
        # CHOICES BLOCK (bottom region) – fixed size, computed first
        choice_block_h = 0
        if self.choices:
            choice_block_h = (len(self.choices) * (self._font.get_height() + 8)
                              + self.PAD + self.MSG_MARGIN_BOT)

        # MESSAGE BLOCK (top region) – how many lines fit in the default box?
        msg_lines_h = len(self.lines) * line_h + self.PAD * 2

        # Total box height: at least BOX_HEIGHT, grows if content needs it
        bh = max(self.BOX_HEIGHT, msg_lines_h + choice_block_h)

        by = self.sh - bh - 8   # box top-left Y, anchored to bottom of screen

        # ── Drop shadow ──
        shd = pygame.Surface((bw + 6, bh + 6), pygame.SRCALPHA)
        shd.fill((0, 0, 0, 100))
        screen.blit(shd, (bx + 4, by + 4))

        # ── Background ──
        bg = pygame.Surface((bw, bh), pygame.SRCALPHA)
        bg.fill((10, 8, 30, 240))
        screen.blit(bg, (bx, by))

        # ── Scanlines (retro RPG feel) ──
        for scan_y in range(0, bh, 4):
            scan_line = pygame.Surface((bw, 1), pygame.SRCALPHA)
            scan_line.fill((0, 0, 0, 25))
            screen.blit(scan_line, (bx, by + scan_y))

        # ── Outer border + glow ──
        pygame.draw.rect(screen, DIALOG_BORDER, (bx, by, bw, bh), self.BORDER_W, border_radius=8)
        pygame.draw.rect(screen, (*DIALOG_BORDER[:3], 60), (bx - 2, by - 2, bw + 4, bh + 4), 1, border_radius=10)
        # Inner thin line
        pygame.draw.rect(screen, (*DIALOG_BORDER[:3], 80), (bx + 4, by + 4, bw - 8, bh - 8), 1, border_radius=6)

        # ── Speaker name tag ──
        spk_color = WHITE
        for prefix, col in SPEAKER_COLORS.items():
            if self.speaker.startswith(prefix):
                spk_color = col
                break

        if self.speaker:
            tag_w = len(self.speaker) * 9 + 20
            tag_w = max(tag_w, 60)
            pygame.draw.rect(screen, (10, 8, 30),  (bx, by - 26, tag_w, 26), border_radius=4)
            pygame.draw.rect(screen, spk_color,    (bx, by - 26, tag_w, 26), 2,  border_radius=4)
            spk_lbl = self._font.render(self.speaker, True, spk_color)
            screen.blit(spk_lbl, (bx + 10, by - 22))

        # ── MESSAGE REGION: top of box ─────────────────────────────────────────
        # Hard ceiling: text must not enter the choices block.
        msg_region_bottom = by + bh - choice_block_h  # absolute Y where choices begin
        text_clip = pygame.Rect(bx, by, bw, msg_region_bottom - by)
        old_clip  = screen.get_clip()
        screen.set_clip(text_clip)          # clip rendering to message area

        chars_left = int(self._revealed)
        text_x = bx + self.PAD
        text_y = by + self.PAD

        for line in self.lines:
            if chars_left <= 0:
                break
            visible = line[:chars_left]
            chars_left -= len(line) + 1
            rendered = self._font.render(visible, True, DIALOG_TEXT)
            screen.blit(rendered, (text_x, text_y))
            text_y += line_h

        screen.set_clip(old_clip)           # restore clip

        # text_y now holds the Y position just after the last rendered line
        text_end_y = text_y  # used to anchor choices dynamically

        # ── CHOICES REGION: anchored to text_end_y + margin ────────────────────
        if self.choices and self._all_shown:
            # choice_y is always below the last text line with a guaranteed gap
            menu_y = max(
                text_end_y + self.MSG_MARGIN_BOT,
                msg_region_bottom + self.PAD        # never inside message region
            )

            # Divider line between message and choices
            pygame.draw.line(screen, (*DIALOG_BORDER, 120),
                             (bx + self.PAD, menu_y - 8),
                             (bx + bw - self.PAD, menu_y - 8), 1)

            for i, choice in enumerate(self.choices):
                cy = menu_y + i * (self._font.get_height() + 8)
                is_sel = (i == self.choice_idx)

                if is_sel:
                    # Animated highlight
                    hl_alpha = int(180 + 40 * math.sin(t / 150))
                    hl = pygame.Surface((bw - self.PAD * 2, self._font.get_height() + 6), pygame.SRCALPHA)
                    hl.fill((*CHOICE_HL, hl_alpha))
                    screen.blit(hl, (bx + self.PAD - 4, cy - 2))
                    pygame.draw.rect(screen, (*UI_GOLD, 200),
                                     (bx + self.PAD - 4, cy - 2, bw - self.PAD * 2, self._font.get_height() + 6),
                                     1, border_radius=4)
                    arrow = self._font.render("▶", True, UI_GOLD)
                    screen.blit(arrow, (bx + self.PAD - 14, cy))

                color = WHITE if is_sel else (160, 160, 190)
                lbl   = self._font.render(choice, True, color)
                screen.blit(lbl, (bx + self.PAD, cy))

        # ── Continue indicator (no choices) ──
        elif self._all_shown:
            bob = int(3 * math.sin(t / 200))
            arrow = self._font.render("▼", True, UI_GOLD)
            screen.blit(arrow, (bx + bw - 22, by + bh - 22 + bob))

        # ── Hint ──
        if not self.choices and not self._all_shown:
            hint = self._small.render("(Space / E to skip)", True, (80, 80, 120))
            screen.blit(hint, (bx + bw - hint.get_width() - 8, by + bh - 18))

    # ── Helper ───────────────────────────────────────────────────────────────

    @staticmethod
    def _wrap(text: str, max_chars: int) -> list[str]:
        if len(text) <= max_chars:
            return [text]
        words  = text.split()
        lines  = []
        cur    = ""
        for w in words:
            if len(cur) + len(w) + 1 <= max_chars:
                cur = (cur + " " + w).strip()
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines if lines else [text]

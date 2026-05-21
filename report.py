"""
PHISHVERSE – report.py
Full-screen Cyber Resilience Report shown at end of game.
Inspired by Pokémon end-of-game summary screens.
"""

import pygame
import math
from constants import *


RISK_COLORS = {
    "LOW":    (80, 220, 120),
    "MEDIUM": (255, 190,  50),
    "HIGH":   (230,  70,  70),
}


class CyberResilienceReport:
    """
    Renders the final CYBER RESILIENCE REPORT screen.
    Animated entry, score reveal, bias bars, and recommendation card.
    """

    def __init__(self, screen_w: int, screen_h: int):
        self.sw = screen_w
        self.sh = screen_h
        self._font  = None
        self._big   = None
        self._small = None
        self._timer  = 0
        self._done   = False
        self._data: dict = {}

    def set_fonts(self, font, big, small):
        self._font  = font
        self._big   = big
        self._small = small

    def set_data(self, data: dict):
        self._data  = data
        self._timer = 0
        self._done  = False

    def handle_key(self, key: int) -> bool:
        """Returns True when user dismisses the report (Q / Esc)."""
        if key in (pygame.K_q, pygame.K_ESCAPE, pygame.K_RETURN):
            self._done = True
            return True
        return False

    @property
    def done(self) -> bool:
        return self._done

    def update(self):
        self._timer += 1

    def draw(self, screen: pygame.Surface):
        t = self._timer

        # ── Animated background ──────────────────────────────────────────────
        for y in range(self.sh):
            shade = int(8 + 6 * math.sin(t / 80 + y / 100))
            pygame.draw.line(screen, (shade, shade, shade + 20), (0, y), (self.sw, y))

        # ── Header panel ────────────────────────────────────────────────────
        header_h = 70
        hdr = pygame.Surface((self.sw, header_h), pygame.SRCALPHA)
        hdr.fill((20, 20, 50, 230))
        screen.blit(hdr, (0, 0))
        pygame.draw.line(screen, UI_BORDER, (0, header_h), (self.sw, header_h), 2)

        title = self._big.render("CYBER RESILIENCE REPORT", True, UI_GOLD)
        screen.blit(title, (self.sw // 2 - title.get_width() // 2, 18))

        d = self._data
        risk_level = d.get("risk_level", "MEDIUM")
        risk_color = RISK_COLORS.get(risk_level, WHITE)

        # ── Score circle ─────────────────────────────────────────────────────
        cx, cy = 130, 200
        score = d.get("score", 0)
        # Background ring
        pygame.draw.circle(screen, (40, 40, 60), (cx, cy), 70, 6)
        # Score arc (approximate with filled circle + inner circle)
        fill_r = max(0, min(1.0, score / 100))
        arc_color = RISK_COLORS.get(risk_level, WHITE)
        arc_surf = pygame.Surface((160, 160), pygame.SRCALPHA)
        pygame.draw.circle(arc_surf, (*arc_color, 200), (80, 80), 70, 10)
        # Mask out the arc portion we don't want (simple approach: overlay angle)
        pygame.draw.circle(arc_surf, (0, 0, 0, 255), (80, 80), 56)  # inner hole
        screen.blit(arc_surf, (cx - 80, cy - 80))

        # Score number
        score_lbl  = self._big.render(f"{score}", True, arc_color)
        score_sub  = self._small.render("/ 100", True, LIGHT_GREY)
        screen.blit(score_lbl,  (cx - score_lbl.get_width() // 2,  cy - 18))
        screen.blit(score_sub,  (cx - score_sub.get_width() // 2,  cy + 16))
        risk_surf = self._font.render(risk_level, True, arc_color)
        screen.blit(risk_surf, (cx - risk_surf.get_width() // 2, cy + 36))

        # ── Stats column ─────────────────────────────────────────────────────
        sx, sy = 240, 100
        stats = [
            ("Threats Survived",  f"{d.get('successful_reports',0)} / {d.get('total_threats',6)}"),
            ("Mistakes Made",     str(d.get("mistakes", 0))),
            ("Reports Filed",     str(d.get("successful_reports", 0))),
        ]
        for i, (label, value) in enumerate(stats):
            yl = sy + i * 42
            pygame.draw.rect(screen, (30, 30, 55), (sx, yl, 300, 34), border_radius=6)
            pygame.draw.rect(screen, UI_BORDER,   (sx, yl, 300, 34), 1, border_radius=6)
            ll = self._small.render(label, True, LIGHT_GREY)
            vl = self._font.render(value, True, UI_HIGHLIGHT)
            screen.blit(ll, (sx + 10, yl + 5))
            screen.blit(vl, (sx + 290 - vl.get_width(), yl + 7))

        # ── Bias bars ────────────────────────────────────────────────────────
        bx, by = 240, 242
        biases = [
            ("Urgency Bias",    d.get("urgency_bias",   0), (230,  80,  80)),
            ("Authority Bias",  d.get("authority_bias", 0), (200, 100,  60)),
            ("Reward Bias",     d.get("reward_bias",    0), (60,  160, 220)),
            ("Fear Bias",       d.get("fear_bias",      0), (180,  60, 200)),
        ]
        bw_max = 300
        for i, (label, val, color) in enumerate(biases):
            yl = by + i * 36
            ll = self._small.render(f"{label}:", True, LIGHT_GREY)
            screen.blit(ll, (bx, yl))
            bar_y = yl + 16
            pygame.draw.rect(screen, (40, 40, 60), (bx, bar_y, bw_max, 12), border_radius=6)
            fill = int(bw_max * min(val / 50, 1.0))
            anim_fill = min(fill, int(bw_max * min(t / 120, 1.0)))  # animate in
            if anim_fill > 0:
                pygame.draw.rect(screen, color, (bx, bar_y, anim_fill, 12), border_radius=6)
            pygame.draw.rect(screen, UI_BORDER, (bx, bar_y, bw_max, 12), 1, border_radius=6)
            vl = self._small.render(str(val), True, color)
            screen.blit(vl, (bx + bw_max + 6, bar_y - 2))

        # ── Weakest area ─────────────────────────────────────────────────────
        wx, wy = 570, 100
        ww, wh = 210, 140
        pygame.draw.rect(screen, (40, 20, 20), (wx, wy, ww, wh), border_radius=8)
        pygame.draw.rect(screen, UI_WARNING,   (wx, wy, ww, wh), 2, border_radius=8)
        wt = self._small.render("WEAKEST AREA", True, UI_WARNING)
        screen.blit(wt, (wx + ww // 2 - wt.get_width() // 2, wy + 10))
        wa = d.get("weakest_area", "N/A")
        # word-wrap weakest area
        words = wa.split()
        line1 = " ".join(words[:2])
        line2 = " ".join(words[2:]) if len(words) > 2 else ""
        wl1 = self._font.render(line1, True, WHITE)
        screen.blit(wl1, (wx + ww // 2 - wl1.get_width() // 2, wy + 38))
        if line2:
            wl2 = self._font.render(line2, True, WHITE)
            screen.blit(wl2, (wx + ww // 2 - wl2.get_width() // 2, wy + 62))

        # ── Recommendation card ───────────────────────────────────────────────
        rx, ry = 570, 260
        rw, rh = 210, 100
        pygame.draw.rect(screen, (20, 40, 20), (rx, ry, rw, rh), border_radius=8)
        pygame.draw.rect(screen, UI_HIGHLIGHT, (rx, ry, rw, rh), 2, border_radius=8)
        rt = self._small.render("RECOMMENDATION", True, UI_HIGHLIGHT)
        screen.blit(rt, (rx + rw // 2 - rt.get_width() // 2, ry + 8))
        rec = d.get("recommendation", "")
        # Word-wrap recommendation into ~25 chars per line
        rec_lines = self._wrap(rec, 22)
        for j, rl in enumerate(rec_lines[:3]):
            rs = self._small.render(rl, True, LIGHT_GREY)
            screen.blit(rs, (rx + 8, ry + 30 + j * 20))

        # ── Divider ──────────────────────────────────────────────────────────
        pygame.draw.line(screen, UI_BORDER, (30, 390), (self.sw - 30, 390), 1)

        # ── Bias tag history ─────────────────────────────────────────────────
        tag_label = self._small.render("ATTACK VECTORS ENCOUNTERED:", True, LIGHT_GREY)
        screen.blit(tag_label, (30, 402))

        tags = ["Urgency Manipulation", "QR Phishing", "USB Drop", "Authority Phishing", "Vishing", "BEC Fraud"]
        tag_x = 30
        for tag in tags:
            tg = self._small.render(f"  {tag}  ", True, BLACK)
            tw = tg.get_width() + 2
            pygame.draw.rect(screen, UI_BORDER, (tag_x - 1, 424, tw + 2, 22), border_radius=4)
            pygame.draw.rect(screen, (50, 80, 180), (tag_x, 425, tw, 20), border_radius=4)
            screen.blit(tg, (tag_x, 426))
            tag_x += tw + 8
            if tag_x > self.sw - 120:
                tag_x = 30

        # ── Certificate banner ───────────────────────────────────────────────
        cert_y = 460
        cert = pygame.Surface((self.sw - 60, 80), pygame.SRCALPHA)
        cert.fill((20, 40, 20, 200))
        screen.blit(cert, (30, cert_y))
        pygame.draw.rect(screen, UI_HIGHLIGHT, (30, cert_y, self.sw - 60, 80), 2, border_radius=8)
        ct1 = self._font.render("🏅  PHISHVERSE CYBER AWARENESS CERTIFICATE", True, UI_GOLD)
        ct2 = self._small.render(f"This player demonstrated {risk_level} risk resilience.  Score: {score}/100", True, LIGHT_GREY)
        screen.blit(ct1, (self.sw // 2 - ct1.get_width() // 2, cert_y + 10))
        screen.blit(ct2, (self.sw // 2 - ct2.get_width() // 2, cert_y + 42))

        # ── Dismiss hint ─────────────────────────────────────────────────────
        if (t // 30) % 2 == 0:
            hint = self._small.render("Press ENTER or ESC to quit", True, MID_GREY)
            screen.blit(hint, (self.sw // 2 - hint.get_width() // 2, self.sh - 20))

    # ── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _wrap(text: str, max_chars: int) -> list[str]:
        words = text.split()
        lines = []
        current = ""
        for word in words:
            if len(current) + len(word) + 1 <= max_chars:
                current = (current + " " + word).strip()
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

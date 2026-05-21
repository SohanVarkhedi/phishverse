"""
PHISHVERSE – npc.py
Improved NPCs with detailed sprites, idle wander animation,
speech bubbles, and cybersecurity hint dialogue.
"""

import pygame
import math
import random
from constants import *


# ── Act-aware NPC dialogue pools ─────────────────────────────────────────────
# Each inner list maps to one NPC slot (7 total, matching NPC_NAMES length).
# Index 0 = Alex, 1 = Jamie, …, 6 = Jordan — consistent per build_npcs() call.

NPC_ACT_DIALOGS: dict[int, list[list[str]]] = {
    # Act 1 — Friendly onboarding, welcoming the new intern
    1: [
        ["Hi! It's your first day — exciting, right?",
         "I'll show you the ropes. Ask me anything!"],
        ["Welcome aboard! Security training starts soon.",
         "Always lock your screen when you step away."],
        ["Great to have a new face here.",
         "Our IT team is top notch — always available."],
        ["If you get lost, the manager is near reception.",
         "Don't be shy — everyone's friendly here."],
        ["We take data protection very seriously.",
         "Even small lapses can cost the whole company."],
        ["The coffee machine is in the cafeteria — lifesaver!",
         "Pro tip: lock your screen before every break."],
        ["Nice to meet you! I'm Jordan from Finance.",
         "Our department handles all the wire transfers."],
    ],

    # Act 2 — Coworkers start noticing strange activity
    2: [
        ["Finance got phishing emails this morning!",
         "Never click links from unknown senders."],
        ["Did you see that QR code in the cafeteria?",
         "It's not from HR — I already checked."],
        ["HR messages look suspicious lately.",
         "Always verify the sender domain first."],
        ["That USB on the floor is NOT ours.",
         "Never plug in unknown devices — ever!"],
        ["IT NEVER asks for OTPs by phone.",
         "Hang up immediately on suspicious callers."],
        ["Urgent emails want you to panic and click.",
         "Take a breath. Slow down. Verify first."],
        ["CEO wire transfer requests? Massive red flag!",
         "Always call the CEO directly to verify."],
    ],

    # Act 3 — Cyber alert, everyone is on edge
    3: [
        ["The office is on full CYBER ALERT right now.",
         "Report EVERYTHING suspicious immediately."],
        ["Don't share OTPs with ANYONE — not even 'IT'.",
         "Legitimate staff will never ask for them."],
        ["Someone fell for a vishing call earlier.",
         "The attackers are posing as our IT team."],
        ["I've locked all my screens and logged out.",
         "You should do the same — right now."],
        ["Security says this attack is still active.",
         "They're targeting multiple departments."],
        ["Don't click, don't scan, don't share anything.",
         "Verify everything in person if you must."],
        ["This feels coordinated and professional.",
         "Stay calm — but stay sharp."],
    ],

    # Act 4 — CEO crisis, maximum tension
    4: [
        ["Something huge is happening in the Meeting Room.",
         "I've never seen security this tense before."],
        ["A fake CEO email went out to the finance team.",
         "Do NOT engage with it under any circumstances."],
        ["This is the most sophisticated attack I've seen.",
         "Social engineering at the executive level."],
        ["Whatever you do in that meeting room — think twice.",
         "The whole company is watching this decision."],
        ["The real CEO confirmed: they sent nothing.",
         "The domain was spoofed — almost identical to ours."],
        ["Our company's future depends on someone catching this.",
         "I'm glad someone like you is on this."],
        ["You've come this far — trust your training.",
         "One correct decision can save everything."],
    ],
}

NPC_NAMES  = ["Alex", "Jamie", "Sam", "Riley", "Morgan", "Casey", "Jordan"]
SKIN_TONES = [(240,190,150),(200,150,110),(160,110,80),(100,70,40)]

# (shirt_color, pants_color, hair_color)
NPC_OUTFITS = [
    ((200,  60,  60), (50, 50, 100), (60, 35, 15)),
    (( 60, 160,  80), (80, 60,  40), (20, 20,  20)),
    ((180, 100,  40), (40, 40,  90), (80, 50,  10)),
    ((100,  60, 180), (60, 50,  80), (40, 20,   5)),
    (( 40, 160, 200), (50, 50,  80), (30, 20,  10)),
    ((200, 180,  40), (50, 50, 100), (20, 20,  20)),
    ((160, 160, 160), (60, 60,  60), (100, 60, 20)),
]


class NPC:
    def __init__(self, tile_x: int, tile_y: int, style_idx: int, dialog_idx: int):
        self.tile_x    = tile_x
        self.tile_y    = tile_y
        self.px        = tile_x * TILE_SIZE
        self.py        = tile_y * TILE_SIZE
        si             = style_idx % len(NPC_OUTFITS)
        self.shirt, self.pants, self.hair_c = NPC_OUTFITS[si]
        self.skin      = SKIN_TONES[style_idx % len(SKIN_TONES)]
        self.name      = NPC_NAMES[dialog_idx % len(NPC_NAMES)]
        self._dialog_idx = dialog_idx % len(NPC_NAMES)   # which slot in the pool
        self._current_act = 1
        self.direction = random.choice(["down", "left", "right"])

        # Idle animation
        self._timer    = random.randint(0, 120)
        self._bob      = 0.0
        self._look_timer = random.randint(60, 200)

        # Speech bubble hint
        self._hint_timer = 0
        self._hint_visible = False

        self._sprites = self._build_sprites()
        self._shadow  = self._make_shadow()

    def _make_shadow(self):
        s = pygame.Surface((TILE_SIZE, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (0, 0, 0, 50), (4, 1, TILE_SIZE - 8, 6))
        return s

    def _build_sprites(self):
        frames = {}
        for direction in ("down", "left", "right", "up"):
            frames[direction] = [self._draw_frame(direction, f) for f in range(2)]
        return frames

    def _draw_frame(self, direction: str, frame: int) -> pygame.Surface:
        s = TILE_SIZE
        surf = pygame.Surface((s, s), pygame.SRCALPHA)
        cx = s // 2
        bob = frame * 1

        # Shoes
        pygame.draw.ellipse(surf, (30, 30, 30), (cx - 7, 27 + bob, 7, 4))
        pygame.draw.ellipse(surf, (30, 30, 30), (cx + 1, 27 - bob, 7, 4))
        # Pants
        pygame.draw.rect(surf, self.pants, (cx - 6, 18, 5, 10 + bob))
        pygame.draw.rect(surf, self.pants, (cx + 1, 18, 5, 10 - bob))
        # Body
        pygame.draw.rect(surf, self.shirt, (cx - 7, 8, 14, 12))
        # Arms
        pygame.draw.rect(surf, self.skin,  (cx - 10, 10, 3, 7 + bob))
        pygame.draw.rect(surf, self.skin,  (cx +  7, 10, 3, 7 - bob))
        # Head
        pygame.draw.ellipse(surf, self.skin,   (cx - 5, 0, 10, 10))
        pygame.draw.ellipse(surf, self.hair_c, (cx - 5, 0, 10, 6))
        pygame.draw.rect(surf,    self.hair_c, (cx - 5, 0, 10, 3))
        # Face
        if direction == "down":
            pygame.draw.rect(surf, (40, 20, 0), (cx - 3, 5, 2, 2))
            pygame.draw.rect(surf, (40, 20, 0), (cx + 1, 5, 2, 2))
        elif direction == "right":
            pygame.draw.rect(surf, (40, 20, 0), (cx + 1, 5, 2, 2))
        elif direction == "left":
            pygame.draw.rect(surf, (40, 20, 0), (cx - 3, 5, 2, 2))
        return surf

    # ── Act-aware dialogue ───────────────────────────────────────────────────

    def set_act(self, act: int):
        """Switch NPC to dialogue lines for the given act (1-4)."""
        self._current_act = max(1, min(4, act))

    def get_dialog(self) -> list[str]:
        """Return the current-act dialogue lines for this NPC."""
        pool = NPC_ACT_DIALOGS.get(self._current_act, NPC_ACT_DIALOGS[1])
        return pool[self._dialog_idx % len(pool)]

    # Keep legacy .dialog property so any existing code still works
    @property
    def dialog(self) -> list[str]:
        return self.get_dialog()

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def update(self):
        self._timer += 1
        self._bob = math.sin(self._timer / 20) * 1.5

        # Occasionally change look direction
        self._look_timer -= 1
        if self._look_timer <= 0:
            self.direction = random.choice(["down", "left", "right"])
            self._look_timer = random.randint(80, 240)

        # Hint bubble timer
        if self._hint_visible:
            self._hint_timer -= 1
            if self._hint_timer <= 0:
                self._hint_visible = False

    def show_hint(self):
        self._hint_visible = True
        self._hint_timer = 180

    def draw(self, screen: pygame.Surface, cam_x: int, cam_y: int):
        sx = self.px - cam_x
        sy = self.py - cam_y + int(self._bob)
        screen.blit(self._shadow, (sx + 4, sy + TILE_SIZE - 6))
        frame = (self._timer // 20) % 2
        screen.blit(self._sprites[self.direction][frame], (sx, sy))

    def draw_label(self, screen: pygame.Surface, cam_x: int, cam_y: int,
                   font: pygame.font.Font, small: pygame.font.Font):
        sx = self.px - cam_x + TILE_SIZE // 2
        sy = self.py - cam_y

        # Name tag
        lbl = font.render(self.name, True, UI_GOLD)
        bx  = sx - lbl.get_width() // 2 - 4
        bg  = pygame.Surface((lbl.get_width() + 8, lbl.get_height() + 4), pygame.SRCALPHA)
        bg.fill((20, 20, 50, 180))
        screen.blit(bg,  (bx, sy - 18))
        screen.blit(lbl, (sx - lbl.get_width() // 2, sy - 16))

        # Speech bubble hint
        if self._hint_visible and self._hint_timer > 0:
            alpha = min(255, self._hint_timer * 4)
            hint_lines = self.dialog
            bubble_w = max(len(l) for l in hint_lines) * 7 + 16
            bubble_h = len(hint_lines) * 14 + 10
            bub = pygame.Surface((bubble_w, bubble_h), pygame.SRCALPHA)
            bub.fill((255, 255, 220, min(220, alpha)))
            pygame.draw.rect(bub, (180, 160, 80, alpha), (0, 0, bubble_w, bubble_h), 2, border_radius=6)
            # Triangle tail
            pygame.draw.polygon(bub, (255, 255, 220, alpha),
                                 [(bubble_w // 2 - 4, bubble_h),
                                  (bubble_w // 2 + 4, bubble_h),
                                  (bubble_w // 2,     bubble_h + 6)])
            screen.blit(bub, (sx - bubble_w // 2, sy - bubble_h - 24))
            for i, line in enumerate(hint_lines):
                tl = small.render(line, True, (40, 30, 0))
                screen.blit(tl, (sx - bubble_w // 2 + 8, sy - bubble_h - 24 + 6 + i * 14))


def build_npcs() -> list[NPC]:
    return [
        # Reception
        NPC(6,  6, 0, 0),
        NPC(28, 6, 1, 1),
        # Work area
        NPC(3,  12, 2, 2),
        NPC(10, 15, 3, 3),
        NPC(16, 11, 4, 4),
        # HR room
        NPC(25, 12, 5, 2),
        NPC(33, 15, 6, 5),
        # Cafeteria
        NPC(4,  21, 0, 1),
        NPC(11, 21, 1, 3),
        # Meeting room
        NPC(26, 20, 2, 4),
        NPC(35, 20, 3, 6),
        # IT support
        NPC(8,  25, 4, 5),
        NPC(20, 25, 5, 6),
        NPC(32, 25, 6, 0),
    ]

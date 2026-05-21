"""
PHISHVERSE – player.py
Enhanced player with detailed pixel-art sprite, 4-frame walk animation,
shadow, and smooth tile-based movement.
"""

import pygame
import math
from constants import *


class Player:
    DIRECTIONS = {
        pygame.K_UP:    (0, -1, "up"),
        pygame.K_DOWN:  (0,  1, "down"),
        pygame.K_LEFT:  (-1, 0, "left"),
        pygame.K_RIGHT: (1,  0, "right"),
        pygame.K_w:     (0, -1, "up"),
        pygame.K_s:     (0,  1, "down"),
        pygame.K_a:     (-1, 0, "left"),
        pygame.K_d:     (1,  0, "right"),
    }

    def __init__(self, tile_x: int, tile_y: int):
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.px = tile_x * TILE_SIZE
        self.py = tile_y * TILE_SIZE
        self.direction = "down"
        self.moving = False
        self.move_progress = 0
        self.target_px = self.px
        self.target_py = self.py
        self.walk_frame = 0
        self.walk_timer = 0
        # Footstep particles
        self.particles: list[dict] = []
        self._sprites = self._build_all_sprites()
        # Shadow surface
        self._shadow = self._make_shadow()
        # Reusable particle surface — avoids allocating per-particle per frame
        self._particle_surf = pygame.Surface((4, 4), pygame.SRCALPHA)

    # ── Sprites ─────────────────────────────────────────────────────────────

    def _make_shadow(self) -> pygame.Surface:
        s = pygame.Surface((TILE_SIZE, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (0, 0, 0, 60), (4, 1, TILE_SIZE - 8, 6))
        return s

    def _build_all_sprites(self) -> dict:
        sprites = {}
        for direction in ("up", "down", "left", "right"):
            sprites[direction] = [self._draw_frame(direction, f) for f in range(4)]
        return sprites

    def _draw_frame(self, direction: str, frame: int) -> pygame.Surface:
        s = TILE_SIZE
        surf = pygame.Surface((s, s), pygame.SRCALPHA)
        # walk bob
        bob = int(math.sin(frame * math.pi / 2) * 2) if frame % 2 == 1 else 0
        base_y = 2 - bob

        skin   = (240, 190, 150)
        hair   = (60,  35,  15)
        shirt  = (60, 120, 200)
        pants  = (30,  30, 100)
        shoes  = (30,  30,  30)
        hl     = (100, 160, 230)   # shirt highlight

        # leg swing: alternate legs each frame
        leg_l = int(math.sin(frame * math.pi / 2) * 4)
        leg_r = -leg_l

        cx = s // 2

        # ── Shoes ──
        if direction != "up":
            pygame.draw.ellipse(surf, shoes, (cx - 7, base_y + 26 + leg_l, 7, 4))
            pygame.draw.ellipse(surf, shoes, (cx + 1, base_y + 26 + leg_r, 7, 4))
        else:
            pygame.draw.ellipse(surf, shoes, (cx - 7, base_y + 26 - leg_l, 7, 4))
            pygame.draw.ellipse(surf, shoes, (cx + 1, base_y + 26 - leg_r, 7, 4))

        # ── Legs (pants) ──
        pygame.draw.rect(surf, pants, (cx - 6, base_y + 18, 5, 10 + leg_l))
        pygame.draw.rect(surf, pants, (cx + 1, base_y + 18, 5, 10 + leg_r))

        # ── Body (shirt) ──
        pygame.draw.rect(surf, shirt, (cx - 7, base_y + 8, 14, 12))
        # Shirt highlight
        pygame.draw.rect(surf, hl,    (cx - 5, base_y + 9,  4,  8))

        # ── Arms ──
        arm_l = int(math.sin(frame * math.pi / 2) * 3)
        arm_r = -arm_l
        if direction == "left":
            # Show extended left arm
            pygame.draw.rect(surf, skin, (cx - 10, base_y + 9,  3, 7 + arm_l))
            pygame.draw.rect(surf, skin, (cx +  7, base_y + 9,  3, 7 - arm_l))
        elif direction == "right":
            pygame.draw.rect(surf, skin, (cx - 10, base_y + 9,  3, 7 - arm_l))
            pygame.draw.rect(surf, skin, (cx +  7, base_y + 9,  3, 7 + arm_l))
        else:
            pygame.draw.rect(surf, skin, (cx - 10, base_y + 9,  3, 7 + arm_l))
            pygame.draw.rect(surf, skin, (cx +  7, base_y + 9,  3, 7 - arm_l))

        # ── Head ──
        head_rect = pygame.Rect(cx - 5, base_y, 10, 10)
        pygame.draw.ellipse(surf, skin, head_rect)
        # Hair
        pygame.draw.ellipse(surf, hair, (cx - 5, base_y,     10, 6))
        pygame.draw.rect(surf,    hair, (cx - 5, base_y,     10, 3))

        # ── Eyes / mouth based on direction ──
        if direction == "down":
            pygame.draw.rect(surf, (40, 20,  0), (cx - 3, base_y + 5, 2, 2))
            pygame.draw.rect(surf, (40, 20,  0), (cx + 1, base_y + 5, 2, 2))
            pygame.draw.rect(surf, (200, 80, 80), (cx - 2, base_y + 8, 4, 1))
        elif direction == "up":
            # Back of head – just hair
            pass
        elif direction == "right":
            pygame.draw.rect(surf, (40, 20,  0), (cx + 1, base_y + 5, 2, 2))
        else:  # left
            pygame.draw.rect(surf, (40, 20,  0), (cx - 3, base_y + 5, 2, 2))

        # ── Name badge (tiny yellow dot on shirt) ──
        pygame.draw.rect(surf, UI_GOLD, (cx - 1, base_y + 10, 3, 2))

        return surf

    # ── Movement ────────────────────────────────────────────────────────────

    def try_move(self, dx: int, dy: int, game_map) -> bool:
        if self.moving:
            return False
        new_tx = self.tile_x + dx
        new_ty = self.tile_y + dy
        if game_map.is_walkable(new_tx, new_ty):
            self.tile_x = new_tx
            self.tile_y = new_ty
            self.target_px = new_tx * TILE_SIZE
            self.target_py = new_ty * TILE_SIZE
            self.moving = True
            self.move_progress = 0
            return True
        return False

    def set_direction(self, dx: int, dy: int):
        if dy < 0:   self.direction = "up"
        elif dy > 0: self.direction = "down"
        elif dx < 0: self.direction = "left"
        elif dx > 0: self.direction = "right"

    def update(self):
        if self.moving:
            self.move_progress += MOVE_SPEED
            if self.px < self.target_px:
                self.px = min(self.px + MOVE_SPEED, self.target_px)
            elif self.px > self.target_px:
                self.px = max(self.px - MOVE_SPEED, self.target_px)
            if self.py < self.target_py:
                self.py = min(self.py + MOVE_SPEED, self.target_py)
            elif self.py > self.target_py:
                self.py = max(self.py - MOVE_SPEED, self.target_py)

            if self.px == self.target_px and self.py == self.target_py:
                self.moving = False
                self._emit_particle()

            self.walk_timer += 1
            if self.walk_timer >= 6:
                self.walk_timer = 0
                self.walk_frame = (self.walk_frame + 1) % 4
        else:
            self.walk_frame = 0

        # Update footstep particles
        self.particles = [p for p in self.particles if p["life"] > 0]
        for p in self.particles:
            p["life"]  -= 4
            p["y"]     -= 0.3
            p["alpha"]  = max(0, p["life"])

    def _emit_particle(self):
        import random
        for _ in range(3):
            self.particles.append({
                "x":    self.px + TILE_SIZE // 2 + random.randint(-6, 6),
                "y":    self.py + TILE_SIZE - 4 + random.randint(0, 4),
                "life": random.randint(60, 100),
                "alpha": 100,
                "r":    random.randint(180, 220),
            })

    def draw(self, screen: pygame.Surface, cx: int, cy: int):
        # Shadow
        screen.blit(self._shadow, (self.px - cx + 4, self.py - cy + TILE_SIZE - 6))
        # Footstep dust particles (reuse single surface)
        for p in self.particles:
            self._particle_surf.fill((p["r"], p["r"] - 20, 140, p["alpha"]))
            screen.blit(self._particle_surf, (p["x"] - cx, p["y"] - cy))
        # Player sprite
        screen.blit(self._sprites[self.direction][self.walk_frame],
                    (self.px - cx, self.py - cy))

    def facing_tile(self) -> tuple[int, int]:
        offsets = {"up": (0,-1), "down": (0,1), "left": (-1,0), "right": (1,0)}
        dx, dy = offsets[self.direction]
        return self.tile_x + dx, self.tile_y + dy

"""
PHISHVERSE 3D – player3d.py
First-person player: WASD move, Left/Right rotate, smooth collision.
"""

import math
from constants import MOVE_SPEED, ROT_SPEED, FOV


class Player3D:
    def __init__(self, x: float, y: float, angle: float = math.pi / 2):
        self.x     = x
        self.y     = y
        self.angle = angle        # radians; 0=east, π/2=south

        # Direction and camera plane derived from angle
        self._update_vectors()

        # View bob (cosmetic)
        self.bob_t   = 0.0
        self.bob_amp = 0.0

    # ── Derived vectors ──────────────────────────────────────────────────────

    def _update_vectors(self):
        self.dir_x   = math.cos(self.angle)
        self.dir_y   = math.sin(self.angle)
        self.plane_x = -math.sin(self.angle) * FOV
        self.plane_y =  math.cos(self.angle) * FOV

    # ── Input ─────────────────────────────────────────────────────────────────

    def update(self, keys, game_map, dt: float = 1.0):
        import pygame
        moved = False

        # Rotation
        if keys[pygame.K_LEFT]  or keys[pygame.K_q]:
            self.angle -= ROT_SPEED * dt
            moved = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_e]:
            self.angle += ROT_SPEED * dt
            moved = True
        self._update_vectors()

        # Forward / backward
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self._try_move(self.dir_x * MOVE_SPEED * dt,
                           self.dir_y * MOVE_SPEED * dt, game_map)
            moved = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self._try_move(-self.dir_x * MOVE_SPEED * dt,
                           -self.dir_y * MOVE_SPEED * dt, game_map)
            moved = True

        # Strafe
        if keys[pygame.K_a]:
            self._try_move(-self.dir_y * MOVE_SPEED * dt,
                            self.dir_x * MOVE_SPEED * dt, game_map)
            moved = True
        if keys[pygame.K_d]:
            self._try_move( self.dir_y * MOVE_SPEED * dt,
                           -self.dir_x * MOVE_SPEED * dt, game_map)
            moved = True

        # View bob
        if moved:
            self.bob_t   += 0.15 * dt
            self.bob_amp  = min(self.bob_amp + 0.04, 1.0)
        else:
            self.bob_amp  = max(self.bob_amp - 0.08, 0.0)

    def _try_move(self, dx: float, dy: float, game_map):
        margin = 0.25
        nx, ny = self.x + dx, self.y + dy
        if not game_map.is_solid(int(nx), int(self.y)) and \
           not game_map.is_solid(int(nx + margin * math.copysign(1, dx)), int(self.y)):
            self.x = nx
        if not game_map.is_solid(int(self.x), int(ny)) and \
           not game_map.is_solid(int(self.x), int(ny + margin * math.copysign(1, dy))):
            self.y = ny

    # ── View bob offset ──────────────────────────────────────────────────────

    @property
    def bob_offset(self) -> float:
        return math.sin(self.bob_t) * 4.0 * self.bob_amp

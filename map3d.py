"""
PHISHVERSE 3D – map3d.py
20×20 office map for raycasting.
0 = walkable space. 1-7 = wall types (different room colours).

Room layout:
  Row 0-3   : RECEPTION (entry lobby)
  Row 4-8   : WORK AREA (left) | HR ROOM (right)   [separated by wall col 10]
  Row 9-13  : CAFETERIA (left) | MEETING ROOM (right)
  Row 14-19 : IT SUPPORT (bottom)
"""

# Wall types
W  = 0   # walkable
R1 = 1   # Reception wall  (cream)
R2 = 2   # Work Area wall  (blue)
R3 = 3   # HR Room wall    (oak)
R4 = 4   # Cafeteria wall  (green)
R5 = 5   # Meeting Room    (red)
R6 = 6   # IT Support      (tech)
DF = 7   # Door frame      (gold)

GRID = [
    # col: 0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19
    [R1, R1, R1, R1, R1, R1, R1, R1, R1, R1, R1, R1, R1, R1, R1, R1, R1, R1, R1, R1],  # 0
    [R1,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W, R1],  # 1
    [R1,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W, R1],  # 2
    [R1,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W, R1],  # 3  ← player starts ~(10,2.5) facing +y
    [R1, R2, R2, DF,  W,  W,  W,  W, DF, R2, R1, R3, R3, DF,  W,  W,  W, DF, R3, R1],  # 4  wall+doors
    [R1, R2,  W,  W,  W,  W,  W,  W,  W, R2, R1, R3,  W,  W,  W,  W,  W,  W, R3, R1],  # 5
    [R1, R2,  W,  W,  W,  W,  W,  W,  W, R2, R1, R3,  W,  W,  W,  W,  W,  W, R3, R1],  # 6
    [R1, R2,  W,  W,  W,  W,  W,  W,  W, R2, R1, R3,  W,  W,  W,  W,  W,  W, R3, R1],  # 7
    [R1, R2, R2, DF,  W,  W,  W, DF, R2, R2, R1, R3, R3, DF,  W,  W, DF, R3, R3, R1],  # 8  wall+doors
    [R1,  W,  W,  W,  W,  W,  W,  W,  W,  W, R1,  W,  W,  W,  W,  W,  W,  W,  W, R1],  # 9  corridor
    [R1, R4, R4, DF,  W,  W,  W, DF, R4, R4, R1, R5, R5, DF,  W,  W, DF, R5, R5, R1],  # 10 wall+doors
    [R1, R4,  W,  W,  W,  W,  W,  W,  W, R4, R1, R5,  W,  W,  W,  W,  W,  W, R5, R1],  # 11
    [R1, R4,  W,  W,  W,  W,  W,  W,  W, R4, R1, R5,  W,  W,  W,  W,  W,  W, R5, R1],  # 12
    [R1, R4, R4, DF,  W,  W,  W, DF, R4, R4, R1, R5, R5, DF,  W,  W, DF, R5, R5, R1],  # 13 wall+doors
    [R1,  W,  W,  W,  W,  W,  W,  W,  W,  W, R1,  W,  W,  W,  W,  W,  W,  W,  W, R1],  # 14 corridor
    [R1, R6, R6, DF,  W,  W,  W,  W, DF, R6, R6, R6, DF,  W,  W,  W, DF, R6, R6, R1],  # 15 IT wall+doors
    [R1, R6,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W, R6, R1],  # 16
    [R1, R6,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W, R6, R1],  # 17
    [R1, R6,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W, R6, R1],  # 18
    [R1, R6, R6, R6, R6, R6, R6, R6, R6, R6, R6, R6, R6, R6, R6, R6, R6, R6, R6, R1],  # 19 bottom wall
]

MAP_W = len(GRID[0])
MAP_H = len(GRID)


def get_wall(tx: int, ty: int) -> int:
    if 0 <= ty < MAP_H and 0 <= tx < MAP_W:
        return GRID[ty][tx]
    return 1


def is_solid(tx: int, ty: int) -> bool:
    return get_wall(tx, ty) != 0


# ── Room label by position ────────────────────────────────────────────────────
def get_room(x: float, y: float) -> str:
    tx, ty = int(x), int(y)
    if ty <= 3:               return "RECEPTION"
    if 4 <= ty <= 8:
        return "WORK AREA" if tx < 10 else "HR ROOM"
    if ty == 9 or ty == 14:   return "CORRIDOR"
    if 10 <= ty <= 13:
        return "CAFETERIA" if tx < 10 else "MEETING ROOM"
    return "IT SUPPORT"


# ── Interactive objects (world pos, event_id, label) ─────────────────────────
OBJECTS = [
    # (world_x, world_y, event_id, icon, label)
    (4.5, 6.5,  "email_phishing", "💻", "COMPUTER"),
    (7.5, 6.5,  "email_phishing", "💻", "COMPUTER"),
    (4.5, 11.5, "qr_phishing",    "📋", "POSTER"),
    (7.5, 11.5, "usb_drop",       "💾", "USB DRIVE"),
    (14.5, 6.5, "hr_message",     "💻", "HR COMPUTER"),
    (15.5, 7.5, "voice_phishing", "📞", "PHONE"),
    (14.5, 11.5,"ceo_fraud",      "🚨", "CEO EMAIL"),
    (16.5, 11.5,"ceo_fraud",      "🚨", "TERMINAL"),
]

# ── NPC spawn points (world_x, world_y, name, dialog_idx) ────────────────────
NPCS = [
    (5.5,  2.0,  "Alex",   0),
    (14.5, 2.0,  "Jamie",  1),
    (3.5,  6.5,  "Sam",    2),
    (13.5, 6.5,  "Riley",  3),
    (3.5,  11.5, "Morgan", 4),
    (13.5, 11.5, "Casey",  5),
    (10.0, 16.5, "Drew",   6),
]

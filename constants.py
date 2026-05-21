"""
PHISHVERSE – constants.py  (2D top-down, clean rewrite)
"""

SCREEN_WIDTH  = 960
SCREEN_HEIGHT = 640
FPS           = 60
TITLE         = "PHISHVERSE — Cybersecurity Awareness RPG"

TILE_SIZE     = 40        # larger tiles = clearer visuals
MOVE_SPEED    = 5         # pixels per frame during step animation
WALK_FRAMES   = TILE_SIZE // MOVE_SPEED

# ── Colour palette ────────────────────────────────────────────────────────────
BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
DARK_GREY   = (30,  30,  40)
MID_GREY    = (90,  90, 100)
LIGHT_GREY  = (190, 190, 200)

# ── Room floor tints (used by tile renderer) ──────────────────────────────────
ROOM_TINTS = {
    "RECEPTION":    (230, 220, 205),
    "WORK AREA":    (210, 215, 230),
    "HR ROOM":      (225, 210, 200),
    "CAFETERIA":    (205, 225, 205),
    "MEETING ROOM": (225, 210, 225),
    "IT SUPPORT":   (205, 215, 230),
    "OUTSIDE":      (155, 175, 140),
}

# ── UI colours ────────────────────────────────────────────────────────────────
UI_BG       = (14,  14,  30)
UI_BORDER   = (80, 160, 255)
UI_TEXT     = (220, 220, 255)
UI_GOLD     = (255, 200,  50)
UI_HIGHLIGHT= (80, 210, 130)
UI_WARNING  = (235,  75,  75)

DIALOG_BG     = (10,   8,  25)
DIALOG_BORDER = (100, 180, 255)
DIALOG_TEXT   = (240, 240, 255)
CHOICE_HL     = (45,  95, 210)

# ── Game states ───────────────────────────────────────────────────────────────
STATE_TITLE   = "title"
STATE_EXPLORE = "explore"
STATE_DIALOG  = "dialog"
STATE_MENU    = "menu"
STATE_REPORT  = "report"

EVENT_FILE    = "data/events.json"
MAX_SCORE     = 100
MIN_SCORE     = 0

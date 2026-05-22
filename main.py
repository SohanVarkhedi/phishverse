"""
PHISHVERSE – main.py  (2D top-down RPG, clean rebuild)
Controls: WASD/Arrows = move,  E/Enter = interact,  ESC = pause
"""

import sys, math, random, pygame
from constants      import *
from player         import Player
from map            import GameMap
from npc            import NPC, build_npcs
from dialogue       import DialogBox
from event_manager  import EventManager
from events         import EventDatabase
from risk_engine    import RiskEngine
from ui             import HUD, PauseMenu, TitleScreen, CampaignSelectScreen, RegistrationScreen, DashboardScreen, LectureScreen, SemesterReportScreen, FinalExamScreen, CertificateScreen
from reporting.semester_report import SemesterReport
from exam.question_engine      import QuestionEngine
from exam.final_exam           import ExamEngine, Certificate
from training.lecture_engine import LectureEngine
from ai import run_ai_analysis
from report         import CyberResilienceReport
from tiles          import TILE_DOOR
from story          import StoryManager
from analytics.result_store  import ResultStore
from analytics.campaign_loader import CampaignLoader

# Objectives are now managed by StoryManager (story.py).
# This list is kept as a short fallback used only before StoryManager initialises.
_FALLBACK_OBJECTIVE = "Head inside — start your workday!"


# ── Score popup ───────────────────────────────────────────────────────────────
class Popup:
    def __init__(self, x, y, text, good):
        self.x, self.y = float(x), float(y)
        self.text, self.good = text, good
        self.life = 100

    def update(self):
        self.y   -= 0.9
        self.life -= 2

    @property
    def alive(self): return self.life > 0

    def draw(self, screen, font):
        col = (80, 220, 130) if self.good else (235, 75, 75)
        lbl = font.render(self.text, True, col)
        bg  = pygame.Surface((lbl.get_width()+14, lbl.get_height()+6), pygame.SRCALPHA)
        bg.fill((0, 0, 0, min(200, self.life*2)))
        screen.blit(bg,  (int(self.x)-7, int(self.y)-3))
        screen.blit(lbl, (int(self.x),   int(self.y)))


# ── Room flash ────────────────────────────────────────────────────────────────
class RoomFlash:
    DURATION = 50
    def __init__(self): self._t = 0; self._name = ""; self._active = False

    def trigger(self, name):
        self._name = name; self._t = self.DURATION; self._active = True

    def update(self):
        if self._active:
            self._t -= 1
            if self._t <= 0: self._active = False

    def draw(self, screen, font, sw, sh):
        if not self._active: return
        t = self._t
        mid = self.DURATION // 2
        a = int(255 * ((t - mid) / mid)) if t > mid else int(255 * (t / mid))
        a = max(0, min(255, a))
        if a < 20: return
        ov = pygame.Surface((sw, sh), pygame.SRCALPHA)
        ov.fill((0, 0, 18, min(160, a * 2)))
        screen.blit(ov, (0, 0))
        lbl = font.render(f"▶  {self._name}  ◀", True, UI_GOLD)
        screen.blit(lbl, (sw//2 - lbl.get_width()//2, sh//2 - lbl.get_height()//2))


class Game:
    START_TILE = (19, 2)

    def __init__(self, campaign=None, employee_id: str = ""):
        """
        campaign    – a Campaign object from analytics.campaign_loader, or None
                      for a free-play session (all events enabled).
        employee_id – used when saving the campaign result file.
        """
        self._campaign    = campaign
        self._employee_id = employee_id
        self._employee: dict = {}

        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock  = pygame.time.Clock()
        self.font, self.big, self.small = self._fonts()

        self.gmap   = GameMap()
        self.player = Player(*self.START_TILE)
        self.npcs   = build_npcs()

        self.risk   = RiskEngine()
        self.db     = EventDatabase()

        # Apply campaign event filter if a campaign is active
        if self._campaign is not None:
            self.db.set_enabled_events(self._campaign.enabled_events)

        self.dialog = DialogBox(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.dialog.set_fonts(self.font, self.small)

        self.ev_mgr = EventManager(self.db, self.dialog, self.risk)
        self.ev_mgr.set_game_end_callback(self._end_game)
        self.ev_mgr.set_score_callback(self._on_score)

        # Story progression
        self.story  = StoryManager()

        self.hud    = HUD(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.hud.set_fonts(self.font, self.big, self.small)
        self.hud.set_objective(self.story.get_current_objective())

        self.pause  = PauseMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.pause.set_fonts(self.font, self.big, self.small)

        self.title  = TitleScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.title.set_fonts(self.font, self.big, self.small)

        # Employee registration screen
        self.reg_screen = RegistrationScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.reg_screen.set_fonts(self.font, self.big, self.small)

        # Campaign selection screen — loads all campaigns from campaigns/
        self.camp_select = CampaignSelectScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.camp_select.set_fonts(self.font, self.big, self.small)
        self.camp_select.set_campaigns(CampaignLoader.load_all())

        self.report = CyberResilienceReport(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.report.set_fonts(self.font, self.big, self.small)

        self.dashboard = DashboardScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.dashboard.set_fonts(self.font, self.big, self.small)

        self.lecture_screen = LectureScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.lecture_screen.set_fonts(self.font, self.big, self.small)

        self.semester_screen = SemesterReportScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.semester_screen.set_fonts(self.font, self.big, self.small)

        self.final_exam_screen = FinalExamScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.final_exam_screen.set_fonts(self.font, self.big, self.small)

        self.cert_screen = CertificateScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.cert_screen.set_fonts(self.font, self.big, self.small)

        self.q_engine         = QuestionEngine()
        self._semester_report: dict = {}   # stored on game end for exam routing
        self._exam_attempt    = 1          # increments on retake

        self.state     = STATE_TITLE
        self._obj_idx  = 0
        self._prev_room = ""
        self._prev_act  = 1           # track last known act for NPC switch

        # Camera (smooth)
        self.cam_x = self.cam_y = 0.0
        self._dcx  = self._dcy  = 0      # draw camera (with shake)

        # Effects
        self._popups: list[Popup] = []
        self._flash_col = None
        self._flash_t   = 0
        self._shake_t   = 0
        self._shake_mag = 0
        self._room_flash = RoomFlash()
        self._interact_hint = ""

        # Pre-allocated surfaces — avoids constructing large SRCALPHA surfaces every frame
        self._flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._marker_glow = pygame.Surface((TILE_SIZE + 10, TILE_SIZE + 10), pygame.SRCALPHA)

        # Pre-rendered glyphs — avoids font.render() inside hot draw loops
        _bang = self.font.render("!", True, UI_GOLD)
        self._marker_badge_lbl = _bang
        self._marker_badge_off = _bang.get_width() // 2
        _bw, _bh = _bang.get_width() + 8, _bang.get_height() + 4
        self._marker_badge_bg = pygame.Surface((_bw, _bh), pygame.SRCALPHA)
        self._marker_badge_bg.fill((20, 15, 0, 200))
        pygame.draw.rect(self._marker_badge_bg, UI_GOLD, (0, 0, _bw, _bh), 1, border_radius=4)

        self._door_arrow = self.small.render("▼", True, (100, 255, 120))

    # ── Fonts ─────────────────────────────────────────────────────────────────
    def _fonts(self):
        try:
            fp = pygame.font.match_font("couriernew,courier,consolas,monospace")
            return pygame.font.Font(fp, 15), pygame.font.Font(fp, 24), pygame.font.Font(fp, 12)
        except Exception:
            return (pygame.font.SysFont("monospace", 15),
                    pygame.font.SysFont("monospace", 24),
                    pygame.font.SysFont("monospace", 12))

    # ── Callbacks ─────────────────────────────────────────────────────────────
    def _end_game(self):
        # Build employee context (in-game registration takes precedence over CLI path)
        emp = self._employee or {
            "employee_name": self._employee_id or "Player",
            "employee_id":   self._employee_id or "player",
            "department":    "",
            "role":          "",
        }
        # Merge employee fields into risk summary so report.py can render them
        report_data = dict(self.risk.summary_dict())
        report_data.update({
            "employee_name": emp.get("employee_name", ""),
            "employee_id":   emp.get("employee_id",   ""),
            "department":    emp.get("department",     ""),
            "role":          emp.get("role",           ""),
            "campaign_name": self._campaign.name if self._campaign else "Free Play",
        })
        self.report.set_data(report_data)
        self.state = STATE_REPORT
        # Generate and save semester report (available immediately on report screen)
        semester = SemesterReport.generate(
            emp, self._campaign, self.risk.summary_dict(),
            list(self.ev_mgr._seen),
        )
        self.semester_screen.set_report(semester)
        if emp.get("employee_id"):
            SemesterReport.save(semester, emp["employee_id"])
        self._semester_report = semester   # store for exam routing
        self._exam_attempt    = 1          # reset on new game
        # Persist campaign result
        if self._campaign is not None:
            ResultStore.save(
                employee=emp,
                campaign=self._campaign,
                risk_summary=self.risk.summary_dict(),
                completed_events=list(self.ev_mgr._seen),
            )
        # Assign lectures based on risk profile then load them into the screen
        emp_id = emp.get("employee_id")
        LectureEngine.assign_lectures(emp_id, self.risk.summary_dict())
        self.lecture_screen.set_employee(emp_id)
        # AI analysis — runs after rule-based systems; augments, does not replace
        if emp_id:
            run_ai_analysis(emp_id, self.risk.summary_dict())

    def _apply_campaign(self, campaign):
        """Apply a campaign chosen from the campaign select screen."""
        self._campaign    = campaign
        self._employee_id = self._employee.get("employee_id") or self._employee_id or "player"
        self.db.set_enabled_events(campaign.enabled_events)
        self.risk.total_threats = len(campaign.enabled_events)

    def _on_score(self, delta, good):
        cx = SCREEN_WIDTH//2 + random.randint(-50, 50)
        cy = SCREEN_HEIGHT//2
        self._popups.append(Popup(cx, cy, f"+{delta} pts" if good else f"-{delta} pts", good))
        if good:
            self._flash_col = (0, 200, 80, 90);  self._flash_t = 20
        else:
            self._flash_col = (220, 30, 30, 120); self._flash_t = 30
            self._shake_t = 16; self._shake_mag = 7

    def _on_act_change(self, act: int, act_name: str):
        """Called once when the story advances to a new act."""
        # 1. Update all NPCs
        for npc in self.npcs:
            npc.set_act(act)
        # 2. Update HUD objective
        self.hud.set_objective(self.story.get_current_objective())
        # 3. Flash the act title banner across the screen
        self._room_flash.trigger(act_name)
        # 4. Brief green/amber flash tint
        if act < 4:
            self._flash_col = (255, 200, 0, 80);  self._flash_t = 40
        else:
            self._flash_col = (220, 30, 30, 120); self._flash_t = 40

    # ── Camera ────────────────────────────────────────────────────────────────
    def _update_camera(self):
        tx = self.player.px - SCREEN_WIDTH  // 2 + TILE_SIZE // 2
        ty = self.player.py - SCREEN_HEIGHT // 2 + TILE_SIZE // 2
        mw = self.gmap.width  * TILE_SIZE
        mh = self.gmap.height * TILE_SIZE
        tx = max(0, min(tx, mw - SCREEN_WIDTH))
        ty = max(0, min(ty, mh - SCREEN_HEIGHT))
        self.cam_x += (tx - self.cam_x) * 0.18
        self.cam_y += (ty - self.cam_y) * 0.18

        ox = oy = 0
        if self._shake_t > 0:
            ox = random.randint(-self._shake_mag, self._shake_mag)
            oy = random.randint(-self._shake_mag, self._shake_mag)
            self._shake_t -= 1
        self._dcx = int(self.cam_x) + ox
        self._dcy = int(self.cam_y) + oy

    # ── Interaction hint ──────────────────────────────────────────────────────
    def _update_hint(self):
        fx, fy = self.player.facing_tile()
        for npc in self.npcs:
            if npc.tile_x == fx and npc.tile_y == fy:
                self._interact_hint = f"[E]  Talk to {npc.name}"
                return
        ev = self.db.get_by_tile(fx, fy)
        if ev and not self.ev_mgr.is_seen(ev.id):
            icons = {"computer":"💻","poster":"📋","usb":"💾","phone":"📞"}
            self._interact_hint = f"[E]  {icons.get(ev.trigger_type,'!')} {ev.title}"
            return
        self._interact_hint = ""

    # ── NPC interaction ───────────────────────────────────────────────────────
    def _npc_interact(self):
        fx, fy = self.player.facing_tile()
        for npc in self.npcs:
            if npc.tile_x == fx and npc.tile_y == fy:
                npc.show_hint()
                # Use act-aware dialogue
                self.dialog.show(speaker=npc.name, lines=list(npc.get_dialog()))
                return True
        return False

    # ── Main loop ─────────────────────────────────────────────────────────────
    def run(self):
        self._dcx = self._dcy = 0
        running = True
        while running:
            self.clock.tick(FPS)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN:
                    running = self._key(ev.key, running, ev.unicode)
            self._update()
            self._draw()
        pygame.quit()
        sys.exit()

    # ── Key handler ─────────────────────────────────────────────────────────────
    def _key(self, key, running, unicode_char: str = ""):
        if self.state == STATE_TITLE:
            if self.title.handle_key(key):
                # Title → Registration (reset form each visit)
                self.reg_screen.reset()
                self.state = STATE_REGISTRATION
            return running

        if self.state == STATE_REGISTRATION:
            result = self.reg_screen.handle_key(key, unicode_char)
            if result == "BACK":
                self.state = STATE_TITLE
            elif isinstance(result, dict):
                self._employee    = result
                self._employee_id = result["employee_id"]
                if self._campaign is not None:
                    # Campaign pre-assigned via CLI — skip selection screen
                    self.risk.total_threats = len(self._campaign.enabled_events)
                    self.state = STATE_EXPLORE
                    self._room_flash.trigger(self._campaign.name.upper())
                else:
                    self.camp_select._slide_in = 0.0
                    self.state = STATE_CAMPAIGN_SELECT
            return running

        if self.state == STATE_CAMPAIGN_SELECT:
            result = self.camp_select.handle_key(key)
            if result == "BACK":
                self.state = STATE_REGISTRATION
            elif result == "FREE_PLAY":
                self.state = STATE_EXPLORE
                self._room_flash.trigger("PHISHVERSE OFFICE  ·  FREE PLAY")
            elif result is not None:        # Campaign object selected
                self._apply_campaign(result)
                self.state = STATE_EXPLORE
                self._room_flash.trigger(result.name.upper())
            return running

        if self.state == STATE_REPORT:
            action = self.report.handle_key(key)
            if action == "DASHBOARD":
                self.state = STATE_SEMESTER_REPORT   # ENTER -> semester report card
            elif action == "QUIT":
                return False
            return running

        if self.state == STATE_SEMESTER_REPORT:
            if key in (pygame.K_RETURN, pygame.K_e):
                # Route: unlocked → Final Exam, locked → Lectures
                if self._semester_report.get("exam_status") == "UNLOCKED":
                    primary  = self._semester_report.get("weakness", {}).get("primary", "")
                    questions = self.q_engine.select_questions(primary, n=10)
                    self.final_exam_screen.start(questions, attempt=self._exam_attempt)
                    self.state = STATE_FINAL_EXAM
                else:
                    self.state = STATE_LECTURES
            elif key in (pygame.K_q, pygame.K_ESCAPE):
                return False
            return running

        if self.state == STATE_FINAL_EXAM:
            result = self.final_exam_screen.handle_key(key)
            if result == "PASS":
                # Generate + save certificate
                emp     = self._employee or {"employee_id": self._employee_id or "player",
                                              "employee_name": "", "department": "", "role": ""}
                exam_r  = ExamEngine.build_result(
                    emp, self.final_exam_screen.score_data, self._semester_report,
                    attempt=self._exam_attempt,
                )
                ExamEngine.save_result(emp.get("employee_id", "player"), exam_r)
                cert    = Certificate.generate(emp, exam_r)
                Certificate.save(cert, emp.get("employee_id", "player"))
                self.cert_screen.set_cert(cert)
                self.state = STATE_CERTIFICATE
            elif result == "FAIL":
                self._exam_attempt += 1
                self.state = STATE_LECTURES    # back to lectures before retake
            elif result == "QUIT":
                return False
            return running

        if self.state == STATE_CERTIFICATE:
            if self.cert_screen.handle_key(key):
                return False
            return running

        if self.state == STATE_LECTURES:
            action = self.lecture_screen.handle_key(key)
            if action == "CONTINUE":
                self.dashboard.load_data()
                self.state = STATE_DASHBOARD
            return running

        if self.state == STATE_DASHBOARD:
            if self.dashboard.handle_key(key):
                return False
            return running

        if self.state == STATE_DIALOG:
            self.dialog.handle_key(key)
            if not self.dialog.active and self.state == STATE_DIALOG:
                self.state = STATE_EXPLORE
            return running

        if self.state == STATE_MENU:
            r = self.pause.handle_key(key)
            if r == "RESUME": self.state = STATE_EXPLORE
            elif r == "QUIT": return False
            return running

        # Explore
        if key == pygame.K_ESCAPE:
            self.state = STATE_MENU
        elif key in (pygame.K_e, pygame.K_RETURN):
            hit = self._npc_interact()
            if not hit:
                fx, fy = self.player.facing_tile()
                hit = self.ev_mgr.check_interaction(fx, fy)
            if hit:
                self.state = STATE_DIALOG
        return running

    # ── Update ─────────────────────────────────────────────────────────────
    def _update(self):
        if self.state == STATE_TITLE:            self.title.update();            return
        if self.state == STATE_REGISTRATION:     self.reg_screen.update();       return
        if self.state == STATE_CAMPAIGN_SELECT:  self.camp_select.update();      return
        if self.state == STATE_REPORT:           self.report.update();           return
        if self.state == STATE_SEMESTER_REPORT:  self.semester_screen.update();     return
        if self.state == STATE_FINAL_EXAM:        self.final_exam_screen.update();   return
        if self.state == STATE_CERTIFICATE:       self.cert_screen.update();         return
        if self.state == STATE_LECTURES:          self.lecture_screen.update();      return
        if self.state == STATE_DASHBOARD:         self.dashboard.update();           return
        if self.state == STATE_DIALOG:
            self.dialog.update()
            if not self.dialog.active and self.state == STATE_DIALOG:
                self.state = STATE_EXPLORE
            return
        if self.state == STATE_MENU:    return

        # Player movement
        if not self.player.moving:
            keys = pygame.key.get_pressed()
            for kc, (dx, dy, _) in Player.DIRECTIONS.items():
                if keys[kc]:
                    self.player.set_direction(dx, dy)
                    self.player.try_move(dx, dy, self.gmap)
                    break

        self.player.update()

        # Step-on events
        if not self.player.moving:
            if self.ev_mgr.check_tile(self.player.tile_x, self.player.tile_y):
                self.state = STATE_DIALOG

        for npc in self.npcs: npc.update()

        self._update_camera()
        self._update_hint()
        self._room_flash.update()

        # Room transition
        room = self.gmap.get_room(self.player.tile_x, self.player.tile_y)
        if room != self._prev_room and room not in ("OFFICE",):
            self._room_flash.trigger(room)
            self._prev_room = room
            # Fire room-entry cutscene for this act (once per act+room combination)
            cutscene = self.story.get_cutscene(room)
            if cutscene:
                speaker, lines = cutscene
                self.dialog.show(speaker=speaker, lines=lines)
                self.state = STATE_DIALOG

        # Story progression — advance acts based on completion + room
        room_now = self.gmap.get_room(self.player.tile_x, self.player.tile_y)
        act_banner = self.story.advance(self.ev_mgr.completed_count, room_now)
        if act_banner and self.story.act != self._prev_act:
            self._prev_act = self.story.act
            self._on_act_change(self.story.act, act_banner)

        # Objective refresh after each completed event
        self.hud.set_objective(self.story.get_current_objective())

        # Flash
        if self._flash_t > 0: self._flash_t -= 1

        # Popups
        for p in self._popups: p.update()
        self._popups = [p for p in self._popups if p.alive]

    # ── Draw ─────────────────────────────────────────────────────────────
    def _draw(self):
        self.screen.fill((12, 12, 22))

        if self.state == STATE_TITLE:
            self.title.draw(self.screen);            pygame.display.flip(); return
        if self.state == STATE_REGISTRATION:
            self.reg_screen.draw(self.screen);       pygame.display.flip(); return
        if self.state == STATE_CAMPAIGN_SELECT:
            self.camp_select.draw(self.screen);      pygame.display.flip(); return
        if self.state == STATE_REPORT:
            self.report.draw(self.screen);           pygame.display.flip(); return
        if self.state == STATE_SEMESTER_REPORT:
            self.semester_screen.draw(self.screen);  pygame.display.flip(); return
        if self.state == STATE_LECTURES:
            self.lecture_screen.draw(self.screen);     pygame.display.flip(); return
        if self.state == STATE_FINAL_EXAM:
            self.final_exam_screen.draw(self.screen);  pygame.display.flip(); return
        if self.state == STATE_CERTIFICATE:
            self.cert_screen.draw(self.screen);        pygame.display.flip(); return
        if self.state == STATE_DASHBOARD:
            self.dashboard.draw(self.screen);          pygame.display.flip(); return

        # World
        self.gmap.draw(self.screen, self._dcx, self._dcy, SCREEN_WIDTH, SCREEN_HEIGHT)
        self._draw_door_glows()
        self._draw_event_markers()

        # NPCs
        for npc in self.npcs:
            npc.draw(self.screen, self._dcx, self._dcy)
            dist = abs(npc.tile_x - self.player.tile_x) + abs(npc.tile_y - self.player.tile_y)
            if dist <= 4:
                npc.draw_label(self.screen, self._dcx, self._dcy, self.small, self.small)

        self.player.draw(self.screen, self._dcx, self._dcy)

        # Alert-mode red atmosphere overlay (acts 3 & 4)
        if self.story.alert_mode:
            t = pygame.time.get_ticks()
            pulse_a = int(18 + 10 * math.sin(t / 600))
            atm = self._flash_surf
            atm.fill((180, 10, 10, pulse_a))
            self.screen.blit(atm, (0, 0))

        # Screen flash (reuse pre-allocated surface)
        if self._flash_t > 0 and self._flash_col:
            a = int(self._flash_col[3] * self._flash_t / 30)
            self._flash_surf.fill((*self._flash_col[:3], min(255, a)))
            self.screen.blit(self._flash_surf, (0, 0))

        # Room flash
        self._room_flash.draw(self.screen, self.big, SCREEN_WIDTH, SCREEN_HEIGHT)

        # HUD
        room = self.gmap.get_room(self.player.tile_x, self.player.tile_y)
        self.hud.draw(self.screen, self.risk.score,
                      self.ev_mgr.completed_count, self.db.total, room)

        # Interaction hint
        if self._interact_hint and self.state == STATE_EXPLORE:
            self._draw_hint()

        # Popups
        for p in self._popups: p.draw(self.screen, self.font)

        if self.state == STATE_DIALOG: self.dialog.draw(self.screen)
        if self.state == STATE_MENU:   self.pause.draw(self.screen)

        pygame.display.flip()

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _draw_event_markers(self):
        t     = pygame.time.get_ticks()
        pulse = int(55 + 45 * math.sin(t / 350))
        bob   = int(3 * math.sin(t / 220))
        for ev in self.db.all_events():
            if self.ev_mgr.is_seen(ev.id): continue
            for (tx, ty) in ev.trigger_tiles:
                sx = tx * TILE_SIZE - self._dcx
                sy = ty * TILE_SIZE - self._dcy
                if not (-TILE_SIZE < sx < SCREEN_WIDTH and -TILE_SIZE < sy < SCREEN_HEIGHT):
                    continue
                # Pulsing glow ring (reuse pre-allocated surface)
                self._marker_glow.fill((0, 0, 0, 0))
                pygame.draw.rect(self._marker_glow, (*UI_GOLD, pulse),
                                 (0, 0, TILE_SIZE + 10, TILE_SIZE + 10), 4, border_radius=6)
                self.screen.blit(self._marker_glow, (sx - 5, sy - 5))
                # Floating ! badge (pre-rendered glyph + background)
                bx = sx + TILE_SIZE // 2 - self._marker_badge_off
                self.screen.blit(self._marker_badge_bg,  (bx - 4, sy - 20 + bob))
                self.screen.blit(self._marker_badge_lbl, (bx,     sy - 18 + bob))

    def _draw_door_glows(self):
        t   = pygame.time.get_ticks()
        bob = int(2 * math.sin(t / 280))
        aw  = self._door_arrow.get_width() // 2
        for tx, ty in self.gmap._door_tiles:
            sx = tx * TILE_SIZE - self._dcx + TILE_SIZE // 2
            sy = ty * TILE_SIZE - self._dcy
            if not (0 < sx < SCREEN_WIDTH and 0 < sy < SCREEN_HEIGHT):
                continue
            self.screen.blit(self._door_arrow, (sx - aw, sy + bob))

    def _draw_hint(self):
        lbl = self.font.render(self._interact_hint, True, WHITE)
        w, h = lbl.get_width()+24, lbl.get_height()+12
        px = SCREEN_WIDTH//2 - w//2
        py = SCREEN_HEIGHT - 190
        bg = pygame.Surface((w, h), pygame.SRCALPHA)
        bg.fill((10, 10, 35, 220))
        pygame.draw.rect(bg, UI_GOLD, (0, 0, w, h), 2, border_radius=6)
        self.screen.blit(bg,  (px, py))
        self.screen.blit(lbl, (px+12, py+6))


if __name__ == "__main__":
    import argparse
    _parser = argparse.ArgumentParser(description="PHISHVERSE")
    _parser.add_argument("--campaign", default=None, help="Campaign ID to pre-load (skips in-game selection)")
    _args, _ = _parser.parse_known_args()

    _campaign = None
    if _args.campaign:
        try:
            _campaign = CampaignLoader.load(_args.campaign)
            print(f"[PHISHVERSE] Campaign loaded: {_campaign.name}")
        except FileNotFoundError as e:
            print(f"[PHISHVERSE] {e}")
            print("[PHISHVERSE] Starting free play.")

    Game(campaign=_campaign).run()

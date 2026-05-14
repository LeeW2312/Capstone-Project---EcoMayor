"""
EcoCity Mayor — screens/moderator_screen.py
Moderator Panel — Manual entry only, no AI features.
"""

import pygame
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from moderator import (add_question, delete_question,
                       add_upgrade, remove_upgrade, get_upgrades)

BG          = (11,  13,  26)
PANEL       = (18,  24,  48)
CARD2       = (16,  20,  42)
ACCENT      = (78,  144, 217)
ACCENT_D    = (12,  44,  88)
TEXT        = (228, 228, 242)
TEXT_DIM    = (115, 120, 155)
GREEN       = (72,  200, 118)
GREEN_D     = (10,  48,  26)
RED         = (215, 65,  65)
RED_D       = (52,  12,  12)
GOLD        = (236, 190, 50)
GOLD_D      = (50,  38,  6)
BORDER      = (38,  42,  72)
BORDER2     = (55,  60,  96)
WHITE       = (255, 255, 255)
ORANGE      = (222, 128, 26)
ORANGE_D    = (50,  24,  4)
PURPLE      = (145, 85,  215)
PURPLE_D    = (34,  10,  70)
PURPLE_M    = (65,  24,  125)
PURPLE_H    = (55,  20, 105)
ORANGE_H    = (80,  42,   8)
GREEN_H     = (14,  62,  32)

SCREEN_W, SCREEN_H = 900, 600
DATA_DIR    = "data"
USERS_FILE  = os.path.join(DATA_DIR, "users.json")
LEADER_FILE = os.path.join(DATA_DIR, "leaderboard.json")

TOP_H    = 58
TAB_Y    = 64
TAB_H    = 28
DIV_Y    = 98
CY       = 108
FOOTER_Y = 570


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return []


def txt(surf, text, font, color, x, y, center=False, mw=0):
    t = str(text)
    if mw and font.size(t)[0] > mw:
        while font.size(t + "...")[0] > mw and t:
            t = t[:-1]
        t += "..."
    img = font.render(t, True, color)
    r   = img.get_rect()
    if center:
        r.center = (x, y)
    else:
        r.topleft = (x, y)
    surf.blit(img, r)


def btn(surf, font, label, rect, hov, active=True,
        bg=None, hbg=None, border=None, fg=None):
    r = pygame.Rect(rect)
    if not active:
        pygame.draw.rect(surf, (24, 26, 46), r, border_radius=7)
        pygame.draw.rect(surf, BORDER, r, 1, border_radius=7)
        txt(surf, label, font, TEXT_DIM, r.centerx, r.centery, center=True)
    elif hov:
        hc = hbg or ACCENT
        pygame.draw.rect(surf, hc, r, border_radius=7)
        pygame.draw.rect(surf, WHITE, r, 2, border_radius=7)
        sh = pygame.Surface((r.w, r.h // 2), pygame.SRCALPHA)
        sh.fill((255, 255, 255, 18))
        surf.blit(sh, (r.x, r.y))
        txt(surf, label, font, WHITE, r.centerx, r.centery, center=True)
    else:
        pygame.draw.rect(surf, bg or ACCENT_D, r, border_radius=7)
        pygame.draw.rect(surf, border or ACCENT, r, 1, border_radius=7)
        txt(surf, label, font, fg or TEXT, r.centerx, r.centery, center=True)
    return r


class IBox:
    def __init__(self, ph="", maxlen=120):
        self.rect   = pygame.Rect(0, 0, 10, 10)
        self.text   = ""
        self.active = False
        self.ph     = ph
        self.maxlen = maxlen

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key not in (pygame.K_RETURN, pygame.K_TAB):
                if len(self.text) < self.maxlen:
                    self.text += event.unicode

    def draw(self, surf, font, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        bc = ACCENT if self.active else BORDER2
        bg = (22, 28, 58) if self.active else (14, 18, 40)
        pygame.draw.rect(surf, bg, self.rect, border_radius=7)
        pygame.draw.rect(surf, bc, self.rect,
                         2 if self.active else 1, border_radius=7)
        disp = self.text if self.text else self.ph
        col  = TEXT if self.text else TEXT_DIM
        mw   = w - 20
        s    = disp
        if font.size(s)[0] > mw:
            while font.size(s)[0] > mw and s:
                s = s[1:]
        txt(surf, s, font, col,
            x + 10, y + h // 2 - font.get_height() // 2)
        if self.active and (pygame.time.get_ticks() // 500) % 2 == 0:
            tw = min(font.size(self.text)[0], mw)
            pygame.draw.line(surf, ACCENT,
                             (x + 10 + tw + 2, y + 5),
                             (x + 10 + tw + 2, y + h - 5), 2)


class ModeratorScreen:
    def __init__(self, screen, fonts, game_state):
        self.screen = screen
        self.fonts  = fonts
        self.state  = game_state

        self.toast_msg  = ""
        self.toast_time = 0
        self.toast_err  = False
        self.session_q  = 0
        self.session_u  = 0

        # Main tabs: 0=Profile  1=Questions  2=Upgrades
        self.main_tab = 0
        self.mtab_rects = [
            pygame.Rect(210, TAB_Y, 145, TAB_H),
            pygame.Rect(365, TAB_Y, 145, TAB_H),
            pygame.Rect(520, TAB_Y, 145, TAB_H),
        ]
        self.mtab_labels  = ["Profile", "Questions", "Upgrades"]
        self.mtab_colours = [ACCENT, PURPLE, ORANGE]

        # Fixed buttons
        self.btn_logout = pygame.Rect(SCREEN_W - 112, 15, 98, 28)
        self.btn_back   = pygame.Rect(12, 15, 138, 28)
        self.btn_go_q   = pygame.Rect(28,  516, 280, 40)
        self.btn_go_u   = pygame.Rect(358, 516, 280, 40)

        # Action buttons — set each frame
        self.btn_add_q = pygame.Rect(0, 0, 1, 1)
        self.btn_add_u = pygame.Rect(0, 0, 1, 1)

        # Question inputs
        self.mq  = IBox("Type your question here...", maxlen=160)
        self.ma1 = IBox("Correct answer (A)", maxlen=120)
        self.ma2 = IBox("Wrong answer (B)", maxlen=120)
        self.ma3 = IBox("Wrong answer (C)", maxlen=120)
        self.ma4 = IBox("Wrong answer (D)", maxlen=120)
        self.mq_inputs = [self.mq, self.ma1, self.ma2, self.ma3, self.ma4]

        # Upgrade inputs
        self.un = IBox("Upgrade name  (e.g. Solar Farm)")
        self.ur = IBox("Pollution reduction %  (e.g. 8.5)")
        self.uc = IBox("Cost in points  (e.g. 100)")
        self.mu_inputs = [self.un, self.ur, self.uc]

        self.q_scroll = 0
        self.del_q    = []
        self.u_scroll = 0
        self.del_u    = []

    # ── Data ──────────────────────────────────────────

    def _qs(self):
        quizzes = load_json(os.path.join(DATA_DIR, "quizzes.json"))
        all_q   = []
        for qz in quizzes:
            for q in qz.get("questions", []):
                all_q.append({**q, "quiz_id": qz["quiz_id"]})
        return all_q

    def _dup_q(self, t):
        return any(q["question_text"].strip().lower() == t.strip().lower()
                   for q in self._qs())

    def _dup_u(self, n):
        return any(u["upgrade_name"].strip().lower() == n.strip().lower()
                   for u in get_upgrades())

    def _stats(self):
        qs    = self._qs()
        us    = get_upgrades()
        lb    = load_json(LEADER_FILE)
        users = load_json(USERS_FILE)
        pl    = [u for u in users if u.get("role") == "Player"]
        s     = len(lb)
        w     = sum(1 for e in lb if e.get("won"))
        ap    = sum(e.get("pollution", 100) for e in lb) / s if s else 100
        return {"tq": len(qs), "tu": len(us), "pl": len(pl),
                "s": s, "w": w, "ap": round(ap, 1)}

    def _toast(self, msg, err=False):
        self.toast_msg  = msg
        self.toast_time = pygame.time.get_ticks() + 3500
        self.toast_err  = err

    # ── Drawing helpers ───────────────────────────────

    def _card(self, s, x, y, w, h, hcol, bcol, title):
        pygame.draw.rect(s, CARD2, (x, y, w, h), border_radius=10)
        pygame.draw.rect(s, bcol, (x, y, w, h), 1, border_radius=10)
        pygame.draw.rect(s, hcol, (x + 1, y + 1, w - 2, 38), border_radius=9)
        pygame.draw.rect(s, bcol, (x + 1, y + 1, 4, 38), border_radius=9)
        txt(s, title, self.fonts["body"], WHITE, x + 18, y + 11)

    def _sblk(self, s, x, y, w, h, label, value, col):
        pygame.draw.rect(s, CARD2, (x, y, w, h), border_radius=10)
        pygame.draw.rect(s, col,   (x, y, w, h), 1, border_radius=10)
        pygame.draw.rect(s, col,   (x + 1, y + 1, w - 2, 3), border_radius=10)
        txt(s, str(value), self.fonts["title"], col,
            x + w // 2, y + h // 2 - 8, center=True)
        txt(s, label, self.fonts["small"], TEXT_DIM,
            x + w // 2, y + h - 16, center=True)

    def _bar(self, s, x, y, w, val, mx, col, label, sub):
        txt(s, label, self.fonts["small"], TEXT_DIM, x, y - 16)
        pygame.draw.rect(s, (18, 20, 44), (x, y, w, 12), border_radius=5)
        fw = int(w * min(val, mx) / mx)
        if fw > 0:
            pygame.draw.rect(s, col, (x, y, fw, 12), border_radius=5)
        pygame.draw.rect(s, BORDER2, (x, y, w, 12), 1, border_radius=5)
        txt(s, sub, self.fonts["small"], col, x + w + 8, y)

    # ══════════════════════════════════════════════════
    # PROFILE
    # ══════════════════════════════════════════════════

    def _draw_profile(self, s, mouse):
        st    = self._stats()
        uname = self.state["user"]["username"]
        role  = self.state["user"]["role"]

        # Identity card
        pygame.draw.rect(s, CARD2,  (12, 68, 350, 116), border_radius=10)
        pygame.draw.rect(s, ACCENT, (12, 68, 350, 116), 1, border_radius=10)
        pygame.draw.rect(s, ACCENT, (12, 68, 3, 116),   border_radius=10)

        pygame.draw.circle(s, ACCENT_D, (68, 126), 32)
        pygame.draw.circle(s, ACCENT,   (68, 126), 32, 2)
        txt(s, uname[0].upper(), self.fonts["title"], WHITE,
            68, 126, center=True)

        txt(s, uname,           self.fonts["body"],  WHITE,    116, 82)
        txt(s, f"Role:  {role}", self.fonts["small"], TEXT_DIM, 116, 106)

        rc = GOLD if role == "Admin" else PURPLE if role == "Moderator" else GREEN
        rb = GOLD_D if role == "Admin" else PURPLE_D if role == "Moderator" else GREEN_D
        rr = pygame.Rect(116, 124, 80, 20)
        pygame.draw.rect(s, rb, rr, border_radius=5)
        pygame.draw.rect(s, rc, rr, 1, border_radius=5)
        txt(s, role, self.fonts["small"], rc,
            rr.centerx, rr.centery, center=True)

        sr = pygame.Rect(208, 124, 138, 20)
        pygame.draw.rect(s, ACCENT_D, sr, border_radius=5)
        pygame.draw.rect(s, ACCENT,   sr, 1, border_radius=5)
        txt(s, f"Session: +{self.session_q}Q  +{self.session_u}U",
            self.fonts["small"], ACCENT,
            sr.centerx, sr.centery, center=True)

        # Stat blocks
        for x, y, w, h, lbl, val, col in [
            (12,  192, 160, 74, "Total Questions", st["tq"],  PURPLE),
            (178, 192, 160, 74, "Total Upgrades",  st["tu"],  ORANGE),
            (344, 192, 160, 74, "Players",         st["pl"],  GOLD),
            (510, 192, 160, 74, "Seasons Played",  st["s"],   ACCENT),
            (676, 192, 212, 74, "Seasons Won",
             f"{st['w']}/{st['s']}", GREEN),
        ]:
            self._sblk(s, x, y, w, h, lbl, val, col)

        # Game Health
        pygame.draw.rect(s, CARD2,  (12, 274, 418, 196), border_radius=10)
        pygame.draw.rect(s, GREEN,  (12, 274, 418, 196), 1, border_radius=10)
        pygame.draw.rect(s, GREEN_H,(13, 275, 416, 36),  border_radius=9)
        pygame.draw.rect(s, GREEN,  (13, 275, 4, 36),    border_radius=9)
        txt(s, "Game Health", self.fonts["body"], GREEN, 26, 284)

        self._bar(s, 26, 344, 366, st["tq"], 20, PURPLE,
                  "Question Pool  (target: 20+)", f"{st['tq']}/20")
        self._bar(s, 26, 392, 366, st["tu"], 10, ORANGE,
                  "Upgrade Variety  (target: 10+)", f"{st['tu']}/10")
        self._bar(s, 26, 440, 366,
                  max(0, 100 - int(st["ap"])), 100, GREEN,
                  f"Avg City Cleanliness  (avg pollution: {st['ap']}%)",
                  f"{max(0, 100 - int(st['ap']))}%")

        # Suggestions
        pygame.draw.rect(s, CARD2, (440, 274, 448, 196), border_radius=10)
        pygame.draw.rect(s, GOLD,  (440, 274, 448, 196), 1, border_radius=10)
        pygame.draw.rect(s, GOLD_D,(441, 275, 446, 36),  border_radius=9)
        pygame.draw.rect(s, GOLD,  (441, 275, 4, 36),    border_radius=9)
        txt(s, "Suggestions", self.fonts["body"], GOLD, 454, 284)

        tips = []
        if st["tq"] < 10: tips.append("Add more questions  (below 10 total)")
        if st["tu"] < 5:  tips.append("Add more upgrades for player variety")
        if st["ap"] > 70: tips.append("Players struggling -- add cheaper upgrades")
        if st["s"] > 0 and st["w"] == 0:
            tips.append("No wins yet -- try easier early upgrades")
        if not tips:
            tips = ["Game is healthy! Keep adding fresh content.",
                    "Try themed question sets for variety.",
                    "Review upgrade costs vs player earnings."]
        for i, tip in enumerate(tips[:5]):
            c = GOLD if i == 0 else TEXT_DIM
            txt(s, f"  *  {tip}", self.fonts["small"], c,
                454, 328 + i * 28, mw=424)

        # Quick actions
        pygame.draw.rect(s, (14, 16, 34), (12, 486, 876, 66),
                         border_radius=10)
        pygame.draw.rect(s, BORDER2, (12, 486, 876, 66),
                         1, border_radius=10)
        txt(s, "Quick Actions:", self.fonts["small"], TEXT_DIM, 26, 492)
        btn(s, self.fonts["body"], "Manage Questions",
            self.btn_go_q, self.btn_go_q.collidepoint(mouse),
            bg=PURPLE_D, hbg=PURPLE_M, border=PURPLE, fg=WHITE)
        btn(s, self.fonts["body"], "Manage Upgrades",
            self.btn_go_u, self.btn_go_u.collidepoint(mouse),
            bg=ORANGE_D, hbg=(148, 84, 16), border=ORANGE, fg=WHITE)

    # ══════════════════════════════════════════════════
    # ADD QUESTION / UPGRADE
    # ══════════════════════════════════════════════════

    def _add_q(self):
        t  = self.mq.text.strip()
        a1 = self.ma1.text.strip()
        a2 = self.ma2.text.strip()
        a3 = self.ma3.text.strip()
        a4 = self.ma4.text.strip()
        if not all([t, a1, a2, a3, a4]):
            self._toast("Please fill in all fields.", err=True)
            return
        if self._dup_q(t):
            self._toast("Duplicate -- already exists.", err=True)
            return
        try:
            add_question(quiz_id=1, question_text=t, answers=[
                {"answer_text": a1, "is_correct": True},
                {"answer_text": a2, "is_correct": False},
                {"answer_text": a3, "is_correct": False},
                {"answer_text": a4, "is_correct": False},
            ])
            for b in self.mq_inputs:
                b.text = ""
            self.session_q += 1
            self._toast("Question added!")
        except Exception as e:
            self._toast(str(e), err=True)

    def _add_u(self):
        n = self.un.text.strip()
        r = self.ur.text.strip()
        c = self.uc.text.strip()
        if not all([n, r, c]):
            self._toast("Please fill in all fields.", err=True)
            return
        if self._dup_u(n):
            self._toast("Duplicate -- already exists.", err=True)
            return
        try:
            add_upgrade(n, float(r), int(c))
            for b in self.mu_inputs:
                b.text = ""
            self.session_u += 1
            self._toast("Upgrade added!")
        except Exception as e:
            self._toast(str(e), err=True)

    # ══════════════════════════════════════════════════
    # QUESTION PANEL
    # ══════════════════════════════════════════════════

    def _p_questions(self, s, mouse):
        ch  = 318
        col = GREEN
        self._card(s, 10, CY, 876, ch, GREEN_H, col,
                   "Add Question  --  Type and Save Your Own Question")

        txt(s, "Question:", self.fonts["small"], TEXT_DIM, 18, CY + 50)
        self.mq.draw(s, self.fonts["body"], 18, CY + 66, 860, 36)

        txt(s, "Correct answer (A):", self.fonts["small"], GREEN,
            18, CY + 116)
        self.ma1.draw(s, self.fonts["body"], 18, CY + 132, 860, 32)

        txt(s, "Wrong answers:", self.fonts["small"], RED, 18, CY + 176)
        self.ma2.draw(s, self.fonts["body"], 18,  CY + 192, 422, 30)
        self.ma3.draw(s, self.fonts["body"], 450, CY + 192, 428, 30)
        self.ma4.draw(s, self.fonts["body"], 18,  CY + 234, 860, 30)

        self.btn_add_q = pygame.Rect(18, CY + 278, 214, 40)
        btn(s, self.fonts["body"], "Add Question",
            self.btn_add_q, self.btn_add_q.collidepoint(mouse),
            bg=GREEN_D, hbg=GREEN, border=GREEN, fg=GREEN)

        txt(s, "Duplicate questions are blocked automatically.",
            self.fonts["small"], TEXT_DIM, 254, CY + 292)

        return CY + ch + 8

    # ══════════════════════════════════════════════════
    # UPGRADE PANEL
    # ══════════════════════════════════════════════════

    def _p_upgrades(self, s, mouse):
        ch  = 234
        col = ORANGE
        self._card(s, 10, CY, 876, ch, ORANGE_H, col,
                   "Add Upgrade  --  Add Your Own Upgrade")

        txt(s, "Upgrade name:", self.fonts["small"], TEXT_DIM, 18, CY + 50)
        self.un.draw(s, self.fonts["body"], 18, CY + 66, 860, 36)

        txt(s, "Pollution reduction %:", self.fonts["small"], GREEN,
            18, CY + 116)
        txt(s, "Cost in points:", self.fonts["small"], GOLD, 450, CY + 116)
        self.ur.draw(s, self.fonts["body"], 18,  CY + 132, 422, 32)
        self.uc.draw(s, self.fonts["body"], 450, CY + 132, 428, 32)

        self.btn_add_u = pygame.Rect(18, CY + 178, 214, 40)
        btn(s, self.fonts["body"], "Add Upgrade",
            self.btn_add_u, self.btn_add_u.collidepoint(mouse),
            bg=ORANGE_D, hbg=ORANGE, border=ORANGE, fg=ORANGE)

        txt(s, "Duplicate upgrade names are blocked automatically.",
            self.fonts["small"], TEXT_DIM, 254, CY + 192)

        return CY + ch + 8

    # ══════════════════════════════════════════════════
    # LISTS
    # ══════════════════════════════════════════════════

    def _qlist(self, s, lt):
        qs  = self._qs()
        LH  = FOOTER_Y - lt - 10
        pygame.draw.rect(s, (20, 24, 54), (10, lt, 876, 26), border_radius=6)
        txt(s, "#",             self.fonts["small"], TEXT_DIM, 16, lt + 5)
        txt(s, "Question",      self.fonts["small"], TEXT_DIM, 42, lt + 5)
        txt(s, "Correct Answer",self.fonts["small"], GREEN,    544, lt + 5)
        txt(s, "Del",           self.fonts["small"], TEXT_DIM, 850, lt + 5)
        rh  = 26
        vis = max(1, LH // rh)
        self.q_scroll = max(0, min(self.q_scroll, max(0, len(qs) - vis)))
        s.set_clip(pygame.Rect(10, lt + 28, 876, LH))
        self.del_q = []
        for i, q in enumerate(qs[self.q_scroll: self.q_scroll + vis + 1]):
            ry = lt + 28 + i * rh
            if ry + rh > lt + 28 + LH:
                break
            pygame.draw.rect(s, (19, 23, 50) if i % 2 == 0 else (13, 17, 38),
                             (10, ry, 876, rh - 1), border_radius=3)
            txt(s, str(self.q_scroll + i + 1),
                self.fonts["small"], TEXT_DIM, 16, ry + 5)
            txt(s, q["question_text"],
                self.fonts["small"], TEXT, 42, ry + 5, mw=486)
            c = next((a["answer_text"] for a in q.get("answers", [])
                      if a.get("is_correct")), "")
            txt(s, c, self.fonts["small"], GREEN, 544, ry + 5, mw=288)
            dr = pygame.Rect(842, ry + 3, 38, 19)
            pygame.draw.rect(s, RED_D, dr, border_radius=4)
            pygame.draw.rect(s, RED, dr, 1, border_radius=4)
            txt(s, "Del", self.fonts["small"], RED,
                dr.centerx, dr.centery, center=True)
            self.del_q.append((dr, q))
        s.set_clip(None)
        txt(s, f"Total:  {len(qs)}  questions",
            self.fonts["small"], TEXT_DIM, 16, FOOTER_Y)
        if len(qs) > vis:
            txt(s,
                f"Scroll  {self.q_scroll + 1}-"
                f"{min(self.q_scroll + vis, len(qs))}/{len(qs)}",
                self.fonts["small"], TEXT_DIM, SCREEN_W - 190, FOOTER_Y)

    def _ulist(self, s, lt):
        us  = get_upgrades()
        LH  = FOOTER_Y - lt - 10
        pygame.draw.rect(s, (20, 24, 54), (10, lt, 876, 26), border_radius=6)
        txt(s, "Upgrade Name",       self.fonts["small"], TEXT_DIM, 18, lt + 5)
        txt(s, "Pollution Reduction",self.fonts["small"], GREEN,    470, lt + 5)
        txt(s, "Point Cost",         self.fonts["small"], GOLD,     620, lt + 5)
        txt(s, "Del",                self.fonts["small"], TEXT_DIM, 850, lt + 5)
        rh  = 28
        vis = max(1, LH // rh)
        self.u_scroll = max(0, min(self.u_scroll, max(0, len(us) - vis)))
        s.set_clip(pygame.Rect(10, lt + 28, 876, LH))
        self.del_u = []
        for i, u in enumerate(us[self.u_scroll: self.u_scroll + vis + 1]):
            ry = lt + 28 + i * rh
            if ry + rh > lt + 28 + LH:
                break
            pygame.draw.rect(s, (19, 23, 50) if i % 2 == 0 else (13, 17, 38),
                             (10, ry, 876, rh - 2), border_radius=3)
            txt(s, u["upgrade_name"],
                self.fonts["body"], TEXT, 18, ry + 5)
            txt(s, f"-{u['pollution_reduction']}%",
                self.fonts["body"], GREEN, 470, ry + 5)
            txt(s, f"{u['cost_points']} pts",
                self.fonts["body"], GOLD, 620, ry + 5)
            dr = pygame.Rect(842, ry + 4, 38, 20)
            pygame.draw.rect(s, RED_D, dr, border_radius=4)
            pygame.draw.rect(s, RED, dr, 1, border_radius=4)
            txt(s, "Del", self.fonts["small"], RED,
                dr.centerx, dr.centery, center=True)
            self.del_u.append((dr, u))
        s.set_clip(None)
        txt(s, f"Total:  {len(us)}  upgrades",
            self.fonts["small"], TEXT_DIM, 16, FOOTER_Y)

    # ── Main draw ─────────────────────────────────────

    def draw(self):
        s     = self.screen
        mouse = pygame.mouse.get_pos()
        s.fill(BG)

        # Top bar
        pygame.draw.rect(s, PANEL, (0, 0, SCREEN_W, TOP_H))
        pygame.draw.rect(s, (22, 32, 66), (0, 0, SCREEN_W, 20))
        pygame.draw.line(s, BORDER2, (0, TOP_H), (SCREEN_W, TOP_H), 1)
        txt(s, "Moderator Panel",
            self.fonts["body"], GREEN, SCREEN_W // 2, 16, center=True)

        if self.main_tab in (1, 2):
            btn(s, self.fonts["small"], "Back to Profile",
                self.btn_back, self.btn_back.collidepoint(mouse),
                bg=(20, 10, 48), hbg=ACCENT, border=ACCENT)
        else:
            txt(s,
                f"{self.state['user']['username']}  "
                f"[{self.state['user']['role']}]",
                self.fonts["small"], TEXT_DIM, 14, 20)

        btn(s, self.fonts["small"], "Logout",
            self.btn_logout, self.btn_logout.collidepoint(mouse),
            bg=RED_D, hbg=RED, border=RED, fg=RED)

        # Main tabs
        for i, (r, lbl) in enumerate(zip(self.mtab_rects, self.mtab_labels)):
            act = i == self.main_tab
            col = self.mtab_colours[i]
            bg  = (col[0] // 5, col[1] // 5, col[2] // 5) if act else (13, 15, 34)
            pygame.draw.rect(s, bg, r, border_radius=8)
            pygame.draw.rect(s, col if act else BORDER2, r, 1, border_radius=8)
            if act:
                pygame.draw.rect(s, col,
                                 (r.x + 6, r.bottom - 2, r.w - 12, 3))
            txt(s, lbl, self.fonts["body"],
                WHITE if act else TEXT_DIM,
                r.centerx, r.centery, center=True)

        # Divider
        if self.main_tab in (1, 2):
            pygame.draw.line(s, BORDER2,
                             (10, DIV_Y), (SCREEN_W - 10, DIV_Y), 1)

        # Content
        if self.main_tab == 0:
            self._draw_profile(s, mouse)
        elif self.main_tab == 1:
            lt = self._p_questions(s, mouse)
            self._qlist(s, lt)
        else:
            lt = self._p_upgrades(s, mouse)
            self._ulist(s, lt)

        # Toast
        if self.toast_msg and pygame.time.get_ticks() < self.toast_time:
            bg_c = RED_D if self.toast_err else GREEN_D
            bd_c = RED   if self.toast_err else GREEN
            ts   = self.fonts["body"].render(self.toast_msg, True, WHITE)
            tw   = ts.get_width()
            tx   = SCREEN_W // 2 - tw // 2 - 22
            pygame.draw.rect(s, bg_c, (tx, 548, tw + 44, 36), border_radius=9)
            pygame.draw.rect(s, bd_c, (tx, 548, tw + 44, 36), 1, border_radius=9)
            s.blit(ts, (tx + 22, 556))

    # ── Events ────────────────────────────────────────

    def handle_event(self, event):
        if self.main_tab == 1:
            for b in self.mq_inputs:
                b.handle_event(event)
        elif self.main_tab == 2:
            for b in self.mu_inputs:
                b.handle_event(event)

        if event.type == pygame.MOUSEWHEEL:
            if   self.main_tab == 1: self.q_scroll = max(0, self.q_scroll - event.y)
            elif self.main_tab == 2: self.u_scroll = max(0, self.u_scroll - event.y)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if   self.main_tab == 1: self.q_scroll = max(0, self.q_scroll - 1)
                elif self.main_tab == 2: self.u_scroll = max(0, self.u_scroll - 1)
            elif event.key == pygame.K_DOWN:
                if   self.main_tab == 1: self.q_scroll += 1
                elif self.main_tab == 2: self.u_scroll += 1

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            if self.btn_logout.collidepoint(pos): return "logout"
            if self.main_tab in (1, 2) and self.btn_back.collidepoint(pos):
                self.main_tab = 0; return None

            for i, r in enumerate(self.mtab_rects):
                if r.collidepoint(pos): self.main_tab = i

            if self.main_tab == 0:
                if self.btn_go_q.collidepoint(pos): self.main_tab = 1
                if self.btn_go_u.collidepoint(pos): self.main_tab = 2

            if self.main_tab == 1:
                if self.btn_add_q.collidepoint(pos): self._add_q()
                for dr, q in self.del_q:
                    if dr.collidepoint(pos):
                        try:
                            delete_question(q["quiz_id"], q["question_id"])
                            self._toast("Question deleted.")
                        except Exception as e:
                            self._toast(str(e), err=True)

            elif self.main_tab == 2:
                if self.btn_add_u.collidepoint(pos): self._add_u()
                for dr, u in self.del_u:
                    if dr.collidepoint(pos):
                        try:
                            remove_upgrade(u["upgrade_id"])
                            self._toast("Upgrade removed.")
                        except Exception as e:
                            self._toast(str(e), err=True)

        return None
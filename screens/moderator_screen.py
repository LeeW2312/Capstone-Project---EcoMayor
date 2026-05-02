"""
EcoCity Mayor — screens/moderator_screen.py
Moderator panel — manage quizzes and upgrades
"""

import pygame
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from moderator import (add_question, delete_question,
                       add_upgrade, remove_upgrade, get_upgrades)

BG          = (15,  15,  30)
PANEL       = (22,  33,  62)
ACCENT      = (78,  144, 217)
ACCENT_DARK = (15,  52,  96)
TEXT        = (220, 220, 220)
TEXT_DIM    = (130, 130, 150)
GREEN       = (168, 216, 168)
RED         = (224, 92,  92)
GOLD        = (244, 200, 66)
BORDER      = (42,  42,  74)
WHITE       = (255, 255, 255)

SCREEN_W, SCREEN_H = 900, 600


def draw_text(surf, text, font, color, x, y, center=False):
    img = font.render(str(text), True, color)
    r   = img.get_rect()
    if center:
        r.center = (x, y)
    else:
        r.topleft = (x, y)
    surf.blit(img, r)

def draw_button(surf, font, text, rect, hovered, active=True):
    r = pygame.Rect(rect)
    if not active:
        pygame.draw.rect(surf, (40,40,60), r, border_radius=8)
        pygame.draw.rect(surf, BORDER, r, 1, border_radius=8)
        draw_text(surf, text, font, TEXT_DIM, r.centerx, r.centery, center=True)
    elif hovered:
        pygame.draw.rect(surf, ACCENT, r, border_radius=8)
        pygame.draw.rect(surf, WHITE, r, 1, border_radius=8)
        draw_text(surf, text, font, WHITE, r.centerx, r.centery, center=True)
    else:
        pygame.draw.rect(surf, ACCENT_DARK, r, border_radius=8)
        pygame.draw.rect(surf, ACCENT, r, 1, border_radius=8)
        draw_text(surf, text, font, TEXT, r.centerx, r.centery, center=True)


class InputBox:
    def __init__(self, x, y, w, h, placeholder=""):
        self.rect        = pygame.Rect(x, y, w, h)
        self.text        = ""
        self.active      = False
        self.placeholder = placeholder

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key not in (pygame.K_RETURN, pygame.K_TAB):
                if len(self.text) < 60:
                    self.text += event.unicode

    def draw(self, surf, font):
        bc = ACCENT if self.active else BORDER
        pygame.draw.rect(surf, (20,20,40), self.rect, border_radius=6)
        pygame.draw.rect(surf, bc, self.rect, 1, border_radius=6)
        display = self.text if self.text else self.placeholder
        col     = TEXT if self.text else TEXT_DIM
        draw_text(surf, display, font, col,
                  self.rect.x+8,
                  self.rect.centery - font.get_height()//2)
        if self.active and (pygame.time.get_ticks()//500)%2==0:
            tw = font.size(self.text)[0]
            cx = self.rect.x + 8 + tw + 2
            cy1 = self.rect.centery - font.get_height()//2 + 2
            cy2 = self.rect.centery + font.get_height()//2 - 2
            pygame.draw.line(surf, ACCENT, (cx,cy1), (cx,cy2), 2)


class ModeratorScreen:
    def __init__(self, screen, fonts, game_state):
        self.screen = screen
        self.fonts  = fonts
        self.state  = game_state

        self.btn_back   = pygame.Rect(20, 15, 90, 34)
        self.toast_msg  = ""
        self.toast_time = 0
        self.error_msg  = ""

        # ── Quiz inputs ───────────────────────────────
        self.q_text = InputBox(30,  110, 390, 34, "Question text")
        self.q_a1   = InputBox(30,  152, 390, 30, "Answer 1 (CORRECT)")
        self.q_a2   = InputBox(30,  188, 190, 30, "Answer 2 (wrong)")
        self.q_a3   = InputBox(228, 188, 190, 30, "Answer 3 (wrong)")
        self.q_a4   = InputBox(30,  224, 390, 30, "Answer 4 (wrong)")
        self.btn_add_q = pygame.Rect(30, 262, 180, 34)

        self.quiz_inputs = [
            self.q_text, self.q_a1, self.q_a2, self.q_a3, self.q_a4
        ]

        # ── Upgrade inputs ────────────────────────────
        self.u_name = InputBox(480, 110, 390, 34, "Upgrade name")
        self.u_red  = InputBox(480, 152, 185, 30, "Pollution reduction %")
        self.u_cost = InputBox(675, 152, 195, 30, "Cost (points)")
        self.btn_add_u = pygame.Rect(480, 192, 180, 34)

        self.upgrade_inputs = [self.u_name, self.u_red, self.u_cost]

        # Delete button rects (built during draw)
        self.del_q_rects = []
        self.del_u_rects = []

    def _load_questions(self):
        path = os.path.join("data", "quizzes.json")
        with open(path) as f:
            quizzes = json.load(f)
        all_q = []
        for quiz in quizzes:
            for q in quiz["questions"]:
                all_q.append({**q, "quiz_id": quiz["quiz_id"]})
        return all_q

    def _show_toast(self, msg, error=False):
        self.toast_msg  = msg
        self.toast_time = pygame.time.get_ticks() + 2500
        self.error_msg  = msg if error else ""

    def _try_add_question(self):
        txt = self.q_text.text.strip()
        a1  = self.q_a1.text.strip()
        a2  = self.q_a2.text.strip()
        a3  = self.q_a3.text.strip()
        a4  = self.q_a4.text.strip()
        if not all([txt, a1, a2, a3, a4]):
            self._show_toast("Fill in all question fields!", error=True)
            return
        try:
            add_question(quiz_id=1,
                question_text=txt,
                answers=[
                    {"answer_text": a1, "is_correct": True},
                    {"answer_text": a2, "is_correct": False},
                    {"answer_text": a3, "is_correct": False},
                    {"answer_text": a4, "is_correct": False},
                ])
            for box in self.quiz_inputs:
                box.text = ""
            self._show_toast("Question added successfully!")
        except Exception as e:
            self._show_toast(str(e), error=True)

    def _try_add_upgrade(self):
        name = self.u_name.text.strip()
        red  = self.u_red.text.strip()
        cost = self.u_cost.text.strip()
        if not all([name, red, cost]):
            self._show_toast("Fill in all upgrade fields!", error=True)
            return
        try:
            add_upgrade(name, float(red), int(cost))
            for box in self.upgrade_inputs:
                box.text = ""
            self._show_toast("Upgrade added successfully!")
        except Exception as e:
            self._show_toast(str(e), error=True)

    def draw(self):
        s     = self.screen
        mouse = pygame.mouse.get_pos()
        s.fill(BG)

        # Top bar
        pygame.draw.rect(s, PANEL, (0, 0, SCREEN_W, 60))
        pygame.draw.line(s, BORDER, (0, 60), (SCREEN_W, 60), 1)
        draw_text(s, "Moderator Panel",
                  self.fonts["body"], GREEN, SCREEN_W//2, 18, center=True)
        draw_button(s, self.fonts["small"], "Back",
                    self.btn_back, self.btn_back.collidepoint(mouse))

        # Divider line between two panels
        pygame.draw.line(s, BORDER, (450, 65), (450, SCREEN_H - 10), 1)

        # ── LEFT: Quiz Management ─────────────────────
        draw_text(s, "Quiz Management",
                  self.fonts["small"], ACCENT, 30, 75)

        for box in self.quiz_inputs:
            box.draw(s, self.fonts["tiny"])

        draw_button(s, self.fonts["small"], "Add Question",
                    self.btn_add_q,
                    self.btn_add_q.collidepoint(mouse))

        # Question list
        draw_text(s, "Questions:", self.fonts["tiny"], TEXT_DIM, 30, 306)
        questions = self._load_questions()
        self.del_q_rects = []
        list_y = 322
        for q in questions:
            if list_y > SCREEN_H - 40:
                break
            short = q["question_text"][:45] + ("..." if len(q["question_text"]) > 45 else "")
            draw_text(s, short, self.fonts["tiny"], TEXT, 30, list_y)
            del_rect = pygame.Rect(400, list_y - 2, 36, 20)
            pygame.draw.rect(s, (80,20,20), del_rect, border_radius=4)
            pygame.draw.rect(s, RED, del_rect, 1, border_radius=4)
            draw_text(s, "X", self.fonts["tiny"], RED,
                      del_rect.centerx, del_rect.centery, center=True)
            self.del_q_rects.append((del_rect, q))
            list_y += 26

        # ── RIGHT: Upgrade Management ─────────────────
        draw_text(s, "Item Management",
                  self.fonts["small"], ACCENT, 480, 75)

        for box in self.upgrade_inputs:
            box.draw(s, self.fonts["tiny"])

        draw_button(s, self.fonts["small"], "Add Upgrade",
                    self.btn_add_u,
                    self.btn_add_u.collidepoint(mouse))

        draw_text(s, "Upgrades:", self.fonts["tiny"], TEXT_DIM, 480, 236)
        upgrades = get_upgrades()
        self.del_u_rects = []
        list_y = 252
        for u in upgrades:
            if list_y > SCREEN_H - 40:
                break
            label = f"{u['upgrade_name']}  -{u['pollution_reduction']}%  {u['cost_points']}pts"
            draw_text(s, label, self.fonts["tiny"], TEXT, 480, list_y)
            del_rect = pygame.Rect(840, list_y - 2, 36, 20)
            pygame.draw.rect(s, (80,20,20), del_rect, border_radius=4)
            pygame.draw.rect(s, RED, del_rect, 1, border_radius=4)
            draw_text(s, "X", self.fonts["tiny"], RED,
                      del_rect.centerx, del_rect.centery, center=True)
            self.del_u_rects.append((del_rect, u))
            list_y += 26

        # Toast
        if self.toast_msg and pygame.time.get_ticks() < self.toast_time:
            is_err = bool(self.error_msg)
            bg_c   = (80,20,20) if is_err else (20,80,40)
            bd_c   = RED if is_err else GREEN
            ts     = self.fonts["small"].render(self.toast_msg, True, WHITE)
            tw     = ts.get_width()
            tx     = SCREEN_W//2 - tw//2 - 16
            pygame.draw.rect(s, bg_c, (tx, 545, tw+32, 34), border_radius=8)
            pygame.draw.rect(s, bd_c, (tx, 545, tw+32, 34), 1, border_radius=8)
            s.blit(ts, (tx+16, 552))

    def handle_event(self, event):
        for box in self.quiz_inputs + self.upgrade_inputs:
            box.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            if self.btn_back.collidepoint(pos):
                return "back"

            if self.btn_add_q.collidepoint(pos):
                self._try_add_question()

            if self.btn_add_u.collidepoint(pos):
                self._try_add_upgrade()

            for (del_rect, q) in self.del_q_rects:
                if del_rect.collidepoint(pos):
                    try:
                        delete_question(q["quiz_id"], q["question_id"])
                        self._show_toast("Question deleted.")
                    except Exception as e:
                        self._show_toast(str(e), error=True)

            for (del_rect, u) in self.del_u_rects:
                if del_rect.collidepoint(pos):
                    try:
                        remove_upgrade(u["upgrade_id"])
                        self._show_toast("Upgrade removed.")
                    except Exception as e:
                        self._show_toast(str(e), error=True)

        return None
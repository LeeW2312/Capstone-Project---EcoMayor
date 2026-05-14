"""
EcoCity Mayor — screens/quiz_screen.py
Quiz with pollution tips, question categories, XP, streak bonuses.
"""

import pygame
import json
import os
import random

from sounds    import SoundManager
from game_data import XP_REWARDS, ECO_TIPS

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
PURPLE      = (145, 85,  215)
ORANGE      = (230, 140, 40)

SCREEN_W, SCREEN_H = 900, 600
POINTS_PER_CORRECT = 30

CATEGORY_COLOURS = {
    "Air":       (78,  144, 217),
    "Water":     (50,  180, 230),
    "Nature":    (72,  200, 118),
    "Energy":    (236, 190, 50),
    "Climate":   (215, 65,  65),
    "Recycling": (145, 85,  215),
}

# Tips shown after wrong answers, keyed by category
CATEGORY_TIPS = {
    "Air":     "Air pollution from vehicles and factories causes serious health problems. Use public transport to help!",
    "Water":   "Only 3% of Earth's water is fresh water. Proper waste disposal prevents water pollution.",
    "Nature":  "Trees absorb CO2 and produce oxygen. Protecting forests is vital for our climate.",
    "Energy":  "Solar and wind energy produce zero emissions. Switching to renewables reduces pollution significantly.",
    "Climate": "Carbon dioxide from burning fuels is the main driver of climate change. Reducing emissions helps.",
    "Recycling":"Recycling saves natural resources and energy. One recycled can saves enough energy for 3 hours of TV.",
}


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
        draw_text(surf, text, font, TEXT_DIM,
                  r.centerx, r.centery, center=True)
    elif hovered:
        pygame.draw.rect(surf, ACCENT, r, border_radius=8)
        pygame.draw.rect(surf, WHITE,  r, 1, border_radius=8)
        draw_text(surf, text, font, WHITE,
                  r.centerx, r.centery, center=True)
    else:
        pygame.draw.rect(surf, ACCENT_DARK, r, border_radius=8)
        pygame.draw.rect(surf, ACCENT,      r, 1, border_radius=8)
        draw_text(surf, text, font, TEXT,
                  r.centerx, r.centery, center=True)


class QuizScreen:
    def __init__(self, screen, fonts, game_state):
        self.screen = screen
        self.fonts  = fonts
        self.state  = game_state

        self.btn_back = pygame.Rect(20, 15, 90, 34)

        self.questions   = self._load_questions()
        random.shuffle(self.questions)
        self.current_idx = 0

        self.answered     = False
        self.chosen_idx   = -1
        self.correct_idx  = -1
        self.feedback     = ""
        self.feedback_col = WHITE
        self.next_timer   = 0
        self.eco_tip      = ""   # shown after wrong answer

        self.answer_rects = [
            pygame.Rect(100, 330, 320, 52),
            pygame.Rect(480, 330, 320, 52),
            pygame.Rect(100, 396, 320, 52),
            pygame.Rect(480, 396, 320, 52),
        ]

    def _load_questions(self):
        path = os.path.join("data", "quizzes.json")
        with open(path) as f:
            quizzes = json.load(f)
        all_q = []
        for quiz in quizzes:
            for q in quiz["questions"]:
                all_q.append(q)
        return all_q

    def _current_question(self):
        if self.current_idx < len(self.questions):
            return self.questions[self.current_idx]
        return None

    def _load_next(self):
        self.current_idx += 1
        self.answered    = False
        self.chosen_idx  = -1
        self.correct_idx = -1
        self.feedback    = ""
        self.eco_tip     = ""
        self.next_timer  = 0

    def _award_xp(self, reason):
        gain = XP_REWARDS.get(reason, 0)
        if gain > 0:
            self.state["xp"] = self.state.get("xp", 0) + gain

    def _update_challenge(self, ctype, amount=1):
        challenges = self.state.get("daily_challenges", [])
        progress   = self.state.get("daily_progress", {})
        completed  = self.state.get("daily_completed", [])
        for c in challenges:
            if c["id"] in completed or c["type"] != ctype:
                continue
            progress[c["id"]] = progress.get(c["id"], 0) + amount
            if progress[c["id"]] >= c["goal"]:
                completed.append(c["id"])
                self.state["points"]      += c["reward"]
                self.state["total_earned"] = \
                    self.state.get("total_earned", 0) + c["reward"]
                SoundManager.play("achievement")
        self.state["daily_progress"] = progress
        self.state["daily_completed"] = completed

    def draw(self):
        s     = self.screen
        mouse = pygame.mouse.get_pos()
        s.fill(BG)

        pygame.draw.rect(s, PANEL, (0, 0, SCREEN_W, 60))
        pygame.draw.line(s, BORDER, (0, 60), (SCREEN_W, 60), 1)
        draw_text(s, "Eco Quiz  --  Answer correctly to earn points",
                  self.fonts["body"], GREEN,
                  SCREEN_W // 2, 18, center=True)
        draw_text(s, f"Points: {self.state['points']}",
                  self.fonts["small"], GOLD, SCREEN_W-150, 10)
        draw_text(s, f"Day {self.state['day']} / 30",
                  self.fonts["small"], TEXT, SCREEN_W-150, 30)
        draw_button(s, self.fonts["small"], "Back",
                    self.btn_back, self.btn_back.collidepoint(mouse))

        q = self._current_question()

        if not q:
            pygame.draw.rect(s, PANEL, (150, 220, 600, 120),
                             border_radius=12)
            pygame.draw.rect(s, BORDER, (150, 220, 600, 120),
                             1, border_radius=12)
            draw_text(s, "All questions answered!",
                      self.fonts["body"], GREEN,
                      SCREEN_W // 2, 260, center=True)
            draw_text(s, "Press Back to return to the city.",
                      self.fonts["small"], TEXT_DIM,
                      SCREEN_W // 2, 295, center=True)
            return

        total = len(self.questions)
        draw_text(s, f"Question  {self.current_idx+1}  of  {total}",
                  self.fonts["tiny"], TEXT_DIM,
                  SCREEN_W//2, 74, center=True)

        # Progress bar
        prog_w = int(700*(self.current_idx+1)/max(total,1))
        pygame.draw.rect(s, BORDER, (100,84,700,8), border_radius=4)
        if prog_w > 0:
            pygame.draw.rect(s, ACCENT, (100,84,prog_w,8), border_radius=4)

        # Category badge
        cat     = q.get("category", "")
        cat_col = CATEGORY_COLOURS.get(cat, ACCENT)
        if cat:
            cb = self.fonts["tiny"].render(f" {cat} ", True, cat_col)
            cb_rect = pygame.Rect(SCREEN_W-cb.get_width()-28, 66,
                                  cb.get_width()+16, 18)
            pygame.draw.rect(s,
                             tuple(c//5 for c in cat_col),
                             cb_rect, border_radius=5)
            pygame.draw.rect(s, cat_col, cb_rect, 1, border_radius=5)
            s.blit(cb, (cb_rect.x+8, cb_rect.y+1))

        # Streak
        streak = self.state.get("correct_answers", 0)
        if streak > 1:
            sc = GOLD if streak < 5 else ORANGE
            draw_text(s, f"Streak: {streak}x  {'🔥' if streak>=5 else ''}",
                      self.fonts["small"], sc, 100, 100)
        if streak >= 5:
            draw_text(s, "DOUBLE POINTS ACTIVE!",
                      self.fonts["tiny"], ORANGE, 100, 118)

        # Question card
        pygame.draw.rect(s, PANEL, (80, 108, 740, 120), border_radius=12)
        pygame.draw.rect(s, BORDER, (80, 108, 740, 120), 1, border_radius=12)

        words    = q["question_text"].split()
        lines    = []
        cur_line = ""
        for word in words:
            test = (cur_line+" "+word).strip()
            if self.fonts["body"].size(test)[0] < 680:
                cur_line = test
            else:
                lines.append(cur_line)
                cur_line = word
        lines.append(cur_line)
        start_y = 128 if len(lines) == 1 else 114
        for i, line in enumerate(lines):
            draw_text(s, line, self.fonts["body"], TEXT,
                      SCREEN_W//2, start_y+i*26, center=True)

        # Answer buttons
        for i, (ans, rect) in enumerate(
                zip(q["answers"], self.answer_rects)):
            if self.answered:
                if i == self.correct_idx:
                    col, bc = (20,100,40), GREEN
                elif i == self.chosen_idx:
                    col, bc = (100,20,20), RED
                else:
                    col, bc = (30,30,50), BORDER
                pygame.draw.rect(s, col, rect, border_radius=8)
                pygame.draw.rect(s, bc,  rect, 1, border_radius=8)
            else:
                hov = rect.collidepoint(mouse)
                pygame.draw.rect(s,
                                 ACCENT_DARK if hov else (30,30,50),
                                 rect, border_radius=8)
                pygame.draw.rect(s,
                                 ACCENT if hov else BORDER,
                                 rect, 1, border_radius=8)
            draw_text(s, ans["answer_text"], self.fonts["small"],
                      TEXT, rect.centerx, rect.centery, center=True)

        # Feedback
        if self.feedback:
            draw_text(s, self.feedback, self.fonts["body"],
                      self.feedback_col,
                      SCREEN_W//2, 462, center=True)

        # Eco tip after wrong answer
        if self.eco_tip:
            tip_surf = pygame.Surface((SCREEN_W-100, 50), pygame.SRCALPHA)
            tip_surf.fill((10,40,10,180))
            s.blit(tip_surf, (50, 478))
            pygame.draw.rect(s, (40,80,40), (50,478,SCREEN_W-100,50),
                             1, border_radius=6)
            # Word-wrap the tip
            words2   = self.eco_tip.split()
            tip_line = ""; tip_lines = []
            for w in words2:
                test = (tip_line+" "+w).strip()
                if self.fonts["tiny"].size(test)[0] < SCREEN_W-120:
                    tip_line = test
                else:
                    tip_lines.append(tip_line)
                    tip_line = w
            tip_lines.append(tip_line)
            for i, tl in enumerate(tip_lines[:2]):
                draw_text(s, tl, self.fonts["tiny"], GREEN,
                          SCREEN_W//2, 492+i*18, center=True)

        if self.answered:
            draw_text(s, "Next question loading...",
                      self.fonts["tiny"], TEXT_DIM,
                      SCREEN_W//2, 534, center=True)

    def handle_event(self, event):
        if self.answered:
            if pygame.time.get_ticks() >= self.next_timer:
                self._load_next()
            return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            if self.btn_back.collidepoint(pos):
                SoundManager.play("back")
                return "back"

            q = self._current_question()
            if not q:
                return None

            for i, (ans, rect) in enumerate(
                    zip(q["answers"], self.answer_rects)):
                if rect.collidepoint(pos):
                    self.answered   = True
                    self.chosen_idx = i
                    self.next_timer = pygame.time.get_ticks() + 2200

                    for j, a in enumerate(q["answers"]):
                        if a["is_correct"]:
                            self.correct_idx = j
                            break

                    if ans["is_correct"]:
                        streak = self.state.get("correct_answers",0)+1
                        self.state["correct_answers"] = streak

                        # Double points at streak 5+
                        pts = POINTS_PER_CORRECT * (2 if streak >= 5 else 1)
                        self.state["points"]      += pts
                        self.state["total_earned"] = \
                            self.state.get("total_earned",0) + pts

                        self.feedback = (
                            f"Correct!  +{pts} pts"
                            + ("  (2x streak bonus!)" if streak>=5 else ""))
                        self.feedback_col = GREEN

                        # Streak sounds
                        if streak >= 5:
                            SoundManager.play("streak")
                        else:
                            SoundManager.play("correct")

                        # XP
                        self._award_xp("correct")
                        if streak >= 5:
                            self._award_xp("streak_5")

                        # Free upgrade at 10x streak
                        if streak == 10:
                            self.state["points"] += 150
                            self.feedback += "  FREE 150 pts for 10x streak!"

                        # Update challenges
                        self._update_challenge("correct", 1)
                        self._update_challenge("streak",  streak)
                        self._update_challenge("points",  pts)

                    else:
                        self.state["correct_answers"] = 0
                        self.feedback     = "Wrong answer!"
                        self.feedback_col = RED
                        SoundManager.play("wrong")

                        # Show eco tip related to question category
                        cat = q.get("category", "")
                        self.eco_tip = CATEGORY_TIPS.get(
                            cat,
                            random.choice(ECO_TIPS))

                    break

        return None
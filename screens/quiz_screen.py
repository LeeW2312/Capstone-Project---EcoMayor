"""
EcoCity Mayor — screens/quiz_screen.py
Quiz screen — answer questions to earn points
"""

import pygame
import json
import os
import random

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
POINTS_PER_CORRECT = 30


def draw_text(surf, text, font, color, x, y, center=False):
    img = font.render(str(text), True, color)
    r   = img.get_rect()
    if center:
        r.center = (x, y)
    else:
        r.topleft = (x, y)
    surf.blit(img, r)

def draw_button(surf, font, text, rect, hovered, active=True, col=None):
    r = pygame.Rect(rect)
    if col:
        pygame.draw.rect(surf, col, r, border_radius=8)
        pygame.draw.rect(surf, WHITE, r, 1, border_radius=8)
        draw_text(surf, text, font, WHITE, r.centerx, r.centery, center=True)
    elif not active:
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


class QuizScreen:
    def __init__(self, screen, fonts, game_state):
        self.screen  = screen
        self.fonts   = fonts
        self.state   = game_state

        self.btn_back = pygame.Rect(20, 15, 90, 34)

        self.questions   = self._load_questions()
        self.current_idx = 0
        random.shuffle(self.questions)

        self.answered     = False
        self.chosen_idx   = -1
        self.correct_idx  = -1
        self.feedback_msg = ""
        self.feedback_col = WHITE
        self.next_timer   = 0

        self.answer_rects = []
        self._build_layout()

    def _load_questions(self):
        path = os.path.join("data", "quizzes.json")
        quizzes = []
        with open(path) as f:
            quizzes = json.load(f)
        all_q = []
        for quiz in quizzes:
            for q in quiz["questions"]:
                all_q.append(q)
        return all_q

    def _build_layout(self):
        self.answer_rects = [
            pygame.Rect(100, 320, 320, 55),
            pygame.Rect(480, 320, 320, 55),
            pygame.Rect(100, 390, 320, 55),
            pygame.Rect(480, 390, 320, 55),
        ]

    def _current_question(self):
        if not self.questions:
            return None
        return self.questions[self.current_idx % len(self.questions)]

    def _load_next(self):
        self.current_idx += 1
        self.answered     = False
        self.chosen_idx   = -1
        self.correct_idx  = -1
        self.feedback_msg = ""
        self.next_timer   = 0
        # Advance game day
        self.state["day"] = min(self.state["day"] + 1, 30)

    def draw(self):
        s = self.screen
        s.fill(BG)

        # Top bar
        pygame.draw.rect(s, PANEL, (0, 0, SCREEN_W, 60))
        pygame.draw.line(s, BORDER, (0, 60), (SCREEN_W, 60), 1)
        draw_text(s, "Quiz — Answer to earn points",
                  self.fonts["body"], GREEN, SCREEN_W//2, 18, center=True)
        draw_text(s, f"Points: {self.state['points']}",
                  self.fonts["small"], GOLD, SCREEN_W - 150, 22)

        mouse = pygame.mouse.get_pos()
        draw_button(s, self.fonts["small"], "Back",
                    self.btn_back, self.btn_back.collidepoint(mouse))

        q = self._current_question()
        if not q:
            draw_text(s, "No questions available. Ask a Moderator to add some!",
                      self.fonts["body"], TEXT_DIM, SCREEN_W//2, 300, center=True)
            return

        # Question panel
        pygame.draw.rect(s, PANEL, (80, 90, 740, 110), border_radius=12)
        pygame.draw.rect(s, BORDER, (80, 90, 740, 110), 1, border_radius=12)

        # Wrap long question text
        words    = q["question_text"].split()
        lines    = []
        cur_line = ""
        for w in words:
            test = (cur_line + " " + w).strip()
            if self.fonts["body"].size(test)[0] < 680:
                cur_line = test
            else:
                lines.append(cur_line)
                cur_line = w
        lines.append(cur_line)

        start_y = 110 if len(lines) == 1 else 100
        for i, line in enumerate(lines):
            draw_text(s, line, self.fonts["body"], TEXT,
                      SCREEN_W//2, start_y + i*26, center=True)

        # Question counter
        total = len(self.questions)
        draw_text(s, f"Question {(self.current_idx % total) + 1} of {total}",
                  self.fonts["tiny"], TEXT_DIM, SCREEN_W//2, 190, center=True)

        # Shuffle answers display order (fixed per question)
        answers = q["answers"]

        for i, (ans, rect) in enumerate(zip(answers, self.answer_rects)):
            if self.answered:
                if i == self.correct_idx:
                    col = (20, 100, 40)
                    border_c = GREEN
                elif i == self.chosen_idx:
                    col = (100, 20, 20)
                    border_c = RED
                else:
                    col = (30, 30, 50)
                    border_c = BORDER
                pygame.draw.rect(s, col, rect, border_radius=8)
                pygame.draw.rect(s, border_c, rect, 1, border_radius=8)
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
        if self.feedback_msg:
            draw_text(s, self.feedback_msg, self.fonts["body"],
                      self.feedback_col, SCREEN_W//2, 470, center=True)

        if self.answered:
            draw_text(s, "Next question loading...",
                      self.fonts["tiny"], TEXT_DIM,
                      SCREEN_W//2, 510, center=True)

    def handle_event(self, event):
        # Auto advance after answering
        if self.answered:
            now = pygame.time.get_ticks()
            if now >= self.next_timer:
                self._load_next()
            return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            if self.btn_back.collidepoint(pos):
                return "back"

            q = self._current_question()
            if not q:
                return None

            for i, (ans, rect) in enumerate(
                    zip(q["answers"], self.answer_rects)):
                if rect.collidepoint(pos):
                    self.answered    = True
                    self.chosen_idx  = i
                    self.next_timer  = pygame.time.get_ticks() + 1800

                    # Find correct answer index
                    for j, a in enumerate(q["answers"]):
                        if a["is_correct"]:
                            self.correct_idx = j
                            break

                    if ans["is_correct"]:
                        self.state["points"] += POINTS_PER_CORRECT
                        self.feedback_msg = f"Correct! +{POINTS_PER_CORRECT} points"
                        self.feedback_col = GREEN
                    else:
                        self.feedback_msg = "Wrong answer. No points earned."
                        self.feedback_col = RED
                    break
        return None
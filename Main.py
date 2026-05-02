"""
EcoCity Mayor — main.py
Main entry point. Run with: python main.py
"""

import pygame
import sys
import json
import os

SCREEN_W, SCREEN_H = 900, 600
FPS   = 60
TITLE = "EcoCity Mayor"

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

DATA_DIR   = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")


def load_json(path):
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def ensure_data():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(USERS_FILE):
        save_json(USERS_FILE, [
            {"user_id":1,"username":"player1","password":"1234","role":"Player"},
            {"user_id":2,"username":"mod1",   "password":"1234","role":"Moderator"},
            {"user_id":3,"username":"admin1", "password":"1234","role":"Admin"},
        ])

    for fname in ("quizzes.json", "upgrades.json"):
        path = os.path.join(DATA_DIR, fname)
        if not os.path.exists(path):
            save_json(path, [])

    upg_path = os.path.join(DATA_DIR, "upgrades.json")
    if not load_json(upg_path):
        save_json(upg_path, [
            {"upgrade_id":1,"upgrade_name":"Plant Trees",
             "pollution_reduction":5.0,"cost_points":50},
            {"upgrade_id":2,"upgrade_name":"Install Solar Panels",
             "pollution_reduction":10.0,"cost_points":120},
            {"upgrade_id":3,"upgrade_name":"Build Recycling Center",
             "pollution_reduction":8.0,"cost_points":90},
            {"upgrade_id":4,"upgrade_name":"Clean River",
             "pollution_reduction":6.0,"cost_points":70},
        ])

    quiz_path = os.path.join(DATA_DIR, "quizzes.json")
    if not load_json(quiz_path):
        save_json(quiz_path, [
            {"quiz_id":1,"quiz_title":"Environmental Awareness Quiz",
             "created_by":2,"created_at":"2026-05-01 10:00:00",
             "questions":[
                {"question_id":1,
                 "question_text":"What is the main cause of air pollution in cities?",
                 "answers":[
                    {"answer_id":1,"answer_text":"Factories and vehicles","is_correct":True},
                    {"answer_id":2,"answer_text":"Rainfall","is_correct":False},
                    {"answer_id":3,"answer_text":"Trees","is_correct":False},
                    {"answer_id":4,"answer_text":"Sunlight","is_correct":False},
                 ]},
                {"question_id":2,
                 "question_text":"Which action helps reduce water pollution?",
                 "answers":[
                    {"answer_id":1,"answer_text":"Proper waste disposal","is_correct":True},
                    {"answer_id":2,"answer_text":"Dumping waste in rivers","is_correct":False},
                    {"answer_id":3,"answer_text":"Using more plastic bags","is_correct":False},
                    {"answer_id":4,"answer_text":"Burning garbage","is_correct":False},
                 ]},
                {"question_id":3,
                 "question_text":"What does planting trees help reduce?",
                 "answers":[
                    {"answer_id":1,"answer_text":"Air pollution","is_correct":True},
                    {"answer_id":2,"answer_text":"Water levels","is_correct":False},
                    {"answer_id":3,"answer_text":"Electricity usage","is_correct":False},
                    {"answer_id":4,"answer_text":"Soil minerals","is_correct":False},
                 ]},
                {"question_id":4,
                 "question_text":"Which energy source is most eco-friendly?",
                 "answers":[
                    {"answer_id":1,"answer_text":"Solar power","is_correct":True},
                    {"answer_id":2,"answer_text":"Coal","is_correct":False},
                    {"answer_id":3,"answer_text":"Diesel","is_correct":False},
                    {"answer_id":4,"answer_text":"Natural gas","is_correct":False},
                 ]},
             ]}
        ])


def draw_text(surf, text, font, color, x, y, center=False):
    img = font.render(str(text), True, color)
    r   = img.get_rect()
    if center:
        r.center = (x, y)
    else:
        r.topleft = (x, y)
    surf.blit(img, r)
    return r

def draw_rect_border(surf, color, rect, radius=8, border=1, border_color=BORDER):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)

def draw_button(surf, font, text, rect, hovered, active=True):
    r = pygame.Rect(rect)
    if not active:
        pygame.draw.rect(surf, (40, 40, 60), r, border_radius=8)
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
    return r


class InputBox:
    def __init__(self, x, y, w, h, placeholder="", secret=False):
        self.rect        = pygame.Rect(x, y, w, h)
        self.text        = ""
        self.active      = False
        self.placeholder = placeholder
        self.secret      = secret

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key not in (pygame.K_RETURN, pygame.K_TAB):
                if len(self.text) < 24:
                    self.text += event.unicode

    def draw(self, surf, font):
        border_col = ACCENT if self.active else BORDER
        pygame.draw.rect(surf, PANEL, self.rect, border_radius=8)
        pygame.draw.rect(surf, border_col, self.rect, 1, border_radius=8)
        if self.text:
            display = ("*" * len(self.text)) if self.secret else self.text
            draw_text(surf, display, font, TEXT,
                      self.rect.x + 12,
                      self.rect.centery - font.get_height() // 2)
        else:
            draw_text(surf, self.placeholder, font, TEXT_DIM,
                      self.rect.x + 12,
                      self.rect.centery - font.get_height() // 2)
        if self.active and (pygame.time.get_ticks() // 500) % 2 == 0:
            display = ("*" * len(self.text)) if self.secret else self.text
            tw = font.size(display)[0]
            cx  = self.rect.x + 12 + tw + 2
            cy1 = self.rect.centery - font.get_height() // 2 + 2
            cy2 = self.rect.centery + font.get_height() // 2 - 2
            pygame.draw.line(surf, ACCENT, (cx, cy1), (cx, cy2), 2)


class LoginScreen:
    def __init__(self, screen, fonts):
        self.screen   = screen
        self.fonts    = fonts
        self.user_box = InputBox(320, 240, 260, 42, placeholder="Username")
        self.pass_box = InputBox(320, 300, 260, 42,
                                 placeholder="Password", secret=True)
        self.error      = ""
        self.login_rect = pygame.Rect(320, 362, 260, 44)
        import random
        random.seed(42)
        self.buildings = []
        x = 0
        while x < SCREEN_W:
            w = random.randint(40, 90)
            h = random.randint(60, 160)
            self.buildings.append((x, SCREEN_H - h, w, h))
            x += w + random.randint(2, 8)

    def handle_event(self, event):
        self.user_box.handle_event(event)
        self.pass_box.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            return self._try_login()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.login_rect.collidepoint(event.pos):
                return self._try_login()
        return None

    def _try_login(self):
        users = load_json(USERS_FILE)
        for u in users:
            if (u["username"] == self.user_box.text and
                    u["password"] == self.pass_box.text):
                return u
        self.error = "Invalid username or password."
        self.pass_box.text = ""
        return None

    def draw(self):
        s = self.screen
        s.fill(BG)
        for (bx, by, bw, bh) in self.buildings:
            pygame.draw.rect(s, (18, 25, 50), (bx, by, bw, bh))
            for wy in range(by + 8, by + bh - 8, 16):
                for wx in range(bx + 6, bx + bw - 6, 14):
                    col = (80,120,180) if (wx+wy)%3!=0 else (30,30,50)
                    pygame.draw.rect(s, col, (wx, wy, 6, 8))
        smog = pygame.Surface((SCREEN_W, 180), pygame.SRCALPHA)
        smog.fill((60, 40, 20, 60))
        s.blit(smog, (0, 0))
        panel_rect = pygame.Rect(260, 160, 380, 310)
        draw_rect_border(s, PANEL, panel_rect, radius=12)
        draw_text(s, "EcoCity Mayor", self.fonts["title"],
                  GREEN, SCREEN_W//2, 190, center=True)
        draw_text(s, "Sign in to continue", self.fonts["small"],
                  TEXT_DIM, SCREEN_W//2, 218, center=True)
        draw_text(s, "Username", self.fonts["small"], TEXT_DIM, 320, 222)
        draw_text(s, "Password", self.fonts["small"], TEXT_DIM, 320, 282)
        self.user_box.draw(s, self.fonts["body"])
        self.pass_box.draw(s, self.fonts["body"])
        mouse = pygame.mouse.get_pos()
        draw_button(s, self.fonts["body"], "Login",
                    self.login_rect, self.login_rect.collidepoint(mouse))
        if self.error:
            draw_text(s, self.error, self.fonts["small"], RED,
                      SCREEN_W//2, 418, center=True)
        draw_text(s, "Accounts: player1 / mod1 / admin1  |  password: 1234",
                  self.fonts["tiny"], TEXT_DIM, SCREEN_W//2, 448, center=True)


def make_fonts():
    return {
        "title": pygame.font.SysFont("segoeui", 32),
        "body":  pygame.font.SysFont("segoeui", 18),
        "small": pygame.font.SysFont("segoeui", 14),
        "tiny":  pygame.font.SysFont("segoeui", 12),
    }


def main():
    ensure_data()
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock  = pygame.time.Clock()
    fonts  = make_fonts()

    from screens.game_screen       import GameScreen
    from screens.quiz_screen       import QuizScreen
    from screens.shop_screen       import ShopScreen
    from screens.moderator_screen  import ModeratorScreen

    login_screen   = LoginScreen(screen, fonts)
    current_screen = login_screen
    game_state     = None
    active_view    = "login"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            result = current_screen.handle_event(event)

            if active_view == "login":
                if isinstance(result, dict) and "role" in result:
                    game_state = {
                        "pollution": 100.0,
                        "points":    0,
                        "day":       1,
                        "user":      result,
                    }
                    current_screen = GameScreen(screen, fonts, game_state)
                    active_view    = "game"

            elif active_view == "game":
                if result == "quiz":
                    current_screen = QuizScreen(screen, fonts, game_state)
                    active_view    = "quiz"
                elif result == "shop":
                    current_screen = ShopScreen(screen, fonts, game_state)
                    active_view    = "shop"
                elif result == "moderator":
                    current_screen = ModeratorScreen(screen, fonts, game_state)
                    active_view    = "moderator"
                elif result == "logout":
                    game_state     = None
                    login_screen   = LoginScreen(screen, fonts)
                    current_screen = login_screen
                    active_view    = "login"

            elif active_view in ("quiz", "shop", "moderator"):
                if result == "back":
                    current_screen = GameScreen(screen, fonts, game_state)
                    active_view    = "game"
                elif result == "logout":
                    game_state     = None
                    login_screen   = LoginScreen(screen, fonts)
                    current_screen = login_screen
                    active_view    = "login"

        current_screen.draw()
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
"""
EcoCity Mayor — main.py  (SQLite version)
Run with: python main.py
All data saved to: data/ecocity.db
"""

import pygame
import sys
import os
import random

from database import (
    init_db,
    get_all_users, get_user, save_user, register_user,
    load_player_pollution, save_player_pollution,
    save_player_progress, save_season_result,
    get_leaderboard, get_all_quizzes, get_all_upgrades,
    log_activity,
)
init_db()

SCREEN_W, SCREEN_H = 900, 600
FPS   = 120
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

DATA_DIR      = "data"
USERS_FILE    = os.path.join(DATA_DIR, "users.json")
QUIZ_FILE     = os.path.join(DATA_DIR, "quizzes.json")
UPGRADE_FILE  = os.path.join(DATA_DIR, "upgrades.json")
LEADER_FILE   = os.path.join(DATA_DIR, "leaderboard.json")
ACTIVITY_FILE = os.path.join(DATA_DIR, "activity_log.json")


def load_json(path):
    name = os.path.basename(path)
    if name == "users.json":
        return get_all_users()
    if name == "quizzes.json":
        return get_all_quizzes()
    if name == "upgrades.json":
        return get_all_upgrades()
    if name == "leaderboard.json":
        return get_leaderboard()
    if name == "activity_log.json":
        from database import get_activity_log
        return get_activity_log()
    import json
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return []


def save_json(path, data):
    name = os.path.basename(path)
    if name == "users.json":
        for u in (data if isinstance(data, list) else []):
            save_user(u)
        return
    if name in ("leaderboard.json", "activity_log.json"):
        return
    import json
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _save_player_pollution(username, pollution):
    save_player_pollution(username, pollution)


def _load_player_pollution(username):
    return load_player_pollution(username)


def _save_player_progress(game_state):
    save_player_progress(game_state)


def ensure_data():
    init_db()


def draw_text(surf, text, font, color, x, y, center=False):
    img = font.render(str(text), True, color)
    r   = img.get_rect()
    if center:
        r.center = (x, y)
    else:
        r.topleft = (x, y)
    surf.blit(img, r)
    return r

def draw_rect_border(surf, color, rect, radius=8,
                     border=1, border_color=BORDER):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)

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
                if len(self.text) < 30:
                    self.text += event.unicode

    def draw(self, surf, font):
        bc = ACCENT if self.active else BORDER
        pygame.draw.rect(surf, PANEL, self.rect, border_radius=8)
        pygame.draw.rect(surf, bc, self.rect, 1, border_radius=8)
        display = ("*" * len(self.text)) if self.secret and self.text else self.text
        if display:
            draw_text(surf, display, font, TEXT,
                      self.rect.x+12, self.rect.centery - font.get_height()//2)
        else:
            draw_text(surf, self.placeholder, font, TEXT_DIM,
                      self.rect.x+12, self.rect.centery - font.get_height()//2)
        if self.active and (pygame.time.get_ticks()//500) % 2 == 0:
            tw  = font.size(display)[0]
            cx  = self.rect.x + 12 + tw + 2
            cy1 = self.rect.centery - font.get_height()//2 + 2
            cy2 = self.rect.centery + font.get_height()//2 - 2
            pygame.draw.line(surf, ACCENT, (cx,cy1), (cx,cy2), 2)


class LoginScreen:
    def __init__(self, screen, fonts):
        self.screen     = screen
        self.fonts      = fonts
        self.user_box   = InputBox(320, 230, 260, 42, placeholder="Username")
        self.pass_box   = InputBox(320, 288, 260, 42, placeholder="Password", secret=True)
        self.error      = ""
        self.login_rect = pygame.Rect(320, 350, 124, 44)
        self.reg_rect   = pygame.Rect(456, 350, 124, 44)

        random.seed(42)
        self.buildings = []
        x = 0
        while x < SCREEN_W:
            w = random.randint(40, 90)
            h = random.randint(60, 160)
            self.buildings.append((x, SCREEN_H-h, w, h))
            x += w + random.randint(2, 8)

    def handle_event(self, event):
        self.user_box.handle_event(event)
        self.pass_box.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            return self._try_login()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.login_rect.collidepoint(event.pos):
                return self._try_login()
            if self.reg_rect.collidepoint(event.pos):
                return "register"
        return None

    def _try_login(self):
        u = get_user(self.user_box.text)
        if u and u["password"] == self.pass_box.text:
            if u.get("banned"):
                self.error = "Account banned. Contact admin."
                return None
            log_activity(u["username"], "LOGIN")
            return u
        self.error = "Invalid username or password."
        self.pass_box.text = ""
        return None

    def draw(self):
        s = self.screen
        s.fill(BG)
        for (bx, by, bw, bh) in self.buildings:
            pygame.draw.rect(s, (18,25,50), (bx,by,bw,bh))
            for wy in range(by+8, by+bh-8, 16):
                for wx in range(bx+6, bx+bw-6, 14):
                    col = (80,120,180) if (wx+wy)%3!=0 else (30,30,50)
                    pygame.draw.rect(s, col, (wx,wy,6,8))
        smog = pygame.Surface((SCREEN_W,200), pygame.SRCALPHA)
        smog.fill((60,40,20,60))
        s.blit(smog, (0,0))
        panel = pygame.Rect(255, 148, 390, 330)
        draw_rect_border(s, PANEL, panel, radius=12)
        draw_text(s, "EcoCity Mayor", self.fonts["title"],
                  GREEN, SCREEN_W//2, 178, center=True)
        draw_text(s, "Sign in to manage your city",
                  self.fonts["small"], TEXT_DIM, SCREEN_W//2, 206, center=True)
        draw_text(s, "Username", self.fonts["small"], TEXT_DIM, 320, 212)
        draw_text(s, "Password", self.fonts["small"], TEXT_DIM, 320, 270)
        self.user_box.draw(s, self.fonts["body"])
        self.pass_box.draw(s, self.fonts["body"])
        mouse = pygame.mouse.get_pos()
        draw_button(s, self.fonts["body"], "Login",
                    self.login_rect, self.login_rect.collidepoint(mouse))
        draw_button(s, self.fonts["body"], "Register",
                    self.reg_rect, self.reg_rect.collidepoint(mouse))
        if self.error:
            draw_text(s, self.error, self.fonts["small"], RED,
                      SCREEN_W//2, 406, center=True)
        draw_text(s, "player1 / mod1 / admin1  |  password: 1234",
                  self.fonts["tiny"], TEXT_DIM, SCREEN_W//2, 448, center=True)


class RegisterScreen:
    def __init__(self, screen, fonts):
        self.screen    = screen
        self.fonts     = fonts
        self.user_box  = InputBox(320, 220, 260, 42, placeholder="Username")
        self.pass_box  = InputBox(320, 278, 260, 42, placeholder="Password", secret=True)
        self.conf_box  = InputBox(320, 336, 260, 42, placeholder="Confirm Password", secret=True)
        self.error     = ""
        self.ok_rect   = pygame.Rect(320, 398, 124, 44)
        self.back_rect = pygame.Rect(456, 398, 124, 44)

    def handle_event(self, event):
        self.user_box.handle_event(event)
        self.pass_box.handle_event(event)
        self.conf_box.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.ok_rect.collidepoint(event.pos):
                return self._try_register()
            if self.back_rect.collidepoint(event.pos):
                return "back"
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            return self._try_register()
        return None

    def _try_register(self):
        u = self.user_box.text.strip()
        p = self.pass_box.text
        c = self.conf_box.text
        if not u:
            self.error = "Username cannot be empty."; return None
        if len(p) < 4:
            self.error = "Password must be at least 4 characters."; return None
        if p != c:
            self.error = "Passwords do not match."; return None
        new_user = register_user(u, p)
        if new_user is None:
            self.error = "Username already taken."; return None
        return new_user

    def draw(self):
        s = self.screen
        s.fill(BG)
        panel = pygame.Rect(255, 148, 390, 330)
        draw_rect_border(s, PANEL, panel, radius=12)
        draw_text(s, "Create Account", self.fonts["title"],
                  GREEN, SCREEN_W//2, 175, center=True)
        draw_text(s, "Username",  self.fonts["small"], TEXT_DIM, 320, 202)
        draw_text(s, "Password",  self.fonts["small"], TEXT_DIM, 320, 260)
        draw_text(s, "Confirm",   self.fonts["small"], TEXT_DIM, 320, 318)
        self.user_box.draw(s, self.fonts["body"])
        self.pass_box.draw(s, self.fonts["body"])
        self.conf_box.draw(s, self.fonts["body"])
        mouse = pygame.mouse.get_pos()
        draw_button(s, self.fonts["body"], "Register",
                    self.ok_rect, self.ok_rect.collidepoint(mouse))
        draw_button(s, self.fonts["body"], "Back",
                    self.back_rect, self.back_rect.collidepoint(mouse))
        if self.error:
            draw_text(s, self.error, self.fonts["small"], RED,
                      SCREEN_W//2, 452, center=True)


def make_fonts():
    return {
        "title": pygame.font.SysFont("segoeui", 32),
        "body":  pygame.font.SysFont("segoeui", 18),
        "small": pygame.font.SysFont("segoeui", 14),
        "tiny":  pygame.font.SysFont("segoeui", 12),
    }


def fresh_game_state(user):
    from game_data import pick_daily_challenges
    challenges = pick_daily_challenges(3)
    return {
        "pollution":          100.0,
        "points":             0,
        "day":                1,
        "user":               user,
        "achievements":       [],
        "total_earned":       0,
        "upgrades_bought":    0,
        "correct_answers":    0,
        "season_history":     [],
        "xp":                 user.get("xp", 0),
        "level":              user.get("level", 1),
        "difficulty":         user.get("difficulty", "medium"),
        "daily_challenges":   challenges,
        "daily_progress":     {c["id"]: 0 for c in challenges},
        "daily_completed":    [],
        "pollution_history":  user.get("pollution_history", []),
        "start_pollution":    None,
        "max_pollution":      0,
        "disasters_survived": 0,
        "shop_spent":         0,
        "perfect_streak":     0,
    }


def _do_logout(game_state, fonts, screen):
    from sounds import SoundManager
    if game_state:
        _save_player_progress(game_state)
    log_activity(
        game_state["user"]["username"] if game_state else "unknown",
        "LOGOUT"
    )
    SoundManager.play("logout")
    SoundManager.stop_music()
    return LoginScreen(screen, fonts)


def _screen_for_role(role, screen, fonts, game_state):
    from screens.game_screen      import GameScreen
    from screens.moderator_screen import ModeratorScreen
    from screens.admin_screen     import AdminScreen

    if role == "Admin":
        return AdminScreen(screen, fonts, game_state), "admin"
    elif role == "Moderator":
        return ModeratorScreen(screen, fonts, game_state), "moderator"
    else:
        return GameScreen(screen, fonts, game_state), "game"


def main():
    ensure_data()
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock  = pygame.time.Clock()
    fonts  = make_fonts()

    from sounds import SoundManager
    SoundManager.init()

    from screens.loading_screen import LoadingScreen
    loader = LoadingScreen(screen, fonts)
    while not loader.done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        loader.update()
        loader.draw()
        pygame.display.flip()
        clock.tick(60)

    from screens.game_screen      import GameScreen
    from screens.quiz_screen      import QuizScreen
    from screens.shop_screen      import ShopScreen
    from screens.moderator_screen import ModeratorScreen
    from screens.admin_screen     import AdminScreen
    from screens.profile_screen   import ProfileScreen
    from screens.settings_screen  import SettingsScreen

    login_screen   = LoginScreen(screen, fonts)
    current_screen = login_screen
    game_state     = None
    active_view    = "login"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if game_state:
                    _save_player_progress(game_state)
                SoundManager.stop_music()
                pygame.quit(); sys.exit()

            result = current_screen.handle_event(event)

            if active_view == "login":
                if isinstance(result, dict) and "role" in result:
                    game_state = fresh_game_state(result)
                    game_state["pollution"] = _load_player_pollution(result["username"])
                    game_state["start_pollution"] = game_state["pollution"]
                    SoundManager.play("login")
                    current_screen, active_view = _screen_for_role(
                        result["role"], screen, fonts, game_state)
                    if active_view == "game":
                        SoundManager.start_music(lambda: game_state["pollution"])
                elif result == "register":
                    current_screen = RegisterScreen(screen, fonts)
                    active_view    = "register"

            elif active_view == "register":
                if result == "back":
                    SoundManager.play("back")
                    login_screen   = LoginScreen(screen, fonts)
                    current_screen = login_screen
                    active_view    = "login"
                elif isinstance(result, dict) and "role" in result:
                    game_state = fresh_game_state(result)
                    game_state["pollution"] = _load_player_pollution(result["username"])
                    game_state["start_pollution"] = game_state["pollution"]
                    SoundManager.play("login")
                    current_screen, active_view = _screen_for_role(
                        result["role"], screen, fonts, game_state)
                    if active_view == "game":
                        SoundManager.start_music(lambda: game_state["pollution"])

            elif active_view == "game":
                if result == "quiz":
                    SoundManager.play("click")
                    current_screen = QuizScreen(screen, fonts, game_state)
                    active_view = "quiz"
                elif result == "shop":
                    SoundManager.play("click")
                    current_screen = ShopScreen(screen, fonts, game_state)
                    active_view = "shop"
                elif result == "moderator":
                    SoundManager.play("click")
                    current_screen = ModeratorScreen(screen, fonts, game_state)
                    active_view = "moderator"
                elif result == "admin":
                    SoundManager.play("click")
                    current_screen = AdminScreen(screen, fonts, game_state)
                    active_view = "admin"
                elif result == "profile":
                    SoundManager.play("click")
                    current_screen = ProfileScreen(screen, fonts, game_state)
                    active_view = "profile"
                elif result == "settings":
                    SoundManager.play("click")
                    current_screen = SettingsScreen(screen, fonts, game_state)
                    active_view = "settings"
                elif result == "save_season":
                    save_season_result(game_state)
                elif result == "logout":
                    login_screen   = _do_logout(game_state, fonts, screen)
                    current_screen = login_screen
                    game_state     = None
                    active_view    = "login"

            elif active_view in ("quiz", "shop", "moderator",
                                 "admin", "profile", "settings"):
                if result == "back":
                    SoundManager.play("back")
                    role = game_state["user"]["role"]
                    current_screen, active_view = _screen_for_role(
                        role, screen, fonts, game_state)
                    if active_view == "game":
                        SoundManager.start_music(lambda: game_state["pollution"])
                elif result == "logout":
                    login_screen   = _do_logout(game_state, fonts, screen)
                    current_screen = login_screen
                    game_state     = None
                    active_view    = "login"

        current_screen.draw()
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
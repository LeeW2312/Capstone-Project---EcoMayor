"""
EcoCity Mayor — screens/game_screen.py
Main city game screen
"""

import pygame
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
BROWN       = (101, 67,  33)
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


class GameScreen:
    def __init__(self, screen, fonts, game_state):
        self.screen = screen
        self.fonts  = fonts
        self.state  = game_state

        self.btn_quiz   = pygame.Rect(20,  70, 120, 38)
        self.btn_shop   = pygame.Rect(155, 70, 140, 38)
        self.btn_mod    = pygame.Rect(310, 70, 160, 38)
        self.btn_logout = pygame.Rect(SCREEN_W - 110, 15, 95, 34)

        random.seed(7)
        self.buildings = self._gen_buildings()
        self.trees     = self._gen_trees()

    def _gen_buildings(self):
        buildings = []
        x = 0
        while x < SCREEN_W:
            w   = random.randint(45, 100)
            h   = random.randint(80, 200)
            col = random.choice([
                (28,40,80),(35,50,90),(20,30,60),(40,55,95)
            ])
            buildings.append((x, SCREEN_H - 140 - h, w, h, col))
            x += w + random.randint(2, 6)
        return buildings

    def _gen_trees(self):
        return [random.randint(30, SCREEN_W - 30) for _ in range(14)]

    def _sky_colour(self):
        p = self.state["pollution"]
        if p >= 70:
            return (50, 35, 20)
        elif p >= 50:
            return (70, 70, 90)
        else:
            return (20, 60, 120)

    def _draw_city(self):
        s = self.screen
        p = self.state["pollution"]

        pygame.draw.rect(s, self._sky_colour(),
                         (0, 115, SCREEN_W, SCREEN_H - 255))

        if p > 50:
            smog = pygame.Surface((SCREEN_W, 80), pygame.SRCALPHA)
            smog.fill((80, 60, 30, min(int((p-50)*3), 120)))
            s.blit(smog, (0, 115))

        pygame.draw.rect(s, (20, 35, 20),
                         (0, SCREEN_H - 140, SCREEN_W, 140))
        pygame.draw.rect(s, (30, 30, 40),
                         (0, SCREEN_H - 110, SCREEN_W, 30))
        for rx in range(0, SCREEN_W, 60):
            pygame.draw.rect(s, GOLD, (rx, SCREEN_H - 97, 35, 4))

        for (bx, by, bw, bh, col) in self.buildings:
            pygame.draw.rect(s, col, (bx, by, bw, bh))
            pygame.draw.rect(s, BORDER, (bx, by, bw, bh), 1)
            win_col = (80,120,200) if p < 60 else (100,80,40)
            for wy in range(by+10, by+bh-10, 18):
                for wx in range(bx+8, bx+bw-8, 16):
                    if (wx+wy) % 5 != 0:
                        pygame.draw.rect(s, win_col, (wx, wy, 7, 9))

        tree_green = (40,140,40) if p < 50 else (30,80,30)
        for tx in self.trees:
            pygame.draw.rect(s, BROWN, (tx-3, SCREEN_H-162, 6, 22))
            pygame.draw.circle(s, tree_green, (tx, SCREEN_H-168), 16)

        if p > 60:
            for sx in [120, 420, 700]:
                for i in range(3):
                    sy  = SCREEN_H - 200 - i*18
                    sr  = 8 + i*5
                    sc  = (90-i*10, 80-i*10, 70-i*10)
                    pygame.draw.circle(s, sc, (sx, sy), sr)

    def _draw_stats(self):
        s = self.screen
        p = self.state["pollution"]

        pygame.draw.rect(s, PANEL, (0, 0, SCREEN_W, 60))
        pygame.draw.line(s, BORDER, (0, 60), (SCREEN_W, 60), 1)

        draw_text(s, "EcoCity Mayor", self.fonts["body"], GREEN, 16, 18)

        poll_col = RED if p >= 70 else (GOLD if p >= 50 else GREEN)
        draw_text(s, f"Pollution: {int(p)}%",
                  self.fonts["small"], poll_col, 310, 10)
        pygame.draw.rect(s, BORDER, (310, 28, 200, 14), border_radius=4)
        fw = int(200 * p / 100)
        if fw > 0:
            pygame.draw.rect(s, poll_col, (310, 28, fw, 14), border_radius=4)
        draw_text(s, "Goal: below 50%",
                  self.fonts["tiny"], TEXT_DIM, 310, 46)

        draw_text(s, f"Points: {self.state['points']}",
                  self.fonts["small"], GOLD, 540, 10)
        draw_text(s, f"Day {self.state['day']} / 30",
                  self.fonts["small"], TEXT, 540, 30)
        draw_text(s, f"{self.state['user']['username']} "
                     f"[{self.state['user']['role']}]",
                  self.fonts["tiny"], TEXT_DIM, 540, 48)

    def _draw_buttons(self):
        s     = self.screen
        mouse = pygame.mouse.get_pos()
        role  = self.state["user"]["role"]

        pygame.draw.rect(s, BG, (0, 61, SCREEN_W, 48))
        pygame.draw.line(s, BORDER, (0, 108), (SCREEN_W, 108), 1)

        draw_button(s, self.fonts["small"], "Quiz",
                    self.btn_quiz, self.btn_quiz.collidepoint(mouse))
        draw_button(s, self.fonts["small"], "Upgrade Shop",
                    self.btn_shop, self.btn_shop.collidepoint(mouse))

        if role in ("Moderator", "Admin"):
            draw_button(s, self.fonts["small"], "Moderator Panel",
                        self.btn_mod, self.btn_mod.collidepoint(mouse))

        draw_button(s, self.fonts["tiny"], "Logout",
                    self.btn_logout, self.btn_logout.collidepoint(mouse))

    def _draw_season_banner(self):
        p   = self.state["pollution"]
        day = self.state["day"]
        if day < 30:
            return
        s   = self.screen
        win = p < 50
        col = GREEN if win else RED
        msg = ("Season Complete! You reduced pollution below 50%!"
               if win else
               "Season Over! Pollution still too high. Try again!")
        pygame.draw.rect(s, PANEL, (50, 230, 800, 80), border_radius=12)
        pygame.draw.rect(s, col,   (50, 230, 800, 80), 2, border_radius=12)
        draw_text(s, msg, self.fonts["body"], col,
                  SCREEN_W//2, 270, center=True)

    def draw(self):
        self.screen.fill(BG)
        self._draw_city()
        self._draw_stats()
        self._draw_buttons()
        self._draw_season_banner()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos  = event.pos
            role = self.state["user"]["role"]
            if self.btn_quiz.collidepoint(pos):
                return "quiz"
            if self.btn_shop.collidepoint(pos):
                return "shop"
            if role in ("Moderator", "Admin"):
                if self.btn_mod.collidepoint(pos):
                    return "moderator"
            if self.btn_logout.collidepoint(pos):
                return "logout"
        return None
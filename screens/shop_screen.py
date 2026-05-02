"""
EcoCity Mayor — screens/shop_screen.py
Upgrade shop — spend points to reduce pollution
"""

import pygame
import json
import os

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


class ShopScreen:
    def __init__(self, screen, fonts, game_state):
        self.screen  = screen
        self.fonts   = fonts
        self.state   = game_state

        self.btn_back = pygame.Rect(20, 15, 90, 34)
        self.toast_msg  = ""
        self.toast_time = 0
        self.buy_rects  = []

    def _load_upgrades(self):
        path = os.path.join("data", "upgrades.json")
        with open(path) as f:
            return json.load(f)

    def draw(self):
        s        = self.screen
        upgrades = self._load_upgrades()
        mouse    = pygame.mouse.get_pos()

        s.fill(BG)

        # Top bar
        pygame.draw.rect(s, PANEL, (0, 0, SCREEN_W, 60))
        pygame.draw.line(s, BORDER, (0, 60), (SCREEN_W, 60), 1)
        draw_text(s, "Upgrade Shop — Spend points to reduce pollution",
                  self.fonts["body"], GREEN, SCREEN_W//2, 18, center=True)
        draw_text(s, f"Points: {self.state['points']}",
                  self.fonts["small"], GOLD, SCREEN_W - 150, 22)

        draw_button(s, self.fonts["small"], "Back",
                    self.btn_back, self.btn_back.collidepoint(mouse))

        # Pollution bar
        p = self.state["pollution"]
        poll_col = RED if p >= 70 else (GOLD if p >= 50 else GREEN)
        draw_text(s, f"Current Pollution: {int(p)}%",
                  self.fonts["small"], poll_col, SCREEN_W//2, 75, center=True)
        pygame.draw.rect(s, BORDER, (200, 90, 500, 12), border_radius=4)
        fw = int(500 * p / 100)
        if fw > 0:
            pygame.draw.rect(s, poll_col, (200, 90, fw, 12), border_radius=4)

        # Upgrade cards — 2 per row
        self.buy_rects = []
        card_w, card_h = 380, 110
        cols    = 2
        start_x = 70
        start_y = 120
        gap_x   = 30
        gap_y   = 20

        for i, u in enumerate(upgrades):
            col_i = i % cols
            row_i = i // cols
            cx = start_x + col_i * (card_w + gap_x)
            cy = start_y + row_i * (card_h + gap_y)

            card_rect = pygame.Rect(cx, cy, card_w, card_h)
            pygame.draw.rect(s, PANEL, card_rect, border_radius=10)
            pygame.draw.rect(s, BORDER, card_rect, 1, border_radius=10)

            draw_text(s, u["upgrade_name"],
                      self.fonts["body"], TEXT, cx+16, cy+14)
            draw_text(s, f"Reduces pollution by {u['pollution_reduction']}%",
                      self.fonts["small"], TEXT_DIM, cx+16, cy+42)
            draw_text(s, f"Cost: {u['cost_points']} points",
                      self.fonts["small"], GOLD, cx+16, cy+64)

            can_afford = self.state["points"] >= u["cost_points"]
            btn_rect   = pygame.Rect(cx + card_w - 120, cy + card_h - 44, 105, 32)
            self.buy_rects.append((btn_rect, u))
            draw_button(s, self.fonts["small"], "Buy",
                        btn_rect, btn_rect.collidepoint(mouse),
                        active=can_afford)

        # Toast notification
        if self.toast_msg:
            if pygame.time.get_ticks() < self.toast_time:
                toast_surf = self.fonts["small"].render(
                    self.toast_msg, True, WHITE)
                tw = toast_surf.get_width()
                tx = SCREEN_W//2 - tw//2 - 16
                pygame.draw.rect(s, (20, 80, 40),
                                 (tx, 545, tw+32, 34), border_radius=8)
                pygame.draw.rect(s, GREEN,
                                 (tx, 545, tw+32, 34), 1, border_radius=8)
                s.blit(toast_surf, (tx+16, 552))
            else:
                self.toast_msg = ""

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.btn_back.collidepoint(pos):
                return "back"
            for (btn_rect, u) in self.buy_rects:
                if btn_rect.collidepoint(pos):
                    if self.state["points"] >= u["cost_points"]:
                        self.state["points"]    -= u["cost_points"]
                        self.state["pollution"]  = max(
                            0.0,
                            self.state["pollution"] - u["pollution_reduction"]
                        )
                        self.toast_msg  = (
                            f"Purchased {u['upgrade_name']}! "
                            f"Pollution -{u['pollution_reduction']}%"
                        )
                        self.toast_time = pygame.time.get_ticks() + 2500
        return None
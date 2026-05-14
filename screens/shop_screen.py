"""
EcoCity Mayor — screens/shop_screen.py
Upgrade shop with difficulty cost multiplier, XP, challenge tracking.
"""

import pygame
import json
import os

from sounds    import SoundManager
from game_data import DIFFICULTY, XP_REWARDS

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


class ShopScreen:
    def __init__(self, screen, fonts, game_state):
        self.screen     = screen
        self.fonts      = fonts
        self.state      = game_state
        self.btn_back   = pygame.Rect(20, 15, 90, 34)
        self.toast_msg  = ""
        self.toast_time = 0
        self.buy_rects  = []

    def _load_upgrades(self):
        with open(os.path.join("data","upgrades.json")) as f:
            return json.load(f)

    def _cost(self, base_cost):
        """Apply difficulty cost multiplier."""
        diff = DIFFICULTY.get(
            self.state.get("difficulty","medium"),
            DIFFICULTY["medium"])
        return int(base_cost * diff["cost_mult"])

    def _award_xp(self):
        gain = XP_REWARDS.get("upgrade", 0)
        self.state["xp"] = self.state.get("xp",0) + gain

    def _update_challenge(self, ctype, amount=1):
        challenges = self.state.get("daily_challenges",[])
        progress   = self.state.get("daily_progress",{})
        completed  = self.state.get("daily_completed",[])
        for c in challenges:
            if c["id"] in completed or c["type"] != ctype:
                continue
            progress[c["id"]] = progress.get(c["id"],0) + amount
            if progress[c["id"]] >= c["goal"]:
                completed.append(c["id"])
                self.state["points"]      += c["reward"]
                self.state["total_earned"] = \
                    self.state.get("total_earned",0) + c["reward"]
                SoundManager.play("achievement")
        self.state["daily_progress"] = progress
        self.state["daily_completed"] = completed

    def draw(self):
        s        = self.screen
        upgrades = self._load_upgrades()
        mouse    = pygame.mouse.get_pos()
        s.fill(BG)

        pygame.draw.rect(s, PANEL, (0,0,SCREEN_W,60))
        pygame.draw.line(s, BORDER, (0,60),(SCREEN_W,60),1)
        draw_text(s,"Upgrade Shop",
                  self.fonts["body"],GREEN,SCREEN_W//2,18,center=True)
        draw_text(s,f"Points: {self.state['points']}",
                  self.fonts["small"],GOLD,SCREEN_W-150,10)
        draw_text(s,f"Bought: {self.state.get('upgrades_bought',0)}",
                  self.fonts["tiny"],TEXT_DIM,SCREEN_W-150,30)
        draw_button(s,self.fonts["small"],"Back",
                    self.btn_back,self.btn_back.collidepoint(mouse))

        # Difficulty label
        diff = DIFFICULTY.get(
            self.state.get("difficulty","medium"),DIFFICULTY["medium"])
        draw_text(s,
                  f"Difficulty: {diff['label']}  "
                  f"(cost x{diff['cost_mult']:.2f})",
                  self.fonts["tiny"],diff["colour"],
                  SCREEN_W//2,46,center=True)

        p = self.state["pollution"]
        poll_col = RED if p>=70 else (GOLD if p>=50 else GREEN)
        draw_text(s,f"Pollution: {int(p)}%",
                  self.fonts["small"],poll_col,SCREEN_W//2,72,center=True)
        pygame.draw.rect(s,BORDER,(200,88,500,12),border_radius=4)
        fw = int(500*p/100)
        if fw > 0:
            pygame.draw.rect(s,poll_col,(200,88,fw,12),border_radius=4)

        self.buy_rects = []
        card_w, card_h = 380, 118
        start_x, start_y = 70, 115

        for i, u in enumerate(upgrades):
            cx = start_x + (i%2)*(card_w+30)
            cy = start_y + (i//2)*(card_h+14)
            if cy+card_h > SCREEN_H-40:
                break

            actual_cost = self._cost(u["cost_points"])
            can_afford  = self.state["points"] >= actual_cost
            card_rect   = pygame.Rect(cx,cy,card_w,card_h)

            if can_afford:
                pygame.draw.rect(s,(25,55,25),card_rect,border_radius=10)
                pygame.draw.rect(s,GREEN,card_rect,1,border_radius=10)
            else:
                pygame.draw.rect(s,PANEL,card_rect,border_radius=10)
                pygame.draw.rect(s,BORDER,card_rect,1,border_radius=10)

            draw_text(s,u["upgrade_name"],
                      self.fonts["body"],TEXT,cx+14,cy+12)
            draw_text(s,f"Reduces pollution by {u['pollution_reduction']}%",
                      self.fonts["small"],GREEN,cx+14,cy+38)
            draw_text(s,f"Cost: {actual_cost} pts",
                      self.fonts["small"],
                      GOLD if can_afford else TEXT_DIM,cx+14,cy+60)
            if not can_afford:
                need = actual_cost - self.state["points"]
                draw_text(s,f"Need {need} more points",
                          self.fonts["tiny"],RED,cx+14,cy+82)

            btn_rect = pygame.Rect(cx+card_w-118, cy+card_h-40, 104,30)
            self.buy_rects.append((btn_rect, u, actual_cost))
            draw_button(s,self.fonts["small"],"Buy",btn_rect,
                        btn_rect.collidepoint(mouse),active=can_afford)

        if self.toast_msg and pygame.time.get_ticks()<self.toast_time:
            ts = self.fonts["small"].render(self.toast_msg,True,WHITE)
            tw = ts.get_width()
            tx = SCREEN_W//2-tw//2-16
            pygame.draw.rect(s,(20,80,40),(tx,545,tw+32,34),border_radius=8)
            pygame.draw.rect(s,GREEN,(tx,545,tw+32,34),1,border_radius=8)
            s.blit(ts,(tx+16,552))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.btn_back.collidepoint(pos):
                SoundManager.play("back")
                return "back"
            for (btn_rect, u, actual_cost) in self.buy_rects:
                if btn_rect.collidepoint(pos):
                    if self.state["points"] >= actual_cost:
                        self.state["points"]    -= actual_cost
                        self.state["pollution"]  = max(
                            0.0,
                            self.state["pollution"]-u["pollution_reduction"])
                        self.state["upgrades_bought"] = \
                            self.state.get("upgrades_bought",0)+1
                        self.toast_msg  = (
                            f"Bought {u['upgrade_name']}!  "
                            f"-{u['pollution_reduction']}% pollution")
                        self.toast_time = pygame.time.get_ticks()+2500
                        SoundManager.play("purchase")
                        self._award_xp()
                        self._update_challenge("upgrade",1)
                        # Track pollution reduction for challenges
                        self._update_challenge(
                            "reduce", u["pollution_reduction"])
                    else:
                        SoundManager.play("insufficient")
        return None
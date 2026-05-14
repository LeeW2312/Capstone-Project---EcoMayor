"""
EcoCity Mayor — screens/register_screen.py
New player registration screen with sounds.
"""

import pygame
import json
import os

from sounds import SoundManager

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
USERS_FILE = os.path.join("data","users.json")


def load_json(path):
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path,"w") as f:
        json.dump(data, f, indent=2)

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
        pygame.draw.rect(surf,(40,40,60),r,border_radius=8)
        pygame.draw.rect(surf,BORDER,r,1,border_radius=8)
        draw_text(surf,text,font,TEXT_DIM,r.centerx,r.centery,center=True)
    elif hovered:
        pygame.draw.rect(surf,ACCENT,r,border_radius=8)
        pygame.draw.rect(surf,WHITE,r,1,border_radius=8)
        draw_text(surf,text,font,WHITE,r.centerx,r.centery,center=True)
    else:
        pygame.draw.rect(surf,ACCENT_DARK,r,border_radius=8)
        pygame.draw.rect(surf,ACCENT,r,1,border_radius=8)
        draw_text(surf,text,font,TEXT,r.centerx,r.centery,center=True)


class InputBox:
    def __init__(self, x, y, w, h, placeholder="", secret=False):
        self.rect        = pygame.Rect(x,y,w,h)
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
            elif event.key not in (pygame.K_RETURN,pygame.K_TAB):
                if len(self.text) < 24:
                    self.text += event.unicode

    def draw(self, surf, font):
        bc = ACCENT if self.active else BORDER
        pygame.draw.rect(surf,PANEL,self.rect,border_radius=8)
        pygame.draw.rect(surf,bc,self.rect,1,border_radius=8)
        display = ("*"*len(self.text)) if self.secret and self.text \
                  else self.text
        if display:
            draw_text(surf,display,font,TEXT,
                      self.rect.x+12,
                      self.rect.centery-font.get_height()//2)
        else:
            draw_text(surf,self.placeholder,font,TEXT_DIM,
                      self.rect.x+12,
                      self.rect.centery-font.get_height()//2)
        if self.active and (pygame.time.get_ticks()//500)%2==0:
            tw  = font.size(display)[0]
            cx  = self.rect.x+12+tw+2
            cy1 = self.rect.centery-font.get_height()//2+2
            cy2 = self.rect.centery+font.get_height()//2-2
            pygame.draw.line(surf,ACCENT,(cx,cy1),(cx,cy2),2)


class RegisterScreen:
    def __init__(self, screen, fonts):
        self.screen = screen
        self.fonts  = fonts

        self.user_box = InputBox(320,210,260,42,"Choose username")
        self.pass_box = InputBox(320,268,260,42,"Choose password",secret=True)
        self.conf_box = InputBox(320,326,260,42,"Confirm password",secret=True)

        self.register_rect = pygame.Rect(320,390,124,44)
        self.back_rect     = pygame.Rect(456,390,124,44)

        self.error   = ""
        self.success = ""

        import random
        random.seed(99)
        self.buildings = []
        x = 0
        while x < SCREEN_W:
            w = random.randint(40,90)
            h = random.randint(60,160)
            self.buildings.append((x,SCREEN_H-h,w,h))
            x += w+random.randint(2,8)

    def _try_register(self):
        uname = self.user_box.text.strip()
        pw    = self.pass_box.text
        conf  = self.conf_box.text

        if not uname or not pw:
            self.error = "Username and password cannot be empty."
            return None
        if len(uname) < 3:
            self.error = "Username must be at least 3 characters."
            return None
        if len(pw) < 4:
            self.error = "Password must be at least 4 characters."
            return None
        if pw != conf:
            self.error = "Passwords do not match."
            self.conf_box.text = ""
            return None

        users = load_json(USERS_FILE)
        if any(u["username"].lower()==uname.lower() for u in users):
            self.error = "Username already taken."
            return None

        new_id   = max((u["user_id"] for u in users),default=0)+1
        new_user = {
            "user_id":          new_id,
            "username":         uname,
            "password":         pw,
            "role":             "Player",
            "banned":           False,
            "last_pollution":   100.0,
            "xp":               0,
            "level":            1,
            "difficulty":       "medium",
            "pollution_history":[],
            "stats":{"seasons_played":0,"best_score":0,
                     "total_points":0,"total_correct":0},
        }
        users.append(new_user)
        save_json(USERS_FILE,users)
        self.success = f"Account created!  Welcome, {uname}!"
        SoundManager.play("login")
        return new_user

    def handle_event(self, event):
        self.user_box.handle_event(event)
        self.pass_box.handle_event(event)
        self.conf_box.handle_event(event)

        if event.type==pygame.KEYDOWN and event.key==pygame.K_RETURN:
            result = self._try_register()
            if result:
                return result

        if event.type==pygame.MOUSEBUTTONDOWN:
            if self.register_rect.collidepoint(event.pos):
                result = self._try_register()
                if result:
                    return result
            if self.back_rect.collidepoint(event.pos):
                SoundManager.play("back")
                return "back"
        return None

    def draw(self):
        s = self.screen
        s.fill(BG)

        for (bx,by,bw,bh) in self.buildings:
            pygame.draw.rect(s,(18,25,50),(bx,by,bw,bh))
            for wy in range(by+8,by+bh-8,16):
                for wx in range(bx+6,bx+bw-6,14):
                    col=(80,120,180) if (wx+wy)%3!=0 else (30,30,50)
                    pygame.draw.rect(s,col,(wx,wy,6,8))
        smog=pygame.Surface((SCREEN_W,200),pygame.SRCALPHA)
        smog.fill((60,40,20,60))
        s.blit(smog,(0,0))

        panel=pygame.Rect(255,138,390,340)
        pygame.draw.rect(s,PANEL,panel,border_radius=12)
        pygame.draw.rect(s,BORDER,panel,1,border_radius=12)

        draw_text(s,"Create Account",self.fonts["title"],
                  GREEN,SCREEN_W//2,168,center=True)
        draw_text(s,"Join EcoCity Mayor",self.fonts["small"],
                  TEXT_DIM,SCREEN_W//2,196,center=True)

        draw_text(s,"Username",self.fonts["small"],TEXT_DIM,320,192)
        draw_text(s,"Password",self.fonts["small"],TEXT_DIM,320,250)
        draw_text(s,"Confirm Password",self.fonts["small"],TEXT_DIM,320,308)

        self.user_box.draw(s,self.fonts["body"])
        self.pass_box.draw(s,self.fonts["body"])
        self.conf_box.draw(s,self.fonts["body"])

        mouse=pygame.mouse.get_pos()
        draw_button(s,self.fonts["body"],"Register",
                    self.register_rect,self.register_rect.collidepoint(mouse))
        draw_button(s,self.fonts["body"],"Back",
                    self.back_rect,self.back_rect.collidepoint(mouse))

        if self.error:
            draw_text(s,self.error,self.fonts["small"],RED,
                      SCREEN_W//2,446,center=True)
        if self.success:
            draw_text(s,self.success,self.fonts["small"],GREEN,
                      SCREEN_W//2,446,center=True)
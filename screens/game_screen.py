"""
EcoCity Mayor — screens/game_screen.py
Main city screen with full achievements, difficulty, eco events,
XP, daily challenges, streak bonuses, settings button.
"""

import pygame
import random
import math
import os
import json

from sounds    import SoundManager
from game_data import (DIFFICULTY, ECO_EVENTS, XP_REWARDS,
                       ACHIEVEMENTS, get_level_info,
                       pick_daily_challenges)

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
ORANGE      = (230, 140, 40)
PURPLE      = (145, 85,  215)
SKY_CLEAN   = (30,  90,  180)
SKY_MID     = (60,  60,  90)
SKY_SMOG    = (50,  35,  20)

SCREEN_W, SCREEN_H = 900, 600

DISASTERS = [
    {"msg": "Factory Fire!  Pollution +5%",     "pollution": 5},
    {"msg": "Chemical Spill!  Pollution +4%",   "pollution": 4},
    {"msg": "Heavy Smog Alert!  Pollution +3%", "pollution": 3},
    {"msg": "Oil Leak!  Pollution +4%",         "pollution": 4},
    {"msg": "Wildfire!  Pollution +5%",         "pollution": 5},
]


def draw_text(surf, text, font, color, x, y, center=False):
    img = font.render(str(text), True, color)
    r   = img.get_rect()
    if center:
        r.center = (x, y)
    else:
        r.topleft = (x, y)
    surf.blit(img, r)

def draw_button(surf, font, text, rect, hovered, active=True,
                base_col=None, hover_col=None, border_col=None):
    r = pygame.Rect(rect)
    if not active:
        pygame.draw.rect(surf, (40,40,60), r, border_radius=10)
        pygame.draw.rect(surf, BORDER, r, 1, border_radius=10)
        draw_text(surf, text, font, TEXT_DIM,
                  r.centerx, r.centery, center=True)
    elif hovered:
        hc = hover_col or ACCENT
        pygame.draw.rect(surf, hc, r, border_radius=10)
        pygame.draw.rect(surf, WHITE, r, 1, border_radius=10)
        glow = pygame.Surface((r.w+6, r.h+6), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*hc, 60),
                         (0,0,r.w+6,r.h+6), border_radius=12)
        surf.blit(glow, (r.x-3, r.y-3))
        draw_text(surf, text, font, WHITE,
                  r.centerx, r.centery, center=True)
    else:
        bc = base_col or ACCENT_DARK
        bd = border_col or ACCENT
        pygame.draw.rect(surf, bc, r, border_radius=10)
        pygame.draw.rect(surf, bd, r, 1, border_radius=10)
        draw_text(surf, text, font, TEXT,
                  r.centerx, r.centery, center=True)
    return r


class GameScreen:
    def __init__(self, screen, fonts, game_state):
        self.screen = screen
        self.fonts  = fonts
        self.state  = game_state

        self.btn_quiz     = pygame.Rect(20,  70, 100, 32)
        self.btn_shop     = pygame.Rect(128, 70, 118, 32)
        self.btn_achieve  = pygame.Rect(254, 70, 118, 32)
        self.btn_profile  = pygame.Rect(380, 70, 88,  32)
        self.btn_settings = pygame.Rect(476, 70, 88,  32)
        self.btn_mod      = pygame.Rect(572, 70, 100, 32)
        self.btn_admin    = pygame.Rect(680, 70, 80,  32)
        self.btn_logout   = pygame.Rect(SCREEN_W-110, 14, 96, 32)

        random.seed(7)
        self.buildings = self._gen_buildings()
        self.trees     = self._gen_trees()
        self.clouds    = self._gen_clouds()
        self.stars     = self._gen_stars()
        self.lampposts = self._gen_lampposts()

        self.raindrops = [
            [random.randint(0, SCREEN_W),
             random.randint(0, SCREEN_H),
             random.randint(3, 7)]
            for _ in range(120)
        ]

        self.sun_angle = 0
        self.cloud_x   = [c[0] for c in self.clouds]
        self.anim_tick = 0

        self.last_event_tick   = pygame.time.get_ticks()
        self.disaster_msg      = ""
        self.disaster_end_time = 0
        self.disaster_is_good  = False

        self.achieve_queue = []
        self.achieve_msg   = ""
        self.achieve_end   = 0

        self.challenge_msg = ""
        self.challenge_end = 0

        self.show_achievements = False
        self.show_challenges   = False
        self.game_over  = False
        self.game_won   = False
        self._retry_btn = None
        self._quit_btn  = None
        self._close_btn = None

        self._prev_poll_zone = None

    # ── Generators ────────────────────────────────────

    def _gen_buildings(self):
        buildings = []
        x = 0
        while x < SCREEN_W:
            w    = random.randint(50, 110)
            h    = random.randint(90, 220)
            base = random.choice([
                (28,42,85),(35,52,95),(22,32,65),
                (42,58,100),(30,46,88),(18,28,58)
            ])
            roof = random.choice(["flat","point","antenna"])
            buildings.append({
                "x":x,"y":SCREEN_H-145-h,
                "w":w,"h":h,"col":base,"roof":roof,
            })
            x += w + random.randint(1, 5)
        return buildings

    def _gen_trees(self):
        return [(random.randint(20,SCREEN_W-20),
                 random.randint(12,22)) for _ in range(18)]

    def _gen_clouds(self):
        return [(random.randint(0,SCREEN_W),
                 random.randint(125,200),
                 random.randint(60,130)) for _ in range(6)]

    def _gen_stars(self):
        return [(random.randint(0,SCREEN_W),
                 random.randint(120,220),
                 random.randint(1,2)) for _ in range(40)]

    def _gen_lampposts(self):
        return [random.randint(60,SCREEN_W-60) for _ in range(8)]

    # ── Helpers ───────────────────────────────────────

    def _lerp_colour(self, c1, c2, t):
        t = max(0.0, min(1.0, t))
        return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))

    def _sky_colour(self):
        p = self.state["pollution"]
        if p >= 70:
            return SKY_SMOG
        elif p >= 50:
            return self._lerp_colour(SKY_MID,SKY_SMOG,(p-50)/20.0)
        else:
            return self._lerp_colour(SKY_CLEAN,SKY_MID,p/50.0)

    def _diff(self):
        return DIFFICULTY.get(
            self.state.get("difficulty","medium"),DIFFICULTY["medium"])

    # ── XP ────────────────────────────────────────────

    def _award_xp(self, reason):
        gain = XP_REWARDS.get(reason, 0)
        if gain <= 0:
            return
        self.state["xp"] = self.state.get("xp",0) + gain
        old_level = self.state.get("level",1)
        new_level, title, _ = get_level_info(self.state["xp"])
        self.state["level"] = new_level
        if new_level > old_level:
            self.achieve_queue.append(
                f"Level Up!  Level {new_level}  --  {title}!")
            SoundManager.play("achievement")

    # ── Daily challenges ──────────────────────────────

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
                self.challenge_msg = (
                    f"Challenge done!  {c['desc']}  "
                    f"+{c['reward']} pts!")
                self.challenge_end = pygame.time.get_ticks() + 3500
                SoundManager.play("achievement")
        self.state["daily_progress"]  = progress
        self.state["daily_completed"] = completed

    # ── Disaster system ───────────────────────────────

    def _update_disasters(self):
        if self.game_over or self.game_won:
            return
        d   = self._diff()
        now = pygame.time.get_ticks()
        if now - self.last_event_tick >= d["dis_interval"]:
            self.last_event_tick = now
            if random.random() < d["dis_chance"]:
                if random.random() < 0.30:
                    ev = random.choice(ECO_EVENTS)
                    self.state["pollution"] = max(
                        0.0, self.state["pollution"] + ev["pollution"])
                    if ev["pollution"] < 0:
                        self._update_challenge(
                            "reduce", abs(ev["pollution"]))
                    self.disaster_msg      = ev["msg"]
                    self.disaster_end_time = now + 3500
                    self.disaster_is_good  = True
                    SoundManager.play("pollution_low")
                else:
                    dis = random.choice(DISASTERS)
                    self.state["pollution"] = min(
                        100.0, self.state["pollution"] + dis["pollution"])
                    self.disaster_msg      = dis["msg"]
                    self.disaster_end_time = now + 3500
                    self.disaster_is_good  = False
                    self.state["disasters_survived"] = \
                        self.state.get("disasters_survived",0) + 1
                    SoundManager.play("disaster")

    # ── Achievement checking ──────────────────────────

    def _check_achievements(self):
        s   = self.state
        a   = s["achievements"]
        p   = s["pollution"]
        now = pygame.time.get_ticks()
        prev_count = len(a)

        def unlock(aid, name):
            if aid not in a:
                a.append(aid)
                self.achieve_queue.append(f"Achievement: {name}!")
                self._award_xp("achievement")

        # ── Quiz ──────────────────────────────────────
        ca = s.get("correct_answers", 0)
        te = s.get("total_earned", 0)
        if ca >= 1:   unlock("first_answer", "First Step")
        if ca >= 5:   unlock("quiz_5",       "Eco Student")
        if ca >= 20:  unlock("quiz_20",      "Eco Scholar")
        if ca >= 3:   unlock("streak_3",     "On a Roll")
        if ca >= 5:   unlock("streak_5",     "Quiz Master")
        if ca >= 10:  unlock("streak_10",    "Unstoppable")

        ps = s.get("perfect_streak", 0)
        if ps >= 10:  unlock("perfect_day",  "Perfect Day")

        # ── Pollution ─────────────────────────────────
        sp = s.get("start_pollution", 100)
        if p < sp:    unlock("first_drop",   "First Breath")
        if p < 80:    unlock("below_80",     "Small Progress")
        if p < 70:    unlock("green_mayor",  "Green Mayor")
        if p < 50:    unlock("clean_city",   "Clean City")
        if p < 30:    unlock("eco_paradise", "Eco Paradise")
        if p < 10:    unlock("zero_hero",    "Zero Hero")

        # ── Points ────────────────────────────────────
        if te >= 30:   unlock("first_points", "Getting Started")
        if te >= 100:  unlock("points_100",   "Point Collector")
        if te >= 300:  unlock("points_300",   "Point Hoarder")
        if te >= 500:  unlock("points_500",   "Points Machine")
        if te >= 1000: unlock("points_1000",  "Eco Millionaire")

        # ── Shop ──────────────────────────────────────
        ub = s.get("upgrades_bought", 0)
        ss = s.get("shop_spent", 0)
        if ub >= 1:   unlock("first_upgrade", "First Investment")
        if ub >= 3:   unlock("shop_3",        "Shop Addict")
        if ub >= 5:   unlock("shop_5",        "Upgrade Fanatic")
        if ss >= 500: unlock("big_spender",   "Big Spender")

        # ── Survival ──────────────────────────────────
        day = s.get("day", 1)
        if day >= 10: unlock("day_10",    "Still Standing")
        if day >= 20: unlock("survivor",  "Survivor")

        # ── Level ─────────────────────────────────────
        lvl = s.get("level", 1)
        if lvl >= 5:  unlock("level_5",   "Rising Star")
        if lvl >= 10: unlock("level_10",  "Earth Guardian")

        # ── Disasters ─────────────────────────────────
        ds = s.get("disasters_survived", 0)
        if ds >= 5:   unlock("disaster_5", "Crisis Manager")

        # ── Daily challenges ──────────────────────────
        compl = s.get("daily_completed", [])
        chal  = s.get("daily_challenges", [])
        if len(compl) >= len(chal) and len(chal) > 0:
            unlock("daily_3", "Dedicated")

        # ── Special (triggered on season end) ─────────
        if self.game_won:
            if day < 20:
                unlock("speedrun", "Speed Mayor")
            if s.get("max_pollution", 0) >= 90:
                unlock("comeback", "The Comeback")

        if len(a) > prev_count:
            SoundManager.play("achievement")

        if self.achieve_queue and now > self.achieve_end:
            self.achieve_msg = self.achieve_queue.pop(0)
            self.achieve_end = now + 3200

        # Track max pollution for comeback
        s["max_pollution"] = max(s.get("max_pollution",0), p)

        # Pollution zone sounds
        zone = "high" if p>=70 else "low" if p<40 else "mid"
        if zone != self._prev_poll_zone:
            self._prev_poll_zone = zone
            if zone == "high":
                SoundManager.play("pollution_high")
            elif zone == "low":
                SoundManager.play("pollution_low")

    # ── Season end ────────────────────────────────────

    def _check_season(self):
        if self.state["day"] >= 30 and \
                not self.game_over and not self.game_won:
            if self.state["pollution"] < 50:
                self.game_won = True
                self._award_xp("win")
                SoundManager.play("game_win")
                SoundManager.stop_music()
            else:
                self.game_over = True
                SoundManager.play("game_over")
                SoundManager.stop_music()

    # ── Draw sky ──────────────────────────────────────

    def _draw_sky(self):
        s   = self.screen
        p   = self.state["pollution"]
        sky = self._sky_colour()
        pygame.draw.rect(s,sky,(0,115,SCREEN_W,SCREEN_H-260))

        if p < 40:
            for (sx,sy,sr) in self.stars:
                if (pygame.time.get_ticks()//600+sx)%2:
                    pygame.draw.circle(s,(200,200,255),(sx,sy),sr)

        if p < 60:
            self.sun_angle = (self.sun_angle+0.4)%360
            sun_x,sun_y   = 820,148
            glow = pygame.Surface((100,100),pygame.SRCALPHA)
            pygame.draw.circle(glow,(255,220,80,60),(50,50),48)
            s.blit(glow,(sun_x-50,sun_y-50))
            for angle in range(0,360,36):
                rad = math.radians(angle+self.sun_angle)
                pygame.draw.line(s,(255,200,50),(sun_x,sun_y),
                    (int(sun_x+52*math.cos(rad)),
                     int(sun_y+52*math.sin(rad))),2)
            pygame.draw.circle(s,(255,230,90),(sun_x,sun_y),26)
            pygame.draw.circle(s,(255,255,150),(sun_x,sun_y),18)

        if p >= 65:
            pygame.draw.circle(s,(200,200,220),(80,148),20)
            pygame.draw.circle(s,sky,(88,142),16)

        self.anim_tick += 1
        if self.anim_tick % 3 == 0:
            self.cloud_x = [(cx+0.3)%(SCREEN_W+150)
                            for cx in self.cloud_x]
        for i,(_,cy,cw) in enumerate(self.clouds):
            cx  = self.cloud_x[i]
            col = (150,150,150) if p>60 else (220,220,240)
            for dx,dy,dr in [(0,0,cw//3),(cw//4,-8,cw//4),
                              (-cw//4,-4,cw//5),(cw//2-4,0,cw//4)]:
                pygame.draw.circle(s,col,(int(cx+dx),int(cy+dy)),dr)

        if p > 45:
            smog = pygame.Surface((SCREEN_W,110),pygame.SRCALPHA)
            smog.fill((80,55,25,min(int((p-45)*3.5),150)))
            s.blit(smog,(0,115))

    def _draw_ground(self):
        s = self.screen
        p = self.state["pollution"]
        pygame.draw.rect(s,(25,70,25) if p<50 else (20,45,20),
                         (0,SCREEN_H-145,SCREEN_W,145))
        pygame.draw.rect(s,(50,50,65),(0,SCREEN_H-115,SCREEN_W,5))
        pygame.draw.rect(s,(35,35,45),(0,SCREEN_H-110,SCREEN_W,35))
        for rx in range(0,SCREEN_W,58):
            pygame.draw.rect(s,(180,160,40),(rx,SCREEN_H-95,34,5))
        pygame.draw.line(s,(160,160,180),
            (0,SCREEN_H-110),(SCREEN_W,SCREEN_H-110),2)
        pygame.draw.line(s,(160,160,180),
            (0,SCREEN_H-75),(SCREEN_W,SCREEN_H-75),1)
        for lx in self.lampposts:
            pygame.draw.rect(s,(160,160,180),(lx,SCREEN_H-175,3,60))
            pygame.draw.line(s,(160,160,180),
                (lx,SCREEN_H-175),(lx+12,SCREEN_H-182),2)
            lc = (255,240,150) if p<70 else (180,160,80)
            pygame.draw.circle(s,lc,(lx+12,SCREEN_H-182),5)
            if p < 70:
                glow = pygame.Surface((24,24),pygame.SRCALPHA)
                pygame.draw.circle(glow,(255,240,150,50),(12,12),11)
                s.blit(glow,(lx,SCREEN_H-194))

    def _draw_buildings(self):
        s = self.screen
        p = self.state["pollution"]
        for b in self.buildings:
            bx,by,bw,bh = b["x"],b["y"],b["w"],b["h"]
            col = b["col"]
            pygame.draw.rect(s,col,(bx,by,bw,bh))
            facade = self._lerp_colour(col,(255,255,255),0.08)
            pygame.draw.rect(s,facade,(bx+2,by,bw-4,bh-2))
            pygame.draw.rect(s,BORDER,(bx,by,bw,bh),1)
            win_on = (90,130,220) if p<60 else (110,90,50)
            tick   = pygame.time.get_ticks()//1200
            for wy in range(by+12,by+bh-12,20):
                for wx in range(bx+10,bx+bw-10,16):
                    wc = win_on if (wx*13+wy*7+tick)%9!=0 else (25,30,55)
                    pygame.draw.rect(s,wc,(wx,wy,8,10))
                    pygame.draw.rect(s,BORDER,(wx,wy,8,10),1)
            if b["roof"]=="point":
                pts=[(bx+bw//2,by-14),(bx+4,by),(bx+bw-4,by)]
                pygame.draw.polygon(s,col,pts)
                pygame.draw.polygon(s,BORDER,pts,1)
            elif b["roof"]=="antenna":
                pygame.draw.line(s,(180,180,200),
                    (bx+bw//2,by),(bx+bw//2,by-20),2)
                pygame.draw.circle(s,RED,(bx+bw//2,by-20),3)

    def _draw_trees(self):
        s = self.screen
        p = self.state["pollution"]
        for (tx,sz) in self.trees:
            ty = SCREEN_H-145
            pygame.draw.rect(s,BROWN,(tx-3,ty-sz-10,6,sz+10))
            g1=(50,160,50) if p<50 else (35,95,35)
            g2=(40,130,40) if p<50 else (28,75,28)
            pygame.draw.circle(s,g1,(tx,ty-sz-10),sz)
            pygame.draw.circle(s,g2,(tx-sz//3,ty-sz-4),sz-4)
            pygame.draw.circle(s,g1,(tx+sz//3,ty-sz-2),sz-5)

    def _draw_rain(self):
        s = self.screen
        if self.state["pollution"] <= 60:
            return
        for drop in self.raindrops:
            pygame.draw.line(s,(70,80,130),(drop[0],drop[1]),
                             (drop[0]-2,drop[1]+12),1)
            drop[1] += drop[2]
            if drop[1] > SCREEN_H:
                drop[1] = 115
                drop[0] = random.randint(0,SCREEN_W)

    def _draw_smoke(self):
        s = self.screen
        p = self.state["pollution"]
        if p <= 55:
            return
        tick = pygame.time.get_ticks()/1000.0
        for sx in [130,440,710]:
            for i in range(5):
                offset = math.sin(tick+sx+i)*6
                sy = SCREEN_H-210-i*22
                sr = 9+i*6
                alpha = max(0,130-i*22)
                shade = max(30,95-i*14)
                smoke = pygame.Surface((sr*2,sr*2),pygame.SRCALPHA)
                pygame.draw.circle(smoke,
                    (shade,shade-10,shade-15,alpha),(sr,sr),sr)
                s.blit(smoke,(int(sx+offset)-sr,sy-sr))

    # ── Stats bar ─────────────────────────────────────

    def _draw_stats(self):
        s = self.screen
        p = self.state["pollution"]
        pygame.draw.rect(s,PANEL,(0,0,SCREEN_W,60))
        pygame.draw.rect(s,(30,44,80),(0,0,SCREEN_W,30))
        pygame.draw.line(s,BORDER,(0,60),(SCREEN_W,60),1)

        draw_text(s,"EcoCity Mayor",self.fonts["body"],GREEN,16,18)

        poll_col = RED if p>=70 else (GOLD if p>=50 else GREEN)
        draw_text(s,f"Pollution: {p:.1f}%",
                  self.fonts["small"],poll_col,290,8)
        bar = pygame.Rect(290,26,160,12)
        pygame.draw.rect(s,(30,30,50),bar,border_radius=5)
        fw = int(160*p/100)
        if fw > 0:
            pygame.draw.rect(s,poll_col,(290,26,fw,12),border_radius=5)
        pygame.draw.rect(s,BORDER,bar,1,border_radius=5)
        draw_text(s,"Goal: <50%",self.fonts["tiny"],TEXT_DIM,458,30)

        draw_text(s,f"Points: {self.state['points']}",
                  self.fonts["small"],GOLD,530,8)
        draw_text(s,f"Day {self.state['day']} / 30",
                  self.fonts["small"],TEXT,530,26)

        xp = self.state.get("xp",0)
        level,title,next_xp = get_level_info(xp)
        diff_cfg = self._diff()
        diff_col = diff_cfg["colour"]
        draw_text(s,f"Lv{level} {title}",
                  self.fonts["tiny"],diff_col,700,8)
        if next_xp:
            xp_bar_w = int(160*xp/next_xp)
            pygame.draw.rect(s,(20,20,40),(700,22,160,8),border_radius=4)
            if xp_bar_w > 0:
                pygame.draw.rect(s,PURPLE,(700,22,xp_bar_w,8),border_radius=4)
            pygame.draw.rect(s,BORDER,(700,22,160,8),1,border_radius=4)
            draw_text(s,f"XP {xp}/{next_xp}",
                      self.fonts["tiny"],TEXT_DIM,700,34)
        else:
            draw_text(s,"MAX LEVEL",self.fonts["tiny"],GOLD,700,22)

        draw_text(s,
                  f"{self.state['user']['username']}  "
                  f"[{diff_cfg['label']}]",
                  self.fonts["tiny"],TEXT_DIM,700,46)

    # ── Nav bar ───────────────────────────────────────

    def _draw_nav(self):
        s     = self.screen
        mouse = pygame.mouse.get_pos()
        role  = self.state["user"]["role"]

        pygame.draw.rect(s,(18,24,50),(0,61,SCREEN_W,46))
        pygame.draw.line(s,BORDER,(0,107),(SCREEN_W,107),1)

        btns = [
            (self.btn_quiz,     "Quiz",        ACCENT_DARK, ACCENT),
            (self.btn_shop,     "Upgrade Shop",ACCENT_DARK, ACCENT),
            (self.btn_achieve,  "Achievements",ACCENT_DARK, ACCENT),
            (self.btn_profile,  "Profile",     ACCENT_DARK, ACCENT),
            (self.btn_settings, "Settings",    ACCENT_DARK, ACCENT),
        ]
        if role in ("Moderator","Admin"):
            btns.append((self.btn_mod,"Moderator",(30,15,50),(140,80,200)))
        if role == "Admin":
            btns.append((self.btn_admin,"Admin",(50,20,10),ORANGE))

        for (rect,label,bc,bd) in btns:
            draw_button(s,self.fonts["tiny"],label,rect,
                        rect.collidepoint(mouse),
                        base_col=bc,hover_col=bd,border_col=bd)

        draw_button(s,self.fonts["tiny"],"Logout",
                    self.btn_logout,
                    self.btn_logout.collidepoint(mouse),
                    base_col=(60,15,15),
                    hover_col=(160,30,30),
                    border_col=RED)

        tooltips = {
            "Quiz":         "Answer questions to earn points",
            "Upgrade Shop": "Spend points to reduce pollution",
            "Achievements": "View your unlocked achievements",
            "Profile":      "View your stats and history",
            "Settings":     "Sound, volume, difficulty settings",
            "Moderator":    "Manage quiz questions and upgrades",
            "Admin":        "Manage users and leaderboard",
        }
        for (rect,label,_,_) in btns:
            if rect.collidepoint(mouse):
                tip = tooltips.get(label,"")
                if tip:
                    ts = self.fonts["tiny"].render(tip,True,TEXT_DIM)
                    s.blit(ts,(rect.x,rect.y+rect.h+4))

    # ── Disaster banner ───────────────────────────────

    def _draw_disaster(self):
        now = pygame.time.get_ticks()
        if not self.disaster_msg or now > self.disaster_end_time:
            return
        s     = self.screen
        good  = self.disaster_is_good
        flash = (now//300)%2==0
        bg_c  = (10,50,20)  if good else (90,15,15)
        bd_c  = GREEN       if good else ((255,60,60) if flash else RED)
        lbl   = "ECO EVENT" if good else "DISASTER EVENT"
        lbl_c = GREEN       if good else ORANGE
        pygame.draw.rect(s,bg_c,(90,192,720,75),border_radius=12)
        pygame.draw.rect(s,bd_c,(90,192,720,75),2,border_radius=12)
        draw_text(s,lbl,self.fonts["small"],lbl_c,
                  SCREEN_W//2,210,center=True)
        draw_text(s,self.disaster_msg,self.fonts["body"],
                  GREEN if good else RED,
                  SCREEN_W//2,240,center=True)

    # ── Achievement toast ─────────────────────────────

    def _draw_achieve_toast(self):
        now = pygame.time.get_ticks()
        if not self.achieve_msg or now > self.achieve_end:
            return
        s      = self.screen
        remain = self.achieve_end - now
        alpha  = min(255,int(remain/500.0*255)) if remain<500 else 255
        ts     = self.fonts["small"].render(self.achieve_msg,True,WHITE)
        tw     = ts.get_width()
        tx     = SCREEN_W//2-tw//2-18
        surf   = pygame.Surface((tw+36,38),pygame.SRCALPHA)
        pygame.draw.rect(surf,(20,70,20,alpha),(0,0,tw+36,38),border_radius=10)
        pygame.draw.rect(surf,(*GREEN,alpha),(0,0,tw+36,38),1,border_radius=10)
        surf.blit(ts,(18,10))
        s.blit(surf,(tx,115))

    # ── Challenge toast ───────────────────────────────

    def _draw_challenge_toast(self):
        now = pygame.time.get_ticks()
        if not self.challenge_msg or now > self.challenge_end:
            return
        s    = self.screen
        ts   = self.fonts["small"].render(self.challenge_msg,True,WHITE)
        tw   = ts.get_width()
        tx   = SCREEN_W//2-tw//2-18
        surf = pygame.Surface((tw+36,38),pygame.SRCALPHA)
        pygame.draw.rect(surf,(50,30,0,210),(0,0,tw+36,38),border_radius=10)
        pygame.draw.rect(surf,(*GOLD,210),(0,0,tw+36,38),1,border_radius=10)
        surf.blit(ts,(18,10))
        s.blit(surf,(tx,158))

    # ── Achievements overlay ──────────────────────────

    def _draw_achievements_panel(self):
        s        = self.screen
        mouse    = pygame.mouse.get_pos()
        unlocked = self.state["achievements"]

        overlay = pygame.Surface((SCREEN_W,SCREEN_H),pygame.SRCALPHA)
        overlay.fill((0,0,0,170))
        s.blit(overlay,(0,0))

        panel = pygame.Rect(60,70,780,470)
        pygame.draw.rect(s,(14,20,46),panel,border_radius=16)
        pygame.draw.rect(s,ACCENT,panel,1,border_radius=16)

        draw_text(s,"Achievements",self.fonts["title"],GOLD,
                  SCREEN_W//2,96,center=True)
        draw_text(s,
                  f"{len(unlocked)} / {len(ACHIEVEMENTS)} unlocked",
                  self.fonts["small"],TEXT_DIM,
                  SCREEN_W//2,124,center=True)

        # Grid: 2 columns
        cols    = 2
        card_w  = 356
        card_h  = 44
        gap_x   = 12
        gap_y   = 6
        start_x = 76
        start_y = 142

        # Scrollable — show first 16
        for i,ach in enumerate(ACHIEVEMENTS[:16]):
            col_i = i % cols
            row_i = i // cols
            cx = start_x + col_i*(card_w+gap_x)
            cy = start_y + row_i*(card_h+gap_y)
            if cy + card_h > panel.bottom - 50:
                break
            achieved = ach["id"] in unlocked
            bg_c = (16,46,16) if achieved else (18,20,44)
            bd_c = GREEN if achieved else BORDER
            card = pygame.Rect(cx,cy,card_w,card_h)
            pygame.draw.rect(s,bg_c,card,border_radius=8)
            pygame.draw.rect(s,bd_c,card,1,border_radius=8)
            icon = "★" if achieved else "○"
            col  = GREEN if achieved else TEXT_DIM
            draw_text(s,f"{icon} {ach['name']}",
                      self.fonts["small"],col,cx+10,cy+6)
            draw_text(s,ach["desc"],
                      self.fonts["tiny"],TEXT_DIM,cx+10,cy+24)
            if achieved:
                draw_text(s,"DONE",self.fonts["tiny"],GREEN,
                          cx+card_w-46,cy+14)

        # Second page label if more than 16
        if len(ACHIEVEMENTS) > 16:
            draw_text(s,
                      f"  +{len(ACHIEVEMENTS)-16} more in Profile > Achievements",
                      self.fonts["tiny"],TEXT_DIM,
                      SCREEN_W//2,panel.bottom-42,center=True)

        close = pygame.Rect(SCREEN_W//2-65,panel.bottom-34,130,28)
        hov   = close.collidepoint(mouse)
        draw_button(s,self.fonts["small"],"Close",close,hov,
                    base_col=ACCENT_DARK,hover_col=ACCENT)
        self._close_btn = close

    # ── Daily challenges overlay ──────────────────────

    def _draw_challenges_panel(self):
        s          = self.screen
        mouse      = pygame.mouse.get_pos()
        challenges = self.state.get("daily_challenges",[])
        progress   = self.state.get("daily_progress",{})
        completed  = self.state.get("daily_completed",[])

        overlay = pygame.Surface((SCREEN_W,SCREEN_H),pygame.SRCALPHA)
        overlay.fill((0,0,0,170))
        s.blit(overlay,(0,0))

        panel = pygame.Rect(180,90,540,420)
        pygame.draw.rect(s,(18,26,55),panel,border_radius=16)
        pygame.draw.rect(s,GOLD,panel,1,border_radius=16)

        draw_text(s,"Daily Challenges",self.fonts["title"],GOLD,
                  SCREEN_W//2,118,center=True)
        draw_text(s,"Complete these for bonus points!",
                  self.fonts["small"],TEXT_DIM,
                  SCREEN_W//2,150,center=True)

        for i,c in enumerate(challenges):
            cy       = 174+i*96
            done     = c["id"] in completed
            prog_val = progress.get(c["id"],0)
            bg_c     = (20,50,20) if done else (20,20,45)
            bd_c     = GREEN if done else GOLD
            row      = pygame.Rect(200,cy,500,82)
            pygame.draw.rect(s,bg_c,row,border_radius=10)
            pygame.draw.rect(s,bd_c,row,1,border_radius=10)
            icon = "✓" if done else f"{prog_val}/{c['goal']}"
            ic   = GREEN if done else GOLD
            draw_text(s,icon,self.fonts["body"],ic,220,cy+12)
            draw_text(s,c["desc"],self.fonts["body"],
                      GREEN if done else TEXT,260,cy+12)
            draw_text(s,f"Reward: +{c['reward']} pts",
                      self.fonts["small"],GOLD,260,cy+38)
            if not done:
                bw=420; bx=260; by=cy+58
                pygame.draw.rect(s,(20,20,40),(bx,by,bw,10),border_radius=4)
                fw=int(bw*min(prog_val,c["goal"])/c["goal"])
                if fw>0:
                    pygame.draw.rect(s,GOLD,(bx,by,fw,10),border_radius=4)
                pygame.draw.rect(s,BORDER,(bx,by,bw,10),1,border_radius=4)

        close = pygame.Rect(SCREEN_W//2-65,488,130,36)
        hov   = close.collidepoint(mouse)
        draw_button(s,self.fonts["small"],"Close",close,hov,
                    base_col=ACCENT_DARK,hover_col=ACCENT)
        self._close_btn = close

    # ── End screen ────────────────────────────────────

    def _draw_end_screen(self):
        s     = self.screen
        mouse = pygame.mouse.get_pos()

        overlay = pygame.Surface((SCREEN_W,SCREEN_H),pygame.SRCALPHA)
        overlay.fill((0,0,0,185))
        s.blit(overlay,(0,0))

        if self.game_won:
            col  = GREEN
            msg1 = "SEASON COMPLETE!"
            msg2 = "You reduced pollution below 50%!"
            msg3 = f"Final score: {self.state['points']} points"
            msg4 = "Great work, Mayor!"
        else:
            col  = RED
            msg1 = "GAME OVER"
            msg2 = "Pollution is too high -- the city suffers!"
            msg3 = "Answer quizzes and buy upgrades faster."
            msg4 = "Try again!"

        panel = pygame.Rect(140,140,620,320)
        pygame.draw.rect(s,(18,22,50),panel,border_radius=16)
        pygame.draw.rect(s,col,panel,2,border_radius=16)
        pygame.draw.rect(s,col,(140,140,620,6),border_radius=16)

        draw_text(s,msg1,self.fonts["title"],col,
                  SCREEN_W//2,192,center=True)
        draw_text(s,msg2,self.fonts["body"],TEXT,
                  SCREEN_W//2,240,center=True)
        draw_text(s,msg3,self.fonts["small"],GOLD,
                  SCREEN_W//2,272,center=True)
        draw_text(s,msg4,self.fonts["small"],col,
                  SCREEN_W//2,300,center=True)

        xp  = self.state.get("xp",0)
        lvl,ttl,_ = get_level_info(xp)
        draw_text(s,f"Level {lvl}  --  {ttl}  |  XP: {xp}",
                  self.fonts["small"],PURPLE,
                  SCREEN_W//2,326,center=True)

        ach_count = len(self.state.get("achievements",[]))
        draw_text(s,f"Achievements unlocked this game: {ach_count}",
                  self.fonts["tiny"],GOLD,
                  SCREEN_W//2,350,center=True)

        retry = pygame.Rect(SCREEN_W//2-145,372,130,42)
        quit_ = pygame.Rect(SCREEN_W//2+15, 372,130,42)
        draw_button(s,self.fonts["small"],"Play Again",
                    retry,retry.collidepoint(mouse),
                    base_col=ACCENT_DARK,hover_col=ACCENT)
        draw_button(s,self.fonts["small"],"Quit",
                    quit_,quit_.collidepoint(mouse),
                    base_col=(60,15,15),
                    hover_col=(160,30,30),
                    border_col=RED)
        self._retry_btn = retry
        self._quit_btn  = quit_

    # ── Main draw ─────────────────────────────────────

    def draw(self):
        self.screen.fill(BG)
        self._update_disasters()
        self._check_achievements()
        self._check_season()
        self._draw_sky()
        self._draw_smoke()
        self._draw_buildings()
        self._draw_trees()
        self._draw_ground()
        self._draw_rain()
        self._draw_stats()
        self._draw_nav()
        self._draw_disaster()
        self._draw_achieve_toast()
        self._draw_challenge_toast()

        if self.show_challenges:
            self._draw_challenges_panel()
        elif self.show_achievements:
            self._draw_achievements_panel()
        elif self.game_over or self.game_won:
            self._draw_end_screen()

    # ── Events ────────────────────────────────────────

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos  = event.pos
            role = self.state["user"]["role"]

            if self.show_challenges:
                if self._close_btn and self._close_btn.collidepoint(pos):
                    SoundManager.play("click")
                    self.show_challenges = False
                return None

            if self.show_achievements:
                if self._close_btn and self._close_btn.collidepoint(pos):
                    SoundManager.play("click")
                    self.show_achievements = False
                return None

            if self.game_over or self.game_won:
                if self._retry_btn and self._retry_btn.collidepoint(pos):
                    SoundManager.play("click")
                    self.state.update({
                        "points":0,"day":1,"achievements":[],
                        "total_earned":0,"upgrades_bought":0,
                        "correct_answers":0,"max_pollution":0,
                        "disasters_survived":0,"shop_spent":0,
                        "perfect_streak":0,
                    })
                    from game_data import pick_daily_challenges
                    chs = pick_daily_challenges(3)
                    self.state["daily_challenges"] = chs
                    self.state["daily_progress"]   = {c["id"]:0 for c in chs}
                    self.state["daily_completed"]  = []
                    self.state["start_pollution"]  = self.state["pollution"]
                    self.game_over = False
                    self.game_won  = False
                    self._prev_poll_zone = None
                    self.last_event_tick = pygame.time.get_ticks()
                    SoundManager.start_music(
                        lambda: self.state["pollution"])
                    return "save_season"
                if self._quit_btn and self._quit_btn.collidepoint(pos):
                    import sys
                    pygame.quit()
                    sys.exit()
                return None

            if self.btn_quiz.collidepoint(pos):
                SoundManager.play("click"); return "quiz"
            if self.btn_shop.collidepoint(pos):
                SoundManager.play("click"); return "shop"
            if self.btn_profile.collidepoint(pos):
                SoundManager.play("click"); return "profile"
            if self.btn_settings.collidepoint(pos):
                SoundManager.play("click"); return "settings"
            if self.btn_achieve.collidepoint(pos):
                SoundManager.play("click")
                self.show_achievements = not self.show_achievements
                self.show_challenges   = False
                return None
            if role in ("Moderator","Admin"):
                if self.btn_mod.collidepoint(pos):
                    SoundManager.play("click"); return "moderator"
            if role == "Admin":
                if self.btn_admin.collidepoint(pos):
                    SoundManager.play("click"); return "admin"
            if self.btn_logout.collidepoint(pos):
                return "logout"

        return None
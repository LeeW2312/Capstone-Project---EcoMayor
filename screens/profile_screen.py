"""
EcoCity Mayor — screens/profile_screen.py
Player profile with XP bar, level, pollution history graph,
daily challenges, season replay.
"""

import pygame
import json
import os

from game_data import ACHIEVEMENTS as ACH_LIST, get_level_info

BG          = (15,  15,  30)
PANEL       = (22,  33,  62)
CARD2       = (16,  20,  42)
ACCENT      = (78,  144, 217)
ACCENT_D    = (12,  44,  88)
TEXT        = (220, 220, 220)
TEXT_DIM    = (130, 130, 150)
GREEN       = (168, 216, 168)
RED         = (224, 92,  92)
GOLD        = (244, 200, 66)
BORDER      = (42,  42,  74)
BORDER2     = (55,  60,  96)
WHITE       = (255, 255, 255)
ORANGE      = (230, 140, 40)
PURPLE      = (145, 85,  215)

SCREEN_W, SCREEN_H = 900, 600
USERS_FILE  = os.path.join("data","users.json")
LEADER_FILE = os.path.join("data","leaderboard.json")

ACHIEVEMENTS = ACH_LIST


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return []

def draw_text(surf, text, font, color, x, y, center=False, mw=0):
    t = str(text)
    if mw and font.size(t)[0] > mw:
        while font.size(t+"...")[0] > mw and t:
            t = t[:-1]
        t += "..."
    img = font.render(t, True, color)
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
        pygame.draw.rect(surf,ACCENT_D,r,border_radius=8)
        pygame.draw.rect(surf,ACCENT,r,1,border_radius=8)
        draw_text(surf,text,font,TEXT,r.centerx,r.centery,center=True)


class ProfileScreen:
    def __init__(self, screen, fonts, game_state):
        self.screen = screen
        self.fonts  = fonts
        self.state  = game_state
        self.tab    = "stats"

        self.btn_back    = pygame.Rect(20,  15, 90, 34)
        self.tab_rects   = [
            pygame.Rect(270, 70, 110, 28),
            pygame.Rect(390, 70, 130, 28),
            pygame.Rect(530, 70, 110, 28),
            pygame.Rect(650, 70, 130, 28),
        ]
        self.tab_labels  = ["Stats","Achievements","History","Challenges"]
        self.tab_colours = [ACCENT, GOLD, ORANGE, PURPLE]

    def _user_data(self):
        users = load_json(USERS_FILE)
        uname = self.state["user"]["username"]
        for u in users:
            if u["username"] == uname:
                return u
        return self.state["user"]

    def _my_results(self):
        lb    = load_json(LEADER_FILE)
        uname = self.state["user"]["username"]
        return [e for e in lb if e["username"] == uname]

    def draw(self):
        s     = self.screen
        mouse = pygame.mouse.get_pos()
        s.fill(BG)

        pygame.draw.rect(s,PANEL,(0,0,SCREEN_W,60))
        pygame.draw.line(s,BORDER,(0,60),(SCREEN_W,60),1)
        draw_text(s,"My Profile",
                  self.fonts["body"],GREEN,SCREEN_W//2,18,center=True)
        draw_button(s,self.fonts["small"],"Back",
                    self.btn_back,self.btn_back.collidepoint(mouse))

        pygame.draw.rect(s,BG,(0,61,SCREEN_W,44))
        pygame.draw.line(s,BORDER,(0,104),(SCREEN_W,104),1)

        for i,(rect,label) in enumerate(zip(self.tab_rects,self.tab_labels)):
            active = self.tab == label.lower()
            col    = self.tab_colours[i]
            bg_c   = (col[0]//5,col[1]//5,col[2]//5) if active else (13,15,34)
            pygame.draw.rect(s,bg_c,rect,border_radius=8)
            pygame.draw.rect(s,col if active else BORDER2,rect,1,border_radius=8)
            if active:
                pygame.draw.rect(s,col,(rect.x+4,rect.bottom-2,rect.w-8,3))
            draw_text(s,label,self.fonts["small"],
                      WHITE if active else TEXT_DIM,
                      rect.centerx,rect.centery,center=True)

        ud = self._user_data()
        if self.tab == "stats":
            self._draw_stats(s, ud)
        elif self.tab == "achievements":
            self._draw_achievements(s)
        elif self.tab == "history":
            self._draw_history(s)
        else:
            self._draw_challenges(s)

    def _draw_stats(self, s, ud):
        uname    = ud["username"]
        role     = ud["role"]
        st       = ud.get("stats",{})
        unlocked = self.state.get("achievements",[])
        xp       = self.state.get("xp",0)
        level, title, next_xp = get_level_info(xp)

        # Avatar
        pygame.draw.circle(s,ACCENT_D,(100,190),48)
        pygame.draw.circle(s,ACCENT,  (100,190),48,2)
        draw_text(s,uname[0].upper(),self.fonts["title"],WHITE,
                  100,190,center=True)

        draw_text(s,uname,self.fonts["body"],GREEN,168,152)
        draw_text(s,f"Role: {role}",self.fonts["small"],TEXT_DIM,168,178)

        # Level badge
        lbadge = pygame.Rect(168,198,160,22)
        pygame.draw.rect(s,(40,10,80),lbadge,border_radius=6)
        pygame.draw.rect(s,PURPLE,lbadge,1,border_radius=6)
        draw_text(s,f"Lv{level}  {title}",
                  self.fonts["small"],PURPLE,
                  lbadge.centerx,lbadge.centery,center=True)

        # XP bar
        xp_bx, xp_by, xp_bw = 168, 228, 300
        pygame.draw.rect(s,(20,20,40),(xp_bx,xp_by,xp_bw,12),border_radius=5)
        if next_xp and next_xp > 0:
            fw = int(xp_bw * min(xp,next_xp) / next_xp)
            if fw > 0:
                pygame.draw.rect(s,PURPLE,(xp_bx,xp_by,fw,12),border_radius=5)
            draw_text(s,f"XP: {xp}/{next_xp}",
                      self.fonts["tiny"],TEXT_DIM,xp_bx,xp_by+16)
        else:
            pygame.draw.rect(s,GOLD,(xp_bx,xp_by,xp_bw,12),border_radius=5)
            draw_text(s,"MAX LEVEL",self.fonts["tiny"],GOLD,xp_bx,xp_by+16)
        pygame.draw.rect(s,BORDER2,(xp_bx,xp_by,xp_bw,12),1,border_radius=5)

        # Stat cards
        cards = [
            ("Seasons Played", st.get("seasons_played",0), TEXT),
            ("Best Score",     st.get("best_score",0),     GOLD),
            ("Total Points",   st.get("total_points",0),   GOLD),
            ("Correct Answers",st.get("total_correct",0),  GREEN),
            ("Achievements",
             f"{len(unlocked)}/{len(ACHIEVEMENTS)}", GREEN),
            ("This Season",    self.state.get("points",0), GOLD),
        ]
        cols = 3; cw = 235; ch = 65; gap = 16
        sx   = 50; sy = 264
        for i,(label,val,col) in enumerate(cards):
            cx = sx + (i%cols)*(cw+gap)
            cy = sy + (i//cols)*(ch+gap)
            card = pygame.Rect(cx,cy,cw,ch)
            pygame.draw.rect(s,CARD2,card,border_radius=10)
            pygame.draw.rect(s,BORDER2,card,1,border_radius=10)
            pygame.draw.rect(s,col,(cx+1,cy+1,cw-2,3),border_radius=10)
            draw_text(s,label,self.fonts["tiny"],TEXT_DIM,cx+12,cy+10)
            draw_text(s,str(val),self.fonts["body"],col,cx+12,cy+32)

        # Pollution history graph
        history = self.state.get("pollution_history",[])
        if len(history) >= 2:
            gx,gy,gw,gh = 50,430,SCREEN_W-100,120
            pygame.draw.rect(s,CARD2,(gx,gy,gw,gh),border_radius=8)
            pygame.draw.rect(s,BORDER2,(gx,gy,gw,gh),1,border_radius=8)
            draw_text(s,"Pollution History",
                      self.fonts["tiny"],TEXT_DIM,gx+8,gy+6)
            # 50% goal line
            goal_y = gy + int(gh * 0.5)
            pygame.draw.line(s,(40,80,40),(gx+4,goal_y),(gx+gw-4,goal_y),1)
            draw_text(s,"50%",self.fonts["tiny"],(40,80,40),gx+gw-28,goal_y-14)
            # Plot line
            pts = []
            for i,val in enumerate(history[-30:]):
                px = gx + 4 + int((gw-8)*i/max(len(history[-30:])-1,1))
                py = gy + int(gh * val/100)
                pts.append((px,py))
            if len(pts) >= 2:
                col_line = RED if history[-1]>=70 else \
                           GOLD if history[-1]>=50 else GREEN
                pygame.draw.lines(s,col_line,False,pts,2)
                pygame.draw.circle(s,col_line,pts[-1],4)

    def _draw_achievements(self, s):
        unlocked = self.state.get("achievements",[])
        draw_text(s,"Achievements",
                  self.fonts["body"],GOLD,SCREEN_W//2,118,center=True)

        for i,ach in enumerate(ACHIEVEMENTS):
            col_i = i%2; row_i = i//2
            cx = 60+col_i*440; cy = 148+row_i*100
            achieved = ach["id"] in unlocked
            card = pygame.Rect(cx,cy,400,85)
            bg_c = (20,50,20) if achieved else PANEL
            bd_c = GREEN if achieved else BORDER
            pygame.draw.rect(s,bg_c,card,border_radius=10)
            pygame.draw.rect(s,bd_c,card,1,border_radius=10)
            icon = "★" if achieved else "○"
            col  = GREEN if achieved else TEXT_DIM
            draw_text(s,f"{icon}  {ach['name']}",
                      self.fonts["body"],col,cx+16,cy+14)
            draw_text(s,ach["desc"],
                      self.fonts["tiny"],TEXT_DIM,cx+16,cy+44)
            if achieved:
                draw_text(s,"UNLOCKED",self.fonts["tiny"],GREEN,
                          cx+card.width-90,cy+14)

        draw_text(s,
                  f"Total: {len(unlocked)} / {len(ACHIEVEMENTS)} unlocked",
                  self.fonts["small"],GOLD,SCREEN_W//2,452,center=True)

    def _draw_history(self, s):
        results = self._my_results()
        draw_text(s,"Season History",
                  self.fonts["body"],GOLD,SCREEN_W//2,118,center=True)

        if not results:
            draw_text(s,"No seasons completed yet.",
                      self.fonts["small"],TEXT_DIM,
                      SCREEN_W//2,280,center=True)
            return

        hx = [60,180,320,450,570,680,800]
        for label,x,col in zip(
                ["#","Points","Pollution","Day","XP","Result",""],
                hx,
                [TEXT_DIM,GOLD,TEXT_DIM,TEXT_DIM,PURPLE,TEXT_DIM,TEXT_DIM]):
            draw_text(s,label,self.fonts["tiny"],col,x,142)
        pygame.draw.line(s,BORDER,(50,158),(860,158),1)

        row_y = 166
        for i,e in enumerate(reversed(results[-14:])):
            if row_y > SCREEN_H-40:
                break
            won_col = GREEN if e.get("won") else RED
            won_lbl = "WIN"  if e.get("won") else "LOSS"
            pygame.draw.rect(s,
                             (20,24,52) if i%2==0 else (14,18,40),
                             (50,row_y-2,820,22),border_radius=3)
            draw_text(s,f"#{i+1}",self.fonts["tiny"],TEXT_DIM,hx[0],row_y)
            draw_text(s,str(e["points"]),self.fonts["tiny"],GOLD,hx[1],row_y)
            draw_text(s,f"{e['pollution']}%",self.fonts["tiny"],TEXT,hx[2],row_y)
            draw_text(s,f"Day {e['day']}",self.fonts["tiny"],TEXT,hx[3],row_y)
            draw_text(s,str(e.get("xp","-")),self.fonts["tiny"],PURPLE,hx[4],row_y)

            pill = pygame.Rect(hx[5],row_y-2,58,18)
            pygame.draw.rect(s,(10,40,10) if e.get("won") else (40,10,10),
                             pill,border_radius=4)
            pygame.draw.rect(s,won_col,pill,1,border_radius=4)
            draw_text(s,won_lbl,self.fonts["tiny"],won_col,
                      pill.centerx,pill.centery,center=True)
            row_y += 26

    def _draw_challenges(self, s):
        challenges = self.state.get("daily_challenges",[])
        progress   = self.state.get("daily_progress",{})
        completed  = self.state.get("daily_completed",[])

        draw_text(s,"Daily Challenges",
                  self.fonts["body"],GOLD,SCREEN_W//2,118,center=True)
        draw_text(s,"Complete each challenge for bonus points.",
                  self.fonts["small"],TEXT_DIM,
                  SCREEN_W//2,148,center=True)

        for i,c in enumerate(challenges):
            cy       = 170+i*110
            done     = c["id"] in completed
            prog_val = progress.get(c["id"],0)

            card = pygame.Rect(60,cy,SCREEN_W-120,94)
            bg_c = (16,48,16) if done else CARD2
            bd_c = GREEN if done else GOLD
            pygame.draw.rect(s,bg_c,card,border_radius=12)
            pygame.draw.rect(s,bd_c,card,1,border_radius=12)

            icon = "✓" if done else f"{prog_val}/{c['goal']}"
            ic   = GREEN if done else GOLD
            pygame.draw.rect(s,
                             (10,40,10) if done else CARD2,
                             (74,cy+12,52,52),border_radius=8)
            pygame.draw.rect(s,bd_c,(74,cy+12,52,52),1,border_radius=8)
            draw_text(s,icon,self.fonts["small"],ic,100,cy+36,center=True)

            draw_text(s,c["desc"],self.fonts["body"],
                      GREEN if done else TEXT,138,cy+14)
            draw_text(s,
                      f"Reward: +{c['reward']} pts  |  Type: {c['type']}",
                      self.fonts["small"],GOLD,138,cy+42)

            if not done:
                bw = SCREEN_W-220; bx = 138; by = cy+66
                pygame.draw.rect(s,(20,20,40),(bx,by,bw,10),border_radius=4)
                fw = int(bw*min(prog_val,c["goal"])/c["goal"])
                if fw > 0:
                    pygame.draw.rect(s,GOLD,(bx,by,fw,10),border_radius=4)
                pygame.draw.rect(s,BORDER,(bx,by,bw,10),1,border_radius=4)
            else:
                draw_text(s,"COMPLETED!",
                          self.fonts["small"],GREEN,138,cy+66)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.btn_back.collidepoint(pos):
                return "back"
            for i,(rect,label) in enumerate(
                    zip(self.tab_rects,self.tab_labels)):
                if rect.collidepoint(pos):
                    self.tab = label.lower()
        return None
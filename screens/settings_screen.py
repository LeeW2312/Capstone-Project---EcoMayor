"""
EcoCity Mayor — screens/settings_screen.py
Settings: display name, sound, volume, difficulty.
Fixed layout — no text blocking.
"""

import pygame
import json
import os

from sounds    import SoundManager
from game_data import DIFFICULTY

BG          = (11,  13,  26)
PANEL       = (18,  24,  48)
CARD2       = (16,  20,  42)
ACCENT      = (78,  144, 217)
ACCENT_D    = (12,  44,  88)
TEXT        = (228, 228, 242)
TEXT_DIM    = (115, 120, 155)
GREEN       = (72,  200, 118)
GREEN_D     = (10,  48,  26)
RED         = (215, 65,  65)
RED_D       = (52,  12,  12)
GOLD        = (236, 190, 50)
GOLD_D      = (50,  38,  6)
BORDER      = (38,  42,  72)
BORDER2     = (55,  60,  96)
WHITE       = (255, 255, 255)
ORANGE      = (222, 128, 26)
PURPLE      = (145, 85,  215)

SCREEN_W, SCREEN_H = 900, 600
USERS_FILE = os.path.join("data", "users.json")

# ── Layout — all absolute, nothing overlaps ────────────
# Section y positions
Y_NAME   = 68    # Display Name card top
Y_SOUND  = 178   # Sound card top
Y_VOL    = 282   # Volume card top
Y_DIFF   = 392   # Difficulty card top
Y_SAVE   = 542   # Save button top

# Card heights
H_NAME  = 100
H_SOUND = 94
H_VOL   = 100
H_DIFF  = 118


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return []

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def txt(surf, text, font, color, x, y, center=False):
    img = font.render(str(text), True, color)
    r   = img.get_rect()
    if center:
        r.center = (x, y)
    else:
        r.topleft = (x, y)
    surf.blit(img, r)

def action_btn(surf, font, label, rect, hov,
               bg=None, hbg=None, border=None, fg=None):
    r = pygame.Rect(rect)
    if hov:
        hc = hbg or ACCENT
        pygame.draw.rect(surf, hc, r, border_radius=8)
        pygame.draw.rect(surf, WHITE, r, 2, border_radius=8)
        sh = pygame.Surface((r.w, r.h//2), pygame.SRCALPHA)
        sh.fill((255,255,255,18))
        surf.blit(sh, (r.x, r.y))
        txt(surf, label, font, WHITE, r.centerx, r.centery, center=True)
    else:
        pygame.draw.rect(surf, bg or ACCENT_D, r, border_radius=8)
        pygame.draw.rect(surf, border or ACCENT, r, 1, border_radius=8)
        txt(surf, label, font, fg or TEXT,
            r.centerx, r.centery, center=True)


class InputBox:
    def __init__(self, x, y, w, h, initial="", maxlen=24):
        self.rect   = pygame.Rect(x, y, w, h)
        self.text   = initial
        self.active = False
        self.maxlen = maxlen

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key not in (pygame.K_RETURN, pygame.K_TAB):
                if len(self.text) < self.maxlen:
                    self.text += event.unicode

    def draw(self, surf, font):
        bc  = ACCENT if self.active else BORDER2
        bgc = (22, 28, 60) if self.active else (14, 18, 42)
        pygame.draw.rect(surf, bgc, self.rect, border_radius=8)
        pygame.draw.rect(surf, bc,  self.rect,
                         2 if self.active else 1, border_radius=8)
        disp = self.text if self.text else "Enter display name..."
        col  = TEXT if self.text else TEXT_DIM
        mw   = self.rect.w - 20
        show = disp
        if font.size(show)[0] > mw:
            while font.size(show)[0] > mw and show:
                show = show[1:]
        txt(surf, show, font, col,
            self.rect.x + 10,
            self.rect.centery - font.get_height()//2)
        if self.active and (pygame.time.get_ticks()//500)%2==0:
            tw = min(font.size(self.text)[0], mw)
            pygame.draw.line(surf, ACCENT,
                (self.rect.x+10+tw+2, self.rect.y+5),
                (self.rect.x+10+tw+2, self.rect.bottom-5), 2)


class SettingsScreen:
    def __init__(self, screen, fonts, game_state):
        self.screen = screen
        self.fonts  = fonts
        self.state  = game_state

        self.btn_back = pygame.Rect(14, 15, 100, 28)
        self.btn_save = pygame.Rect(SCREEN_W//2-90, Y_SAVE, 180, 42)

        # Name input — sits inside name card, below subtitle
        current = game_state["user"]["username"]
        self.name_box = InputBox(
            SCREEN_W//2-220, Y_NAME+58,
            440, 34, initial=current)

        # Sound
        self.sound_on  = SoundManager._enabled
        self.btn_sound = pygame.Rect(
            SCREEN_W//2-80, Y_SOUND+52, 160, 32)

        # Volume
        self.volume   = game_state.get("volume", 75)
        vol_opts      = [0, 25, 50, 75, 100]
        self.vol_opts = vol_opts
        self.vol_lbls = ["0%","25%","50%","75%","100%"]
        bw = 92; gap = 12
        tw = len(vol_opts)*bw + (len(vol_opts)-1)*gap
        sx = SCREEN_W//2 - tw//2
        self.vol_rects = [
            pygame.Rect(sx+i*(bw+gap), Y_VOL+58, bw, 30)
            for i in range(len(vol_opts))
        ]

        # Difficulty
        self.difficulty = game_state.get("difficulty","medium")
        self.diff_keys  = ["easy","medium","hard"]
        dbw = 158; dgap = 18
        dtw = len(self.diff_keys)*dbw + (len(self.diff_keys)-1)*dgap
        dsx = SCREEN_W//2 - dtw//2
        self.diff_rects = [
            pygame.Rect(dsx+i*(dbw+dgap), Y_DIFF+62, dbw, 38)
            for i in range(len(self.diff_keys))
        ]

        self.toast_msg  = ""
        self.toast_time = 0
        self.toast_err  = False

    # ── Card background ───────────────────────────────

    def _card(self, s, y, h, title, subtitle, col):
        """Draw section card with title and subtitle — no content overlap."""
        # Background
        pygame.draw.rect(s, CARD2, (60, y, SCREEN_W-120, h),
                         border_radius=10)
        # Border
        pygame.draw.rect(s, col,  (60, y, SCREEN_W-120, h),
                         1, border_radius=10)
        # Left accent stripe
        pygame.draw.rect(s, col,  (61, y+1, 4, h-2),
                         border_radius=10)
        # Title — always at y+12
        txt(s, title,    self.fonts["body"],  col,     80, y+12)
        # Subtitle — always at y+34, guaranteed above content (y+56+)
        txt(s, subtitle, self.fonts["small"], TEXT_DIM, 80, y+34)

    # ── Save ─────────────────────────────────────────

    def _save(self):
        new_name = self.name_box.text.strip()
        if len(new_name) < 3:
            self.toast_msg  = "Username must be at least 3 characters."
            self.toast_time = pygame.time.get_ticks() + 3000
            self.toast_err  = True
            return

        SoundManager._enabled = self.sound_on
        SoundManager.set_volume(self.volume / 100.0)

        users    = load_json(USERS_FILE)
        old_name = self.state["user"]["username"]
        for u in users:
            if u["username"] == old_name:
                u["username"]   = new_name
                u["difficulty"] = self.difficulty
                u["volume"]     = self.volume
                u["sound_on"]   = self.sound_on
                break
        save_json(USERS_FILE, users)

        self.state["user"]["username"] = new_name
        self.state["difficulty"]       = self.difficulty
        self.state["volume"]           = self.volume

        self.toast_msg  = "Settings saved!"
        self.toast_time = pygame.time.get_ticks() + 2500
        self.toast_err  = False
        SoundManager.play("save")

    # ── Draw ─────────────────────────────────────────

    def draw(self):
        s     = self.screen
        mouse = pygame.mouse.get_pos()
        s.fill(BG)

        # Top bar
        pygame.draw.rect(s, PANEL, (0, 0, SCREEN_W, 58))
        pygame.draw.rect(s, (22,32,66), (0, 0, SCREEN_W, 20))
        pygame.draw.line(s, BORDER2, (0,58),(SCREEN_W,58),1)
        txt(s,"Settings",self.fonts["body"],GREEN,
            SCREEN_W//2,16,center=True)
        action_btn(s,self.fonts["small"],"Back",
                   self.btn_back,self.btn_back.collidepoint(mouse),
                   bg=(20,10,48),hbg=ACCENT,border=ACCENT,fg=TEXT)

        # ── 1. Display Name ───────────────────────────
        # Card: y=68, h=100 → title@80, subtitle@102, input@126
        self._card(s, Y_NAME, H_NAME,
                   "Display Name",
                   "Changes your visible username in the game.",
                   ACCENT)
        self.name_box.draw(s, self.fonts["body"])

        # ── 2. Sound ──────────────────────────────────
        # Card: y=178, h=94 → title@190, subtitle@212, btn@230
        snd_col = GREEN if self.sound_on else RED
        snd_sub = ("Sound is currently ON  --  click to turn OFF"
                   if self.sound_on else
                   "Sound is currently OFF  --  click to turn ON")
        self._card(s, Y_SOUND, H_SOUND,
                   "Sound Effects & Music", snd_sub, snd_col)
        action_btn(s, self.fonts["small"],
                   "Sound: ON" if self.sound_on else "Sound: OFF",
                   self.btn_sound,
                   self.btn_sound.collidepoint(mouse),
                   bg=GREEN_D  if self.sound_on else RED_D,
                   hbg=GREEN   if self.sound_on else RED,
                   border=GREEN if self.sound_on else RED,
                   fg=GREEN    if self.sound_on else RED)

        # ── 3. Volume ─────────────────────────────────
        # Card: y=282, h=100 → title@294, subtitle@316, btns@340
        self._card(s, Y_VOL, H_VOL,
                   "Volume",
                   "Adjust the volume of all sound effects and music.",
                   ACCENT)
        for r, lbl, val in zip(
                self.vol_rects, self.vol_lbls, self.vol_opts):
            sel = val == self.volume
            hov = r.collidepoint(mouse)
            if sel:
                pygame.draw.rect(s, ACCENT, r, border_radius=7)
                pygame.draw.rect(s, WHITE,  r, 2, border_radius=7)
                txt(s, lbl, self.fonts["body"], WHITE,
                    r.centerx, r.centery, center=True)
            elif hov:
                pygame.draw.rect(s,(30,34,70),r,border_radius=7)
                pygame.draw.rect(s,BORDER2,r,1,border_radius=7)
                txt(s,lbl,self.fonts["small"],WHITE,
                    r.centerx,r.centery,center=True)
            else:
                pygame.draw.rect(s,(14,16,36),r,border_radius=7)
                pygame.draw.rect(s,BORDER,r,1,border_radius=7)
                txt(s,lbl,self.fonts["small"],TEXT_DIM,
                    r.centerx,r.centery,center=True)

        # ── 4. Difficulty ─────────────────────────────
        # Card: y=392, h=118 → title@404, subtitle@426, btns@454
        diff_descs = {
            "easy":   "Slower rise, fewer disasters, upgrades cost 20% less",
            "medium": "Balanced challenge for most players",
            "hard":   "Faster rise, more disasters, upgrades cost 25% more",
        }
        self._card(s, Y_DIFF, H_DIFF,
                   "Difficulty",
                   "Affects pollution rise speed, disaster frequency and upgrade costs.",
                   GOLD)

        for r, key in zip(self.diff_rects, self.diff_keys):
            d   = DIFFICULTY[key]
            sel = key == self.difficulty
            col = d["colour"]
            hov = r.collidepoint(mouse)
            if sel:
                bg_c = tuple(c//4 for c in col)
                pygame.draw.rect(s, bg_c, r, border_radius=8)
                pygame.draw.rect(s, col,  r, 2, border_radius=8)
                pygame.draw.rect(s, col,
                    (r.x+6, r.bottom-3, r.w-12, 3))
                txt(s, d["label"], self.fonts["body"], col,
                    r.centerx, r.centery, center=True)
            elif hov:
                pygame.draw.rect(s,(28,32,64),r,border_radius=8)
                pygame.draw.rect(s,col,r,1,border_radius=8)
                txt(s,d["label"],self.fonts["body"],WHITE,
                    r.centerx,r.centery,center=True)
            else:
                pygame.draw.rect(s,(14,16,36),r,border_radius=8)
                pygame.draw.rect(s,BORDER,r,1,border_radius=8)
                txt(s,d["label"],self.fonts["body"],TEXT_DIM,
                    r.centerx,r.centery,center=True)

        # Selected difficulty description — below card
        sel_col  = DIFFICULTY[self.difficulty]["colour"]
        sel_desc = diff_descs.get(self.difficulty,"")
        txt(s, sel_desc, self.fonts["small"], sel_col,
            SCREEN_W//2, Y_DIFF+H_DIFF+12, center=True)

        # ── Save button ───────────────────────────────
        action_btn(s,self.fonts["body"],"Save Settings",
                   self.btn_save,self.btn_save.collidepoint(mouse),
                   bg=GREEN_D,hbg=GREEN,border=GREEN,fg=GREEN)

        # ── Toast ─────────────────────────────────────
        if self.toast_msg and pygame.time.get_ticks()<self.toast_time:
            bg_c = RED_D  if self.toast_err else GREEN_D
            bd_c = RED    if self.toast_err else GREEN
            ts   = self.fonts["body"].render(
                self.toast_msg,True,WHITE)
            tw   = ts.get_width()
            tx   = SCREEN_W//2 - tw//2 - 20
            pygame.draw.rect(s,bg_c,(tx,560,tw+40,34),border_radius=9)
            pygame.draw.rect(s,bd_c,(tx,560,tw+40,34),1,border_radius=9)
            s.blit(ts,(tx+20,568))

    # ── Events ────────────────────────────────────────

    def handle_event(self, event):
        self.name_box.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            if self.btn_back.collidepoint(pos):
                SoundManager.play("back")
                return "back"

            if self.btn_save.collidepoint(pos):
                self._save()

            if self.btn_sound.collidepoint(pos):
                self.sound_on = not self.sound_on
                SoundManager.play("click")

            for r, val in zip(self.vol_rects, self.vol_opts):
                if r.collidepoint(pos):
                    self.volume = val
                    SoundManager.set_volume(val/100.0)
                    SoundManager.play("click")

            for r, key in zip(self.diff_rects, self.diff_keys):
                if r.collidepoint(pos):
                    self.difficulty = key
                    SoundManager.play("click")

        return None
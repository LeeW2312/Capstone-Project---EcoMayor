"""
EcoCity Mayor — screens/admin_screen.py
Admin Panel — clean redesign matching moderator style.
"""

import pygame
import json
import os

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
ORANGE_D    = (50,  24,  4)
PURPLE      = (145, 85,  215)
PURPLE_D    = (34,  10,  70)

SCREEN_W, SCREEN_H = 900, 600
USERS_FILE  = os.path.join("data", "users.json")
LEADER_FILE = os.path.join("data", "leaderboard.json")

TOP_H    = 58
TAB_Y    = 64
TAB_H    = 28
DIV_Y    = 97
FOOTER_Y = 572


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return []


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def txt(surf, text, font, color, x, y, center=False, mw=0):
    t = str(text)
    if mw and font.size(t)[0] > mw:
        while font.size(t + "...")[0] > mw and t:
            t = t[:-1]
        t += "..."
    img = font.render(t, True, color)
    r   = img.get_rect()
    if center:
        r.center = (x, y)
    else:
        r.topleft = (x, y)
    surf.blit(img, r)


def btn(surf, font, label, rect, hov, active=True,
        bg=None, hbg=None, border=None, fg=None):
    r = pygame.Rect(rect)
    if not active:
        pygame.draw.rect(surf, (24, 26, 46), r, border_radius=7)
        pygame.draw.rect(surf, BORDER, r, 1, border_radius=7)
        txt(surf, label, font, TEXT_DIM, r.centerx, r.centery, center=True)
    elif hov:
        hc = hbg or ACCENT
        pygame.draw.rect(surf, hc, r, border_radius=7)
        pygame.draw.rect(surf, WHITE, r, 2, border_radius=7)
        sh = pygame.Surface((r.w, r.h // 2), pygame.SRCALPHA)
        sh.fill((255, 255, 255, 18))
        surf.blit(sh, (r.x, r.y))
        txt(surf, label, font, WHITE, r.centerx, r.centery, center=True)
    else:
        pygame.draw.rect(surf, bg or ACCENT_D, r, border_radius=7)
        pygame.draw.rect(surf, border or ACCENT, r, 1, border_radius=7)
        txt(surf, label, font, fg or TEXT, r.centerx, r.centery, center=True)
    return r


class AdminScreen:
    def __init__(self, screen, fonts, game_state):
        self.screen = screen
        self.fonts  = fonts
        self.state  = game_state

        self.tab = "users"

        # Fixed buttons
        self.btn_back    = pygame.Rect(12,  15, 138, 28)
        self.btn_logout  = pygame.Rect(SCREEN_W - 112, 15, 98, 28)
        self.btn_clr_lb  = pygame.Rect(SCREEN_W - 200, TAB_Y, 186, TAB_H)

        # Tab buttons
        self.tab_rects = [
            pygame.Rect(210, TAB_Y, 190, TAB_H),
            pygame.Rect(410, TAB_Y, 190, TAB_H),
        ]
        self.tab_labels  = ["User Management", "Leaderboard"]
        self.tab_colours = [ACCENT, GOLD]

        self.toast_msg  = ""
        self.toast_time = 0
        self.toast_err  = False

        self.action_rects = []
        self.u_scroll     = 0
        self.l_scroll     = 0

    # ── Helpers ───────────────────────────────────────

    def _toast(self, msg, err=False):
        self.toast_msg  = msg
        self.toast_time = pygame.time.get_ticks() + 3000
        self.toast_err  = err

    def _ban_user(self, username):
        users = load_json(USERS_FILE)
        for u in users:
            if u["username"] == username:
                u["banned"] = not u.get("banned", False)
                action = "banned" if u["banned"] else "unbanned"
                save_json(USERS_FILE, users)
                self._toast(f"{username} has been {action}.")
                return
        self._toast("User not found.", err=True)

    def _change_role(self, username, new_role):
        users = load_json(USERS_FILE)
        for u in users:
            if u["username"] == username:
                u["role"] = new_role
                save_json(USERS_FILE, users)
                self._toast(f"{username} is now {new_role}.")
                return

    def _reset_leaderboard(self):
        save_json(LEADER_FILE, [])
        self._toast("Leaderboard cleared.")

    def _reset_user_stats(self, username):
        users = load_json(USERS_FILE)
        for u in users:
            if u["username"] == username:
                u["stats"] = {
                    "seasons_played": 0, "best_score": 0,
                    "total_points":   0, "total_correct": 0,
                }
                save_json(USERS_FILE, users)
                self._toast(f"{username} stats reset.")
                return

    # ── Stats summary ─────────────────────────────────

    def _summary_stats(self):
        users = load_json(USERS_FILE)
        lb    = load_json(LEADER_FILE)
        total = len(users)
        banned = sum(1 for u in users if u.get("banned"))
        mods   = sum(1 for u in users if u.get("role") == "Moderator")
        admins = sum(1 for u in users if u.get("role") == "Admin")
        seasons = len(lb)
        wins    = sum(1 for e in lb if e.get("won"))
        return {
            "total": total, "banned": banned,
            "mods": mods,   "admins": admins,
            "seasons": seasons, "wins": wins,
        }

    def _sblk(self, s, x, y, w, h, label, value, col):
        pygame.draw.rect(s, CARD2, (x, y, w, h), border_radius=10)
        pygame.draw.rect(s, col,   (x, y, w, h), 1, border_radius=10)
        pygame.draw.rect(s, col,   (x+1, y+1, w-2, 3), border_radius=10)
        txt(s, str(value), self.fonts["title"], col,
            x + w//2, y + h//2 - 8, center=True)
        txt(s, label, self.fonts["small"], TEXT_DIM,
            x + w//2, y + h - 16, center=True)

    # ══════════════════════════════════════════════════
    # USERS TAB
    # ══════════════════════════════════════════════════

    def _draw_users(self, s, mouse):
        users   = load_json(USERS_FILE)
        my_name = self.state["user"]["username"]
        st      = self._summary_stats()

        # ── Summary stat blocks ───────────────────────
        for x, y, w, h, lbl, val, col in [
            (12,  104, 130, 68, "Total Users",  st["total"],   ACCENT),
            (148, 104, 130, 68, "Banned",       st["banned"],  RED),
            (284, 104, 130, 68, "Moderators",   st["mods"],    PURPLE),
            (420, 104, 130, 68, "Admins",       st["admins"],  ORANGE),
            (556, 104, 130, 68, "Seasons",      st["seasons"], GOLD),
            (692, 104, 196, 68, "Seasons Won",
             f"{st['wins']}/{st['seasons']}", GREEN),
        ]:
            self._sblk(s, x, y, w, h, lbl, val, col)

        # ── Table header ──────────────────────────────
        HY = 180
        pygame.draw.rect(s, (22, 26, 56), (10, HY, 876, 28), border_radius=6)

        cols = [
            (18,  "#"),
            (50,  "Username"),
            (200, "Role"),
            (310, "Status"),
            (410, "Seasons"),
            (500, "Best Score"),
            (610, "Ban / Unban"),
            (730, "Change Role"),
            (848, "Reset"),
        ]
        for x, label in cols:
            txt(s, label, self.fonts["small"], ACCENT, x, HY + 6)

        # ── Scrollable user rows ──────────────────────
        ROW_H    = 32
        LIST_TOP = HY + 30
        LIST_H   = FOOTER_Y - LIST_TOP - 10
        visible  = max(1, LIST_H // ROW_H)
        max_scroll = max(0, len(users) - visible)
        self.u_scroll = max(0, min(self.u_scroll, max_scroll))

        s.set_clip(pygame.Rect(10, LIST_TOP, 876, LIST_H))
        self.action_rects = []

        for i, u in enumerate(
                users[self.u_scroll: self.u_scroll + visible + 1]):
            ry     = LIST_TOP + i * ROW_H
            if ry + ROW_H > LIST_TOP + LIST_H + 4:
                break
            is_me  = u["username"] == my_name
            banned = u.get("banned", False)

            # Row background
            row_bg = (48, 10, 10) if banned else (
                     (20, 24, 52) if i % 2 == 0 else (14, 18, 40))
            pygame.draw.rect(s, row_bg, (10, ry, 876, ROW_H - 1),
                             border_radius=4)

            # Banned stripe on left
            if banned:
                pygame.draw.rect(s, RED, (10, ry, 3, ROW_H - 1),
                                 border_radius=4)

            st_u     = u.get("stats", {})
            name_col = RED if banned else (TEXT_DIM if is_me else TEXT)
            status   = "BANNED" if banned else ("You" if is_me else "Active")
            stat_col = RED if banned else (ACCENT if is_me else GREEN)

            txt(s, str(self.u_scroll + i + 1),
                self.fonts["small"], TEXT_DIM, 18, ry + 8)
            txt(s, u["username"],
                self.fonts["body"], name_col, 50, ry + 8, mw=140)
            txt(s, u["role"],
                self.fonts["small"], TEXT, 200, ry + 8)
            txt(s, status,
                self.fonts["small"], stat_col, 310, ry + 8)
            txt(s, str(st_u.get("seasons_played", 0)),
                self.fonts["small"], TEXT, 410, ry + 8)
            txt(s, str(st_u.get("best_score", 0)),
                self.fonts["small"], GOLD, 500, ry + 8)

            if not is_me:
                # Ban / Unban button
                ban_r   = pygame.Rect(610, ry + 4, 96, 22)
                ban_bg  = PURPLE_D if banned else RED_D
                ban_bd  = PURPLE   if banned else RED
                ban_lbl = "Unban" if banned else "Ban"
                pygame.draw.rect(s, ban_bg, ban_r, border_radius=5)
                pygame.draw.rect(s, ban_bd, ban_r, 1, border_radius=5)
                txt(s, ban_lbl, self.fonts["small"],
                    WHITE, ban_r.centerx, ban_r.centery, center=True)
                self.action_rects.append(("ban", u["username"], ban_r))

                # Role cycle button
                roles     = ["Player", "Moderator", "Admin"]
                cur_idx   = roles.index(u["role"]) if u["role"] in roles else 0
                next_role = roles[(cur_idx + 1) % len(roles)]
                role_col  = {
                    "Player":    (ACCENT,  ACCENT_D),
                    "Moderator": (PURPLE,  PURPLE_D),
                    "Admin":     (ORANGE,  ORANGE_D),
                }.get(next_role, (ACCENT, ACCENT_D))

                role_r = pygame.Rect(730, ry + 4, 104, 22)
                pygame.draw.rect(s, role_col[1], role_r, border_radius=5)
                pygame.draw.rect(s, role_col[0], role_r, 1, border_radius=5)
                txt(s, f"Make {next_role}", self.fonts["small"],
                    WHITE, role_r.centerx, role_r.centery, center=True)
                self.action_rects.append(
                    ("role", u["username"], role_r, next_role))

                # Reset stats button
                rst_r = pygame.Rect(848, ry + 4, 30, 22)
                pygame.draw.rect(s, GOLD_D, rst_r, border_radius=5)
                pygame.draw.rect(s, GOLD,   rst_r, 1, border_radius=5)
                txt(s, "R", self.fonts["small"],
                    GOLD, rst_r.centerx, rst_r.centery, center=True)
                self.action_rects.append(("reset", u["username"], rst_r))

        s.set_clip(None)

        # Footer
        txt(s, f"Total:  {len(users)}  users",
            self.fonts["small"], TEXT_DIM, 18, FOOTER_Y)
        if len(users) > visible:
            txt(s,
                f"Scroll  {self.u_scroll + 1}-"
                f"{min(self.u_scroll + visible, len(users))}"
                f" / {len(users)}",
                self.fonts["small"], TEXT_DIM,
                SCREEN_W - 190, FOOTER_Y)

    # ══════════════════════════════════════════════════
    # LEADERBOARD TAB
    # ══════════════════════════════════════════════════

    def _draw_leaderboard(self, s, mouse):
        lb = load_json(LEADER_FILE)

        # Summary
        if lb:
            wins   = sum(1 for e in lb if e.get("won"))
            avg_pt = sum(e.get("points", 0) for e in lb) // max(len(lb), 1)
            best   = max(lb, key=lambda e: e.get("points", 0))

            for x, y, w, h, lbl, val, col in [
                (12,  104, 160, 68, "Seasons Played", len(lb),      GOLD),
                (178, 104, 160, 68, "Seasons Won",    wins,          GREEN),
                (344, 104, 160, 68, "Avg Score",      avg_pt,        ACCENT),
                (510, 104, 248, 68, "Top Player",
                 best["username"], ORANGE),
                (764, 104, 124, 68, "Top Score",
                 best.get("points", 0), GOLD),
            ]:
                self._sblk(s, x, y, w, h, lbl, val, col)
        else:
            pygame.draw.rect(s, CARD2, (12, 104, 876, 68), border_radius=10)
            pygame.draw.rect(s, BORDER2, (12, 104, 876, 68), 1, border_radius=10)
            txt(s, "No leaderboard data yet.  Players need to finish a season first.",
                self.fonts["body"], TEXT_DIM,
                SCREEN_W // 2, 138, center=True)

        # Table header
        HY = 180
        pygame.draw.rect(s, (22, 26, 56), (10, HY, 876, 28), border_radius=6)
        for x, label, col in [
            (18,  "Rank",     GOLD),
            (80,  "Username", ACCENT),
            (240, "Points",   GOLD),
            (370, "Pollution",TEXT_DIM),
            (490, "Day",      TEXT_DIM),
            (580, "Result",   TEXT_DIM),
            (680, "Date",     TEXT_DIM),
        ]:
            txt(s, label, self.fonts["small"], col, x, HY + 6)

        if not lb:
            return

        # Scrollable rows
        ROW_H    = 30
        LIST_TOP = HY + 30
        LIST_H   = FOOTER_Y - LIST_TOP - 10
        visible  = max(1, LIST_H // ROW_H)
        max_scroll = max(0, len(lb) - visible)
        self.l_scroll = max(0, min(self.l_scroll, max_scroll))

        s.set_clip(pygame.Rect(10, LIST_TOP, 876, LIST_H))

        for i, entry in enumerate(
                lb[self.l_scroll: self.l_scroll + visible + 1]):
            ry = LIST_TOP + i * ROW_H
            if ry + ROW_H > LIST_TOP + LIST_H + 4:
                break

            # Row bg — gold tint for top 3
            row_bg = (
                (45, 36, 5) if i + self.l_scroll == 0 else
                (28, 28, 45) if i % 2 == 0 else
                (18, 20, 38)
            )
            pygame.draw.rect(s, row_bg,
                             (10, ry, 876, ROW_H - 1), border_radius=4)

            rank    = self.l_scroll + i + 1
            rank_col = GOLD if rank == 1 else (ACCENT if rank == 2
                       else (ORANGE if rank == 3 else TEXT_DIM))
            won     = entry.get("won", False)
            won_col = GREEN if won else RED
            won_lbl = "WIN" if won else "LOSS"
            poll_col = GREEN if entry.get("pollution", 100) < 50 else RED

            # Medal for top 3
            medal = {1: "1st", 2: "2nd", 3: "3rd"}.get(rank, f"#{rank}")
            txt(s, medal, self.fonts["small"], rank_col, 18, ry + 7)
            txt(s, entry.get("username", ""),
                self.fonts["body"], TEXT, 80, ry + 7, mw=150)
            txt(s, str(entry.get("points", 0)),
                self.fonts["body"], GOLD, 240, ry + 7)
            txt(s, f"{entry.get('pollution', 0)}%",
                self.fonts["small"], poll_col, 370, ry + 7)
            txt(s, f"Day {entry.get('day', 0)}",
                self.fonts["small"], TEXT, 490, ry + 7)

            # Result pill
            pill = pygame.Rect(580, ry + 5, 72, 20)
            pygame.draw.rect(s, GREEN_D if won else RED_D,
                             pill, border_radius=5)
            pygame.draw.rect(s, won_col, pill, 1, border_radius=5)
            txt(s, won_lbl, self.fonts["small"],
                won_col, pill.centerx, pill.centery, center=True)

        s.set_clip(None)

        txt(s, f"Total:  {len(lb)}  entries",
            self.fonts["small"], TEXT_DIM, 18, FOOTER_Y)
        if len(lb) > visible:
            txt(s,
                f"Scroll  {self.l_scroll + 1}-"
                f"{min(self.l_scroll + visible, len(lb))}"
                f" / {len(lb)}",
                self.fonts["small"], TEXT_DIM, SCREEN_W - 190, FOOTER_Y)

    # ── Main draw ─────────────────────────────────────

    def draw(self):
        s     = self.screen
        mouse = pygame.mouse.get_pos()
        s.fill(BG)

        # Top bar
        pygame.draw.rect(s, PANEL, (0, 0, SCREEN_W, TOP_H))
        pygame.draw.rect(s, (22, 32, 66), (0, 0, SCREEN_W, 20))
        pygame.draw.line(s, BORDER2, (0, TOP_H), (SCREEN_W, TOP_H), 1)

        txt(s, "Admin Panel",
            self.fonts["body"], ORANGE, SCREEN_W // 2, 16, center=True)
        txt(s,
            f"{self.state['user']['username']}  "
            f"[{self.state['user']['role']}]",
            self.fonts["small"], TEXT_DIM, 14, 20)


        # Logout button
        btn(s, self.fonts["small"], "Logout",
            self.btn_logout, self.btn_logout.collidepoint(mouse),
            bg=RED_D, hbg=RED, border=RED, fg=RED)

        # Main tabs
        for i, (r, lbl) in enumerate(zip(self.tab_rects, self.tab_labels)):
            act = (self.tab == ["users", "leaderboard"][i])
            col = self.tab_colours[i]
            bg  = (col[0] // 5, col[1] // 5, col[2] // 5) if act else (13, 15, 34)
            pygame.draw.rect(s, bg, r, border_radius=8)
            pygame.draw.rect(s, col if act else BORDER2, r, 1, border_radius=8)
            if act:
                pygame.draw.rect(s, col,
                                 (r.x + 6, r.bottom - 2, r.w - 12, 3))
            txt(s, lbl, self.fonts["body"],
                WHITE if act else TEXT_DIM,
                r.centerx, r.centery, center=True)

        # Clear leaderboard button
        btn(s, self.fonts["small"], "Clear Leaderboard",
            self.btn_clr_lb, self.btn_clr_lb.collidepoint(mouse),
            bg=RED_D, hbg=(130, 30, 30), border=RED, fg=RED)

        # Divider
        pygame.draw.line(s, BORDER2, (10, DIV_Y), (SCREEN_W - 10, DIV_Y), 1)

        # Content
        if self.tab == "users":
            self._draw_users(s, mouse)
        else:
            self._draw_leaderboard(s, mouse)

        # Toast
        if self.toast_msg and pygame.time.get_ticks() < self.toast_time:
            bg_c = RED_D  if self.toast_err else GREEN_D
            bd_c = RED    if self.toast_err else GREEN
            ts   = self.fonts["body"].render(self.toast_msg, True, WHITE)
            tw   = ts.get_width()
            tx   = SCREEN_W // 2 - tw // 2 - 22
            pygame.draw.rect(s, bg_c, (tx, 548, tw + 44, 36), border_radius=9)
            pygame.draw.rect(s, bd_c, (tx, 548, tw + 44, 36), 1, border_radius=9)
            s.blit(ts, (tx + 22, 556))

    # ── Events ────────────────────────────────────────

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            if   self.tab == "users":
                self.u_scroll = max(0, self.u_scroll - event.y)
            elif self.tab == "leaderboard":
                self.l_scroll = max(0, self.l_scroll - event.y)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if   self.tab == "users":       self.u_scroll = max(0, self.u_scroll - 1)
                elif self.tab == "leaderboard": self.l_scroll = max(0, self.l_scroll - 1)
            elif event.key == pygame.K_DOWN:
                if   self.tab == "users":       self.u_scroll += 1
                elif self.tab == "leaderboard": self.l_scroll += 1

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            # Back and Logout
            if self.btn_logout.collidepoint(pos):  return "logout"

            # Tab switching
            if self.tab_rects[0].collidepoint(pos): self.tab = "users"
            if self.tab_rects[1].collidepoint(pos): self.tab = "leaderboard"

            # Clear leaderboard
            if self.btn_clr_lb.collidepoint(pos):
                self._reset_leaderboard()

            # User action buttons
            for item in self.action_rects:
                action = item[0]
                uname  = item[1]
                r      = item[2]
                if r.collidepoint(pos):
                    if   action == "ban":   self._ban_user(uname)
                    elif action == "role":  self._change_role(uname, item[3])
                    elif action == "reset": self._reset_user_stats(uname)

        return None
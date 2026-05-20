"""player/game_screen.py — Animated city + HUD + navigation (122 FPS)"""
import tkinter as tk
import random, math
from core.theme import *
from core.game_data import GameData, ACHIEVEMENTS
import core.sounds as SND

_FRAME_MS = 8   # ~122 FPS


class GameScreen(tk.Frame):
    def __init__(self, master, nav, gd: GameData):
        super().__init__(master, bg=BG)
        self.nav = nav
        self.gd  = gd
        self.pack(fill="both", expand=True)
        self._toast_queue   = []
        self._toast_visible = False
        self._anim_step     = 0
        self._clouds        = []
        self._rain          = []
        self._windows       = []
        self._running       = True
        self._build()
        self._animate()
        self._check_day_end()
        self._check_toasts()

    # ── Build ──────────────────────────────────────────────────────────────────

    def _build(self):
        self._canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        self._canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._draw_city()
        self._init_clouds()
        self._init_rain()

        self._hud = tk.Frame(self, bg=PANEL2, pady=4)
        self._hud.place(relx=0, rely=0, relwidth=1)
        self._hud.lift()
        self._build_hud()

        # FIXED: was "#00000000" (invalid RGBA) — now valid 6-char hex
        self._navrow = tk.Frame(self, bg="#0a1030")
        self._navrow.place(relx=0, y=56, relwidth=1)
        self._navrow.lift()
        self._build_navrow()

        self._toast_frame = tk.Label(
            self, text="", font=F_SUB,
            fg=WHITE, bg=GREEN, padx=18, pady=8, relief="flat")
        self._toast_frame.lift()

    # ── HUD ────────────────────────────────────────────────────────────────────

    def _build_hud(self):
        hud = self._hud
        gd  = self.gd

        tk.Label(hud, text="EcoCity Mayor",
                 font=F_SUB, fg=GREEN, bg=PANEL2).pack(side="left", padx=10)

        centre = tk.Frame(hud, bg=PANEL2)
        centre.pack(side="left", expand=True)

        poll_color = RED if gd.pollution > 50 else ORANGE if gd.pollution > 30 else GREEN
        self._poll_lbl = tk.Label(
            centre, text=f"Pollution: {gd.pollution:.1f}%",
            font=F_BODY, fg=poll_color, bg=PANEL2)
        self._poll_lbl.pack()

        self._poll_bar_canvas = tk.Canvas(
            centre, bg=PANEL2, height=10, highlightthickness=0, width=200)
        self._poll_bar_canvas.pack()
        self._draw_poll_bar()

        tk.Label(centre, text=f"Goal: <{gd.goal_pollution:.0f}%",
                 font=F_SMALL, fg=DIM, bg=PANEL2).pack()

        right1 = tk.Frame(hud, bg=PANEL2)
        right1.pack(side="left", padx=12)
        self._pts_lbl = tk.Label(
            right1, text=f"Points: {gd.points}",
            font=F_BODY, fg=YELLOW, bg=PANEL2)
        self._pts_lbl.pack(anchor="e")
        self._day_lbl = tk.Label(
            right1, text=f"Day {gd.day} / {gd.season_duration}",
            font=F_BODY, fg=ORANGE, bg=PANEL2)
        self._day_lbl.pack(anchor="e")

        right2 = tk.Frame(hud, bg=PANEL2)
        right2.pack(side="left", padx=6)
        self._lvl_lbl = tk.Label(
            right2, text=f"Lv{gd.level} {gd.level_title}",
            font=F_SMALL, fg=PURPLE, bg=PANEL2)
        self._lvl_lbl.pack(anchor="e")
        self._xp_lbl = tk.Label(
            right2, text=f"XP {gd.xp}/{gd.xp_for_next}",
            font=F_SMALL, fg=PURPLE, bg=PANEL2)
        self._xp_lbl.pack(anchor="e")
        tk.Label(right2,
                 text=f"{gd.display_name} [{gd.difficulty.capitalize()}]",
                 font=F_SMALL, fg=DIM, bg=PANEL2).pack(anchor="e")

        button(hud, "Logout", fg=WHITE, bg=RED,
               cmd=self._logout, padx=10, pady=4).pack(side="right", padx=8)

    def _draw_poll_bar(self):
        c = self._poll_bar_canvas
        c.delete("all")
        pct = max(0, min(100, self.gd.pollution)) / 100
        col = RED if pct > .5 else ORANGE if pct > .3 else GREEN
        c.create_rectangle(0, 0, 200, 10, fill=PANEL, outline="")
        c.create_rectangle(0, 0, int(200 * pct), 10, fill=col, outline="")
        goal_x = int(200 * self.gd.goal_pollution / 100)
        c.create_line(goal_x, 0, goal_x, 10, fill=YELLOW, width=2)

    def _build_navrow(self):
        bg_f = tk.Frame(self._navrow, bg="#0a1030", pady=6)
        bg_f.pack(fill="x")
        for lbl, cmd, col in [
            ("Quiz",         self._go_quiz,           BLUE),
            ("Upgrade Shop", self._go_shop,           GREEN),
            ("Achievements", self._open_achievements, YELLOW),
            ("Profile",      self._go_profile,        PURPLE),
            ("Settings",     self._go_settings,       DIM),
        ]:
            button(bg_f, lbl, fg=col, bg="#0d1535",
                   cmd=cmd, padx=14, pady=5).pack(side="left", padx=5)

    # ── City drawing ───────────────────────────────────────────────────────────

    def _draw_city(self):
        c = self._canvas
        W, H = 1140, 720
        gy = int(H * 0.72)

        p     = self.gd.pollution / 100
        r_sky = int(8  + p * 30)
        g_sky = int(12 + p * 8)
        b_sky = int(32 - p * 20)

        for i in range(25):
            y  = i * (H * .65 / 25)
            rr = min(255, int(r_sky + i))
            gg = min(255, int(g_sky + i * .3))
            bb = min(255, int(b_sky + i * .5))
            c.create_rectangle(0, y, W, y + H * .65 / 25 + 1,
                               fill=f"#{rr:02x}{gg:02x}{bb:02x}", outline="")

        if p < 0.8:
            for _ in range(70):
                x, y = random.randint(0, W), random.randint(0, int(H * .55))
                r2   = random.choice([1, 1, 2])
                a    = int(255 * (1 - p))
                c.create_oval(x - r2, y - r2, x + r2, y + r2,
                              fill=f"#{a:02x}{a:02x}{a:02x}", outline="")

        c.create_oval(60, 35, 115, 90, fill="#b8c4d8", outline="")
        c.create_oval(78, 28, 133, 83,
                      fill=f"#{r_sky:02x}{g_sky:02x}{b_sky:02x}", outline="")

        c.create_rectangle(0, gy, W, H, fill="#0a150a", outline="")

        ry = int(H * .83)
        c.create_rectangle(0, ry, W, H, fill="#14142a", outline="")
        for x in range(0, W, 80):
            c.create_rectangle(x, ry + 18, x + 44, ry + 26,
                               fill="#888800", outline="")

        builds = [
            (10,  .42, 80, "#16203a"), (110, .33, 70, "#101c34"),
            (200, .50, 90, "#1a2650"), (310, .28, 65, "#141e38"),
            (395, .46, 85, "#18244a"), (500, .36, 75, "#1c2a54"),
            (595, .30, 68, "#16203a"), (683, .48, 88, "#101c34"),
            (790, .32, 70, "#1a2650"), (880, .44, 80, "#141e38"),
            (980, .26, 60, "#18244a"), (1060, .38, 70, "#1c2a54"),
        ]
        self._windows = []
        for bx, hf, bw, col in builds:
            by = int(gy - H * hf)
            c.create_rectangle(bx, by, bx + bw, gy,
                               fill=col, outline="#0a1030", width=1)
            mx = bx + bw // 2
            c.create_line(mx, by, mx, by - 18, fill="#223355", width=2)
            c.create_oval(mx - 3, by - 22, mx + 3, by - 16,
                          fill=RED, outline="")
            for wy2 in range(by + 8, gy - 8, 20):
                for wx2 in range(bx + 6, bx + bw - 6, 16):
                    lit = random.random() > .25
                    wc  = "#ffcc44" if lit else "#1a2255"
                    win = c.create_rectangle(wx2, wy2, wx2 + 9, wy2 + 12,
                                             fill=wc, outline="")
                    self._windows.append((win, lit))

        num_trees = max(2, int(10 * (1 - p)))
        for tx in [48, 148, 295, 450, 570, 660, 770, 880, 990, 1090][:num_trees]:
            ty = gy - 8
            c.create_rectangle(tx - 3, ty - 28, tx + 3, ty,
                               fill="#2d1a0a", outline="")
            gc = "#1e4a1a" if p < .5 else "#2a3a1a"
            c.create_oval(tx - 20, ty - 60, tx + 20, ty - 28,
                          fill=gc, outline="")
            c.create_oval(tx - 14, ty - 72, tx + 14, ty - 42,
                          fill="#265e22" if p < .5 else "#334422", outline="")

        for lx in [82, 232, 388, 538, 686, 840, 996]:
            ly = gy - 4
            c.create_line(lx, ly, lx, ly - 52, fill="#9999bb", width=3)
            c.create_line(lx, ly - 52, lx + 16, ly - 52,
                          fill="#9999bb", width=2)
            c.create_oval(lx + 10, ly - 58, lx + 26, ly - 46,
                          fill="#ffe88a", outline="")

    def _init_clouds(self):
        for _ in range(6):
            self._spawn_cloud(random.randint(0, 1140),
                              random.randint(30, 150),
                              random.uniform(.7, 1.4))

    def _spawn_cloud(self, x, y, s):
        c    = self._canvas
        p    = self.gd.pollution / 100
        gc   = int(42 + p * 30)
        fill = f"#{gc:02x}{gc:02x}{int(gc * .9):02x}"
        parts = []
        for ox, oy, r in [(-32, 0, 26), (0, -16, 31), (32, 0, 26), (0, 12, 21)]:
            part = c.create_oval(
                x + ox * s - r * s, y + oy * s - r * s,
                x + ox * s + r * s, y + oy * s + r * s,
                fill=fill, outline="")
            parts.append(part)
        self._clouds.append(parts)

    def _init_rain(self):
        c = self._canvas
        p = self.gd.pollution / 100
        for _ in range(int(60 + p * 120)):
            x    = random.randint(0, 1140)
            y    = random.randint(-720, 720)
            rain = c.create_line(
                x, y, x + 3, y + 12,
                fill=f"#3a{int(50+p*50):02x}{int(80+p*60):02x}",
                width=1)
            self._rain.append(rain)

    # ── Animation at 122 FPS ───────────────────────────────────────────────────

    def _animate(self):
        if not self._running or not self.winfo_exists():
            return
        self._anim_step += 1
        c = self._canvas

        for parts in self._clouds:
            for p in parts:
                c.move(p, -0.3, 0)
            if c.coords(parts[0]) and c.coords(parts[0])[2] < 0:
                for p in parts:
                    c.move(p, 1340, 0)

        speed = 2.5 + self.gd.pollution / 100 * 3
        for rain in self._rain:
            c.move(rain, 0.8, speed)
            coords = c.coords(rain)
            if coords and coords[1] > 720:
                x = random.randint(0, 1140)
                c.coords(rain, x, -10, x + 3, 2)

        if self._anim_step % 240 == 0 and self._windows:
            for _ in range(3):
                win, lit = random.choice(self._windows)
                try:
                    c.itemconfig(win, fill="#ffcc44" if not lit else "#1a2255")
                except Exception:
                    pass

        self.after(_FRAME_MS, self._animate)

    # ── HUD refresh ────────────────────────────────────────────────────────────

    def refresh_hud(self):
        gd  = self.gd
        p   = gd.pollution
        col = RED if p > 50 else ORANGE if p > 30 else GREEN
        self._poll_lbl.configure(text=f"Pollution: {p:.1f}%", fg=col)
        self._draw_poll_bar()
        self._pts_lbl.configure(text=f"Points: {gd.points}")
        self._day_lbl.configure(text=f"Day {gd.day} / {gd.season_duration}")
        self._lvl_lbl.configure(text=f"Lv{gd.level} {gd.level_title}")
        self._xp_lbl.configure(text=f"XP {gd.xp}/{gd.xp_for_next}")

    # ── Season-end check ───────────────────────────────────────────────────────
    #
    #  THE DEFINITIVE FIX — only two valid end conditions:
    #
    #  WIN  → pollution < goal  (player successfully cleaned the city)
    #  LOSE → day > season_duration (real calendar days ran out)
    #
    #  NEVER check "pollution >= 100" — that is the STARTING value.
    #  NEVER check "pollution >= 100" — that is the STARTING value.
    #  NEVER check "pollution >= 100" — that is the STARTING value.
    #
    #  game_data.py now stores day WITHOUT a cap, so day CAN exceed
    #  season_duration, making the lose condition reachable.

    def _check_day_end(self):
        gd = self.gd

        # ── WIN: player genuinely cleaned the city ─────────────────────────
        won  = gd.pollution < gd.goal_pollution

        # ── LOSE: real-world calendar days ran out ─────────────────────────
        # day is NOT capped in game_data.py anymore, so this CAN be True.
        lost = gd.day > gd.season_duration

        if won or lost:
            self.after(500, self._trigger_season_end)

    def _trigger_season_end(self):
        self._running = False
        self.gd.save()
        self.nav.go_season_end()

    # ── Achievement toasts ─────────────────────────────────────────────────────

    def _check_toasts(self):
        if not self.winfo_exists():
            return
        self._toast_queue.extend(self.gd.pop_new_achievements())
        if not self._toast_visible and self._toast_queue:
            self._show_toast(self._toast_queue.pop(0))
        self.after(2000, self._check_toasts)

    def _show_toast(self, name):
        self._toast_visible = True
        self._toast_frame.configure(text=f"  Achievement: {name}!")
        self._toast_frame.place(relx=.5, rely=.18, anchor="center")
        self._toast_frame.lift()
        SND.play("achieve")
        self.after(2800, self._hide_toast)

    def _hide_toast(self):
        self._toast_frame.place_forget()
        self._toast_visible = False

    def _open_achievements(self):
        AchievementsPopup(self.master, self.gd)

    # ── Navigation ─────────────────────────────────────────────────────────────

    def _go_quiz(self):
        self._running = False
        self.gd.save()
        self.nav.go_quiz()

    def _go_shop(self):
        self._running = False
        self.gd.save()
        self.nav.go_shop()

    def _go_profile(self):
        self._running = False
        self.gd.save()
        self.nav.go_profile()

    def _go_settings(self):
        self._running = False
        self.gd.save()
        self.nav.go_settings()

    def _logout(self):
        self._running = False
        self.gd.save()
        import core.database as DB
        DB.log(self.gd.username, "LOGOUT")
        self.nav.logout()


# ── Achievements popup ─────────────────────────────────────────────────────────

class AchievementsPopup(tk.Toplevel):
    def __init__(self, master, gd: GameData):
        super().__init__(master)
        self.title("Achievements")
        self.configure(bg=BG)
        self.grab_set()
        self.resizable(False, False)
        self._build(gd)
        self._center()

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(
            f"+{(self.winfo_screenwidth()  - w) // 2}"
            f"+{(self.winfo_screenheight() - h) // 2}")

    def _build(self, gd):
        total = len(ACHIEVEMENTS)
        done  = sum(1 for a in ACHIEVEMENTS if a["id"] in gd.achievements)
        tk.Label(self, text="  Achievements",
                 font=F_TITLE, fg=YELLOW, bg=BG).pack(pady=(12, 2))
        tk.Label(self, text=f"{done} / {total} unlocked",
                 font=F_BODY, fg=DIM, bg=BG).pack(pady=(0, 8))

        canvas = tk.Canvas(self, bg=BG, highlightthickness=0,
                           height=420, width=680)
        sb     = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        frame  = tk.Frame(canvas, bg=BG)
        frame.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y", padx=(0, 8))
        canvas.pack(padx=10, fill="both")

        for i, a in enumerate(ACHIEVEMENTS):
            unlocked   = a["id"] in gd.achievements
            fg_c       = GREEN if unlocked else DIM
            bg_c       = "#0a1e0a" if unlocked else PANEL
            border     = GREEN if unlocked else PANEL2
            cell_outer = tk.Frame(frame, bg=border, padx=2, pady=2)
            cell_outer.grid(row=i // 2, column=i % 2,
                            padx=4, pady=3, sticky="nsew")
            cell = tk.Frame(cell_outer, bg=bg_c, padx=10, pady=6, width=290)
            cell.pack(fill="both")
            icon     = "+" if unlocked else "-"
            name_row = tk.Frame(cell, bg=bg_c)
            name_row.pack(fill="x")
            tk.Label(name_row, text=f"{icon}  {a['name']}",
                     font=F_BODY, fg=fg_c, bg=bg_c).pack(side="left")
            if unlocked:
                tk.Label(name_row, text="DONE",
                         font=F_SMALL, fg=GREEN, bg=bg_c).pack(side="right")
            tk.Label(cell, text=a["desc"],
                     font=F_SMALL, fg=DIM, bg=bg_c,
                     wraplength=250, anchor="w").pack(anchor="w")

        button(self, "Close", fg=TEXT, bg=PANEL2,
               cmd=self.destroy, padx=20, pady=8).pack(pady=10)
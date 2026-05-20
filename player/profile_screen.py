"""player/profile_screen.py — Stats, Achievements, History, Challenges"""
import tkinter as tk
from core.theme import *
from core.game_data import GameData, ACHIEVEMENTS
import core.database as DB


class ProfileScreen(tk.Frame):
    def __init__(self, master, nav, gd: GameData):
        super().__init__(master, bg=BG)
        self.nav = nav; self.gd = gd
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=PANEL2, pady=6); top.pack(fill="x")
        button(top, "Back", fg=BLUE, bg=PANEL2, cmd=self._back,
               padx=10, pady=4).pack(side="left", padx=8)
        tk.Label(top, text="My Profile", font=F_TITLE,
                 fg=BLUE, bg=PANEL2).pack(side="left", expand=True)
        bar = tk.Frame(self, bg=BG, pady=4); bar.pack(fill="x", padx=10)
        self._tab_btns = {}
        for lbl, key, col in [
            ("Stats","stats",BLUE),("Achievements","ach",YELLOW),
            ("History","hist",ORANGE),("Challenges","chal",PURPLE),
        ]:
            b = button(bar, lbl, fg=col, bg=PANEL2,
                       cmd=lambda k=key: self._show(k), padx=12, pady=5)
            b.pack(side="left", padx=4)
            self._tab_btns[key] = b
        self._content = tk.Frame(self, bg=BG)
        self._content.pack(fill="both", expand=True, padx=10, pady=4)
        self._show("stats")

    def _show(self, key):
        for k, b in self._tab_btns.items():
            b.configure(bg=PANEL if k == key else PANEL2)
        for w in self._content.winfo_children(): w.destroy()
        {"stats": self._tab_stats, "ach": self._tab_achievements,
         "hist": self._tab_history, "chal": self._tab_challenges}[key]()

    def _tab_stats(self):
        p = self._content; gd = self.gd
        header = tk.Frame(p, bg=BG, pady=10); header.pack(fill="x")
        av = tk.Canvas(header, width=80, height=80, bg=BG, highlightthickness=0)
        av.pack(side="left", padx=16)
        av.create_oval(2, 2, 78, 78, fill=BLUE, outline=PANEL2, width=3)
        av.create_text(40, 40, text=gd.display_name[0].upper(),
                       font=("Courier New",30,"bold"), fill=WHITE)
        info = tk.Frame(header, bg=BG); info.pack(side="left")
        tk.Label(info, text=gd.display_name,
                 font=F_TITLE, fg=WHITE, bg=BG).pack(anchor="w")
        tk.Label(info, text=f"Role: {gd.role.capitalize()}",
                 font=F_BODY, fg=DIM, bg=BG).pack(anchor="w")
        tk.Label(info, text=f"Lv{gd.level}  {gd.level_title}",
                 font=F_BODY, fg=PURPLE, bg=BG).pack(anchor="w")
        xp_bar = tk.Canvas(info, bg=PANEL2, height=14, highlightthickness=0, width=280)
        xp_bar.pack(anchor="w", pady=(4,0))
        xp_bar.update_idletasks()
        max_xp = gd.xp_for_next
        pct    = min(gd.xp / max_xp, 1.0) if max_xp > 0 else 1.0
        xp_bar.create_rectangle(0, 0, int(280*pct), 14, fill=PURPLE, outline="")
        tk.Label(info, text=f"XP: {gd.xp}/{max_xp}",
                 font=F_SMALL, fg=PURPLE, bg=BG).pack(anchor="w")
        r1 = tk.Frame(p, bg=BG); r1.pack(fill="x", pady=6)
        stat_card(r1, gd.seasons_played, "Seasons Played", YELLOW)
        stat_card(r1, gd.best_score,     "Best Score",     ORANGE)
        stat_card(r1, gd.points,         "Points",         BLUE)
        r2 = tk.Frame(p, bg=BG); r2.pack(fill="x", pady=6)
        done = sum(1 for a in ACHIEVEMENTS if a["id"] in gd.achievements)
        stat_card(r2, gd.total_correct,            "Correct Answers", GREEN)
        stat_card(r2, f"{done}/{len(ACHIEVEMENTS)}","Achievements",    PURPLE)
        stat_card(r2, gd.seasons_won,              "Seasons Won",     ORANGE)
        outer, inner = card(p, BLUE, pady=10, padx=10)
        outer.pack(fill="x", pady=10)
        tk.Label(inner, text="Pollution History",
                 font=F_SUB, fg=BLUE, bg=PANEL).pack(anchor="w")
        h = gd.pollution_history
        if len(h) >= 2:
            graph = tk.Canvas(inner, bg=PANEL2, height=100, highlightthickness=0)
            graph.pack(fill="x", pady=6)
            graph.update_idletasks()
            W = graph.winfo_width() or 700; H = 100
            goal_y = int(H * (1 - gd.goal_pollution / 100))
            graph.create_line(0, goal_y, W, goal_y, fill=YELLOW, dash=(4,2))
            pts = []
            for i, val in enumerate(h):
                x = int(i / (len(h)-1) * W); y = int(H * (1 - val/100))
                pts.extend([x, y])
            if len(pts) >= 4:
                graph.create_line(*pts, fill=RED, width=2)

    def _tab_achievements(self):
        p = self._content; gd = self.gd
        done = sum(1 for a in ACHIEVEMENTS if a["id"] in gd.achievements)
        tk.Label(p, text=f"{done} / {len(ACHIEVEMENTS)} unlocked",
                 font=F_BODY, fg=DIM, bg=BG).pack(anchor="w", pady=4)
        _, frame = scrollable(p)
        for i, a in enumerate(ACHIEVEMENTS):
            unlocked = a["id"] in gd.achievements
            row_bg   = "#0a1e0a" if unlocked else PANEL
            bord     = GREEN if unlocked else PANEL2
            outer    = tk.Frame(frame, bg=bord, padx=2, pady=2)
            outer.pack(fill="x", pady=2)
            inner    = tk.Frame(outer, bg=row_bg, padx=10, pady=6)
            inner.pack(fill="both")
            icon = "■" if unlocked else "□"
            r    = tk.Frame(inner, bg=row_bg); r.pack(fill="x")
            fg   = GREEN if unlocked else DIM
            tk.Label(r, text=f"{icon}  {a['name']}",
                     font=F_BODY, fg=fg, bg=row_bg).pack(side="left")
            if unlocked:
                tk.Label(r, text="DONE", font=F_SMALL, fg=GREEN, bg=row_bg).pack(side="right")
            tk.Label(inner, text=a["desc"], font=F_SMALL,
                     fg=DIM, bg=row_bg, anchor="w").pack(anchor="w")

    def _tab_history(self):
        p  = self._content
        lb = [e for e in DB.get_leaderboard() if e.get("username") == self.gd.username]
        if not lb:
            tk.Label(p, text="No season history yet.",
                     font=F_BODY, fg=PURPLE, bg=BG).pack(pady=30); return
        col_header(p, [("#",5),("Points",10),("Pollution",12),
                       ("Day",8),("Result",10),("Date",20)])
        _, frame = scrollable(p)
        for i, e in enumerate(reversed(lb)):
            row_bg = PANEL if i%2==0 else PANEL2
            r = tk.Frame(frame, bg=row_bg, pady=2); r.pack(fill="x")
            res = e.get("result","?"); rc = GREEN if res=="Win" else RED
            for val, w, fg_c in [
                (str(i+1),5,DIM),(str(e.get("points",0)),10,YELLOW),
                (f"{e.get('pollution','?')}%",12,rc),(str(e.get("day","?")),8,TEXT),
                (res,10,rc),(e.get("date",""),20,DIM),
            ]:
                tk.Label(r, text=val, font=F_SMALL, fg=fg_c,
                         bg=row_bg, width=w, anchor="w").pack(side="left", padx=4)

    def _tab_challenges(self):
        p = self._content; gd = self.gd
        tk.Label(p, text="Active Challenges", font=F_SUB,
                 fg=PURPLE, bg=BG).pack(anchor="w", pady=6)
        challenges = [
            ("Reduce Pollution by 10%", f"Current: {gd.pollution:.1f}%  →  target: {gd.pollution-10:.1f}%", ORANGE),
            ("Earn 100 more points",    f"Current: {gd.points}  →  target: {gd.points+100}", YELLOW),
            ("Answer 5 quiz questions", f"Correct this session: {gd.session_correct}",        BLUE),
            ("Survive to Day 15",       f"Current day: {gd.day}",                             GREEN),
            ("Buy 1 upgrade",           f"Bought this season: {len(gd.upgrades_bought)}",     PURPLE),
        ]
        for name, progress, col in challenges:
            outer, inner = card(p, col, pady=8, padx=12); outer.pack(fill="x", pady=4)
            tk.Label(inner, text=name,     font=F_BODY,  fg=col, bg=PANEL).pack(anchor="w")
            tk.Label(inner, text=progress, font=F_SMALL, fg=DIM, bg=PANEL).pack(anchor="w")

    def _back(self): self.gd.save(); self.nav.go_game()
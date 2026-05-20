"""player/season_end_screen.py — Win/lose screen with starfield and leaderboard"""
import tkinter as tk
import random, math
from core.theme import *
from core.game_data import GameData
import core.database as DB
import core.sounds as SND


class SeasonEndScreen(tk.Frame):
    def __init__(self, master, nav, gd: GameData):
        super().__init__(master, bg=BG)
        self.nav   = nav; self.gd = gd
        self.pack(fill="both", expand=True)
        self._result = gd.end_season()
        self._won    = self._result["won"]
        self._step   = 0; self._stars = []
        self._build_bg()
        self._build_ui()
        self._tick()
        SND.play("win" if self._won else "lose")

    def _build_bg(self):
        self._canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        self._canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        for _ in range(100):
            x = random.randint(0, 1140); y = random.randint(0, 720)
            r = random.choice([1,1,2])
            s = self._canvas.create_oval(x-r, y-r, x+r, y+r, fill="white", outline="")
            self._stars.append(s)

    def _tick(self):
        if not self.winfo_exists(): return
        self._step += 1
        c = self._canvas
        for i, s in enumerate(self._stars):
            alpha = int(abs(math.sin(self._step*0.04 + i*0.4)) * 200 + 55)
            alpha = min(255, alpha)
            col   = f"#{alpha:02x}{alpha:02x}{alpha:02x}"
            try: c.itemconfig(s, fill=col)
            except Exception: return
        self.after(60, self._tick)

    def _build_ui(self):
        res   = self._result; won = self._won; color = GREEN if won else RED
        outer = tk.Frame(self, bg=color, padx=3, pady=3)
        outer.place(relx=0.5, rely=0.5, anchor="center")
        inner = tk.Frame(outer, bg=PANEL, padx=48, pady=32); inner.pack()

        headline = "🌿  SEASON WON!" if won else "💨  SEASON LOST"
        sub      = ("You saved the city from pollution!"
                    if won else "Pollution stayed too high. Try again!")
        tk.Label(inner, text=headline, font=("Courier New",30,"bold"),
                 fg=color, bg=PANEL).pack(pady=(0,4))
        tk.Label(inner, text=sub, font=F_SUB, fg=TEXT, bg=PANEL).pack(pady=(0,18))
        tk.Frame(inner, bg=color, height=2).pack(fill="x", pady=(0,18))

        stats_f = tk.Frame(inner, bg=PANEL); stats_f.pack()
        for col_i, (lbl, val, c) in enumerate([
            ("Final Pollution", f"{res['pollution']}%", GREEN if won else RED),
            ("Goal",            f"< {self.gd.goal_pollution:.0f}%", YELLOW),
            ("Points Earned",   str(res["points"]),                  BLUE),
            ("Days Survived",   f"{res['day']} / {self.gd.season_duration}", ORANGE),
        ]):
            cell = tk.Frame(stats_f, bg=PANEL2, padx=20, pady=10)
            cell.grid(row=0, column=col_i, padx=8)
            tk.Label(cell, text=val, font=("Courier New",20,"bold"), fg=c, bg=PANEL2).pack()
            tk.Label(cell, text=lbl, font=F_SMALL, fg=TEXT, bg=PANEL2).pack()

        if won:
            bonus = tk.Frame(inner, bg="#003a10", padx=12, pady=6); bonus.pack(pady=(14,0))
            tk.Label(bonus, text=f"🎁  Season Win Bonus: +{self.gd.bonus_win} pts!",
                     font=F_BODY, fg=GREEN, bg="#003a10").pack()

        tk.Frame(inner, bg=PANEL2, height=1).pack(fill="x", pady=14)
        tk.Label(inner, text="Final Pollution Level:",
                 font=F_BODY, fg=TEXT, bg=PANEL, anchor="w").pack(fill="x")
        bar = tk.Canvas(inner, bg=PANEL2, height=22, highlightthickness=0, width=500)
        bar.pack(fill="x"); bar.update_idletasks()
        pct = min(res["pollution"] / 100, 1.0)
        bar.create_rectangle(0, 0, int(500*pct), 22,
                              fill=RED if res["pollution"] > 50 else GREEN, outline="")
        goal_x = int(500 * self.gd.goal_pollution / 100)
        bar.create_line(goal_x, 0, goal_x, 22, fill=YELLOW, width=2)
        bar.create_text(goal_x+4, 4, text=f"Goal {self.gd.goal_pollution:.0f}%",
                        fill=YELLOW, anchor="nw", font=("Courier New",8))

        lb       = DB.get_leaderboard()
        sorted_lb = sorted(lb, key=lambda x: x.get("points",0), reverse=True)
        my_rank  = next((i+1 for i,e in enumerate(sorted_lb)
                         if e.get("username")==res["username"]
                         and e.get("points")==res["points"]), "?")
        tk.Label(inner, text=f"🏆  Leaderboard Rank:  #{my_rank}",
                 font=F_SUB, fg=YELLOW, bg=PANEL).pack(pady=(12,0))
        tk.Frame(inner, bg=color, height=2).pack(fill="x", pady=14)

        btn_row = tk.Frame(inner, bg=PANEL); btn_row.pack()
        button(btn_row, "🔄  Play New Season",
               fg=GREEN if won else ORANGE,
               bg="#003a10" if won else "#3a2000",
               cmd=self._new_season, padx=20, pady=10).pack(side="left", padx=8)
        button(btn_row, "🏠  Main Menu",
               fg=TEXT, bg=PANEL2,
               cmd=self._main_menu, padx=16, pady=10).pack(side="left", padx=8)
        button(btn_row, "🏆  Leaderboard",
               fg=YELLOW, bg=PANEL2,
               cmd=lambda: LeaderboardPopup(self.master, res["username"]),
               padx=16, pady=10).pack(side="left", padx=8)

    def _new_season(self): self.nav.go_game()
    def _main_menu(self):
        DB.log(self.gd.username,"LOGOUT"); self.nav.logout()


class LeaderboardPopup(tk.Toplevel):
    def __init__(self, master, current_user=""):
        super().__init__(master)
        self.title("Leaderboard"); self.configure(bg=BG)
        self.resizable(False, False); self.grab_set()
        lb = sorted(DB.get_leaderboard(), key=lambda x: x.get("points",0), reverse=True)
        self._build(lb, current_user)
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{(self.winfo_screenwidth()-w)//2}"
                      f"+{(self.winfo_screenheight()-h)//2}")

    def _build(self, lb, me):
        tk.Label(self, text="🏆  All-Time Leaderboard",
                 font=F_TITLE, fg=YELLOW, bg=BG).pack(pady=(12,4))
        col_header(self, [("Rank",6),("Username",16),("Points",10),
                          ("Pollution",12),("Day",8),("Result",10),("Date",18)])
        canvas = tk.Canvas(self, bg=BG, highlightthickness=0, height=320, width=760)
        sb     = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        frame  = tk.Frame(canvas, bg=BG)
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y", padx=(0,8))
        canvas.pack(padx=10, fill="both")
        if not lb:
            tk.Label(frame, text="No records yet.",
                     font=F_BODY, fg=PURPLE, bg=BG).pack(pady=20)
        else:
            for i, e in enumerate(lb):
                is_me  = e.get("username") == me
                row_bg = "#0a200a" if is_me else (PANEL if i%2==0 else PANEL2)
                row    = tk.Frame(frame, bg=row_bg, pady=2); row.pack(fill="x")
                res    = e.get("result","?"); rc = GREEN if res=="Win" else RED
                for val, w, col in [
                    (str(i+1),6,DIM),
                    (e.get("username","?"),16,GREEN if is_me else TEXT),
                    (str(e.get("points",0)),10,YELLOW),
                    (f"{e.get('pollution','?')}%",12,rc),
                    (str(e.get("day","?")),8,TEXT),
                    (res,10,rc),(e.get("date",""),18,DIM),
                ]:
                    tk.Label(row, text=val, font=F_SMALL, fg=col,
                             bg=row_bg, width=w, anchor="w").pack(side="left", padx=4)
        button(self, "Close", fg=TEXT, bg=PANEL2, cmd=self.destroy,
               padx=20, pady=8).pack(pady=10)
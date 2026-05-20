"""admin/leaderboard_panel.py — View all-time leaderboard, clear it"""
import tkinter as tk
from tkinter import messagebox
from core.theme import *
import core.database as DB


class LeaderboardPanel(tk.Frame):
    def __init__(self, parent, admin_user: dict):
        super().__init__(parent, bg=BG)
        self.admin_user = admin_user
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        lb = sorted(DB.get_leaderboard(),
                    key=lambda x: x.get("points", 0), reverse=True)

        toolbar = tk.Frame(self, bg=BG); toolbar.pack(fill="x", pady=(0, 6))
        tk.Label(toolbar, text=f"{len(lb)} season records",
                 font=F_BODY, fg=DIM, bg=BG).pack(side="left")
        button(toolbar, "🗑  Clear Leaderboard", fg=RED, bg="#2a0808",
               cmd=self._clear, padx=10, pady=4).pack(side="right")

        if lb:
            wins = sum(1 for e in lb if e.get("result") == "Win")
            top  = lb[0]
            row  = tk.Frame(self, bg=BG); row.pack(fill="x", pady=(0, 8))
            stat_card(row, wins,                    "Total Wins",  GREEN)
            stat_card(row, len(lb) - wins,          "Losses",      RED)
            stat_card(row, top.get("points", 0),    "Top Score",   GOLD)
            stat_card(row, top.get("username", "?"),"Leader",      YELLOW)

        if not lb:
            tk.Label(self, text="No leaderboard data yet.",
                     font=F_BODY, fg=PURPLE, bg=BG).pack(pady=40)
            return

        col_header(self, [
            ("Rank", 6), ("Username", 16), ("Points", 10),
            ("Pollution", 12), ("Day", 8), ("Result", 10), ("Date", 20),
        ])
        _, frame = scrollable(self)
        for i, e in enumerate(lb):
            row_bg = PANEL if i % 2 == 0 else PANEL2
            r = tk.Frame(frame, bg=row_bg, pady=2); r.pack(fill="x")
            res   = e.get("result", "?")
            r_col = GREEN if res == "Win" else RED
            for val, w, fg_c in [
                (str(i+1), 6, DIM),
                (e.get("username","?"), 16, TEXT),
                (str(e.get("points",0)), 10, YELLOW),
                (f"{e.get('pollution','?')}%", 12, r_col),
                (str(e.get("day","?")), 8, TEXT),
                (res, 10, r_col),
                (e.get("date",""), 20, DIM),
            ]:
                tk.Label(r, text=val, font=F_SMALL, fg=fg_c,
                         bg=row_bg, width=w, anchor="w").pack(side="left", padx=4)

    def _clear(self):
        if messagebox.askyesno("Clear Leaderboard",
                "Permanently delete ALL leaderboard records?"):
            DB.clear_leaderboard()
            DB.log(self.admin_user["username"], "CLEAR_LB")
            messagebox.showinfo("Done", "Leaderboard cleared.")
            for w in self.winfo_children(): w.destroy()
            self._build()
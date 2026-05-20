"""moderator/profile_panel.py — Dashboard: profile card, game health, suggestions"""
import tkinter as tk
from core.theme import *
import core.database as DB


class ProfilePanel(tk.Frame):
    def __init__(self, parent, mod_user: dict, show_tab):
        super().__init__(parent, bg=BG)
        self.mod_user = mod_user
        self.show_tab = show_tab
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        users    = DB.get_users()
        quizzes  = DB.get_quizzes()
        upgrades = DB.get_upgrades()
        players  = [u for u in users if u.get("role") == "player"]
        avg_poll = (sum(u.get("pollution",100) for u in players) / len(players)
                    if players else 100.0)

        outer, inner = card(self, PURPLE, pady=10, padx=14)
        outer.pack(fill="x", pady=(0, 8))
        row = tk.Frame(inner, bg=PANEL); row.pack(fill="x")
        av = tk.Canvas(row, width=64, height=64, bg=PANEL, highlightthickness=0)
        av.pack(side="left", padx=(0, 14))
        av.create_oval(2, 2, 62, 62, fill=PURPLE, outline="")
        av.create_text(32, 32, text=self.mod_user["username"][0].upper(),
                       font=("Courier New",24,"bold"), fill=WHITE)
        info = tk.Frame(row, bg=PANEL); info.pack(side="left")
        tk.Label(info, text=self.mod_user["username"],
                 font=F_TITLE, fg=WHITE, bg=PANEL).pack(anchor="w")
        tk.Label(info, text="Role: Moderator",
                 font=F_BODY, fg=PURPLE, bg=PANEL).pack(anchor="w")
        tk.Label(info,
                 text=f"{len(quizzes)} questions  ·  {len(upgrades)} upgrades  ·  {len(players)} players",
                 font=F_SMALL, fg=DIM, bg=PANEL).pack(anchor="w")

        r2 = tk.Frame(self, bg=BG); r2.pack(fill="x", pady=6)
        stat_card(r2, len(quizzes),     "Questions",    PURPLE)
        stat_card(r2, len(upgrades),    "Upgrades",     ORANGE)
        stat_card(r2, len(players),     "Players",      BLUE)
        stat_card(r2, f"{avg_poll:.1f}%","Avg Pollution",RED if avg_poll>50 else GREEN)

        split = tk.Frame(self, bg=BG); split.pack(fill="x", pady=8)

        outG, inG = card(split, GREEN, pady=10, padx=12)
        outG.pack(side="left", fill="both", expand=True, padx=(0, 4))
        tk.Label(inG, text="Game Health",
                 font=F_SUB, fg=GREEN, bg=PANEL).pack(anchor="w", pady=(0, 8))
        for lbl, val, target, col in [
            ("Question Pool",    len(quizzes),        20, PURPLE),
            ("Upgrade Variety",  len(upgrades),       10, ORANGE),
            ("City Cleanliness", int(100 - avg_poll), 50, GREEN),
        ]:
            r = tk.Frame(inG, bg=PANEL); r.pack(fill="x", pady=3)
            tk.Label(r, text=f"{lbl} (≥{target})", font=F_SMALL,
                     fg=TEXT, bg=PANEL).pack(anchor="w")
            bar = tk.Canvas(r, bg=PANEL2, height=14, width=300, highlightthickness=0)
            bar.pack(anchor="w")
            bar.update_idletasks()
            pct = min(val / target, 1.0) if target else 1.0
            bar.create_rectangle(0, 0, int(300*pct), 14, fill=col, outline="")
            bar.create_text(296, 7, text=f"{val}/{target}", anchor="e",
                            fill=TEXT, font=("Courier New",8))

        outS, inS = card(split, YELLOW, pady=10, padx=12)
        outS.pack(side="left", fill="both", expand=True, padx=(4, 0))
        tk.Label(inS, text="Suggestions",
                 font=F_SUB, fg=YELLOW, bg=PANEL).pack(anchor="w", pady=(0, 8))
        suggestions = []
        if len(quizzes)  < 10: suggestions.append("Add more questions (below 10)")
        if len(upgrades) < 5:  suggestions.append("Add more upgrades (below 5)")
        if avg_poll      > 70: suggestions.append("Players struggling — add cheaper upgrades")
        if not players:        suggestions.append("No players registered yet")
        for s in suggestions:
            tk.Label(inS, text=f"• {s}", font=F_BODY, fg=TEXT,
                     bg=PANEL, anchor="w").pack(fill="x")
        if not suggestions:
            tk.Label(inS, text="✓  Everything looks healthy!",
                     font=F_BODY, fg=GREEN, bg=PANEL).pack(anchor="w")

        qa = tk.Frame(self, bg=BG); qa.pack(fill="x", pady=8)
        tk.Label(qa, text="Quick Actions:", font=F_BODY, fg=DIM, bg=BG).pack(anchor="w")
        btns = tk.Frame(qa, bg=BG); btns.pack(fill="x")
        for lbl, tab, col, bg_c in [
            ("Manage Questions",      "questions", WHITE, PURPLE),
            ("Manage Upgrades",       "upgrades",  WHITE, ORANGE),
            ("Enforcement & Monitor", "enforce",   WHITE, "#3a1050"),
        ]:
            button(btns, lbl, fg=col, bg=bg_c,
                   cmd=lambda t=tab: self.show_tab(t),
                   padx=18, pady=10).pack(side="left", padx=6)
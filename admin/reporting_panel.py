"""admin/reporting_panel.py — Activity Log, System Stats, Season History"""
import tkinter as tk
from tkinter import messagebox
from collections import Counter
from core.theme import *
import core.database as DB


class ReportingPanel(tk.Frame):
    def __init__(self, parent, admin_user: dict):
        super().__init__(parent, bg=BG)
        self.admin_user  = admin_user
        self._search_var = tk.StringVar()
        self.pack(fill="both", expand=True)
        self._build_subtabs()
        self._show_sub("log")

    def _build_subtabs(self):
        bar = tk.Frame(self, bg=BG, pady=4); bar.pack(fill="x")
        self._sub_btns = {}
        for lbl, key, col in [
            ("📋 Activity Log",   "log",     BLUE),
            ("📊 System Stats",   "stats",   GREEN),
            ("🏆 Season History", "seasons", ORANGE),
        ]:
            b = button(bar, lbl, fg=col, bg=PANEL2,
                       cmd=lambda k=key: self._show_sub(k), padx=10, pady=5)
            b.pack(side="left", padx=3)
            self._sub_btns[key] = b
        self._sub_content = tk.Frame(self, bg=BG)
        self._sub_content.pack(fill="both", expand=True)

    def _show_sub(self, key):
        for k, b in self._sub_btns.items():
            b.configure(bg=PANEL if k == key else PANEL2)
        for w in self._sub_content.winfo_children(): w.destroy()
        {"log": self._build_log,
         "stats": self._build_stats,
         "seasons": self._build_seasons}[key]()

    def _build_log(self):
        p    = self._sub_content
        logs = DB.get_logs()
        ctrl = tk.Frame(p, bg=BG); ctrl.pack(fill="x", pady=(0, 4))
        tk.Label(ctrl, text="Search:", font=F_BODY, fg=TEXT, bg=BG).pack(side="left")
        e = tk.Entry(ctrl, textvariable=self._search_var,
                     bg=PANEL2, fg=YELLOW, insertbackground=YELLOW,
                     font=F_BODY, relief="flat", width=22)
        e.pack(side="left", padx=6)
        e.bind("<KeyRelease>", lambda _: self._redraw_log(logs, frame))
        button(ctrl, "🗑 Clear Log", fg=RED, bg="#2a0808",
               cmd=lambda: self._clear_log(logs, frame),
               padx=8, pady=4).pack(side="right")
        tk.Label(ctrl, text=f"Total: {len(logs)}",
                 font=F_SMALL, fg=DIM, bg=BG).pack(side="right", padx=10)
        col_header(p, [("#",4),("Timestamp",18),("Username",14),("Action",14),("Detail",38)])
        _, frame = scrollable(p)
        self._log_frame = frame
        self._redraw_log(logs, frame)

    def _redraw_log(self, logs, frame):
        for w in frame.winfo_children(): w.destroy()
        q = self._search_var.get().lower()
        filtered = [l for l in reversed(logs)
                    if q in l.get("username","").lower()
                    or q in l.get("action","").lower()
                    or q in l.get("detail","").lower()]
        AC = {"LOGIN":GREEN,"LOGOUT":PURPLE,"BAN":RED,"UNBAN":ORANGE,
              "ROLE_CHANGE":BLUE,"QUIZ":YELLOW,"UPGRADE":GREEN,
              "SEASON_END":ORANGE,"REGISTER":BLUE,"RESET":RED}
        for i, l in enumerate(filtered):
            row_bg = PANEL if i % 2 == 0 else PANEL2
            r = tk.Frame(frame, bg=row_bg, pady=2); r.pack(fill="x")
            act = l.get("action","").upper()
            col = AC.get(act, TEXT)
            for val, w, fg_c in [
                (str(i+1), 4, DIM), (l.get("ts",""), 18, DIM),
                (l.get("username",""), 14, TEXT), (act, 14, col),
                (l.get("detail","")[:42], 38, TEXT),
            ]:
                tk.Label(r, text=val, font=F_SMALL, fg=fg_c,
                         bg=row_bg, width=w, anchor="w").pack(side="left", padx=4)
        if not filtered:
            tk.Label(frame, text="No entries.", font=F_BODY, fg=PURPLE, bg=BG).pack(pady=16)

    def _clear_log(self, logs, frame):
        if messagebox.askyesno("Clear", "Delete all activity log entries?"):
            DB.clear_logs(); logs.clear()
            self._redraw_log(logs, frame)

    def _build_stats(self):
        p     = self._sub_content
        users = DB.get_users()
        logs  = DB.get_logs()
        lb    = DB.get_leaderboard()
        total   = len(users)
        players = sum(1 for u in users if u.get("role") == "player")
        mods    = sum(1 for u in users if u.get("role") == "moderator")
        admins  = sum(1 for u in users if u.get("role") == "admin")
        banned  = sum(1 for u in users if u.get("status") == "banned")
        r1 = tk.Frame(p, bg=BG); r1.pack(fill="x", pady=6)
        stat_card(r1, total,   "Total Users", BLUE)
        stat_card(r1, players, "Players",     GREEN)
        stat_card(r1, mods,    "Moderators",  PURPLE)
        stat_card(r1, admins,  "Admins",      ORANGE)
        stat_card(r1, banned,  "Banned",      RED)
        stat_card(r1, len(logs), "Log Entries", YELLOW)

        outer, inner = card(p, BLUE, pady=10, padx=12)
        outer.pack(fill="x", pady=8)
        tk.Label(inner, text="User Role Breakdown",
                 font=F_SUB, fg=BLUE, bg=PANEL).pack(anchor="w")
        for role, cnt, col in [("Player",players,GREEN),("Moderator",mods,PURPLE),("Admin",admins,ORANGE)]:
            pct = int(cnt / total * 100) if total else 0
            row = tk.Frame(inner, bg=PANEL); row.pack(fill="x", pady=2)
            tk.Label(row, text=f"{role:12s}  {cnt:3d}  ({pct}%)",
                     font=F_BODY, fg=col, bg=PANEL, width=26, anchor="w").pack(side="left")
            bar = tk.Canvas(row, bg=PANEL2, height=14, width=300, highlightthickness=0)
            bar.pack(side="left", padx=6)
            bar.create_rectangle(0, 0, pct*3, 14, fill=col, outline="")

        outer2, inner2 = card(p, GREEN, pady=10, padx=12)
        outer2.pack(fill="x", pady=8)
        tk.Label(inner2, text="Most Active Users",
                 font=F_SUB, fg=GREEN, bg=PANEL).pack(anchor="w")
        uc = Counter(l.get("username") for l in logs)
        for rank, (uname, cnt) in enumerate(uc.most_common(5), 1):
            tk.Label(inner2, text=f"  #{rank}  {uname or '?':22s}  {cnt} actions",
                     font=F_BODY, fg=TEXT, bg=PANEL).pack(anchor="w")

    def _build_seasons(self):
        p  = self._sub_content
        lb = sorted(DB.get_leaderboard(), key=lambda x: x.get("points",0), reverse=True)
        if not lb:
            tk.Label(p, text="No season history yet.",
                     font=F_BODY, fg=PURPLE, bg=BG).pack(pady=30); return
        wins  = sum(1 for e in lb if e.get("result") == "Win")
        r = tk.Frame(p, bg=BG); r.pack(fill="x", pady=(0, 8))
        stat_card(r, len(lb), "Total Seasons", BLUE)
        stat_card(r, wins,    "Wins",          GREEN)
        stat_card(r, len(lb)-wins, "Losses",   RED)
        col_header(p, [("Rank",6),("Username",16),("Points",10),
                       ("Pollution",12),("Day",8),("Result",10),("Date",20)])
        _, frame = scrollable(p)
        for i, e in enumerate(lb):
            row_bg = PANEL if i%2==0 else PANEL2
            r = tk.Frame(frame, bg=row_bg, pady=2); r.pack(fill="x")
            res = e.get("result","?"); rc = GREEN if res=="Win" else RED
            for val, w, fg_c in [
                (str(i+1),6,DIM),(e.get("username","?"),16,TEXT),
                (str(e.get("points",0)),10,YELLOW),(f"{e.get('pollution','?')}%",12,rc),
                (str(e.get("day","?")),8,TEXT),(res,10,rc),(e.get("date",""),20,DIM),
            ]:
                tk.Label(r, text=val, font=F_SMALL, fg=fg_c,
                         bg=row_bg, width=w, anchor="w").pack(side="left", padx=4)
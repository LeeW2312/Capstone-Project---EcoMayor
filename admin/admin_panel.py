"""admin/admin_panel.py — Shell: topbar + 4 tab buttons"""
import tkinter as tk
from core.theme import *
import core.database as DB


class AdminPanel(tk.Frame):
    def __init__(self, master, nav, user: dict):
        super().__init__(master, bg=BG)
        self.nav  = nav
        self.user = user
        self.pack(fill="both", expand=True)
        self._build_topbar()
        self._build_tabs()
        self._show("users")

    def _build_topbar(self):
        top = tk.Frame(self, bg=PANEL2, pady=6); top.pack(fill="x")
        tk.Label(top, text=f"  {self.user['username']} [Admin]",
                 font=F_BODY, fg=ORANGE, bg=PANEL2).pack(side="left")
        tk.Label(top, text="Admin Panel",
                 font=F_TITLE, fg=ORANGE, bg=PANEL2).pack(side="left", expand=True)
        button(top, "Logout", fg=WHITE, bg=RED,
               cmd=self._logout, padx=14, pady=4).pack(side="right", padx=10)

    def _logout(self):
        DB.log(self.user["username"], "LOGOUT")
        self.nav.logout()

    def _build_tabs(self):
        bar = tk.Frame(self, bg=BG, pady=4); bar.pack(fill="x", padx=10)
        self._tab_btns = {}
        for lbl, key, col in [
            ("👥  User Management",  "users",       BLUE),
            ("🏆  Leaderboard",      "leaderboard", YELLOW),
            ("📋  Reporting & Logs", "reporting",   GREEN),
            ("⏱  Season Control",   "season",      ORANGE),
        ]:
            b = button(bar, lbl, fg=col, bg=PANEL2,
                       cmd=lambda k=key: self._show(k), padx=12, pady=6)
            b.pack(side="left", padx=4)
            self._tab_btns[key] = b
        self._content = tk.Frame(self, bg=BG)
        self._content.pack(fill="both", expand=True, padx=10, pady=4)

    def _show(self, key):
        for k, b in self._tab_btns.items():
            b.configure(bg=PANEL if k == key else PANEL2)
        for w in self._content.winfo_children():
            w.destroy()
        if key == "users":
            from admin.user_management import UserManagementPanel
            UserManagementPanel(self._content, self.user)
        elif key == "leaderboard":
            from admin.leaderboard_panel import LeaderboardPanel
            LeaderboardPanel(self._content, self.user)
        elif key == "reporting":
            from admin.reporting_panel import ReportingPanel
            ReportingPanel(self._content, self.user)
        elif key == "season":
            from admin.season_control_panel import SeasonControlPanel
            SeasonControlPanel(self._content, self.user)
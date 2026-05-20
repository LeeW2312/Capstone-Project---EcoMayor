"""admin/season_control_panel.py — Configure all game settings"""
import tkinter as tk
from tkinter import messagebox
from core.theme import *
import core.database as DB


class SeasonControlPanel(tk.Frame):
    def __init__(self, parent, admin_user: dict):
        super().__init__(parent, bg=BG)
        self.admin_user = admin_user
        self._sv = {}
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        s = DB.get_settings()
        button(self, "💾  Save All Settings", fg=GREEN, bg="#003a10",
               cmd=self._save, padx=14, pady=6).pack(anchor="e", pady=4)
        _, frame = scrollable(self)

        self._section(frame, "⏱  Season Settings", ORANGE, s, [
            ("Season Duration (days)",      "season_duration",    int),
            ("Starting Pollution (%)",       "starting_pollution", int),
            ("Pollution Goal (%)",           "goal_pollution",     int),
            ("Questions per Quiz Session",   "quiz_per_session",   int),
            ("Bonus Points for Winning",     "bonus_win",          int),
            ("Points per Correct Answer",    "pts_per_correct",    int),
        ])
        self._section(frame, "🏭  Pollution Rise per Day", RED, s, [
            ("Easy Mode   (+% / day)",  "rise_easy",   float),
            ("Medium Mode (+% / day)",  "rise_medium", float),
            ("Hard Mode   (+% / day)",  "rise_hard",   float),
        ])
        self._section(frame, "💰  Upgrade Cost Multipliers", YELLOW, s, [
            ("Easy Mode   (×)",  "mult_easy",   float),
            ("Medium Mode (×)",  "mult_medium", float),
            ("Hard Mode   (×)",  "mult_hard",   float),
        ])
        self._danger_zone(frame)

    def _section(self, parent, title, color, settings, fields):
        outer, inner = card(parent, color, pady=10, padx=14)
        outer.pack(fill="x", pady=8)
        tk.Label(inner, text=title, font=F_SUB,
                 fg=color, bg=PANEL).pack(anchor="w", pady=(0, 8))
        for lbl, key, dtype in fields:
            r = tk.Frame(inner, bg=PANEL); r.pack(fill="x", pady=3)
            tk.Label(r, text=f"{lbl}:", font=F_BODY, fg=TEXT,
                     bg=PANEL, width=36, anchor="w").pack(side="left")
            v = tk.StringVar(value=str(settings.get(key, "")))
            self._sv[key] = (v, dtype)
            tk.Entry(r, textvariable=v, font=F_BODY, bg=PANEL2,
                     fg=YELLOW, insertbackground=YELLOW,
                     relief="flat", width=12).pack(side="left", padx=6)

    def _danger_zone(self, parent):
        outer, inner = card(parent, RED, pady=10, padx=14)
        outer.pack(fill="x", pady=8)
        tk.Label(inner, text="⚠  Danger Zone",
                 font=F_SUB, fg=RED, bg=PANEL).pack(anchor="w", pady=(0, 8))
        for lbl, cmd in [
            ("Reset ALL players' pollution", self._reset_all_pollution),
            ("Clear entire leaderboard",     self._clear_lb),
            ("Reset all settings to defaults", self._reset_defaults),
        ]:
            r = tk.Frame(inner, bg=PANEL); r.pack(fill="x", pady=4)
            tk.Label(r, text=lbl, font=F_BODY, fg=TEXT, bg=PANEL).pack(side="left")
            button(r, "Execute", fg=RED, bg="#3a0000",
                   cmd=cmd, padx=8).pack(side="right")

    def _save(self):
        s = DB.get_settings(); errors = []
        for key, (v, dtype) in self._sv.items():
            try: s[key] = dtype(v.get())
            except ValueError: errors.append(key)
        if errors:
            messagebox.showerror("Error", "Fix:\n" + "\n".join(errors)); return
        DB.save_settings(s)
        messagebox.showinfo("Saved", "Settings saved.")

    def _reset_all_pollution(self):
        s = DB.get_settings()
        if not messagebox.askyesno("Confirm", "Reset ALL players' pollution?"): return
        users = DB.get_users(); start = s.get("starting_pollution", 100)
        for u in users:
            if u.get("role") == "player" and u.get("status") != "banned":
                u.update({"pollution": start, "points": 0, "day": 1,
                          "upgrades_bought": [], "pollution_history": [start]})
        DB.save_users(users)
        messagebox.showinfo("Done", f"All players reset to {start}%.")

    def _clear_lb(self):
        if messagebox.askyesno("Clear", "Delete all leaderboard records?"):
            DB.clear_leaderboard()
            messagebox.showinfo("Done", "Leaderboard cleared.")

    def _reset_defaults(self):
        from core.database import _DEFAULT_SETTINGS
        if messagebox.askyesno("Reset", "Reset all settings to defaults?"):
            DB.save_settings(dict(_DEFAULT_SETTINGS))
            messagebox.showinfo("Done", "Settings reset.")
            for w in self.winfo_children(): w.destroy()
            self._sv.clear(); self._build()
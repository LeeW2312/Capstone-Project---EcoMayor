"""admin/user_management.py — View, ban, change role, reset users"""
import tkinter as tk
from tkinter import messagebox
from core.theme import *
import core.database as DB


class UserManagementPanel(tk.Frame):
    def __init__(self, parent, admin_user: dict):
        super().__init__(parent, bg=BG)
        self.admin_user = admin_user
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        users = DB.get_users()
        total         = len(users)
        banned        = sum(1 for u in users if u.get("status") == "banned")
        moderators    = sum(1 for u in users if u.get("role")   == "moderator")
        admins        = sum(1 for u in users if u.get("role")   == "admin")
        seasons_total = sum(u.get("seasons_played", 0) for u in users)
        wins_total    = sum(u.get("seasons_won",    0) for u in users)

        row = tk.Frame(self, bg=BG); row.pack(fill="x", pady=(0, 8))
        stat_card(row, total,       "Total Users", BLUE)
        stat_card(row, banned,      "Banned",      RED)
        stat_card(row, moderators,  "Moderators",  PURPLE)
        stat_card(row, admins,      "Admins",      ORANGE)
        stat_card(row, seasons_total, "Seasons",   YELLOW)
        stat_card(row, f"{wins_total}/{seasons_total}", "Won", GREEN)

        col_header(self, [
            ("#", 4), ("Username", 14), ("Role", 12), ("Status", 10),
            ("Seasons", 8), ("Best", 8), ("Actions", 30),
        ])
        _, frame = scrollable(self)
        me = self.admin_user["username"]

        for i, u in enumerate(users):
            row_bg = PANEL if i % 2 == 0 else PANEL2
            r      = tk.Frame(frame, bg=row_bg, pady=3); r.pack(fill="x")
            uname  = u.get("username", "?")
            role   = u.get("role",     "player")
            status = u.get("status",   "active")
            r_col  = ROLE_COLORS.get(role, TEXT)
            s_col  = GREEN if status == "active" else RED
            is_me  = (uname == me)
            for val, w, fg_c in [
                (str(i+1), 4, DIM),
                (uname, 14, PURPLE if is_me else TEXT),
                (role.capitalize(), 12, r_col),
                ("You" if is_me else status.upper(), 10, PURPLE if is_me else s_col),
                (str(u.get("seasons_played", 0)), 8, TEXT),
                (str(u.get("best_score",    0)), 8, YELLOW),
            ]:
                tk.Label(r, text=val, font=F_SMALL, fg=fg_c,
                         bg=row_bg, width=w, anchor="w").pack(side="left", padx=4)
            if not is_me:
                self._action_buttons(r, u)

        tk.Label(frame, text=f"Total: {total} users",
                 font=F_SMALL, fg=DIM, bg=BG, anchor="w").pack(fill="x", pady=4)

    def _action_buttons(self, row, u):
        uname  = u.get("username", "?")
        role   = u.get("role",   "player")
        status = u.get("status", "active")
        if status == "banned":
            button(row, "Unban", fg=GREEN, bg="#003a10",
                   cmd=lambda: self._set_status(uname, "active"),
                   padx=5, font=F_SMALL).pack(side="left", padx=2)
        else:
            button(row, "Ban", fg=RED, bg="#3a0000",
                   cmd=lambda: self._set_status(uname, "banned"),
                   padx=5, font=F_SMALL).pack(side="left", padx=2)
        for new_role in [r for r in ["player","moderator","admin"] if r != role]:
            button(row, f"→{new_role.capitalize()}",
                   fg=ROLE_COLORS[new_role], bg=PANEL,
                   cmd=lambda nr=new_role: self._change_role(uname, nr),
                   padx=4, font=F_SMALL).pack(side="left", padx=2)
        button(row, "Reset", fg=ORANGE, bg="#3a2000",
               cmd=lambda: self._reset(uname),
               padx=4, font=F_SMALL).pack(side="left", padx=2)

    def _set_status(self, username, new_status):
        action = "ban" if new_status == "banned" else "unban"
        if not messagebox.askyesno("Confirm", f"{action.capitalize()} {username}?"):
            return
        users = DB.get_users()
        for u in users:
            if u["username"] == username: u["status"] = new_status; break
        DB.save_users(users)
        DB.log(self.admin_user["username"],
               "BAN" if new_status == "banned" else "UNBAN", username)
        self._refresh()

    def _change_role(self, username, new_role):
        if not messagebox.askyesno("Confirm",
                f"Change {username}'s role to {new_role}?"): return
        users = DB.get_users()
        for u in users:
            if u["username"] == username: u["role"] = new_role; break
        DB.save_users(users)
        DB.log(self.admin_user["username"], "ROLE_CHANGE", f"{username} → {new_role}")
        self._refresh()

    def _reset(self, username):
        if not messagebox.askyesno("Confirm",
                f"Reset {username}'s game progress?"): return
        users = DB.get_users()
        for u in users:
            if u["username"] == username:
                u.update({"pollution": 100, "points": 0, "day": 1,
                          "upgrades_bought": [], "pollution_history": [100]}); break
        DB.save_users(users)
        DB.log(self.admin_user["username"], "RESET", username)
        messagebox.showinfo("Done", f"{username} has been reset.")
        self._refresh()

    def _refresh(self):
        for w in self.winfo_children(): w.destroy()
        self._build()
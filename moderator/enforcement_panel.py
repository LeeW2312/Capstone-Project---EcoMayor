"""moderator/enforcement_panel.py — Player Monitor, Issue Warning, Reports"""
import tkinter as tk
from tkinter import messagebox, ttk
from collections import Counter
from datetime import datetime
from core.theme import *
import core.database as DB


class EnforcementPanel(tk.Frame):
    def __init__(self, parent, mod_user: dict):
        super().__init__(parent, bg=BG)
        self.mod_user = mod_user
        self.pack(fill="both", expand=True)
        self._build_subtabs()
        self._show_sub("monitor")

    def _build_subtabs(self):
        bar = tk.Frame(self, bg=BG, pady=4); bar.pack(fill="x")
        self._sub_btns = {}
        for lbl, key, col in [
            ("👁  Player Monitor", "monitor", BLUE),
            ("⚠  Issue Warning",   "warn",    ORANGE),
            ("📩  Reports",        "reports", RED),
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
        {"monitor": self._build_monitor,
         "warn":    self._build_warn,
         "reports": self._build_reports}[key]()

    # ── Player Monitor ────────────────────────────────────────────────────────

    def _build_monitor(self):
        p       = self._sub_content
        players = [u for u in DB.get_users() if u.get("role") == "player"]
        ac      = Counter(l.get("username") for l in DB.get_logs())

        row = tk.Frame(p, bg=BG); row.pack(fill="x", pady=(0,8))
        stat_card(row, len(players), "Total Players", GREEN)
        stat_card(row, sum(1 for u in players if u.get("status")!="banned"), "Active", BLUE)
        stat_card(row, sum(1 for u in players if u.get("status")=="banned"),  "Banned", RED)
        stat_card(row, sum(1 for u in players if u.get("warnings",0)>0),      "Warned", ORANGE)

        col_header(p, [("#",4),("Username",14),("Status",10),("Warnings",10),
                       ("Seasons",9),("Best",9),("Logs",10),("Actions",24)])
        _, frame = scrollable(p)

        for i, u in enumerate(players):
            row_bg = PANEL if i%2==0 else PANEL2
            r = tk.Frame(frame, bg=row_bg, pady=3); r.pack(fill="x")
            status = u.get("status","active"); warns = u.get("warnings",0)
            uname  = u.get("username","?")
            for val, w, fg_c in [
                (str(i+1),4,DIM),(uname,14,TEXT),(status.upper(),10,GREEN if status=="active" else RED),
                (str(warns),10,ORANGE if warns>0 else TEXT),
                (str(u.get("seasons_played",0)),9,TEXT),(str(u.get("best_score",0)),9,YELLOW),
                (str(ac.get(uname,0)),10,DIM),
            ]:
                tk.Label(r, text=val, font=F_SMALL, fg=fg_c,
                         bg=row_bg, width=w, anchor="w").pack(side="left", padx=4)
            button(r, "Warn", fg=ORANGE, bg="#3a2000", font=F_SMALL, padx=4,
                   cmd=lambda u=uname: self._quick_warn(u)).pack(side="left", padx=2)
            if status == "active":
                button(r, "Suspend", fg=RED, bg="#3a0000", font=F_SMALL, padx=4,
                       cmd=lambda u=uname: self._suspend(u)).pack(side="left", padx=2)
            else:
                button(r, "Reinstate", fg=GREEN, bg="#003a10", font=F_SMALL, padx=4,
                       cmd=lambda u=uname: self._reinstate(u)).pack(side="left", padx=2)

    def _quick_warn(self, username):
        users = DB.get_users()
        for u in users:
            if u["username"] == username:
                u["warnings"] = u.get("warnings",0) + 1
                if u["warnings"] >= 3: u["status"] = "banned"
                break
        DB.save_users(users)
        DB.add_report({"type":"warning","ts":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                       "target":username,"reason":"Quick warning from monitor",
                       "notes":"","by":self.mod_user["username"]})
        DB.log(self.mod_user["username"],"WARNING",f"Quick warn: {username}")
        self._show_sub("monitor")

    def _suspend(self, username):
        if not messagebox.askyesno("Suspend", f"Suspend {username}?"): return
        users = DB.get_users()
        for u in users:
            if u["username"] == username: u["status"] = "banned"; break
        DB.save_users(users)
        DB.log(self.mod_user["username"],"SUSPEND",username)
        self._show_sub("monitor")

    def _reinstate(self, username):
        if not messagebox.askyesno("Reinstate", f"Reinstate {username}?"): return
        users = DB.get_users()
        for u in users:
            if u["username"] == username: u["status"] = "active"; break
        DB.save_users(users)
        DB.log(self.mod_user["username"],"REINSTATE",username)
        self._show_sub("monitor")

    # ── Issue Warning ─────────────────────────────────────────────────────────

    def _build_warn(self):
        p       = self._sub_content
        players = [u for u in DB.get_users() if u.get("role") == "player"]
        unames  = [u["username"] for u in players]

        outer, inner = card(p, ORANGE, pady=10, padx=14)
        outer.pack(fill="x", pady=(0,8))
        tk.Label(inner, text="⚠  Issue a Formal Warning",
                 font=F_SUB, fg=ORANGE, bg=PANEL).pack(anchor="w", pady=(0,10))
        self._wp = tk.StringVar(); self._wr = tk.StringVar()
        for lbl, var, opts in [
            ("Select Player", self._wp, unames),
            ("Reason",        self._wr, ["Inappropriate language","Cheating suspected",
                                          "Spam / quiz abuse","Exploiting game bugs",
                                          "Community guidelines","Other"]),
        ]:
            r = tk.Frame(inner, bg=PANEL); r.pack(fill="x", pady=4)
            tk.Label(r, text=f"{lbl}:", font=F_BODY, fg=TEXT,
                     bg=PANEL, width=16, anchor="w").pack(side="left")
            ttk.Combobox(r, textvariable=var, values=opts,
                         state="readonly", font=F_BODY, width=28).pack(side="left", padx=6)
        tk.Label(inner, text="Notes:", font=F_BODY, fg=TEXT, bg=PANEL).pack(anchor="w")
        self._wnotes = tk.Text(inner, height=3, width=58, font=F_BODY,
                               bg=PANEL2, fg=TEXT, insertbackground=TEXT, relief="flat")
        self._wnotes.pack(pady=(2,8))
        button(inner, "Issue Warning", fg=WHITE, bg="#3a2000",
               cmd=self._submit_warn, padx=14, pady=6).pack(anchor="w")
        tk.Label(inner, text="Auto-suspended after 3 warnings.",
                 font=F_SMALL, fg=DIM, bg=PANEL).pack(anchor="w", pady=(4,0))

        tk.Frame(p, bg=ORANGE, height=1).pack(fill="x", pady=(10,4))
        tk.Label(p, text="Recent Warnings (last 10)",
                 font=F_SUB, fg=ORANGE, bg=BG).pack(anchor="w")
        warnings = [r for r in DB.get_reports() if r.get("type") == "warning"]
        if not warnings:
            tk.Label(p, text="No warnings yet.", font=F_BODY, fg=DIM, bg=BG).pack(anchor="w", pady=6)
        else:
            for rpt in reversed(warnings[-10:]):
                row = tk.Frame(p, bg=PANEL2, pady=3); row.pack(fill="x", pady=1)
                tk.Label(row,
                         text=f"  {rpt.get('ts','?')[:16]}  │  "
                              f"{rpt.get('target','?'):16s}  │  "
                              f"{rpt.get('reason','?')}  │  by {rpt.get('by','?')}",
                         font=F_SMALL, fg=ORANGE, bg=PANEL2, anchor="w").pack(side="left")

    def _submit_warn(self):
        player = self._wp.get(); reason = self._wr.get()
        if not player: messagebox.showerror("Error","Select a player."); return
        if not reason: messagebox.showerror("Error","Select a reason."); return
        users = DB.get_users(); warn_count = 0
        for u in users:
            if u["username"] == player:
                u["warnings"] = u.get("warnings",0) + 1
                warn_count    = u["warnings"]
                if warn_count >= 3: u["status"] = "banned"
                break
        DB.save_users(users)
        DB.add_report({"type":"warning","ts":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                       "target":player,"reason":reason,
                       "notes":self._wnotes.get("1.0","end").strip(),
                       "by":self.mod_user["username"]})
        DB.log(self.mod_user["username"],"WARNING",f"Warned {player}: {reason}")
        msg = f"Warning #{warn_count} issued to {player}."
        if warn_count >= 3: msg += f"\n{player} auto-suspended."
        messagebox.showinfo("Done", msg)
        self._wp.set(""); self._wr.set(""); self._wnotes.delete("1.0","end")
        self._show_sub("warn")

    # ── Reports ───────────────────────────────────────────────────────────────

    def _build_reports(self):
        p       = self._sub_content
        players = [u for u in DB.get_users() if u.get("role") == "player"]
        unames  = [u["username"] for u in players]

        outer, inner = card(p, RED, pady=10, padx=14)
        outer.pack(fill="x", pady=(0,8))
        tk.Label(inner, text="📩  File a Report",
                 font=F_SUB, fg=RED, bg=PANEL).pack(anchor="w", pady=(0,10))
        self._rp = tk.StringVar(); self._rt = tk.StringVar()
        for lbl, var, opts in [
            ("Reported Player", self._rp, unames),
            ("Issue Type",      self._rt, ["Cheating","Exploit","Harassment",
                                            "Bug abuse","Suspicious score","Other"]),
        ]:
            r = tk.Frame(inner, bg=PANEL); r.pack(fill="x", pady=4)
            tk.Label(r, text=f"{lbl}:", font=F_BODY, fg=TEXT,
                     bg=PANEL, width=16, anchor="w").pack(side="left")
            ttk.Combobox(r, textvariable=var, values=opts,
                         font=F_BODY, width=28).pack(side="left", padx=6)
        tk.Label(inner, text="Description:", font=F_BODY, fg=TEXT, bg=PANEL).pack(anchor="w")
        self._rdesc = tk.Text(inner, height=3, width=58, font=F_BODY,
                              bg=PANEL2, fg=TEXT, insertbackground=TEXT, relief="flat")
        self._rdesc.pack(pady=(2,8))
        button(inner, "Submit Report", fg=WHITE, bg="#3a0000",
               cmd=self._submit_report, padx=14, pady=6).pack(anchor="w")

        tk.Frame(p, bg=RED, height=1).pack(fill="x", pady=(10,4))
        tk.Label(p, text="All Reports", font=F_SUB, fg=RED, bg=BG).pack(anchor="w")
        col_header(p, [("#",4),("Time",18),("Target",14),("Issue",16),("By",12),("Status",10),("Act",6)])
        _, frame = scrollable(p)
        reports = [r for r in DB.get_reports() if r.get("type") == "report"]
        if not reports:
            tk.Label(frame, text="No reports yet.",
                     font=F_BODY, fg=DIM, bg=BG).pack(pady=10)
        else:
            for i, rpt in enumerate(reversed(reports)):
                row_bg = PANEL if i%2==0 else PANEL2
                r = tk.Frame(frame, bg=row_bg, pady=2); r.pack(fill="x")
                resolved = rpt.get("resolved", False)
                st = "Resolved" if resolved else "Open"
                for val, w, fg_c in [
                    (str(i+1),4,DIM),(rpt.get("ts","")[:16],18,DIM),
                    (rpt.get("target","?"),14,TEXT),(rpt.get("issue_type","?"),16,TEXT),
                    (rpt.get("by","?"),12,DIM),(st,10,GREEN if resolved else ORANGE),
                ]:
                    tk.Label(r, text=val, font=F_SMALL, fg=fg_c,
                             bg=row_bg, width=w, anchor="w").pack(side="left", padx=4)
                button(r, "✓" if not resolved else "↺", fg=GREEN, bg=PANEL, font=F_SMALL, padx=4,
                       cmd=lambda rpt=rpt: self._toggle(rpt)).pack(side="left")

    def _submit_report(self):
        player = self._rp.get(); itype = self._rt.get()
        if not player: messagebox.showerror("Error","Select a player."); return
        if not itype:  messagebox.showerror("Error","Select issue type."); return
        DB.add_report({"type":"report","ts":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                       "target":player,"issue_type":itype,
                       "description":self._rdesc.get("1.0","end").strip(),
                       "by":self.mod_user["username"],"resolved":False})
        DB.log(self.mod_user["username"],"REPORT",f"{player}: {itype}")
        messagebox.showinfo("Done","Report submitted.")
        self._rp.set(""); self._rt.set(""); self._rdesc.delete("1.0","end")
        self._show_sub("reports")

    def _toggle(self, report):
        reports = DB.get_reports()
        for rpt in reports:
            if rpt.get("ts") == report.get("ts") and rpt.get("target") == report.get("target"):
                rpt["resolved"] = not rpt.get("resolved", False); break
        DB.save_reports(reports)
        self._show_sub("reports")
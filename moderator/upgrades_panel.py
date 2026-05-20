"""moderator/upgrades_panel.py — Add/Edit/Delete upgrades + EditUpgradeDialog"""
import tkinter as tk
from tkinter import messagebox
from core.theme import *
import core.database as DB


class UpgradesPanel(tk.Frame):
    def __init__(self, parent, mod_user: dict):
        super().__init__(parent, bg=BG)
        self.mod_user = mod_user
        self.pack(fill="both", expand=True)
        self._build_form()
        self._build_list()

    def _build_form(self):
        outer, inner = card(self, ORANGE, pady=10, padx=14)
        outer.pack(fill="x", pady=(0, 8))
        tk.Label(inner, text="Add New Upgrade",
                 font=F_SUB, fg=ORANGE, bg=PANEL).pack(anchor="w", pady=(0, 8))
        self._uN = tk.StringVar(); self._uR = tk.StringVar(); self._uC = tk.StringVar()
        for lbl, var, width in [
            ("Upgrade Name",                      self._uN, 36),
            ("Pollution Reduction % (e.g. 8.5)",  self._uR, 14),
            ("Cost in Points (e.g. 100)",          self._uC, 14),
        ]:
            r = tk.Frame(inner, bg=PANEL); r.pack(fill="x", pady=3)
            tk.Label(r, text=f"{lbl}:", font=F_BODY, fg=TEXT,
                     bg=PANEL, width=30, anchor="w").pack(side="left")
            tk.Entry(r, textvariable=var, font=F_BODY, bg=PANEL2,
                     fg=YELLOW, insertbackground=YELLOW,
                     relief="flat", width=width).pack(side="left", padx=6)
        self._err = tk.Label(inner, text="", font=F_SMALL, fg=RED, bg=PANEL)
        self._err.pack(anchor="w")
        row = tk.Frame(inner, bg=PANEL); row.pack(fill="x", pady=(4, 0))
        button(row, "Add Upgrade", fg=WHITE, bg="#3a2000",
               cmd=self._add, padx=12, pady=6).pack(side="left")
        tk.Label(row, text="  Duplicates blocked automatically.",
                 font=F_SMALL, fg=DIM, bg=PANEL).pack(side="left")

    def _build_list(self):
        col_header(self, [("Upgrade Name",26),("Pollution Reduction",20),
                          ("Point Cost",12),("Edit",6),("Del",6)])
        _, frame = scrollable(self)
        self._list_frame = frame
        self._redraw()

    def _redraw(self):
        for w in self._list_frame.winfo_children(): w.destroy()
        upgrades = DB.get_upgrades()
        for i, u in enumerate(upgrades):
            row_bg = PANEL if i%2==0 else PANEL2
            r = tk.Frame(self._list_frame, bg=row_bg, pady=4); r.pack(fill="x")
            for val, w, fg_c in [
                (u.get("name",""), 26, TEXT),
                (f"-{u.get('pollution_reduction',0):.1f}%", 20, GREEN),
                (f"{u.get('cost',0)} pts", 12, YELLOW),
            ]:
                tk.Label(r, text=val, font=F_BODY, fg=fg_c,
                         bg=row_bg, width=w, anchor="w").pack(side="left", padx=4)
            button(r, "Edit", fg=GREEN, bg="#003a10", font=F_SMALL, padx=4,
                   cmd=lambda u=u: EditUpgradeDialog(
                       self.winfo_toplevel(), u, self._redraw)
                   ).pack(side="left", padx=2)
            button(r, "Del",  fg=RED,   bg="#3a0000", font=F_SMALL, padx=4,
                   cmd=lambda u=u: self._delete(u)
                   ).pack(side="left", padx=2)
        tk.Label(self._list_frame, text=f"Total: {len(upgrades)} upgrades",
                 font=F_SMALL, fg=DIM, bg=BG, anchor="w").pack(fill="x", pady=4)

    def _add(self):
        n = self._uN.get().strip(); r = self._uR.get().strip(); c = self._uC.get().strip()
        if not all([n, r, c]):
            self._err.configure(text="All fields required."); return
        try: float(r); int(c)
        except ValueError:
            self._err.configure(text="Reduction = number; Cost = integer."); return
        ok, msg = DB.add_upgrade(n, float(r), int(c))
        if not ok: self._err.configure(text=msg); return
        DB.log(self.mod_user["username"], "ADD_UPGRADE", n)
        for v in [self._uN, self._uR, self._uC]: v.set("")
        self._err.configure(text=""); self._redraw()

    def _delete(self, u):
        if messagebox.askyesno("Delete", f"Delete \"{u['name']}\"?"):
            DB.delete_upgrade(u["name"])
            DB.log(self.mod_user["username"], "DEL_UPGRADE", u["name"])
            self._redraw()


class EditUpgradeDialog(tk.Toplevel):
    def __init__(self, master, upgrade: dict, on_save):
        super().__init__(master)
        self.title("Edit Upgrade"); self.configure(bg=BG)
        self.resizable(False, False); self.grab_set()
        self.upgrade = upgrade; self.on_save = on_save
        self._build(); self._center()

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{(self.winfo_screenwidth()-w)//2}"
                      f"+{(self.winfo_screenheight()-h)//2}")

    def _build(self):
        tk.Frame(self, bg=ORANGE, height=3).pack(fill="x")
        body = tk.Frame(self, bg=PANEL, padx=22, pady=16); body.pack(fill="both")
        tk.Label(body, text="✏  Edit Upgrade",
                 font=F_TITLE, fg=ORANGE, bg=PANEL).pack(anchor="w", pady=(0,10))
        u = self.upgrade
        self._n = tk.StringVar(value=u.get("name",""))
        self._r = tk.StringVar(value=str(u.get("pollution_reduction",0)))
        self._c = tk.StringVar(value=str(u.get("cost",0)))
        for lbl, var, col in [
            ("Upgrade Name",             self._n, ORANGE),
            ("Pollution Reduction (%)",  self._r, GREEN),
            ("Cost (points)",            self._c, YELLOW),
        ]:
            r = tk.Frame(body, bg=PANEL); r.pack(fill="x", pady=4)
            tk.Label(r, text=f"{lbl}:", font=F_BODY, fg=col,
                     bg=PANEL, width=24, anchor="w").pack(side="left")
            tk.Entry(r, textvariable=var, font=F_BODY, bg=PANEL2,
                     fg=YELLOW, insertbackground=YELLOW,
                     relief="flat", width=30).pack(side="left", padx=6)
        br = tk.Frame(body, bg=PANEL); br.pack(fill="x", pady=(8,0))
        button(br, "💾  Save", fg=GREEN, bg="#003a10",
               cmd=self._save, padx=12, pady=6).pack(side="left", padx=4)
        button(br, "Cancel", fg=TEXT, bg=PANEL2,
               cmd=self.destroy, padx=12, pady=6).pack(side="left")

    def _save(self):
        n = self._n.get().strip()
        try: r = float(self._r.get()); c = int(self._c.get())
        except ValueError:
            messagebox.showerror("Error","Invalid number.",parent=self); return
        if not n:
            messagebox.showerror("Error","Name required.",parent=self); return
        DB.edit_upgrade(self.upgrade["name"], n, r, c)
        self.destroy(); self.on_save()
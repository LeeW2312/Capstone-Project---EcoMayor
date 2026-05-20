"""moderator/questions_panel.py — Add/Edit/Delete questions + EditQuestionDialog"""
import tkinter as tk
from tkinter import messagebox
from core.theme import *
import core.database as DB


class QuestionsPanel(tk.Frame):
    def __init__(self, parent, mod_user: dict):
        super().__init__(parent, bg=BG)
        self.mod_user = mod_user
        self.pack(fill="both", expand=True)
        self._build_form()
        self._build_list()

    def _build_form(self):
        outer, inner = card(self, GREEN, pady=10, padx=14)
        outer.pack(fill="x", pady=(0, 8))
        tk.Label(inner, text="Add New Question",
                 font=F_SUB, fg=GREEN, bg=PANEL).pack(anchor="w", pady=(0, 8))
        self._qQ = tk.StringVar(); self._qC = tk.StringVar()
        self._qB = tk.StringVar(); self._qC2= tk.StringVar(); self._qD = tk.StringVar()
        for lbl, var, color in [
            ("Question",           self._qQ, TEXT),
            ("Correct Answer (A)", self._qC, GREEN),
            ("Wrong Answer  (B)",  self._qB, RED),
            ("Wrong Answer  (C)",  self._qC2,RED),
            ("Wrong Answer  (D)",  self._qD, RED),
        ]:
            r = tk.Frame(inner, bg=PANEL); r.pack(fill="x", pady=3)
            tk.Label(r, text=f"{lbl}:", font=F_BODY, fg=color,
                     bg=PANEL, width=22, anchor="w").pack(side="left")
            tk.Entry(r, textvariable=var, font=F_BODY, bg=PANEL2,
                     fg=YELLOW, insertbackground=YELLOW,
                     relief="flat", width=50).pack(side="left", padx=6)
        self._err = tk.Label(inner, text="", font=F_SMALL, fg=RED, bg=PANEL)
        self._err.pack(anchor="w")
        row = tk.Frame(inner, bg=PANEL); row.pack(fill="x", pady=(4, 0))
        button(row, "Add Question", fg=WHITE, bg="#003a10",
               cmd=self._add, padx=12, pady=6).pack(side="left")
        tk.Label(row, text="  Duplicates blocked automatically.",
                 font=F_SMALL, fg=DIM, bg=PANEL).pack(side="left")

    def _build_list(self):
        col_header(self, [("#",4),("Question",50),("Correct Answer",24),("Edit",6),("Del",6)])
        _, frame = scrollable(self)
        self._list_frame = frame
        self._redraw()

    def _redraw(self):
        for w in self._list_frame.winfo_children(): w.destroy()
        qs = DB.get_quizzes()
        for i, q in enumerate(qs):
            row_bg = PANEL if i%2==0 else PANEL2
            r = tk.Frame(self._list_frame, bg=row_bg, pady=3); r.pack(fill="x")
            for val, w, fg_c in [
                (str(i+1), 4, DIM),
                (q.get("question","")[:60], 50, TEXT),
                (q.get("correct","")[:26],  24, GREEN),
            ]:
                tk.Label(r, text=val, font=F_SMALL, fg=fg_c,
                         bg=row_bg, width=w, anchor="w").pack(side="left", padx=4)
            button(r, "Edit", fg=GREEN, bg="#003a10", font=F_SMALL, padx=4,
                   cmd=lambda q=q: EditQuestionDialog(
                       self.winfo_toplevel(), q, self._redraw)
                   ).pack(side="left", padx=2)
            button(r, "Del",  fg=RED,   bg="#3a0000", font=F_SMALL, padx=4,
                   cmd=lambda q=q: self._delete(q)
                   ).pack(side="left", padx=2)
        tk.Label(self._list_frame, text=f"Total: {len(qs)} questions",
                 font=F_SMALL, fg=DIM, bg=BG, anchor="w").pack(fill="x", pady=4)

    def _add(self):
        q  = self._qQ.get().strip(); c  = self._qC.get().strip()
        b  = self._qB.get().strip(); c2 = self._qC2.get().strip()
        d  = self._qD.get().strip()
        if not all([q, c, b, c2, d]):
            self._err.configure(text="All fields required."); return
        ok, msg = DB.add_quiz(q, c, [b, c2, d])
        if not ok: self._err.configure(text=msg); return
        DB.log(self.mod_user["username"], "ADD_QUESTION", q[:50])
        for v in [self._qQ, self._qC, self._qB, self._qC2, self._qD]: v.set("")
        self._err.configure(text="")
        self._redraw()

    def _delete(self, q):
        if messagebox.askyesno("Delete", f"Delete:\n\"{q['question'][:70]}\""):
            DB.delete_quiz(q["question"])
            DB.log(self.mod_user["username"], "DEL_QUESTION", q["question"][:50])
            self._redraw()


class EditQuestionDialog(tk.Toplevel):
    def __init__(self, master, question: dict, on_save):
        super().__init__(master)
        self.title("Edit Question"); self.configure(bg=BG)
        self.resizable(False, False); self.grab_set()
        self.question = question; self.on_save = on_save
        self._build(); self._center()

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{(self.winfo_screenwidth()-w)//2}"
                      f"+{(self.winfo_screenheight()-h)//2}")

    def _build(self):
        tk.Frame(self, bg=GREEN, height=3).pack(fill="x")
        body = tk.Frame(self, bg=PANEL, padx=22, pady=16); body.pack(fill="both")
        tk.Label(body, text="✏  Edit Question",
                 font=F_TITLE, fg=GREEN, bg=PANEL).pack(anchor="w", pady=(0,10))
        q     = self.question
        wrong = q.get("wrong", [q.get("wrong_b",""), q.get("wrong_c",""), q.get("wrong_d","")])
        tk.Label(body, text="Question:", font=F_BODY, fg=TEXT, bg=PANEL, anchor="w").pack(fill="x")
        self._qt = tk.Text(body, height=3, width=62, font=F_BODY,
                           bg=PANEL2, fg=YELLOW, insertbackground=YELLOW, relief="flat")
        self._qt.insert("1.0", q.get("question",""))
        self._qt.pack(fill="x", pady=(2,8))
        self._vars = {}
        for lbl, key, default, col in [
            ("Correct (A)", "correct", q.get("correct",""),          GREEN),
            ("Wrong   (B)", "b",       wrong[0] if wrong else "",      RED),
            ("Wrong   (C)", "c",       wrong[1] if len(wrong)>1 else "",RED),
            ("Wrong   (D)", "d",       wrong[2] if len(wrong)>2 else "",RED),
        ]:
            r = tk.Frame(body, bg=PANEL); r.pack(fill="x", pady=3)
            tk.Label(r, text=f"{lbl}:", font=F_BODY, fg=col,
                     bg=PANEL, width=14, anchor="w").pack(side="left")
            v = tk.StringVar(value=default); self._vars[key] = v
            tk.Entry(r, textvariable=v, font=F_BODY, bg=PANEL2,
                     fg=YELLOW, insertbackground=YELLOW,
                     relief="flat", width=50).pack(side="left", padx=6)
        br = tk.Frame(body, bg=PANEL); br.pack(fill="x", pady=(12,0))
        button(br, "💾  Save", fg=GREEN, bg="#003a10",
               cmd=self._save, padx=12, pady=6).pack(side="left", padx=4)
        button(br, "Cancel", fg=TEXT, bg=PANEL2,
               cmd=self.destroy, padx=12, pady=6).pack(side="left")

    def _save(self):
        nq = self._qt.get("1.0","end").strip()
        c  = self._vars["correct"].get().strip()
        b, cc, d = [self._vars[k].get().strip() for k in ["b","c","d"]]
        if not all([nq, c, b, cc, d]):
            messagebox.showerror("Error","All fields required.",parent=self); return
        DB.edit_quiz(self.question["question"], nq, c, [b, cc, d])
        self.destroy(); self.on_save()
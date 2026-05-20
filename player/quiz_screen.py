"""
player/quiz_screen.py
Quiz earns points + XP ONLY.
Days are driven by the real calendar in game_data.py — NOT by quiz completion.
"""
import tkinter as tk
import random
from core.theme import *
from core.game_data import GameData
import core.database as DB
import core.sounds as SND


class QuizScreen(tk.Frame):
    def __init__(self, master, nav, gd: GameData):
        super().__init__(master, bg=BG)
        self.nav = nav
        self.gd  = gd
        self.pack(fill="both", expand=True)
        self._qs  = self._load_questions()
        self._idx = 0
        if not self._qs:
            self._no_questions()
            return
        self._build_hud()
        self._show_question()

    def _load_questions(self):
        all_qs = DB.get_quizzes()
        n = self.gd.quiz_per_session
        if len(all_qs) <= n:
            return list(all_qs)
        return random.sample(all_qs, n)

    def _no_questions(self):
        tk.Label(self,
                 text="No quiz questions available!\nAsk a moderator to add some.",
                 font=F_TITLE, fg=PURPLE, bg=BG).pack(expand=True)
        button(self, "Back", fg=BLUE, bg=PANEL2,
               cmd=self._back, padx=16, pady=8).pack(pady=10)

    def _build_hud(self):
        from datetime import date as _d
        top = tk.Frame(self, bg=PANEL2, pady=6)
        top.pack(fill="x")
        button(top, "Back", fg=BLUE, bg=PANEL2,
               cmd=self._back, padx=10, pady=4).pack(side="left", padx=8)
        tk.Label(top,
                 text="Eco Quiz  —  Answer correctly to earn points",
                 font=F_TITLE, fg=BLUE, bg=PANEL2).pack(side="left", expand=True)
        self._pts_lbl = tk.Label(top, text=f"Points: {self.gd.points}",
                                  font=F_BODY, fg=YELLOW, bg=PANEL2)
        self._pts_lbl.pack(side="right", padx=4)
        tk.Label(top,
                 text=f"Day {self.gd.day} / {self.gd.season_duration}  "
                      f"({_d.today().strftime('%d %b %Y')})",
                 font=F_BODY, fg=ORANGE, bg=PANEL2).pack(side="right", padx=12)

    def _show_question(self):
        if self._idx >= len(self._qs):
            self._quiz_done()
            return
        for w in self.pack_slaves():
            if hasattr(w, "_is_q"):
                w.destroy()

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=60, pady=30)
        body._is_q = True

        n = len(self._qs)
        i = self._idx
        tk.Label(body, text=f"Question {i+1} of {n}",
                 font=F_BODY, fg=DIM, bg=BG).pack()

        prog = tk.Canvas(body, bg=PANEL2, height=12,
                         highlightthickness=0, width=800)
        prog.pack(fill="x", pady=(2, 20))
        prog.update_idletasks()
        prog.create_rectangle(0, 0, int(800 * (i + 1) / n), 12,
                              fill=BLUE, outline="")

        q = self._qs[i]

        q_outer = tk.Frame(body, bg=BLUE, padx=2, pady=2)
        q_outer.pack(fill="x", pady=(0, 40))
        q_inner = tk.Frame(q_outer, bg="#0d1a30", padx=20, pady=24)
        q_inner.pack(fill="both")
        tk.Label(q_inner, text=q["question"], font=F_SUB, fg=WHITE,
                 bg="#0d1a30", wraplength=720, justify="center").pack()

        answers = [(q["correct"], True)] + [(w, False) for w in q.get("wrong", [])]
        random.shuffle(answers)

        grid = tk.Frame(body, bg=BG)
        grid.pack()
        self._ans_btns = []
        for idx2, (ans, correct) in enumerate(answers):
            b = tk.Button(
                grid, text=ans, font=F_BODY, fg=TEXT, bg=PANEL,
                relief="flat", cursor="hand2", width=40, pady=16,
                wraplength=350,
                command=lambda a=ans, c=correct: self._answer(a, c))
            b.grid(row=idx2 // 2, column=idx2 % 2,
                   padx=10, pady=8, sticky="nsew")
            self._ans_btns.append((b, correct))

        self._feedback = tk.Label(body, text="", font=F_SUB, fg=GREEN, bg=BG)
        self._feedback.pack(pady=8)

    def _answer(self, ans, correct):
        for b, c in self._ans_btns:
            b.configure(state="disabled")
            if c:   b.configure(bg="#003a10", fg=GREEN)
            else:   b.configure(bg="#3a0000", fg=RED)
        if correct:
            self.gd.on_correct()
            self._feedback.configure(
                text=f"Correct!  +{self.gd.pts_per_correct} pts", fg=GREEN)
            self._pts_lbl.configure(text=f"Points: {self.gd.points}")
            SND.play("correct")
        else:
            self.gd.on_wrong()
            correct_text = [b.cget("text") for b, c in self._ans_btns if c][0]
            self._feedback.configure(
                text=f"Wrong.  Correct: {correct_text}", fg=RED)
            SND.play("wrong")
        self.after(1400, self._next)

    def _next(self):
        self._idx += 1
        self._show_question()

    def _quiz_done(self):
        # ── IMPORTANT: do NOT call advance_day() here ───────────────────────
        # Days are tracked by the real calendar in game_data.py.
        # Quiz sessions only award points and XP.
        # ─────────────────────────────────────────────────────────────────────
        self.gd.save()

        for w in self.pack_slaves():
            if hasattr(w, "_is_q"):
                w.destroy()

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)
        body._is_q = True

        tk.Label(body, text="Quiz Complete!",
                 font=F_HUGE, fg=GREEN, bg=BG).pack(pady=(60, 8))
        tk.Label(body,
                 text=f"Session: +{self.gd.session_correct} correct  |  "
                      f"Streak: {self.gd.session_streak}x",
                 font=F_BODY, fg=TEXT, bg=BG).pack()
        tk.Label(body, text=f"Points this season: {self.gd.points}",
                 font=F_TITLE, fg=YELLOW, bg=BG).pack(pady=8)
        tk.Label(body,
                 text=f"Day {self.gd.day} / {self.gd.season_duration}   "
                      f"Pollution: {self.gd.pollution:.1f}%",
                 font=F_BODY, fg=ORANGE, bg=BG).pack()

        from datetime import date as _d
        tk.Label(body,
                 text=f"Season started: {self.gd.season_start_date}   "
                      f"Today: {_d.today().isoformat()}",
                 font=F_SMALL, fg=DIM, bg=BG).pack()

        # ── DEFINITIVE SEASON END CONDITIONS ───────────────────────────────
        # WIN:  player reduced pollution below the goal
        # LOSE: calendar days exceeded season length
        # NEVER: "pollution >= 100" — that is always the starting value!
        won     = self.gd.is_season_won()   # pollution < goal_pollution
        days_up = self.gd.is_season_lost()  # day > season_duration

        if won or days_up:
            button(body,
                   "View Season Results",
                   fg=WHITE,
                   bg="#003a10" if won else "#3a2000",
                   cmd=self.nav.go_season_end,
                   padx=18, pady=10).pack(pady=20)
        else:
            button(body,
                   "Return to City",
                   fg=WHITE, bg="#0a2a50",
                   cmd=self._back,
                   padx=18, pady=10).pack(pady=20)

    def _back(self):
        self.gd.save()
        self.nav.go_game()
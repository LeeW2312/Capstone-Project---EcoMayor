"""player/settings_screen.py — Display name, sound, volume, difficulty"""
import tkinter as tk
from tkinter import messagebox
from core.theme import *
from core.game_data import GameData
import core.sounds as SND


class SettingsScreen(tk.Frame):
    def __init__(self, master, nav, gd: GameData):
        super().__init__(master, bg=BG)
        self.nav = nav; self.gd = gd
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=PANEL2, pady=6); top.pack(fill="x")
        button(top, "Back", fg=BLUE, bg=PANEL2, cmd=self._back,
               padx=10, pady=4).pack(side="left", padx=8)
        tk.Label(top, text="Settings", font=F_TITLE,
                 fg=BLUE, bg=PANEL2).pack(side="left", expand=True)
        body = tk.Frame(self, bg=BG); body.pack(fill="both", expand=True, padx=80, pady=30)

        # Display Name
        outer, inner = card(body, BLUE, pady=10, padx=14); outer.pack(fill="x", pady=8)
        tk.Label(inner, text="Display Name", font=F_SUB, fg=BLUE, bg=PANEL).pack(anchor="w")
        tk.Label(inner, text="Changes your visible name in the game.",
                 font=F_SMALL, fg=DIM, bg=PANEL).pack(anchor="w")
        self._name_var = tk.StringVar(value=self.gd.display_name)
        tk.Entry(inner, textvariable=self._name_var, font=F_BODY,
                 bg=PANEL2, fg=YELLOW, insertbackground=YELLOW,
                 relief="flat", width=32).pack(pady=(6,0))

        # Sound
        outer, inner = card(body, GREEN, pady=10, padx=14); outer.pack(fill="x", pady=8)
        tk.Label(inner, text="Sound Effects", font=F_SUB, fg=GREEN, bg=PANEL).pack(anchor="w")
        self._sound_on = self.gd.sound
        self._sound_lbl = tk.Label(inner,
            text=f"Sound is {'ON' if self._sound_on else 'OFF'}",
            font=F_BODY, fg=DIM, bg=PANEL)
        self._sound_lbl.pack(anchor="w")
        self._sound_btn = button(inner,
            f"Sound: {'ON' if self._sound_on else 'OFF'}",
            fg=WHITE, bg=GREEN if self._sound_on else RED,
            cmd=self._toggle_sound, padx=16, pady=6)
        self._sound_btn.pack(anchor="w", pady=6)

        # Volume
        outer, inner = card(body, BLUE, pady=10, padx=14); outer.pack(fill="x", pady=8)
        tk.Label(inner, text="Volume", font=F_SUB, fg=BLUE, bg=PANEL).pack(anchor="w")
        vol_row = tk.Frame(inner, bg=PANEL); vol_row.pack(pady=6)
        self._vol_var = tk.IntVar(value=self.gd.volume)
        for pct in [0, 25, 50, 75, 100]:
            sel = self.gd.volume == pct
            button(vol_row, f"{pct}%",
                   fg=WHITE if sel else TEXT,
                   bg=BLUE if sel else PANEL2,
                   padx=10, pady=5,
                   cmd=lambda v=pct: self._set_vol(v)).pack(side="left", padx=4)

        # Difficulty
        outer, inner = card(body, YELLOW, pady=10, padx=14); outer.pack(fill="x", pady=8)
        tk.Label(inner, text="Difficulty", font=F_SUB, fg=YELLOW, bg=PANEL).pack(anchor="w")
        tk.Label(inner, text="Affects pollution rise speed and upgrade costs.",
                 font=F_SMALL, fg=DIM, bg=PANEL).pack(anchor="w")
        diff_row = tk.Frame(inner, bg=PANEL); diff_row.pack(pady=6)
        self._diff_var = tk.StringVar(value=self.gd.difficulty)
        desc = {"easy":   "Easier pollution rise, cheaper upgrades",
                "medium": "Balanced for most players",
                "hard":   "Faster pollution, more expensive upgrades"}
        self._diff_desc = tk.Label(inner, text=desc.get(self.gd.difficulty,""),
                                    font=F_SMALL, fg=TEXT, bg=PANEL)
        self._diff_desc.pack()
        for d in ["easy","medium","hard"]:
            sel = self.gd.difficulty == d
            button(diff_row, d.capitalize(),
                   fg="#1a1200" if sel else TEXT,
                   bg=YELLOW if sel else PANEL2,
                   padx=12, pady=6,
                   cmd=lambda d=d: self._set_diff(d)).pack(side="left", padx=4)

        button(body, "💾  Save Settings", fg=WHITE, bg="#003a10",
               cmd=self._save, padx=20, pady=10).pack(pady=12)

    def _toggle_sound(self):
        self._sound_on = not self._sound_on
        self._sound_btn.configure(text=f"Sound: {'ON' if self._sound_on else 'OFF'}",
                                   bg=GREEN if self._sound_on else RED)
        self._sound_lbl.configure(text=f"Sound is {'ON' if self._sound_on else 'OFF'}")
        SND.set_enabled(self._sound_on)

    def _set_vol(self, pct):
        self._vol_var.set(pct); SND.set_volume(pct)

    def _set_diff(self, d):
        self._diff_var.set(d)
        desc = {"easy":"Easier pollution rise, cheaper upgrades",
                "medium":"Balanced for most players",
                "hard":"Faster pollution, more expensive upgrades"}
        self._diff_desc.configure(text=desc.get(d,""))

    def _save(self):
        self.gd.display_name = self._name_var.get().strip() or self.gd.username
        self.gd.sound        = self._sound_on
        self.gd.volume       = self._vol_var.get()
        self.gd.difficulty   = self._diff_var.get()
        self.gd.save()
        messagebox.showinfo("Saved","Settings saved successfully.")

    def _back(self): self.gd.save(); self.nav.go_game()
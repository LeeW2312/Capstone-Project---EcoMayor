"""player/shop_screen.py — Upgrade shop with difficulty cost multiplier"""
import tkinter as tk
from core.theme import *
from core.game_data import GameData
import core.database as DB
import core.sounds as SND


class ShopScreen(tk.Frame):
    def __init__(self, master, nav, gd: GameData):
        super().__init__(master, bg=BG)
        self.nav = nav; self.gd = gd
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=PANEL2, pady=6); top.pack(fill="x")
        button(top, "Back", fg=BLUE, bg=PANEL2, cmd=self._back,
               padx=10, pady=4).pack(side="left", padx=8)
        tk.Label(top, text="Upgrade Shop", font=F_TITLE,
                 fg=GREEN, bg=PANEL2).pack(side="left", expand=True)
        self._pts_lbl = tk.Label(top, text=f"Points: {self.gd.points}",
                                  font=F_BODY, fg=YELLOW, bg=PANEL2)
        self._pts_lbl.pack(side="right", padx=6)
        tk.Label(top, text=f"Bought: {len(self.gd.upgrades_bought)}",
                 font=F_BODY, fg=GREEN, bg=PANEL2).pack(side="right", padx=6)

        info = tk.Frame(self, bg=BG, pady=6); info.pack(fill="x", padx=20)
        tk.Label(info, text=f"Difficulty: {self.gd.difficulty.capitalize()}  "
                            f"(cost ×{self.gd.cost_multiplier:.2f})",
                 font=F_BODY, fg=YELLOW, bg=BG).pack()
        self._poll_lbl = tk.Label(info, text=f"Pollution: {self.gd.pollution:.1f}%",
                                   font=F_SUB, fg=RED, bg=BG)
        self._poll_lbl.pack()
        self._bar_canvas = tk.Canvas(info, bg=PANEL2, height=18,
                                      highlightthickness=0, width=700)
        self._bar_canvas.pack()
        self._draw_bar()

        self._grid_frame = tk.Frame(self, bg=BG)
        self._grid_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self._draw_cards()

    def _draw_bar(self):
        c = self._bar_canvas; c.delete("all")
        pct = max(0, min(100, self.gd.pollution)) / 100
        col = RED if pct > .5 else ORANGE if pct > .3 else GREEN
        c.create_rectangle(0, 0, 700, 18, fill=PANEL, outline="")
        c.create_rectangle(0, 0, int(700*pct), 18, fill=col, outline="")
        goal_x = int(700 * self.gd.goal_pollution / 100)
        c.create_line(goal_x, 0, goal_x, 18, fill=YELLOW, width=2)

    def _draw_cards(self):
        for w in self._grid_frame.winfo_children(): w.destroy()
        upgrades = DB.get_upgrades()
        if not upgrades:
            tk.Label(self._grid_frame,
                     text="No upgrades available. Ask a moderator to add some!",
                     font=F_BODY, fg=PURPLE, bg=BG).pack(expand=True)
            return
        for i, upg in enumerate(upgrades):
            col     = i % 2; row = i // 2
            cost    = self.gd.effective_cost(upg["cost"])
            already = upg["name"] in self.gd.upgrades_bought
            can_buy = self.gd.points >= cost and not already
            border  = GREEN if already else (BLUE if can_buy else PANEL2)
            outer   = tk.Frame(self._grid_frame, bg=border, padx=2, pady=2)
            outer.grid(row=row, column=col, padx=10, pady=8, sticky="nsew")
            inner   = tk.Frame(outer, bg=PANEL, padx=16, pady=14, width=440)
            inner.pack(fill="both")
            tk.Label(inner, text=upg["name"], font=F_SUB, fg=WHITE, bg=PANEL).pack(anchor="w")
            tk.Label(inner, text=f"Reduces pollution by {upg['pollution_reduction']:.1f}%",
                     font=F_BODY, fg=GREEN, bg=PANEL).pack(anchor="w")
            tk.Label(inner, text=f"Cost: {cost} pts",
                     font=F_BODY, fg=YELLOW, bg=PANEL).pack(anchor="w")
            if already:
                tk.Label(inner, text="✓ Already purchased",
                         font=F_BODY, fg=GREEN, bg=PANEL).pack(anchor="w")
            elif not can_buy:
                tk.Label(inner, text=f"Need {cost - self.gd.points} more points",
                         font=F_SMALL, fg=RED, bg=PANEL).pack(anchor="w")
            tk.Button(inner, text="Buy", font=F_BODY,
                      fg=GREEN if can_buy else DIM,
                      bg="#003a10" if can_buy else PANEL2,
                      relief="flat", cursor="hand2" if can_buy else "arrow",
                      state="normal" if can_buy else "disabled",
                      command=lambda u=upg: self._buy(u)).pack(anchor="e", pady=(8,0))
        self._grid_frame.columnconfigure(0, weight=1)
        self._grid_frame.columnconfigure(1, weight=1)

    def _buy(self, upg):
        if self.gd.buy_upgrade(upg):
            SND.play("upgrade")
            self._pts_lbl.configure(text=f"Points: {self.gd.points}")
            self._poll_lbl.configure(text=f"Pollution: {self.gd.pollution:.1f}%")
            self._draw_bar(); self._draw_cards(); self.gd.save()

    def _back(self): self.gd.save(); self.nav.go_game()
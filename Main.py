"""
Main.py — EcoCity Mayor entry point & navigation controller
Run: python Main.py
"""
import tkinter as tk
import sys, os

sys.path.insert(0, os.path.dirname(__file__))

import core.database as DB
from core.game_data import GameData
from core.theme import BG


class App:
    W, H = 1140, 720

    def __init__(self):
        DB.init()
        self.root = tk.Tk()
        self.root.title("EcoCity Mayor")
        self.root.geometry(f"{self.W}x{self.H}")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self._current  = None
        self.game_data = None
        self._go(self._make_login)
        self.root.mainloop()

    def _go(self, factory):
        # destroy ALL children first — prevents ghost/double frames
        for w in list(self.root.winfo_children()):
            try:
                w.destroy()
            except Exception:
                pass
        self._current = None
        self._current = factory()

    def after_login(self, user_dict: dict):
        self.game_data = GameData(user_dict)
        role = user_dict.get("role", "player")
        if role == "admin":
            self.go_admin()
        elif role == "moderator":
            self.go_moderator()
        else:
            self.go_game()

    def go_game(self):       self._go(self._make_game)
    def go_quiz(self):       self._go(self._make_quiz)
    def go_shop(self):       self._go(self._make_shop)
    def go_profile(self):    self._go(self._make_profile)
    def go_settings(self):   self._go(self._make_settings)
    def go_season_end(self): self._go(self._make_season_end)
    def go_admin(self):      self._go(self._make_admin)
    def go_moderator(self):  self._go(self._make_mod)

    def logout(self):
        self.game_data = None
        self._go(self._make_login)

    def _make_login(self):
        from screens.login_screen import LoginScreen
        return LoginScreen(self.root, nav=self)

    def _make_game(self):
        from player.game_screen import GameScreen
        return GameScreen(self.root, nav=self, gd=self.game_data)

    def _make_quiz(self):
        from player.quiz_screen import QuizScreen
        return QuizScreen(self.root, nav=self, gd=self.game_data)

    def _make_shop(self):
        from player.shop_screen import ShopScreen
        return ShopScreen(self.root, nav=self, gd=self.game_data)

    def _make_profile(self):
        from player.profile_screen import ProfileScreen
        return ProfileScreen(self.root, nav=self, gd=self.game_data)

    def _make_settings(self):
        from player.settings_screen import SettingsScreen
        return SettingsScreen(self.root, nav=self, gd=self.game_data)

    def _make_season_end(self):
        from player.season_end_screen import SeasonEndScreen
        return SeasonEndScreen(self.root, nav=self, gd=self.game_data)

    def _make_admin(self):
        from admin.admin_panel import AdminPanel
        user = DB.get_user(self.game_data.username) or {}
        return AdminPanel(self.root, nav=self, user=user)

    def _make_mod(self):
        from moderator.mod_panel import ModPanel
        user = DB.get_user(self.game_data.username) or {}
        return ModPanel(self.root, nav=self, user=user)


if __name__ == "__main__":
    App()
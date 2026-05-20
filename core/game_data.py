"""
core/game_data.py
Day counter is driven by the real-world calendar.
One calendar day = one in-game day.
Pollution rises automatically for every real day the player was away.
"""
from datetime import date as _date
from core.database import (get_settings, update_user, log,
                            add_leaderboard_entry)

# ── XP level table ─────────────────────────────────────────────────────────────
LEVELS = [
    (1,    0,   "Eco Newcomer"),
    (2,  100,   "Eco Learner"),
    (3,  250,   "Green Citizen"),
    (4,  450,   "Eco Activist"),
    (5,  700,   "Eco Warrior"),
    (6, 1000,   "Green Champion"),
    (7, 1400,   "Eco Guardian"),
    (8, 1900,   "Green Defender"),
    (9, 2500,   "Eco Hero"),
    (10, 3200,  "Eco Master"),
]

def xp_to_level(xp):
    lvl, title, nxt = LEVELS[0][0], LEVELS[0][2], LEVELS[1][1]
    for i, (l, req, t) in enumerate(LEVELS):
        if xp >= req:
            lvl = l; title = t
            nxt = LEVELS[i+1][1] if i+1 < len(LEVELS) else req
    return lvl, title, nxt

# ── 32 achievements ────────────────────────────────────────────────────────────
ACHIEVEMENTS = [
    {"id":"first_step",      "name":"First Step",       "desc":"Answer your first quiz question correctly"},
    {"id":"eco_student",     "name":"Eco Student",       "desc":"Answer 5 questions correctly in one session"},
    {"id":"eco_scholar",     "name":"Eco Scholar",       "desc":"Answer 20 questions correctly in one session"},
    {"id":"on_a_roll",       "name":"On a Roll",         "desc":"Get a 3x correct answer streak"},
    {"id":"quiz_master",     "name":"Quiz Master",       "desc":"Get a 5x correct answer streak"},
    {"id":"unstoppable",     "name":"Unstoppable",       "desc":"Get a 10x correct answer streak"},
    {"id":"perfect_day",     "name":"Perfect Day",       "desc":"Answer 10 questions without a wrong answer"},
    {"id":"knowledge_seeker","name":"Knowledge Seeker",  "desc":"Answer 50 questions correctly (all time)"},
    {"id":"first_breath",    "name":"First Breath",      "desc":"Reduce pollution for the first time"},
    {"id":"small_progress",  "name":"Small Progress",    "desc":"Reduce pollution below 80%"},
    {"id":"green_mayor",     "name":"Green Mayor",       "desc":"Reduce pollution below 70%"},
    {"id":"clean_city",      "name":"Clean City",        "desc":"Reduce pollution below 50%"},
    {"id":"eco_paradise",    "name":"Eco Paradise",      "desc":"Reduce pollution below 30%"},
    {"id":"zero_hero",       "name":"Zero Hero",         "desc":"Reduce pollution below 10%"},
    {"id":"pollution_fighter","name":"Pollution Fighter","desc":"Reduce pollution by 30% in one season"},
    {"id":"comeback_kid",    "name":"Comeback Kid",      "desc":"Win after pollution reached 90%"},
    {"id":"getting_started", "name":"Getting Started",   "desc":"Earn your first 30 points"},
    {"id":"point_collector", "name":"Point Collector",   "desc":"Earn 100 points in a session"},
    {"id":"point_hoarder",   "name":"Point Hoarder",     "desc":"Earn 500 points in a season"},
    {"id":"upgrade_buyer",   "name":"Upgrade Buyer",     "desc":"Buy your first upgrade"},
    {"id":"green_investor",  "name":"Green Investor",    "desc":"Buy 3 upgrades in a season"},
    {"id":"eco_builder",     "name":"Eco Builder",       "desc":"Buy 5 upgrades in a season"},
    {"id":"season_starter",  "name":"Season Starter",    "desc":"Complete your first season"},
    {"id":"season_winner",   "name":"Season Winner",     "desc":"Win your first season"},
    {"id":"eco_champion",    "name":"Eco Champion",      "desc":"Win 3 seasons total"},
    {"id":"eco_legend",      "name":"Eco Legend",        "desc":"Win 5 seasons total"},
    {"id":"hard_winner",     "name":"Eco Master",        "desc":"Win a season on Hard difficulty"},
    {"id":"quick_start",     "name":"Quick Start",       "desc":"Answer a quiz on Day 1"},
    {"id":"dedicated",       "name":"Dedicated",         "desc":"Survive 10 days in a season"},
    {"id":"halfway_there",   "name":"Halfway There",     "desc":"Reach Day 15 of a season"},
    {"id":"marathon_runner", "name":"Marathon Runner",   "desc":"Survive all 30 days of a season"},
    {"id":"rising_star",     "name":"Rising Star",       "desc":"Reach Player Level 5"},
]


class GameData:
    """
    Real-time calendar day tracking:
      season_start_date  — date the current season began
      last_active_date   — last date the player was seen
      self.day           — (today - season_start).days + 1   (NO CAP)

    Season ends:
      WIN  → pollution drops below goal at any point
      LOSE → day counter exceeds season_duration (real calendar days ran out)

    Quiz sessions give points/XP only. They do NOT advance the day counter.
    """

    def __init__(self, user_dict: dict):
        u         = user_dict
        today_str = _date.today().isoformat()

        # ── Basic fields ───────────────────────────────────────────────────────
        self.username        = u["username"]
        self.role            = u.get("role",          "player")
        self.display_name    = u.get("display_name",  u["username"])
        self.status          = u.get("status",        "active")
        self.pollution       = float(u.get("pollution",  100.0))
        self.points          = int(u.get("points",    0))
        self.difficulty      = u.get("difficulty",    "medium")
        self.upgrades_bought = list(u.get("upgrades_bought", []))
        self.xp              = int(u.get("xp",        0))
        self.level, self.level_title, self._xp_next = xp_to_level(self.xp)
        self.seasons_played  = int(u.get("seasons_played",  0))
        self.seasons_won     = int(u.get("seasons_won",      0))
        self.best_score      = int(u.get("best_score",       0))
        self.total_correct   = int(u.get("total_correct",    0))
        self.achievements    = dict(u.get("achievements",    {}))
        self.pollution_history = list(u.get("pollution_history", [100.0]))
        self.warnings        = int(u.get("warnings",  0))
        self.sound           = bool(u.get("sound",    True))
        self.volume          = int(u.get("volume",    75))

        # ── Season/difficulty settings ─────────────────────────────────────────
        s = get_settings()
        self.season_duration  = int(s.get("season_duration",  30))
        self.goal_pollution   = float(s.get("goal_pollution",  50))
        rise_map = {"easy": s.get("rise_easy", 0.5),
                    "medium": s.get("rise_medium", 1.0),
                    "hard":   s.get("rise_hard",   2.0)}
        mult_map = {"easy": s.get("mult_easy",   0.75),
                    "medium": s.get("mult_medium", 1.00),
                    "hard":   s.get("mult_hard",   1.50)}
        self.pollution_rise   = float(rise_map.get(self.difficulty, 1.0))
        self.cost_multiplier  = float(mult_map.get(self.difficulty, 1.0))
        self.pts_per_correct  = int(s.get("pts_per_correct",  20))
        self.quiz_per_session = int(s.get("quiz_per_session",  5))
        self.bonus_win        = int(s.get("bonus_win",        100))

        # ── Real-time calendar day tracking ────────────────────────────────────
        raw_start = u.get("season_start_date", "")
        raw_last  = u.get("last_active_date",  "")

        # Initialise dates — default to today if not set
        self.season_start_date = raw_start if raw_start else today_str
        self.last_active_date  = raw_last  if raw_last  else today_str

        today_date = _date.today()
        try:
            start_date = _date.fromisoformat(self.season_start_date)
        except (ValueError, TypeError):
            start_date = today_date
            self.season_start_date = today_str

        try:
            last_date = _date.fromisoformat(self.last_active_date)
        except (ValueError, TypeError):
            last_date = today_date
            self.last_active_date = today_str

        # ── KEY FIX: do NOT cap day at season_duration ─────────────────────────
        # Capping at 30 meant "day > 30" could never be True → season never ended
        # Correct: let day exceed season_duration so the lose condition fires
        days_elapsed = max(0, (today_date - start_date).days)
        self.day = days_elapsed + 1          # Day 1 on start date, Day 31 = season over

        # Apply pollution rise for every real day the player was away
        days_away = max(0, (today_date - last_date).days)
        if days_away > 0:
            total_rise     = days_away * self.pollution_rise
            self.pollution = min(100.0, self.pollution + total_rise)
            for _ in range(days_away):
                self.pollution_history.append(round(self.pollution, 1))
            self._check_day_achievements_silent()

        # Update last-seen to today
        self.last_active_date = today_str

        # ── Session-only trackers (never persisted) ────────────────────────────
        self.session_correct   = 0
        self.session_wrong     = 0
        self.session_streak    = 0
        self.session_upgrades  = 0
        self.session_pts       = 0
        self.peaked_90         = self.pollution >= 90
        self.pollution_start   = self.pollution
        self._new_achievements = []

    # ── Computed ──────────────────────────────────────────────────────────────

    @property
    def xp_for_next(self): return self._xp_next

    def effective_cost(self, base_cost):
        return int(base_cost * self.cost_multiplier)

    # ── Season end check (used by UI) ─────────────────────────────────────────

    def is_season_won(self)  -> bool:
        """Player won: pollution genuinely below goal."""
        return self.pollution < self.goal_pollution

    def is_season_lost(self) -> bool:
        """Player lost: real calendar days exceeded season length."""
        return self.day > self.season_duration

    def is_season_over(self) -> bool:
        return self.is_season_won() or self.is_season_lost()

    # ── Quiz outcome ──────────────────────────────────────────────────────────

    def on_correct(self):
        pts = self.pts_per_correct
        self.points          += pts
        self.session_pts     += pts
        self.total_correct   += 1
        self.session_correct += 1
        self.session_streak  += 1
        self.xp              += 30
        self.level, self.level_title, self._xp_next = xp_to_level(self.xp)
        self._check_quiz_achievements()
        log(self.username, "QUIZ", f"Correct +{pts}pts")

    def on_wrong(self):
        self.session_wrong  += 1
        self.session_streak  = 0

    # ── Upgrade purchase ──────────────────────────────────────────────────────

    def buy_upgrade(self, upgrade: dict) -> bool:
        cost = self.effective_cost(upgrade["cost"])
        if self.points < cost:
            return False
        self.points           -= cost
        self.pollution        -= upgrade["pollution_reduction"]
        self.pollution         = max(0.0, self.pollution)
        self.upgrades_bought.append(upgrade["name"])
        self.session_upgrades += 1
        self.pollution_history.append(round(self.pollution, 1))
        self._check_upgrade_achievements()
        self._check_pollution_achievements()
        log(self.username, "UPGRADE",
            f"Bought {upgrade['name']} -{upgrade['pollution_reduction']}%")
        return True

    # ── Season end ────────────────────────────────────────────────────────────

    def end_season(self) -> dict:
        won = self.is_season_won()
        if won:
            self.points      += self.bonus_win
            self.seasons_won += 1
        self.seasons_played += 1
        if self.points > self.best_score:
            self.best_score = self.points
        self._check_season_achievements(won)

        entry = {
            "username":  self.username,
            "points":    self.points,
            "pollution": round(self.pollution, 1),
            "day":       self.day,
            "result":    "Win" if won else "Lose",
            "date":      _date.today().isoformat(),
        }
        add_leaderboard_entry(entry)
        log(self.username, "SEASON_END",
            f"{'WIN' if won else 'LOSE'} | "
            f"{self.pollution:.1f}% | {self.points}pts | Day {self.day}")

        # Reset for new season — starts TODAY
        today_str              = _date.today().isoformat()
        self.pollution         = 100.0
        self.points            = 0
        self.day               = 1
        self.upgrades_bought   = []
        self.pollution_history = [100.0]
        self.season_start_date = today_str
        self.last_active_date  = today_str
        self.session_correct   = 0
        self.session_wrong     = 0
        self.session_streak    = 0
        self.session_upgrades  = 0
        self.session_pts       = 0
        self.peaked_90         = False
        self.pollution_start   = 100.0

        self.save()
        return {**entry, "won": won}

    # ── Achievement engine ────────────────────────────────────────────────────

    def _unlock(self, aid):
        if aid not in self.achievements:
            self.achievements[aid] = True
            a = next((x for x in ACHIEVEMENTS if x["id"] == aid), None)
            if a:
                self._new_achievements.append(a["name"])

    def _check_quiz_achievements(self):
        if self.total_correct >= 1:    self._unlock("first_step")
        if self.session_correct >= 5:  self._unlock("eco_student")
        if self.session_correct >= 20: self._unlock("eco_scholar")
        if self.session_streak  >= 3:  self._unlock("on_a_roll")
        if self.session_streak  >= 5:  self._unlock("quiz_master")
        if self.session_streak  >= 10: self._unlock("unstoppable")
        if (self.session_correct >= 10
                and self.session_wrong == 0):   self._unlock("perfect_day")
        if self.total_correct   >= 50: self._unlock("knowledge_seeker")
        if self.session_pts     >= 100:self._unlock("point_collector")
        if self.points          >= 30: self._unlock("getting_started")
        if self.points          >= 500:self._unlock("point_hoarder")
        if self.day == 1:              self._unlock("quick_start")

    def _check_upgrade_achievements(self):
        self._unlock("first_breath")
        self._unlock("upgrade_buyer")
        if self.session_upgrades >= 3: self._unlock("green_investor")
        if self.session_upgrades >= 5: self._unlock("eco_builder")

    def _check_pollution_achievements(self):
        p = self.pollution
        if p < 80: self._unlock("small_progress")
        if p < 70: self._unlock("green_mayor")
        if p < 50: self._unlock("clean_city")
        if p < 30: self._unlock("eco_paradise")
        if p < 10: self._unlock("zero_hero")
        if self.pollution_start - p >= 30:
            self._unlock("pollution_fighter")

    def _check_day_achievements_silent(self):
        """Called on login to handle days-away achievements without toasts."""
        if self.day >= 10: self._achievements.get("dedicated") or self._unlock("dedicated")
        if self.day >= 15: self._unlock("halfway_there")
        if self.day >= 30: self._unlock("marathon_runner")
        if self.level >= 5:self._unlock("rising_star")

    def _check_day_achievements(self):
        if self.day >= 10: self._unlock("dedicated")
        if self.day >= 15: self._unlock("halfway_there")
        if self.day >= 30: self._unlock("marathon_runner")
        if self.level >= 5:self._unlock("rising_star")

    def _check_season_achievements(self, won):
        self._unlock("season_starter")
        if won:
            self._unlock("season_winner")
            if self.seasons_won >= 3:     self._unlock("eco_champion")
            if self.seasons_won >= 5:     self._unlock("eco_legend")
            if self.difficulty == "hard": self._unlock("hard_winner")
            if self.peaked_90:            self._unlock("comeback_kid")

    def pop_new_achievements(self):
        result = list(self._new_achievements)
        self._new_achievements.clear()
        return result

    # ── Persistence ───────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        from core.database import get_user as _gu
        existing = _gu(self.username) or {}
        return {
            "username":          self.username,
            "role":              self.role,
            "display_name":      self.display_name,
            "status":            self.status,
            "password":          existing.get("password", ""),
            "pollution":         round(self.pollution, 1),
            "points":            self.points,
            "day":               self.day,
            "difficulty":        self.difficulty,
            "xp":                self.xp,
            "level":             self.level,
            "level_title":       self.level_title,
            "seasons_played":    self.seasons_played,
            "seasons_won":       self.seasons_won,
            "best_score":        self.best_score,
            "total_correct":     self.total_correct,
            "achievements":      self.achievements,
            "pollution_history": self.pollution_history[-60:],
            "upgrades_bought":   self.upgrades_bought,
            "warnings":          self.warnings,
            "sound":             self.sound,
            "volume":            self.volume,
            "season_start_date": self.season_start_date,
            "last_active_date":  self.last_active_date,
        }

    def save(self):
        from core.database import get_user
        u = get_user(self.username) or {}
        update_user({**u, **self.to_dict()})
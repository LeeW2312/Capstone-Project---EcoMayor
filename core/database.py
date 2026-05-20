"""
core/database.py
Primary storage: SQLite (data/ecocity.db)
Backup:          JSON files in data/
"""
import json, os, hashlib, sqlite3
from datetime import datetime

_BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_DB   = os.path.join(_BASE, "ecocity.db")

# ── helpers ───────────────────────────────────────────────────────────────────

def _conn():
    c = sqlite3.connect(_DB)
    c.row_factory = sqlite3.Row
    return c

def _hash(pw): return hashlib.sha256(pw.encode()).hexdigest()

def _jpath(name): return os.path.join(_BASE, name)

def _jload(name, default):
    try:
        with open(_jpath(name)) as f: return json.load(f)
    except Exception: return default

def _jsave(name, data):
    os.makedirs(_BASE, exist_ok=True)
    with open(_jpath(name), "w") as f: json.dump(data, f, indent=2)

# ── default seed data ─────────────────────────────────────────────────────────

_DEFAULT_USERS = [
    {"username":"admin1","password":_hash("1234"),"role":"admin","status":"active",
     "seasons_played":0,"seasons_won":0,"best_score":0,"pollution":100.0,"points":0,
     "day":1,"difficulty":"medium","xp":0,"level":1,"level_title":"Eco Newcomer",
     "total_correct":0,"achievements":{},"pollution_history":[100.0],
     "upgrades_bought":[],"warnings":0,"display_name":"admin1","sound":True,"volume":75,
     "season_start_date":"","last_active_date":""},
    {"username":"mod1","password":_hash("1234"),"role":"moderator","status":"active",
     "seasons_played":0,"seasons_won":0,"best_score":0,"pollution":100.0,"points":0,
     "day":1,"difficulty":"medium","xp":0,"level":1,"level_title":"Eco Newcomer",
     "total_correct":0,"achievements":{},"pollution_history":[100.0],
     "upgrades_bought":[],"warnings":0,"display_name":"mod1","sound":True,"volume":75,
     "season_start_date":"","last_active_date":""},
    {"username":"player1","password":_hash("1234"),"role":"player","status":"active",
     "seasons_played":0,"seasons_won":0,"best_score":0,"pollution":100.0,"points":0,
     "day":1,"difficulty":"medium","xp":0,"level":1,"level_title":"Eco Newcomer",
     "total_correct":0,"achievements":{},"pollution_history":[100.0],
     "upgrades_bought":[],"warnings":0,"display_name":"player1","sound":True,"volume":75,
     "season_start_date":"","last_active_date":""},
]

_DEFAULT_QUIZZES = [
    {"question":"What is the main cause of air pollution in cities?",
     "correct":"Factories and vehicles","wrong":["Rainfall","Trees","Sunlight"]},
    {"question":"Which action helps reduce water pollution?",
     "correct":"Proper waste disposal",
     "wrong":["Burning fossil fuels","Using more plastic","Littering"]},
    {"question":"What does planting trees help reduce?",
     "correct":"Air pollution","wrong":["Water levels","Sunlight","Wind speed"]},
    {"question":"Which energy source is most eco-friendly?",
     "correct":"Solar power","wrong":["Coal","Natural gas","Oil"]},
    {"question":"What is the greenhouse effect?",
     "correct":"Trapping of heat in Earth's atmosphere",
     "wrong":["Growing plants in a glass house","Cooling of the oceans","Blocking sunlight"]},
]

_DEFAULT_UPGRADES = [
    {"name":"Plant Trees",            "pollution_reduction":5.0,  "cost":50},
    {"name":"Install Solar Panels",   "pollution_reduction":10.0, "cost":120},
    {"name":"Build Recycling Center", "pollution_reduction":8.0,  "cost":90},
    {"name":"Clean River",            "pollution_reduction":6.0,  "cost":70},
    {"name":"Wind Turbines",          "pollution_reduction":12.0, "cost":150},
]

_DEFAULT_SETTINGS = {
    "season_duration":30,"starting_pollution":100,"goal_pollution":50,
    "rise_easy":0.5,"rise_medium":1.0,"rise_hard":2.0,
    "mult_easy":0.75,"mult_medium":1.00,"mult_hard":1.50,
    "bonus_win":100,"pts_per_correct":20,"quiz_per_session":5,
}

# ── initialise ────────────────────────────────────────────────────────────────

def init():
    """Create SQLite DB + tables, seed default data, migrate old JSON."""
    os.makedirs(_BASE, exist_ok=True)

    with _conn() as db:
        db.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                data     TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS quizzes (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT    UNIQUE NOT NULL,
                correct  TEXT    NOT NULL,
                wrong    TEXT    NOT NULL
            );
            CREATE TABLE IF NOT EXISTS upgrades (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                name                TEXT    UNIQUE NOT NULL,
                pollution_reduction REAL    NOT NULL,
                cost                INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS leaderboard (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                username  TEXT    NOT NULL,
                points    INTEGER NOT NULL,
                pollution REAL    NOT NULL,
                day       INTEGER NOT NULL,
                result    TEXT    NOT NULL,
                date      TEXT    NOT NULL
            );
            CREATE TABLE IF NOT EXISTS activity_log (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                ts       TEXT    NOT NULL,
                username TEXT    NOT NULL,
                action   TEXT    NOT NULL,
                detail   TEXT    DEFAULT ""
            );
            CREATE TABLE IF NOT EXISTS reports (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT    NOT NULL
            );
            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
        ''')

    # Seed if empty
    if not get_users():
        # Try migrating old JSON first
        old_users = _jload("users.json", [])
        if old_users:
            for u in old_users:
                update_user(u)
        else:
            for u in _DEFAULT_USERS:
                update_user(u)

    if not get_quizzes():
        old_q = _jload("quizzes.json", [])
        if old_q:
            for q in old_q:
                add_quiz(q["question"], q["correct"], q.get("wrong", []))
        else:
            for q in _DEFAULT_QUIZZES:
                add_quiz(q["question"], q["correct"], q["wrong"])

    if not get_upgrades():
        old_u = _jload("upgrades.json", [])
        if old_u:
            for u in old_u:
                add_upgrade(u["name"],
                            u.get("pollution_reduction", u.get("effect", 0)),
                            u.get("cost", u.get("point_cost", 0)))
        else:
            for u in _DEFAULT_UPGRADES:
                add_upgrade(u["name"], u["pollution_reduction"], u["cost"])

    s = get_settings()
    for k, v in _DEFAULT_SETTINGS.items():
        if k not in s:
            with _conn() as db:
                db.execute("INSERT OR IGNORE INTO settings VALUES (?,?)",
                           (k, str(v)))

    # Migrate leaderboard
    old_lb = _jload("leaderboard.json", [])
    if old_lb and not get_leaderboard():
        for e in old_lb:
            add_leaderboard_entry(e)

    # Migrate reports
    old_r = _jload("reports.json", [])
    if old_r and not get_reports():
        for r in old_r:
            add_report(r)

    # Migrate activity log
    old_log = _jload("activity_log.json", [])
    if old_log:
        with _conn() as db:
            count = db.execute("SELECT COUNT(*) FROM activity_log").fetchone()[0]
            if count == 0:
                for l in old_log:
                    db.execute(
                        "INSERT INTO activity_log (ts,username,action,detail) VALUES (?,?,?,?)",
                        (l.get("ts",""), l.get("username",""),
                         l.get("action",""), l.get("detail","")))

# ── Users ─────────────────────────────────────────────────────────────────────

def get_users():
    with _conn() as db:
        rows = db.execute("SELECT data FROM users").fetchall()
    users = [json.loads(r["data"]) for r in rows]
    # backup JSON
    _jsave("users.json", users)
    return users

def save_users(users):
    with _conn() as db:
        for u in users:
            db.execute("INSERT OR REPLACE INTO users (username,data) VALUES (?,?)",
                       (u["username"], json.dumps(u)))
    _jsave("users.json", users)

def get_user(username):
    with _conn() as db:
        row = db.execute("SELECT data FROM users WHERE username=?",
                         (username,)).fetchone()
    return json.loads(row["data"]) if row else None

def update_user(user_dict):
    with _conn() as db:
        db.execute("INSERT OR REPLACE INTO users (username,data) VALUES (?,?)",
                   (user_dict["username"], json.dumps(user_dict)))
    # keep JSON backup in sync
    users = get_users()
    _jsave("users.json", users)

def login(username, password):
    u = get_user(username)
    if u and u["password"] == _hash(password): return u
    return None

def register(username, password, role="player"):
    if get_user(username):    return False, "Username already taken."
    if len(username) < 3:     return False, "Username must be at least 3 characters."
    if len(password) < 4:     return False, "Password must be at least 4 characters."
    new = {**_DEFAULT_USERS[2], "username": username,
           "password": _hash(password), "role": role, "display_name": username,
           "season_start_date": "", "last_active_date": ""}
    update_user(new)
    return True, "Registered successfully."

# ── Quizzes ───────────────────────────────────────────────────────────────────

def get_quizzes():
    with _conn() as db:
        rows = db.execute("SELECT question,correct,wrong FROM quizzes").fetchall()
    result = [{"question": r["question"], "correct": r["correct"],
               "wrong": json.loads(r["wrong"])} for r in rows]
    _jsave("quizzes.json", result)
    return result

def add_quiz(question, correct, wrong):
    with _conn() as db:
        existing = db.execute("SELECT id FROM quizzes WHERE LOWER(question)=LOWER(?)",
                              (question,)).fetchone()
        if existing: return False, "Duplicate question."
        db.execute("INSERT INTO quizzes (question,correct,wrong) VALUES (?,?,?)",
                   (question, correct, json.dumps(wrong)))
    _jsave("quizzes.json", get_quizzes())
    return True, "Added."

def edit_quiz(old_q, new_q, correct, wrong):
    with _conn() as db:
        db.execute("UPDATE quizzes SET question=?,correct=?,wrong=? WHERE question=?",
                   (new_q, correct, json.dumps(wrong), old_q))
    _jsave("quizzes.json", get_quizzes())

def delete_quiz(question):
    with _conn() as db:
        db.execute("DELETE FROM quizzes WHERE question=?", (question,))
    _jsave("quizzes.json", get_quizzes())

# ── Upgrades ──────────────────────────────────────────────────────────────────

def get_upgrades():
    with _conn() as db:
        rows = db.execute(
            "SELECT name,pollution_reduction,cost FROM upgrades").fetchall()
    result = [{"name": r["name"], "pollution_reduction": r["pollution_reduction"],
               "cost": r["cost"]} for r in rows]
    _jsave("upgrades.json", result)
    return result

def add_upgrade(name, reduction, cost):
    with _conn() as db:
        existing = db.execute("SELECT id FROM upgrades WHERE LOWER(name)=LOWER(?)",
                              (name,)).fetchone()
        if existing: return False, "Duplicate upgrade."
        db.execute("INSERT INTO upgrades (name,pollution_reduction,cost) VALUES (?,?,?)",
                   (name, float(reduction), int(cost)))
    _jsave("upgrades.json", get_upgrades())
    return True, "Added."

def edit_upgrade(old_name, new_name, reduction, cost):
    with _conn() as db:
        db.execute(
            "UPDATE upgrades SET name=?,pollution_reduction=?,cost=? WHERE name=?",
            (new_name, float(reduction), int(cost), old_name))
    _jsave("upgrades.json", get_upgrades())

def delete_upgrade(name):
    with _conn() as db:
        db.execute("DELETE FROM upgrades WHERE name=?", (name,))
    _jsave("upgrades.json", get_upgrades())

# ── Leaderboard ───────────────────────────────────────────────────────────────

def get_leaderboard():
    with _conn() as db:
        rows = db.execute(
            "SELECT username,points,pollution,day,result,date FROM leaderboard"
        ).fetchall()
    result = [dict(r) for r in rows]
    _jsave("leaderboard.json", result)
    return result

def clear_leaderboard():
    with _conn() as db:
        db.execute("DELETE FROM leaderboard")
    _jsave("leaderboard.json", [])

def add_leaderboard_entry(entry):
    with _conn() as db:
        db.execute(
            "INSERT INTO leaderboard (username,points,pollution,day,result,date)"
            " VALUES (?,?,?,?,?,?)",
            (entry.get("username",""), entry.get("points",0),
             entry.get("pollution",0), entry.get("day",0),
             entry.get("result",""), entry.get("date","")))
    _jsave("leaderboard.json", get_leaderboard())

# ── Activity Log ──────────────────────────────────────────────────────────────

def get_logs():
    with _conn() as db:
        rows = db.execute(
            "SELECT ts,username,action,detail FROM activity_log ORDER BY id"
        ).fetchall()
    return [dict(r) for r in rows]

def clear_logs():
    with _conn() as db:
        db.execute("DELETE FROM activity_log")

def log(username, action, detail=""):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _conn() as db:
        db.execute(
            "INSERT INTO activity_log (ts,username,action,detail) VALUES (?,?,?,?)",
            (ts, username, action, detail))

# ── Reports ───────────────────────────────────────────────────────────────────

def get_reports():
    with _conn() as db:
        rows = db.execute("SELECT id,data FROM reports").fetchall()
    result = [json.loads(r["data"]) for r in rows]
    _jsave("reports.json", result)
    return result

def save_reports(reports_list):
    with _conn() as db:
        db.execute("DELETE FROM reports")
        for r in reports_list:
            db.execute("INSERT INTO reports (data) VALUES (?)", (json.dumps(r),))
    _jsave("reports.json", reports_list)

def add_report(report_dict):
    with _conn() as db:
        db.execute("INSERT INTO reports (data) VALUES (?)",
                   (json.dumps(report_dict),))

# ── Settings ──────────────────────────────────────────────────────────────────

def get_settings():
    with _conn() as db:
        rows = db.execute("SELECT key,value FROM settings").fetchall()
    s = {}
    for r in rows:
        try:    s[r["key"]] = float(r["value"]) if "." in r["value"] else int(r["value"])
        except: s[r["key"]] = r["value"]
    for k, v in _DEFAULT_SETTINGS.items():
        s.setdefault(k, v)
    return s

def save_settings(settings_dict):
    with _conn() as db:
        for k, v in settings_dict.items():
            db.execute("INSERT OR REPLACE INTO settings (key,value) VALUES (?,?)",
                       (k, str(v)))
    _jsave("game_settings.json", settings_dict)

_DEFAULT_SETTINGS_REF = _DEFAULT_SETTINGS
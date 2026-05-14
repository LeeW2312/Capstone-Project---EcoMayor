"""
database.py  —  EcoCity Mayor
SQLite database layer.
Drop-in replacement for all load_json / save_json calls in main.py.

Run this file directly once to initialise (or re-initialise) the DB:
    python database.py
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH  = os.path.join("data", "ecocity.db")


def get_conn():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    c    = conn.cursor()

    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id           INTEGER PRIMARY KEY AUTOINCREMENT,
            username          TEXT    NOT NULL UNIQUE,
            password          TEXT    NOT NULL,
            role              TEXT    NOT NULL DEFAULT 'Player',
            banned            INTEGER NOT NULL DEFAULT 0,
            last_pollution    REAL    NOT NULL DEFAULT 100.0,
            xp                INTEGER NOT NULL DEFAULT 0,
            level             INTEGER NOT NULL DEFAULT 1,
            difficulty        TEXT    NOT NULL DEFAULT 'medium',
            pollution_history TEXT    NOT NULL DEFAULT '[]'
        );

        CREATE TABLE IF NOT EXISTS user_stats (
            user_id        INTEGER PRIMARY KEY
                               REFERENCES users(user_id) ON DELETE CASCADE,
            seasons_played INTEGER NOT NULL DEFAULT 0,
            best_score     INTEGER NOT NULL DEFAULT 0,
            total_points   INTEGER NOT NULL DEFAULT 0,
            total_correct  INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS quizzes (
            quiz_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_title TEXT    NOT NULL,
            created_by INTEGER REFERENCES users(user_id),
            created_at TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS questions (
            question_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id       INTEGER NOT NULL
                              REFERENCES quizzes(quiz_id) ON DELETE CASCADE,
            category      TEXT    NOT NULL DEFAULT '',
            question_text TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS answers (
            answer_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL
                            REFERENCES questions(question_id) ON DELETE CASCADE,
            answer_text TEXT    NOT NULL,
            is_correct  INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS upgrades (
            upgrade_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            upgrade_name        TEXT    NOT NULL,
            pollution_reduction REAL    NOT NULL DEFAULT 0.0,
            cost_points         INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS leaderboard (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    NOT NULL,
            points      INTEGER NOT NULL DEFAULT 0,
            pollution   REAL    NOT NULL DEFAULT 100.0,
            day         INTEGER NOT NULL DEFAULT 1,
            won         INTEGER NOT NULL DEFAULT 0,
            xp          INTEGER NOT NULL DEFAULT 0,
            recorded_at TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS activity_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT NOT NULL,
            action      TEXT NOT NULL,
            detail      TEXT NOT NULL DEFAULT '',
            recorded_at TEXT NOT NULL
        );
    """)

    conn.commit()
    _seed_default_data(conn)
    conn.close()
    print(f"[DB] Initialised → {DB_PATH}")


def _seed_default_data(conn):
    c = conn.cursor()

    defaults = [
        ("player1", "1234", "Player"),
        ("mod1",    "1234", "Moderator"),
        ("admin1",  "1234", "Admin"),
    ]
    for username, password, role in defaults:
        c.execute("SELECT 1 FROM users WHERE username=?", (username,))
        if not c.fetchone():
            c.execute(
                "INSERT INTO users (username, password, role) VALUES (?,?,?)",
                (username, password, role)
            )
            uid = c.lastrowid
            c.execute("INSERT INTO user_stats (user_id) VALUES (?)", (uid,))

    c.execute("SELECT COUNT(*) FROM upgrades")
    if c.fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO upgrades (upgrade_name, pollution_reduction, cost_points) VALUES (?,?,?)",
            [
                ("Plant Trees",            5.0,  50),
                ("Install Solar Panels",  10.0, 120),
                ("Build Recycling Center", 8.0,  90),
                ("Clean River",            6.0,  70),
                ("Wind Turbines",         12.0, 150),
            ]
        )

    c.execute("SELECT COUNT(*) FROM quizzes")
    if c.fetchone()[0] == 0:
        c.execute("SELECT user_id FROM users WHERE username='mod1'")
        row    = c.fetchone()
        mod_id = row[0] if row else None
        c.execute(
            "INSERT INTO quizzes (quiz_title, created_by, created_at) VALUES (?,?,?)",
            ("Environmental Awareness", mod_id, "2026-05-01 10:00:00")
        )
        quiz_id = c.lastrowid

        questions = [
            ("Air",       "What is the main cause of air pollution in cities?",
             [("Factories and vehicles", 1), ("Rainfall", 0), ("Trees", 0), ("Sunlight", 0)]),
            ("Water",     "Which action helps reduce water pollution?",
             [("Proper waste disposal", 1), ("Dumping waste in rivers", 0),
              ("Using more plastic bags", 0), ("Burning garbage", 0)]),
            ("Nature",    "What does planting trees help reduce?",
             [("Air pollution", 1), ("Water levels", 0),
              ("Electricity usage", 0), ("Soil minerals", 0)]),
            ("Energy",    "Which energy source is most eco-friendly?",
             [("Solar power", 1), ("Coal", 0), ("Diesel", 0), ("Natural gas", 0)]),
            ("Climate",   "What is the main greenhouse gas causing global warming?",
             [("Carbon dioxide", 1), ("Oxygen", 0), ("Nitrogen", 0), ("Hydrogen", 0)]),
            ("Recycling", "What does recycling help conserve?",
             [("Natural resources", 1), ("Electricity only", 0),
              ("Water only", 0), ("Nothing", 0)]),
        ]
        for cat, qtext, ans_list in questions:
            c.execute(
                "INSERT INTO questions (quiz_id, category, question_text) VALUES (?,?,?)",
                (quiz_id, cat, qtext)
            )
            qid = c.lastrowid
            c.executemany(
                "INSERT INTO answers (question_id, answer_text, is_correct) VALUES (?,?,?)",
                [(qid, at, ic) for at, ic in ans_list]
            )

    conn.commit()


# ── USER functions ────────────────────────────────────────────

def get_all_users():
    conn = get_conn()
    rows = conn.execute(
        """SELECT u.*, s.seasons_played, s.best_score,
                  s.total_points, s.total_correct
           FROM users u
           LEFT JOIN user_stats s ON u.user_id = s.user_id"""
    ).fetchall()
    conn.close()
    return [_user_row_to_dict(r) for r in rows]


def get_user(username):
    conn = get_conn()
    row  = conn.execute(
        """SELECT u.*, s.seasons_played, s.best_score,
                  s.total_points, s.total_correct
           FROM users u
           LEFT JOIN user_stats s ON u.user_id = s.user_id
           WHERE u.username = ?""",
        (username,)
    ).fetchone()
    conn.close()
    return _user_row_to_dict(row) if row else None


def _user_row_to_dict(row):
    d = dict(row)
    d["pollution_history"] = json.loads(d.get("pollution_history") or "[]")
    d["banned"]            = bool(d["banned"])
    d["stats"] = {
        "seasons_played": d.pop("seasons_played", 0) or 0,
        "best_score":     d.pop("best_score",     0) or 0,
        "total_points":   d.pop("total_points",   0) or 0,
        "total_correct":  d.pop("total_correct",  0) or 0,
    }
    return d


def save_user(user_dict):
    conn    = get_conn()
    c       = conn.cursor()
    history = json.dumps(user_dict.get("pollution_history", []))
    stats   = user_dict.get("stats", {})

    c.execute("SELECT user_id FROM users WHERE username=?", (user_dict["username"],))
    row = c.fetchone()

    if row:
        uid = row[0]
        c.execute(
            """UPDATE users SET password=?, role=?, banned=?,
               last_pollution=?, xp=?, level=?, difficulty=?,
               pollution_history=? WHERE user_id=?""",
            (user_dict.get("password", ""),
             user_dict.get("role", "Player"),
             int(user_dict.get("banned", False)),
             user_dict.get("last_pollution", 100.0),
             user_dict.get("xp", 0),
             user_dict.get("level", 1),
             user_dict.get("difficulty", "medium"),
             history, uid)
        )
        c.execute(
            """UPDATE user_stats SET seasons_played=?, best_score=?,
               total_points=?, total_correct=? WHERE user_id=?""",
            (stats.get("seasons_played", 0), stats.get("best_score", 0),
             stats.get("total_points", 0), stats.get("total_correct", 0), uid)
        )
    else:
        c.execute(
            """INSERT INTO users
               (username, password, role, banned, last_pollution,
                xp, level, difficulty, pollution_history)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (user_dict["username"],
             user_dict.get("password", ""),
             user_dict.get("role", "Player"),
             int(user_dict.get("banned", False)),
             user_dict.get("last_pollution", 100.0),
             user_dict.get("xp", 0),
             user_dict.get("level", 1),
             user_dict.get("difficulty", "medium"),
             history)
        )
        uid = c.lastrowid
        c.execute(
            """INSERT INTO user_stats
               (user_id, seasons_played, best_score, total_points, total_correct)
               VALUES (?,?,?,?,?)""",
            (uid, stats.get("seasons_played", 0), stats.get("best_score", 0),
             stats.get("total_points", 0), stats.get("total_correct", 0))
        )

    conn.commit()
    conn.close()


def register_user(username, password, role="Player"):
    if get_user(username):
        return None
    user_dict = {
        "username": username, "password": password, "role": role,
        "banned": False, "last_pollution": 100.0, "xp": 0, "level": 1,
        "difficulty": "medium", "pollution_history": [],
        "stats": {"seasons_played": 0, "best_score": 0,
                  "total_points": 0, "total_correct": 0}
    }
    save_user(user_dict)
    log_activity(username, "REGISTER", "New account created")
    return get_user(username)


def ban_user(username, banned=True):
    conn = get_conn()
    conn.execute("UPDATE users SET banned=? WHERE username=?", (int(banned), username))
    conn.commit()
    conn.close()
    log_activity("system", "BAN" if banned else "UNBAN", username)


def delete_user(username):
    conn = get_conn()
    conn.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    conn.close()
    log_activity("system", "DELETE_USER", username)


# ── QUIZ functions ────────────────────────────────────────────

def get_all_quizzes():
    conn    = get_conn()
    quizzes = conn.execute("SELECT * FROM quizzes").fetchall()
    result  = []
    for qz in quizzes:
        questions = conn.execute(
            "SELECT * FROM questions WHERE quiz_id=?", (qz["quiz_id"],)
        ).fetchall()
        q_list = []
        for q in questions:
            answers = conn.execute(
                "SELECT * FROM answers WHERE question_id=?", (q["question_id"],)
            ).fetchall()
            q_list.append({
                "question_id":   q["question_id"],
                "category":      q["category"],
                "question_text": q["question_text"],
                "answers": [
                    {"answer_id":   a["answer_id"],
                     "answer_text": a["answer_text"],
                     "is_correct":  bool(a["is_correct"])}
                    for a in answers
                ]
            })
        result.append({
            "quiz_id":    qz["quiz_id"],
            "quiz_title": qz["quiz_title"],
            "created_by": qz["created_by"],
            "created_at": qz["created_at"],
            "questions":  q_list,
        })
    conn.close()
    return result


def add_quiz(title, created_by_username):
    conn = get_conn()
    row  = conn.execute(
        "SELECT user_id FROM users WHERE username=?", (created_by_username,)
    ).fetchone()
    uid  = row[0] if row else None
    conn.execute(
        "INSERT INTO quizzes (quiz_title, created_by, created_at) VALUES (?,?,?)",
        (title, uid, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    quiz_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    log_activity(created_by_username, "ADD_QUIZ", title)
    return quiz_id


def add_question(quiz_id, category, question_text, answers):
    conn = get_conn()
    conn.execute(
        "INSERT INTO questions (quiz_id, category, question_text) VALUES (?,?,?)",
        (quiz_id, category, question_text)
    )
    qid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.executemany(
        "INSERT INTO answers (question_id, answer_text, is_correct) VALUES (?,?,?)",
        [(qid, at, int(ic)) for at, ic in answers]
    )
    conn.commit()
    conn.close()
    return qid


def update_question(question_id, category, question_text):
    conn = get_conn()
    conn.execute(
        "UPDATE questions SET category=?, question_text=? WHERE question_id=?",
        (category, question_text, question_id)
    )
    conn.commit()
    conn.close()


def delete_question(question_id):
    conn = get_conn()
    conn.execute("DELETE FROM questions WHERE question_id=?", (question_id,))
    conn.commit()
    conn.close()


def delete_quiz(quiz_id):
    conn = get_conn()
    conn.execute("DELETE FROM quizzes WHERE quiz_id=?", (quiz_id,))
    conn.commit()
    conn.close()


# ── UPGRADE functions ─────────────────────────────────────────

def get_all_upgrades():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM upgrades").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_upgrade(name, pollution_reduction, cost_points):
    conn = get_conn()
    conn.execute(
        "INSERT INTO upgrades (upgrade_name, pollution_reduction, cost_points) VALUES (?,?,?)",
        (name, pollution_reduction, cost_points)
    )
    conn.commit()
    conn.close()
    log_activity("system", "ADD_UPGRADE", name)


def update_upgrade(upgrade_id, name, pollution_reduction, cost_points):
    conn = get_conn()
    conn.execute(
        """UPDATE upgrades SET upgrade_name=?, pollution_reduction=?,
           cost_points=? WHERE upgrade_id=?""",
        (name, pollution_reduction, cost_points, upgrade_id)
    )
    conn.commit()
    conn.close()


def delete_upgrade(upgrade_id):
    conn = get_conn()
    conn.execute("DELETE FROM upgrades WHERE upgrade_id=?", (upgrade_id,))
    conn.commit()
    conn.close()


# ── LEADERBOARD functions ─────────────────────────────────────

def get_leaderboard(limit=20):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM leaderboard ORDER BY points DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_leaderboard_entry(username, points, pollution, day, won, xp):
    conn = get_conn()
    conn.execute(
        """INSERT INTO leaderboard
           (username, points, pollution, day, won, xp, recorded_at)
           VALUES (?,?,?,?,?,?,?)""",
        (username, points, round(pollution, 1), day, int(won), xp,
         datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.execute(
        """DELETE FROM leaderboard WHERE id NOT IN (
               SELECT id FROM leaderboard ORDER BY points DESC LIMIT 20
           )"""
    )
    conn.commit()
    conn.close()


# ── ACTIVITY LOG ──────────────────────────────────────────────

def log_activity(username, action, detail=""):
    conn = get_conn()
    conn.execute(
        "INSERT INTO activity_log (username, action, detail, recorded_at) VALUES (?,?,?,?)",
        (username, action, detail, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


def get_activity_log(limit=100):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM activity_log ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Pollution helpers ─────────────────────────────────────────

def save_player_pollution(username, pollution):
    conn = get_conn()
    conn.execute(
        "UPDATE users SET last_pollution=? WHERE username=?",
        (min(100.0, round(pollution, 4)), username)
    )
    conn.commit()
    conn.close()


def load_player_pollution(username):
    conn = get_conn()
    row  = conn.execute(
        "SELECT last_pollution FROM users WHERE username=?", (username,)
    ).fetchone()
    conn.close()
    if row:
        new = min(100.0, round(row["last_pollution"] + 0.01, 4))
        save_player_pollution(username, new)
        return new
    return 100.0


def save_player_progress(game_state):
    from game_data import get_level_info
    username    = game_state["user"]["username"]
    xp          = game_state.get("xp", 0)
    level, _, _ = get_level_info(xp)
    history     = game_state.get("pollution_history", [])
    history.append(round(game_state["pollution"], 1))
    if len(history) > 30:
        history = history[-30:]
    conn = get_conn()
    conn.execute(
        """UPDATE users SET xp=?, level=?, difficulty=?,
           pollution_history=?, last_pollution=? WHERE username=?""",
        (xp, level, game_state.get("difficulty", "medium"),
         json.dumps(history),
         min(100.0, round(game_state["pollution"], 4)),
         username)
    )
    conn.commit()
    conn.close()
    log_activity(username, "SAVE_PROGRESS",
                 f"pollution={game_state['pollution']:.1f} xp={xp}")


def save_season_result(game_state):
    user   = game_state["user"]
    points = game_state["points"]
    poll   = game_state["pollution"]
    day    = game_state["day"]
    won    = poll < 50
    xp     = game_state.get("xp", 0)

    add_leaderboard_entry(user["username"], points, poll, day, won, xp)

    conn = get_conn()
    uid  = conn.execute(
        "SELECT user_id FROM users WHERE username=?", (user["username"],)
    ).fetchone()
    if uid:
        uid = uid[0]
        conn.execute(
            """UPDATE user_stats
               SET seasons_played = seasons_played + 1,
                   best_score     = MAX(best_score, ?),
                   total_points   = total_points + ?,
                   total_correct  = total_correct + ?
               WHERE user_id=?""",
            (points, points, game_state.get("correct_answers", 0), uid)
        )
    conn.commit()
    conn.close()
    log_activity(user["username"], "SEASON_END",
                 f"won={won} points={points} pollution={poll:.1f}")


if __name__ == "__main__":
    init_db()
    print("\nUsers:")
    for u in get_all_users():
        print(f"  {u['username']} | {u['role']} | xp={u['xp']}")
    print("\nUpgrades:")
    for up in get_all_upgrades():
        print(f"  {up['upgrade_name']} | -{up['pollution_reduction']}% | {up['cost_points']}pts")
    print("\nQuizzes:")
    for qz in get_all_quizzes():
        print(f"  [{qz['quiz_id']}] {qz['quiz_title']} — {len(qz['questions'])} questions")
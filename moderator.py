"""
EcoCity Mayor — moderator.py
Moderator logic: Quiz Management + Item Management
"""

import json
import os
from datetime import datetime

DATA_DIR     = "data"
QUIZ_FILE    = os.path.join(DATA_DIR, "quizzes.json")
UPGRADE_FILE = os.path.join(DATA_DIR, "upgrades.json")


def _load_json(filepath):
    with open(filepath) as f:
        return json.load(f)

def _save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def _next_id(records, id_field):
    if not records:
        return 1
    return max(r[id_field] for r in records) + 1


# ── Quiz Management ───────────────────────────────────────

def add_quiz(moderator_id, quiz_title):
    quizzes  = _load_json(QUIZ_FILE)
    new_quiz = {
        "quiz_id":    _next_id(quizzes, "quiz_id"),
        "quiz_title": quiz_title.strip(),
        "created_by": moderator_id,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "questions":  []
    }
    quizzes.append(new_quiz)
    _save_json(QUIZ_FILE, quizzes)
    return new_quiz

def get_all_questions():
    quizzes = _load_json(QUIZ_FILE)
    all_q   = []
    for quiz in quizzes:
        for q in quiz["questions"]:
            q["quiz_id"] = quiz["quiz_id"]
            all_q.append(q)
    return all_q

def add_question(quiz_id, question_text, answers):
    correct_count = sum(1 for a in answers if a.get("is_correct"))
    if correct_count != 1:
        raise ValueError("Exactly one answer must be correct.")
    if len(answers) < 2:
        raise ValueError("Need at least 2 answers.")
    quizzes = _load_json(QUIZ_FILE)
    quiz    = next((q for q in quizzes if q["quiz_id"] == quiz_id), None)
    if not quiz:
        raise ValueError(f"Quiz {quiz_id} not found.")
    existing = [q["question_id"] for q in quiz["questions"]] or [0]
    new_id   = max(existing) + 1
    built    = [{"answer_id": i+1,
                 "answer_text": a["answer_text"].strip(),
                 "is_correct":  bool(a["is_correct"])}
                for i, a in enumerate(answers)]
    new_q = {"question_id": new_id,
              "question_text": question_text.strip(),
              "answers": built}
    quiz["questions"].append(new_q)
    _save_json(QUIZ_FILE, quizzes)
    return new_q

def delete_question(quiz_id, question_id):
    quizzes = _load_json(QUIZ_FILE)
    quiz    = next((q for q in quizzes if q["quiz_id"] == quiz_id), None)
    if not quiz:
        raise ValueError(f"Quiz {quiz_id} not found.")
    before = len(quiz["questions"])
    quiz["questions"] = [q for q in quiz["questions"]
                         if q["question_id"] != question_id]
    if len(quiz["questions"]) == before:
        return False
    _save_json(QUIZ_FILE, quizzes)
    return True

def edit_question(quiz_id, question_id, new_text=None, new_answers=None):
    quizzes  = _load_json(QUIZ_FILE)
    quiz     = next((q for q in quizzes if q["quiz_id"] == quiz_id), None)
    if not quiz:
        raise ValueError(f"Quiz {quiz_id} not found.")
    question = next((q for q in quiz["questions"]
                     if q["question_id"] == question_id), None)
    if not question:
        raise ValueError(f"Question {question_id} not found.")
    if new_text:
        question["question_text"] = new_text.strip()
    if new_answers:
        question["answers"] = [
            {"answer_id": i+1,
             "answer_text": a["answer_text"].strip(),
             "is_correct":  bool(a["is_correct"])}
            for i, a in enumerate(new_answers)
        ]
    _save_json(QUIZ_FILE, quizzes)
    return question


# ── Item (Upgrade) Management ─────────────────────────────

def add_upgrade(upgrade_name, pollution_reduction, cost_points):
    if pollution_reduction <= 0:
        raise ValueError("Reduction must be > 0.")
    if cost_points <= 0:
        raise ValueError("Cost must be > 0.")
    upgrades = _load_json(UPGRADE_FILE)
    names    = [u["upgrade_name"].lower() for u in upgrades]
    if upgrade_name.strip().lower() in names:
        raise ValueError(f"Upgrade '{upgrade_name}' already exists.")
    new_u = {
        "upgrade_id":          _next_id(upgrades, "upgrade_id"),
        "upgrade_name":        upgrade_name.strip(),
        "pollution_reduction": round(float(pollution_reduction), 2),
        "cost_points":         int(cost_points),
        "added_at":            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    upgrades.append(new_u)
    _save_json(UPGRADE_FILE, upgrades)
    return new_u

def get_upgrades():
    return _load_json(UPGRADE_FILE)

def update_upgrade(upgrade_id, new_name=None,
                   new_pollution_reduction=None, new_cost_points=None):
    upgrades = _load_json(UPGRADE_FILE)
    upgrade  = next((u for u in upgrades if u["upgrade_id"] == upgrade_id), None)
    if not upgrade:
        raise ValueError(f"Upgrade {upgrade_id} not found.")
    if new_name:
        upgrade["upgrade_name"] = new_name.strip()
    if new_pollution_reduction is not None:
        upgrade["pollution_reduction"] = round(float(new_pollution_reduction), 2)
    if new_cost_points is not None:
        upgrade["cost_points"] = int(new_cost_points)
    _save_json(UPGRADE_FILE, upgrades)
    return upgrade

def remove_upgrade(upgrade_id):
    upgrades = _load_json(UPGRADE_FILE)
    before   = len(upgrades)
    upgrades = [u for u in upgrades if u["upgrade_id"] != upgrade_id]
    if len(upgrades) == before:
        return False
    _save_json(UPGRADE_FILE, upgrades)
    return True
"""
EcoCity Mayor — game_data.py
Shared constants used across all screens.
"""

import random

# ── Player levels ─────────────────────────────────────
LEVELS = [
    (1,    0,    "Eco Novice"),
    (2,    60,   "Eco Learner"),
    (3,    150,  "Eco Activist"),
    (4,    280,  "Green Citizen"),
    (5,    450,  "Eco Warrior"),
    (6,    660,  "Green Mayor"),
    (7,    920,  "Pollution Slayer"),
    (8,   1240,  "Eco Champion"),
    (9,   1630,  "Earth Defender"),
    (10,  2100,  "Earth Guardian"),
]

def get_level_info(xp):
    level, title = 1, "Eco Novice"
    for lvl, req, ttl in LEVELS:
        if xp >= req:
            level, title = lvl, ttl
    next_xp = None
    for _, req, _ in LEVELS:
        if req > xp:
            next_xp = req
            break
    return level, title, next_xp

XP_REWARDS = {
    "correct":     15,
    "streak_5":    25,
    "upgrade":     20,
    "achievement": 30,
    "win":         100,
}

# ── Difficulty settings ───────────────────────────────
DIFFICULTY = {
    "easy": {
        "label":       "Easy",
        "description": "Slower pollution, fewer disasters, cheaper upgrades",
        "poll_rise":   0.005,
        "dis_interval":20000,
        "dis_chance":  0.10,
        "cost_mult":   0.80,
        "colour":      (72, 200, 118),
    },
    "medium": {
        "label":       "Medium",
        "description": "Balanced challenge for most players",
        "poll_rise":   0.01,
        "dis_interval":15000,
        "dis_chance":  0.20,
        "cost_mult":   1.00,
        "colour":      (236, 190, 50),
    },
    "hard": {
        "label":       "Hard",
        "description": "Fast pollution, frequent disasters, costly upgrades",
        "poll_rise":   0.02,
        "dis_interval":10000,
        "dis_chance":  0.35,
        "cost_mult":   1.25,
        "colour":      (215, 65, 65),
    },
}

# ── Daily challenges ──────────────────────────────────
CHALLENGE_POOL = [
    {"id":"c_correct_3",  "desc":"Answer 3 questions correctly",  "goal":3,   "reward":30,  "type":"correct"},
    {"id":"c_correct_5",  "desc":"Answer 5 questions correctly",  "goal":5,   "reward":60,  "type":"correct"},
    {"id":"c_correct_10", "desc":"Answer 10 questions correctly", "goal":10,  "reward":120, "type":"correct"},
    {"id":"c_buy_1",      "desc":"Buy 1 upgrade from the shop",   "goal":1,   "reward":25,  "type":"upgrade"},
    {"id":"c_buy_2",      "desc":"Buy 2 upgrades from the shop",  "goal":2,   "reward":50,  "type":"upgrade"},
    {"id":"c_streak_3",   "desc":"Get a 3x answer streak",        "goal":3,   "reward":40,  "type":"streak"},
    {"id":"c_streak_5",   "desc":"Get a 5x answer streak",        "goal":5,   "reward":80,  "type":"streak"},
    {"id":"c_earn_60",    "desc":"Earn 60 points this session",   "goal":60,  "reward":30,  "type":"points"},
    {"id":"c_earn_150",   "desc":"Earn 150 points this session",  "goal":150, "reward":70,  "type":"points"},
    {"id":"c_reduce_5",   "desc":"Reduce pollution by 5%",        "goal":5,   "reward":50,  "type":"reduce"},
    {"id":"c_reduce_15",  "desc":"Reduce pollution by 15%",       "goal":15,  "reward":100, "type":"reduce"},
]

def pick_daily_challenges(n=3):
    return random.sample(CHALLENGE_POOL, min(n, len(CHALLENGE_POOL)))

# ── Eco tips ──────────────────────────────────────────
ECO_TIPS = [
    "Recycling one aluminium can saves enough energy to run a TV for 3 hours.",
    "A single tree can absorb up to 48 pounds of CO2 per year.",
    "80% of ocean pollution comes from land-based activities.",
    "The average person generates over 4 pounds of solid waste daily.",
    "Solar panels can reduce a household carbon footprint by up to 80%.",
    "Switching to LED bulbs uses 75% less energy than incandescent lights.",
    "About 8 million metric tons of plastic enter our oceans every year.",
    "Electric vehicles produce zero direct emissions while driving.",
    "Composting food waste reduces methane emissions from landfills.",
    "Wind energy is one of the fastest growing energy sources worldwide.",
    "Deforestation accounts for about 10% of global carbon emissions.",
    "A dripping tap can waste up to 15 litres of water per day.",
    "Using public transport instead of a car can cut emissions by 45%.",
    "Coral reefs support 25% of all marine life despite covering 1% of the ocean.",
    "The ozone layer protects Earth from 97-99% of harmful UV radiation.",
    "Renewable energy could power 80% of the world's electricity by 2050.",
    "Air pollution causes approximately 7 million premature deaths per year.",
    "Planting grass on rooftops can reduce building energy use by 30%.",
    "The ocean produces over 50% of the world's oxygen.",
    "Turning off a tap while brushing teeth saves up to 6 litres per minute.",
    "Fast fashion is responsible for 10% of global carbon emissions.",
    "Buying local produce significantly reduces transportation emissions.",
    "A reusable bag saves approximately 700 plastic bags over its lifetime.",
    "Paper recycling saves 17 trees and 7,000 gallons of water per ton.",
    "Buildings account for nearly 40% of global energy consumption.",
]

# ── Positive eco events ───────────────────────────────
ECO_EVENTS = [
    {"msg": "Community Clean Up!  Pollution -2%",       "pollution": -2.0},
    {"msg": "Heavy Rain clears the air!  Pollution -1.5%", "pollution": -1.5},
    {"msg": "New Green Policy passed!  Pollution -2%",  "pollution": -2.0},
    {"msg": "Solar Farm opened!  Pollution -3%",        "pollution": -3.0},
    {"msg": "Tree Planting Drive!  Pollution -1.5%",    "pollution": -1.5},
    {"msg": "Electric Bus Fleet launched!  Pollution -2%","pollution": -2.0},
    {"msg": "City Recycling Rate hits record high! -2%","pollution": -2.0},
]

# ── Achievements ──────────────────────────────────────
ACHIEVEMENTS = [
    # Quiz
    {"id":"first_answer",  "name":"First Step",
     "desc":"Answer your first quiz question correctly"},
    {"id":"quiz_5",        "name":"Eco Student",
     "desc":"Answer 5 questions correctly in one session"},
    {"id":"quiz_20",       "name":"Eco Scholar",
     "desc":"Answer 20 questions correctly in one session"},
    {"id":"streak_3",      "name":"On a Roll",
     "desc":"Get a 3x correct answer streak"},
    {"id":"streak_5",      "name":"Quiz Master",
     "desc":"Get a 5x correct answer streak"},
    {"id":"streak_10",     "name":"Unstoppable",
     "desc":"Get a 10x correct answer streak"},
    {"id":"perfect_day",   "name":"Perfect Day",
     "desc":"Answer 10 questions without a single wrong answer"},

    # Pollution
    {"id":"first_drop",    "name":"First Breath",
     "desc":"Reduce pollution for the first time"},
    {"id":"below_80",      "name":"Small Progress",
     "desc":"Reduce pollution below 80%"},
    {"id":"green_mayor",   "name":"Green Mayor",
     "desc":"Reduce pollution below 70%"},
    {"id":"clean_city",    "name":"Clean City",
     "desc":"Reduce pollution below 50%"},
    {"id":"eco_paradise",  "name":"Eco Paradise",
     "desc":"Reduce pollution below 30%"},
    {"id":"zero_hero",     "name":"Zero Hero",
     "desc":"Reduce pollution below 10%"},

    # Points
    {"id":"first_points",  "name":"Getting Started",
     "desc":"Earn your first 30 points"},
    {"id":"points_100",    "name":"Point Collector",
     "desc":"Earn 100 total points"},
    {"id":"points_300",    "name":"Point Hoarder",
     "desc":"Earn 300 total points"},
    {"id":"points_500",    "name":"Points Machine",
     "desc":"Earn 500 total points"},
    {"id":"points_1000",   "name":"Eco Millionaire",
     "desc":"Earn 1000 total points"},

    # Shop
    {"id":"first_upgrade", "name":"First Investment",
     "desc":"Buy your first upgrade from the shop"},
    {"id":"shop_3",        "name":"Shop Addict",
     "desc":"Buy 3 upgrades in one season"},
    {"id":"shop_5",        "name":"Upgrade Fanatic",
     "desc":"Buy 5 upgrades in one season"},
    {"id":"big_spender",   "name":"Big Spender",
     "desc":"Spend 500 points in the shop"},

    # Survival
    {"id":"day_10",        "name":"Still Standing",
     "desc":"Reach Day 10"},
    {"id":"survivor",      "name":"Survivor",
     "desc":"Reach Day 20 without losing"},
    {"id":"veteran",       "name":"Veteran Mayor",
     "desc":"Complete 3 full seasons"},
    {"id":"champion",      "name":"Champion",
     "desc":"Win 3 seasons in a row"},

    # Special
    {"id":"disaster_5",    "name":"Crisis Manager",
     "desc":"Survive 5 disaster events in one season"},
    {"id":"comeback",      "name":"The Comeback",
     "desc":"Win a season after pollution reaches 90%"},
    {"id":"speedrun",      "name":"Speed Mayor",
     "desc":"Win a season before Day 20"},
    {"id":"daily_3",       "name":"Dedicated",
     "desc":"Complete all 3 daily challenges in one session"},
    {"id":"level_5",       "name":"Rising Star",
     "desc":"Reach player level 5"},
    {"id":"level_10",      "name":"Earth Guardian",
     "desc":"Reach the maximum player level 10"},
]
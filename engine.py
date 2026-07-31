#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smart Learning Engine - Spaced Repetition & Adaptive Learning"""

import math
from datetime import datetime, timedelta


class LearningEngine:
    def __init__(self, db):
        self.db = db

    def calculate_next_review(self, quality, review_count):
        if quality < 3:
            interval = 1
        elif quality == 3:
            interval = 3
        elif quality == 4:
            interval = 7
        else:
            interval = min(30, 2 ** review_count)
        return datetime.now() + timedelta(days=interval)

    def get_difficulty_score(self, uid, exercise):
        stats = self.db.get_stats(uid)
        level = stats["level"]
        level_map = {"beginner": 1, "intermediate": 2, "advanced": 3}
        ex_level = level_map.get(exercise.get("level", "beginner"), 1)
        user_level = level_map.get(level, 1)
        difficulty = abs(ex_level - user_level)
        if ex_level > user_level:
            return 0.8 + difficulty * 0.1
        elif ex_level < user_level:
            return 0.3 - difficulty * 0.1
        return 0.5

    def should_review(self, uid, word_data):
        if "next_review" not in word_data:
            return True
        next_review = datetime.fromisoformat(word_data["next_review"])
        return datetime.now() >= next_review

    def get_learning_path(self, uid):
        stats = self.db.get_stats(uid)
        level = stats["level"]
        path = []
        if stats["words"] < 20:
            path.append({"type": "words", "count": 5, "priority": "high"})
        if stats["grammar"] < 10:
            path.append({"type": "grammar", "count": 3, "priority": "high"})
        path.append({"type": "quiz", "count": 10, "priority": "medium"})
        if stats["streak"] >= 3:
            path.append({"type": "challenge", "count": 1, "priority": "low"})
        return path

    def calculate_xp_reward(self, correct, streak, level):
        base = 10 if correct else 2
        streak_bonus = min(streak * 2, 20)
        level_bonus = {"beginner": 0, "intermediate": 5, "advanced": 10}.get(level, 0)
        return base + streak_bonus + level_bonus

    def get_daily_goal_progress(self, uid):
        stats = self.db.get_stats(uid)
        goals = {
            "words": {"target": 10, "current": stats["words"]},
            "exercises": {"target": 20, "current": stats["exercises"]},
            "streak": {"target": 7, "current": stats["streak"]},
        }
        return goals

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Achievement System"""

ACHIEVEMENTS = [
    {"id":"first_word","title":"أول كلمة","desc":"تعلّم كلمة واحدة","icon":"📝","condition": lambda s: s["words"] >= 1},
    {"id":"word_10","title":"متعلم","desc":"تعلّم 10 كلمات","icon":"📚","condition": lambda s: s["words"] >= 10},
    {"id":"word_50","title":"خبير كلمات","desc":"تعلّم 50 كلمة","icon":"🎓","condition": lambda s: s["words"] >= 50},
    {"id":"word_100","title":"ماهر لغوي","desc":"تعلّم 100 كلمة","icon":"👑","condition": lambda s: s["words"] >= 100},
    {"id":"grammar_10","title":"نحوي مبتدئ","desc":"أكمل 10 قواعد","icon":"📖","condition": lambda s: s["grammar"] >= 10},
    {"id":"grammar_50","title":"نحوي خبير","desc":"أكمل 50 قاعدة","icon":"🏅","condition": lambda s: s["grammar"] >= 50},
    {"id":"exercise_20","title":"متمرن","desc":"أكمل 20 تمرين","icon":"🎯","condition": lambda s: s["exercises"] >= 20},
    {"id":"exercise_100","title":"بطل التمارين","desc":"أكمل 100 تمرين","icon":"🏆","condition": lambda s: s["exercises"] >= 100},
    {"id":"streak_3","title":"ملتزم","desc":"3 أيام متتالية","icon":"🔥","condition": lambda s: s["streak"] >= 3},
    {"id":"streak_7","title":"أسبوع ذهبي","desc":"7 أيام متتالية","icon":"⭐","condition": lambda s: s["streak"] >= 7},
    {"id":"streak_30","title":"أسطورة","desc":"30 يوم متتالي","icon":"💎","condition": lambda s: s["streak"] >= 30},
    {"id":"quiz_5","title":"محلل","desc":"أكمل 5 اختبارات","icon":"✅","condition": lambda s: s["quizzes"] >= 5},
    {"id":"quiz_20","title":"خبير اختبارات","desc":"أكمل 20 اختبار","icon":"🎖️","condition": lambda s: s["quizzes"] >= 20},
    {"id":"accuracy_90","title":"دقة عالية","desc":"نسبة دقة 90%+","icon":"🎯","condition": lambda s: s["accuracy"] >= 90},
    {"id":"xp_500","title":"نجم","desc":"اجمع 500 نقطة","icon":"🌟","condition": lambda s: s["xp"] >= 500},
    {"id":"xp_1000","title":"متألق","desc":"اجمع 1000 نقطة","icon":"💫","condition": lambda s: s["xp"] >= 1000},
    {"id":"xp_5000","title":"أسطورة","desc":"اجمع 5000 نقطة","icon":"👑","condition": lambda s: s["xp"] >= 5000},
    {"id":"level_intermediate","title":"متوسط","desc":"الوصول للمستوى المتوسط","icon":"🌿","condition": lambda s: s["level"] in ["intermediate","advanced"]},
    {"id":"level_advanced","title":"متقدم","desc":"الوصول للمستوى المتقدم","icon":"🌳","condition": lambda s: s["level"] == "advanced"},
]


def check_achievements(uid, db):
    stats = db.get_stats(uid)
    user = db.get_user(uid)
    if not user:
        return []
    earned = user.get("achievements", [])
    new_earned = []
    for ach in ACHIEVEMENTS:
        if ach["id"] not in earned and ach["condition"](stats):
            earned.append(ach["id"])
            new_earned.append(ach)
    if new_earned:
        user["achievements"] = earned
        db.save_all()
    return new_earned


def get_all_achievements(uid, db):
    user = db.get_user(uid)
    earned = user.get("achievements", []) if user else []
    result = []
    for ach in ACHIEVEMENTS:
        result.append({**ach, "earned": ach["id"] in earned})
    return result

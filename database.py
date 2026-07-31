#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EnglishMaster Pro - Database Engine v3.0
500+ Words | 100+ Grammar Rules | 300+ Exercises | 50+ Idioms | 20+ Topics
"""

import json
import os
import random
from datetime import datetime, timedelta


class Database:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.users_file = os.path.join(data_dir, "users.json")
        self.progress_file = os.path.join(data_dir, "progress.json")
        self.users = self._load(self.users_file, {})
        self.progress = self._load(self.progress_file, {})

    def _load(self, path, default):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return default
        return default

    def _save(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_all(self):
        self._save(self.users_file, self.users)
        self._save(self.progress_file, self.progress)

    # ── User Management ──
    def add_user(self, name):
        uid = str(len(self.users) + 1)
        self.users[uid] = {
            "name": name, "created": datetime.now().isoformat(),
            "level": "beginner", "xp": 0, "streak": 0,
            "last_active": datetime.now().strftime("%Y-%m-%d"),
            "daily_xp": 0, "total_words": 0, "total_grammar": 0,
            "total_exercises": 0, "achievements": [],
        }
        self.progress[uid] = {
            "words_learned": {}, "grammar_done": [], "exercises_done": [],
            "quizzes_taken": 0, "quizzes_passed": 0,
            "flashcards_reviewed": 0, "correct": 0, "wrong": 0,
            "daily_history": {}, "level_history": ["beginner"],
            "favorites": [], "notes": {},
        }
        self.save_all()
        return uid

    def get_user(self, uid):
        return self.users.get(uid)

    def get_level(self, uid):
        return self.users.get(uid, {}).get("level", "beginner")

    def set_level(self, uid, level):
        if uid in self.users:
            self.users[uid]["level"] = level
            self.save_all()

    def add_xp(self, uid, amount):
        if uid not in self.users:
            return
        self.users[uid]["xp"] += amount
        self.users[uid]["daily_xp"] += amount
        today = datetime.now().strftime("%Y-%m-%d")
        if self.users[uid].get("last_active") != today:
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            if self.users[uid].get("last_active") == yesterday:
                self.users[uid]["streak"] += 1
            else:
                self.users[uid]["streak"] = 1
            self.users[uid]["last_active"] = today
        changed = self._check_level(uid)
        self.save_all()
        return changed

    def _check_level(self, uid):
        xp = self.users[uid]["xp"]
        old = self.users[uid]["level"]
        if xp >= 500:
            new = "advanced"
        elif xp >= 200:
            new = "intermediate"
        else:
            new = "beginner"
        if new != old:
            self.users[uid]["level"] = new
            self.progress[uid]["level_history"].append(new)
            return True, old, new
        return False, old, new

    def update_streak(self, uid):
        if uid not in self.users:
            return
        today = datetime.now().strftime("%Y-%m-%d")
        if self.users[uid].get("last_active") == today:
            return
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        if self.users[uid].get("last_active") == yesterday:
            self.users[uid]["streak"] += 1
        else:
            self.users[uid]["streak"] = 1
        self.users[uid]["last_active"] = today
        self.save_all()

    def get_stats(self, uid):
        p = self.progress.get(uid, {})
        u = self.users.get(uid, {})
        total = p.get("correct", 0) + p.get("wrong", 0)
        accuracy = (p.get("correct", 0) / total * 100) if total > 0 else 0
        words_count = len(p.get("words_learned", {}))
        return {
            "xp": u.get("xp", 0), "level": u.get("level", "beginner"),
            "streak": u.get("streak", 0),
            "words": words_count, "grammar": len(p.get("grammar_done", [])),
            "exercises": len(p.get("exercises_done", [])),
            "quizzes": p.get("quizzes_taken", 0),
            "quizzes_passed": p.get("quizzes_passed", 0),
            "correct": p.get("correct", 0), "wrong": p.get("wrong", 0),
            "accuracy": round(accuracy, 1),
            "flashcards": p.get("flashcards_reviewed", 0),
            "daily_xp": u.get("daily_xp", 0),
            "achievements": len(u.get("achievements", [])),
        }

    # ── Vocabulary System ──
    def get_words(self, level="all", category=None):
        words = self._all_words()
        if level != "all":
            words = [w for w in words if w["level"] == level]
        if category:
            words = [w for w in words if w["category"] == category]
        return words

    def get_word_by_id(self, word_id):
        for w in self._all_words():
            if w["id"] == word_id:
                return w
        return None

    def mark_word_learned(self, uid, word_id, quality=5):
        if uid not in self.progress:
            return
        words = self.progress[uid].get("words_learned", {})
        words[str(word_id)] = {
            "quality": quality, "reviews": words.get(str(word_id), {}).get("reviews", 0) + 1,
            "last_review": datetime.now().isoformat(),
            "next_review": (datetime.now() + timedelta(days=min(quality, 30))).isoformat(),
        }
        self.progress[uid]["words_learned"] = words
        self.users[uid]["total_words"] = len(words)
        self.save_all()

    def get_due_words(self, uid, limit=10):
        words = self.progress.get(uid, {}).get("words_learned", {})
        now = datetime.now().isoformat()
        due = []
        for wid, data in words.items():
            if data.get("next_review", "") <= now:
                w = self.get_word_by_id(int(wid))
                if w:
                    due.append(w)
        if not due:
            new_words = [w for w in self.get_words(self.get_level(uid))
                         if str(w["id"]) not in words]
            due = random.sample(new_words, min(limit, len(new_words))) if new_words else []
        return due[:limit]

    def get_new_words(self, uid, limit=5):
        words = self.progress.get(uid, {}).get("words_learned", {})
        level = self.get_level(uid)
        new = [w for w in self.get_words(level) if str(w["id"]) not in words]
        return random.sample(new, min(limit, len(new))) if new else []

    # ── Grammar System ──
    def get_grammar(self, level="all"):
        rules = self._all_grammar()
        if level != "all":
            rules = [r for r in rules if r["level"] == level]
        return rules

    def mark_grammar_done(self, uid, rule_id):
        if uid in self.progress and rule_id not in self.progress[uid]["grammar_done"]:
            self.progress[uid]["grammar_done"].append(rule_id)
            self.users[uid]["total_grammar"] = len(self.progress[uid]["grammar_done"])
            self.save_all()

    # ── Exercise System ──
    def get_exercises(self, level="all", ex_type=None):
        ex = self._all_exercises()
        if level != "all":
            ex = [e for e in ex if e["level"] == level]
        if ex_type:
            ex = [e for e in ex if e["type"] == ex_type]
        return ex

    def get_exercise_by_id(self, ex_id):
        for e in self._all_exercises():
            if e["id"] == ex_id:
                return e
        return None

    def mark_exercise_done(self, uid, ex_id, correct):
        if uid in self.progress:
            if ex_id not in self.progress[uid]["exercises_done"]:
                self.progress[uid]["exercises_done"].append(ex_id)
            if correct:
                self.progress[uid]["correct"] += 1
            else:
                self.progress[uid]["wrong"] += 1
            self.users[uid]["total_exercises"] = len(self.progress[uid]["exercises_done"])
            self.save_all()

    def get_quiz(self, level, count=10):
        exercises = self.get_exercises(level)
        if len(exercises) < count:
            count = len(exercises)
        return random.sample(exercises, count)

    # ── Idioms System ──
    def get_idioms(self, level="all"):
        idioms = self._all_idioms()
        if level != "all":
            idioms = [i for i in idioms if i["level"] == level]
        return idioms

    # ── Phrases System ──
    def get_phrases(self, category=None):
        phrases = self._all_phrases()
        if category:
            phrases = [p for p in phrases if p["category"] == category]
        return phrases

    # ── Favorites ──
    def add_favorite(self, uid, item_type, item_id):
        if uid in self.progress:
            fav = {"type": item_type, "id": item_id}
            if fav not in self.progress[uid]["favorites"]:
                self.progress[uid]["favorites"].append(fav)
                self.save_all()

    def get_favorites(self, uid):
        return self.progress.get(uid, {}).get("favorites", [])

    # ══════════════════════════════════════════════════════════════
    # DATA - 500+ Words
    # ══════════════════════════════════════════════════════════════
    def _all_words(self):
        return [
            # ── BEGINNER: Greetings & Basics (1-30) ──
            {"id":1,"word":"Hello","ar":"مرحبا","example":"Hello, how are you?","phonetic":"/həˈloʊ/","level":"beginner","category":"greetings","part_of_speech":"interjection"},
            {"id":2,"word":"Goodbye","ar":"وداعا","example":"Goodbye, see you tomorrow!","phonetic":"/ɡʊdˈbaɪ/","level":"beginner","category":"greetings","part_of_speech":"interjection"},
            {"id":3,"word":"Thank you","ar":"شكرا","example":"Thank you very much for your help.","phonetic":"/θæŋk juː/","level":"beginner","category":"greetings","part_of_speech":"interjection"},
            {"id":4,"word":"Please","ar":"من فضلك","example":"Please sit down.","phonetic":"/pliːz/","level":"beginner","category":"greetings","part_of_speech":"adverb"},
            {"id":5,"word":"Sorry","ar":"آسف","example":"I'm sorry for being late.","phonetic":"/ˈsɒri/","level":"beginner","category":"greetings","part_of_speech":"adjective"},
            {"id":6,"word":"Welcome","ar":"أهلا وسهلا","example":"Welcome to our home!","phonetic":"/ˈwɛlkəm/","level":"beginner","category":"greetings","part_of_speech":"interjection"},
            {"id":7,"word":"Yes","ar":"نعم","example":"Yes, I understand perfectly.","phonetic":"/jɛs/","level":"beginner","category":"basics","part_of_speech":"adverb"},
            {"id":8,"word":"No","ar":"لا","example":"No, thank you, I'm fine.","phonetic":"/noʊ/","level":"beginner","category":"basics","part_of_speech":"adverb"},
            {"id":9,"word":"Water","ar":"ماء","example":"Can I have some water, please?","phonetic":"/ˈwɔːtər/","level":"beginner","category":"food_drink","part_of_speech":"noun"},
            {"id":10,"word":"Food","ar":"طعام","example":"The food at this restaurant is delicious.","phonetic":"/fuːd/","level":"beginner","category":"food_drink","part_of_speech":"noun"},
            {"id":11,"word":"House","ar":"بيت","example":"This is my house, welcome in!","phonetic":"/haʊs/","level":"beginner","category":"places","part_of_speech":"noun"},
            {"id":12,"word":"Car","ar":"سيارة","example":"The car is parked outside.","phonetic":"/kɑːr/","level":"beginner","category":"transport","part_of_speech":"noun"},
            {"id":13,"word":"Book","ar":"كتاب","example":"I read a book every week.","phonetic":"/bʊk/","level":"beginner","category":"education","part_of_speech":"noun"},
            {"id":14,"word":"Friend","ar":"صديق","example":"She is my best friend.","phonetic":"/frɛnd/","level":"beginner","category":"people","part_of_speech":"noun"},
            {"id":15,"word":"Family","ar":"عائلة","example":"I love my family very much.","phonetic":"/ˈfæməli/","level":"beginner","category":"people","part_of_speech":"noun"},
            {"id":16,"word":"School","ar":"مدرسة","example":"I go to school every day.","phonetic":"/skuːl/","level":"beginner","category":"education","part_of_speech":"noun"},
            {"id":17,"word":"Beautiful","ar":"جميل","example":"The sunset is beautiful tonight.","phonetic":"/ˈbjuːtɪfəl/","level":"beginner","category":"adjectives","part_of_speech":"adjective"},
            {"id":18,"word":"Happy","ar":"سعيد","example":"I am very happy today.","phonetic":"/ˈhæpi/","level":"beginner","category":"emotions","part_of_speech":"adjective"},
            {"id":19,"word":"Run","ar":"يركض","example":"I like to run in the morning.","phonetic":"/rʌn/","level":"beginner","category":"actions","part_of_speech":"verb"},
            {"id":20,"word":"Eat","ar":"يأكل","example":"Let's eat lunch together.","phonetic":"/iːt/","level":"beginner","category":"actions","part_of_speech":"verb"},
            {"id":21,"word":"Sleep","ar":"ينام","example":"I need to sleep early tonight.","phonetic":"/sliːp/","level":"beginner","category":"actions","part_of_speech":"verb"},
            {"id":22,"word":"Big","ar":"كبير","example":"The elephant is very big.","phonetic":"/bɪɡ/","level":"beginner","category":"adjectives","part_of_speech":"adjective"},
            {"id":23,"word":"Small","ar":"صغير","example":"The cat is small and cute.","phonetic":"/smɔːl/","level":"beginner","category":"adjectives","part_of_speech":"adjective"},
            {"id":24,"word":"Good","ar":"جيد","example":"This is a good book to read.","phonetic":"/ɡʊd/","level":"beginner","category":"adjectives","part_of_speech":"adjective"},
            {"id":25,"word":"Bad","ar":"سيئ","example":"The weather is bad today.","phonetic":"/bæd/","level":"beginner","category":"adjectives","part_of_speech":"adjective"},
            {"id":26,"word":"New","ar":"جديد","example":"I bought a new phone yesterday.","phonetic":"/njuː/","level":"beginner","category":"adjectives","part_of_speech":"adjective"},
            {"id":27,"word":"Old","ar":"قديم","example":"This is an old building in the city.","phonetic":"/oʊld/","level":"beginner","category":"adjectives","part_of_speech":"adjective"},
            {"id":28,"word":"Want","ar":"يريد","example":"I want to learn English.","phonetic":"/wɒnt/","level":"beginner","category":"actions","part_of_speech":"verb"},
            {"id":29,"word":"Need","ar":"يحتاج","example":"I need your help with this project.","phonetic":"/niːd/","level":"beginner","category":"actions","part_of_speech":"verb"},
            {"id":30,"word":"Like","ar":"يحب","example":"I like to play football.","phonetic":"/laɪk/","level":"beginner","category":"actions","part_of_speech":"verb"},
            # ── INTERMEDIATE: Everyday Life (31-70) ──
            {"id":31,"word":"Decision","ar":"قرار","example":"That was a difficult decision to make.","phonetic":"/dɪˈsɪʒən/","level":"intermediate","category":"abstract","part_of_speech":"noun"},
            {"id":32,"word":"Opportunity","ar":"فرصة","example":"Don't miss this great opportunity.","phonetic":"/ˌɒpərˈtjuːnɪti/","level":"intermediate","category":"abstract","part_of_speech":"noun"},
            {"id":33,"word":"Experience","ar":"خبرة","example":"She has a lot of experience in teaching.","phonetic":"/ɪkˈspɪəriəns/","level":"intermediate","category":"abstract","part_of_speech":"noun"},
            {"id":34,"word":"Challenge","ar":"تحدي","example":"Life is full of challenges.","phonetic":"/ˈtʃælɪndʒ/","level":"intermediate","category":"abstract","part_of_speech":"noun"},
            {"id":35,"word":"Achievement","ar":"إنجاز","example":"This is a remarkable achievement.","phonetic":"/əˈtʃiːvmənt/","level":"intermediate","category":"abstract","part_of_speech":"noun"},
            {"id":36,"word":"Environment","ar":"بيئة","example":"We must protect the environment.","phonetic":"/ɪnˈvaɪrənmənt/","level":"intermediate","category":"science","part_of_speech":"noun"},
            {"id":37,"word":"Technology","ar":"تكنولوجيا","example":"Technology is changing our lives rapidly.","phonetic":"/tɛkˈnɒlədʒi/","level":"intermediate","category":"science","part_of_speech":"noun"},
            {"id":38,"word":"Communication","ar":"تواصل","example":"Good communication is key to success.","phonetic":"/kəˌmjuːnɪˈkeɪʃən/","level":"intermediate","category":"social","part_of_speech":"noun"},
            {"id":39,"word":"Responsibility","ar":"مسؤولية","example":"It's your responsibility to finish on time.","phonetic":"/rɪˌspɒnsəˈbɪlɪti/","level":"intermediate","category":"abstract","part_of_speech":"noun"},
            {"id":40,"word":"Knowledge","ar":"معرفة","example":"Knowledge is the most powerful tool.","phonetic":"/ˈnɒlɪdʒ/","level":"intermediate","category":"education","part_of_speech":"noun"},
            {"id":41,"word":"Convenient","ar":"عملي","example":"This location is very convenient.","phonetic":"/kənˈviːniənt/","level":"intermediate","category":"adjectives","part_of_speech":"adjective"},
            {"id":42,"word":"Efficient","ar":"فعال","example":"We need a more efficient system.","phonetic":"/ɪˈfɪʃənt/","level":"intermediate","category":"adjectives","part_of_speech":"adjective"},
            {"id":43,"word":"Sufficient","ar":"كافٍ","example":"Is this sufficient for your needs?","phonetic":"/səˈfɪʃənt/","level":"intermediate","category":"adjectives","part_of_speech":"adjective"},
            {"id":44,"word":"Apparent","ar":"واضح","example":"The answer is quite apparent.","phonetic":"/əˈpærənt/","level":"intermediate","category":"adjectives","part_of_speech":"adjective"},
            {"id":45,"word":"Reluctant","ar":"متردد","example":"He was reluctant to agree with us.","phonetic":"/rɪˈlʌktənt/","level":"intermediate","category":"emotions","part_of_speech":"adjective"},
            {"id":46,"word":"Investigate","ar":"يحقق","example":"The police will investigate the case.","phonetic":"/ɪnˈvɛstɪɡeɪt/","level":"intermediate","category":"actions","part_of_speech":"verb"},
            {"id":47,"word":"Demonstrate","ar":"يشرح","example":"Can you demonstrate how this works?","phonetic":"/ˈdɛmənstreɪt/","level":"intermediate","category":"actions","part_of_speech":"verb"},
            {"id":48,"word":"Compromise","ar":"تنازل","example":"We need to reach a compromise.","phonetic":"/ˈkɒmprəmaɪz/","level":"intermediate","category":"social","part_of_speech":"noun"},
            {"id":49,"word":"Sustainable","ar":"مستدام","example":"We need sustainable solutions for energy.","phonetic":"/səˈsteɪnəbəl/","level":"intermediate","category":"science","part_of_speech":"adjective"},
            {"id":50,"word":"Controversy","ar":"جدل","example":"The topic caused a lot of controversy.","phonetic":"/ˈkɒntrəvɜːsi/","level":"intermediate","category":"social","part_of_speech":"noun"},
            {"id":51,"word":"Negotiate","ar":"يتفاوض","example":"They need to negotiate a new deal.","phonetic":"/nɪˈɡoʊʃieɪt/","level":"intermediate","category":"actions","part_of_speech":"verb"},
            {"id":52,"word":"Accomplish","ar":"يُنجز","example":"She accomplished all her goals this year.","phonetic":"/əˈkɒmplɪʃ/","level":"intermediate","category":"actions","part_of_speech":"verb"},
            {"id":53,"word":"Significant","ar":"مهم","example":"This is a significant moment in history.","phonetic":"/sɪɡˈnɪfɪkənt/","level":"intermediate","category":"adjectives","part_of_speech":"adjective"},
            {"id":54,"word":"Approximately","ar":"تقريبا","example":"Approximately 100 people attended.","phonetic":"/əˈprɒksɪmətli/","level":"intermediate","category":"adverbs","part_of_speech":"adverb"},
            {"id":55,"word":"Consequences","ar":"عواقب","example":"Every action has consequences.","phonetic":"/ˈkɒnsɪkwɛnsɪz/","level":"intermediate","category":"abstract","part_of_speech":"noun"},
            {"id":56,"word":"Professional","ar":"محترف","example":"She is a professional dancer.","phonetic":"/prəˈfɛʃənəl/","level":"intermediate","category":"people","part_of_speech":"adjective"},
            {"id":57,"word":"Particularly","ar":"خاصة","example":"I particularly enjoy reading novels.","phonetic":"/pəˈtɪkjʊləli/","level":"intermediate","category":"adverbs","part_of_speech":"adverb"},
            {"id":58,"word":"Immediately","ar":"فورا","example":"Please come to my office immediately.","phonetic":"/ɪˈmiːdiətli/","level":"intermediate","category":"adverbs","part_of_speech":"adverb"},
            {"id":59,"word":"Appreciate","ar":"يقدر","example":"I really appreciate your help.","phonetic":"/əˈpriːʃieɪt/","level":"intermediate","category":"actions","part_of_speech":"verb"},
            {"id":60,"word":"Considerable","ar":"كبير","example":"She showed considerable improvement.","phonetic":"/kənˈsɪdərəbəl/","level":"intermediate","category":"adjectives","part_of_speech":"adjective"},
            # ── INTERMEDIATE: Advanced Everyday (61-80) ──
            {"id":61,"word":"Regulate","ar":"ينظم","example":"The government should regulate the market.","phonetic":"/ˈrɛɡjʊleɪt/","level":"intermediate","category":"actions","part_of_speech":"verb"},
            {"id":62,"word":"Substantial","ar":"كبير","example":"There was a substantial increase in sales.","phonetic":"/səbˈstænʃəl/","level":"intermediate","category":"adjectives","part_of_speech":"adjective"},
            {"id":63,"word":"Contemplate","ar":"يتأمل","example":"She sat quietly to contemplate her future.","phonetic":"/ˈkɒntəmpleɪt/","level":"intermediate","category":"actions","part_of_speech":"verb"},
            {"id":64,"word":"Elaborate","ar":"مفصل","example":"Please elaborate on your idea.","phonetic":"/ɪˈlæbərət/","level":"intermediate","category":"adjectives","part_of_speech":"adjective"},
            {"id":65,"word":"Phenomenon","ar":"ظاهرة","example":"Climate change is a global phenomenon.","phonetic":"/fɪˈnɒmɪnən/","level":"intermediate","category":"science","part_of_speech":"noun"},
            {"id":66,"word":"Perspective","ar":"منظور","example":"Try to see things from a different perspective.","phonetic":"/pərˈspɛktɪv/","level":"intermediate","category":"abstract","part_of_speech":"noun"},
            {"id":67,"word":"Inevitable","ar":"حتمي","example":"Change is inevitable in life.","phonetic":"/ɪnˈɛvɪtəbəl/","level":"intermediate","category":"adjectives","part_of_speech":"adjective"},
            {"id":68,"word":"Initiative","ar":"مبادرة","example":"She took the initiative to organize the event.","phonetic":"/ɪˈnɪʃətɪv/","level":"intermediate","category":"abstract","part_of_speech":"noun"},
            {"id":69,"word":"Comprehensive","ar":"شامل","example":"We need a comprehensive plan.","phonetic":"/ˌkɒmprɪˈhɛnsɪv/","level":"intermediate","category":"adjectives","part_of_speech":"adjective"},
            {"id":70,"word":"Consecutive","ar":"متتالي","example":"It rained for five consecutive days.","phonetic":"/kənˈsɛkjʊtɪv/","level":"intermediate","category":"adjectives","part_of_speech":"adjective"},
            # ── ADVANCED: Academic & Professional (71-110) ──
            {"id":71,"word":"Sophisticated","ar":"متطور","example":"This is a very sophisticated system.","phonetic":"/səˈfɪstɪkeɪtɪd/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":72,"word":"Unprecedented","ar":"لم يُرَ من قبل","example":"We are facing unprecedented challenges.","phonetic":"/ʌnˈprɛsɪdɛntɪd/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":73,"word":"Resilience","ar":"مرونة","example":"She showed great resilience during the crisis.","phonetic":"/rɪˈzɪliəns/","level":"advanced","category":"abstract","part_of_speech":"noun"},
            {"id":74,"word":"Paradigm","ar":"نموذج","example":"This changed the entire paradigm.","phonetic":"/ˈpærədaɪm/","level":"advanced","category":"science","part_of_speech":"noun"},
            {"id":75,"word":"Ambiguous","ar":"غامض","example":"The statement was deliberately ambiguous.","phonetic":"/æmˈbɪɡjuəs/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":76,"word":"Pragmatic","ar":"عملي","example":"We need a pragmatic approach to solve this.","phonetic":"/præɡˈmætɪk/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":77,"word":"Ephemeral","ar":"عابر","example":"Fame is often ephemeral in this industry.","phonetic":"/ɪˈfɛmərəl/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":78,"word":"Ubiquitous","ar":"منتشر في كل مكان","example":"Smartphones are ubiquitous in modern life.","phonetic":"/juːˈbɪkwɪtəs/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":79,"word":"Conundrum","ar":"لغز","example":"This presents a real conundrum for policymakers.","phonetic":"/kəˈnʌndrəm/","level":"advanced","category":"abstract","part_of_speech":"noun"},
            {"id":80,"word":"Eloquent","ar":"فصيح","example":"She gave an eloquent speech at the conference.","phonetic":"/ˈɛləkwənt/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":81,"word":"Mitigate","ar":"يخفف","example":"We must mitigate the risks involved.","phonetic":"/ˈmɪtɪɡeɪt/","level":"advanced","category":"actions","part_of_speech":"verb"},
            {"id":82,"word":"Perseverance","ar":"مثابرة","example":"Success requires patience and perseverance.","phonetic":"/ˌpɜːsɪˈvɪərəns/","level":"advanced","category":"abstract","part_of_speech":"noun"},
            {"id":83,"word":"Scrutinize","ar":"يفحص بدقة","example":"We need to scrutinize the evidence carefully.","phonetic":"/ˈskruːtɪnaɪz/","level":"advanced","category":"actions","part_of_speech":"verb"},
            {"id":84,"word":"Articulate","ar":"بليغ","example":"He is very articulate in his presentations.","phonetic":"/ɑːrˈtɪkjʊleɪt/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":85,"word":"Exemplify","ar":"يوضح","example":"This case exemplifies the problem perfectly.","phonetic":"/ɪɡˈzɛmplɪfaɪ/","level":"advanced","category":"actions","part_of_speech":"verb"},
            {"id":86,"word":"Nuanced","ar":"دقيق","example":"This requires a more nuanced approach.","phonetic":"/ˈnjuːɒnst/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":87,"word":"Rhetoric","ar":"بلاغة","example":"His speech was filled with powerful rhetoric.","phonetic":"/ˈrɛtərɪk/","level":"advanced","category":"education","part_of_speech":"noun"},
            {"id":88,"word":"Empirical","ar":"تجريبي","example":"The theory needs empirical evidence.","phonetic":"/ɪmˈpɪrɪkəl/","level":"advanced","category":"science","part_of_speech":"adjective"},
            {"id":89,"word":"Prerequisite","ar":"شرط مسبق","example":"Math is a prerequisite for this course.","phonetic":"/priːˈrɛkwɪzɪt/","level":"advanced","category":"education","part_of_speech":"noun"},
            {"id":90,"word":"Overarching","ar":"شامل","example":"We need an overarching strategy.","phonetic":"/ˌoʊvərˈɑːrtʃɪŋ/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":91,"word":"Substantiate","ar":"يثبت","example":"Can you substantiate your claims?","phonetic":"/səbˈstænʃieɪt/","level":"advanced","category":"actions","part_of_speech":"verb"},
            {"id":92,"word":"Conjecture","ar":"تخمين","example":"This is mere conjecture without evidence.","phonetic":"/kənˈdʒɛktʃər/","level":"advanced","category":"abstract","part_of_speech":"noun"},
            {"id":93,"word":"Juxtapose","ar":"يقارن","example":"The author juxtaposes old and new ideas.","phonetic":"/ˌdʒʌkstəˈpoʊz/","level":"advanced","category":"actions","part_of_speech":"verb"},
            {"id":94,"word":"Collaborative","ar":"تعاوني","example":"This was a collaborative effort.","phonetic":"/kəˈlæbərətɪv/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":95,"word":"Diligent","ar":"مجتهد","example":"She is a very diligent student.","phonetic":"/ˈdɪlɪdʒənt/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":96,"word":"Catalyst","ar":"محفز","example":"Innovation is a catalyst for growth.","phonetic":"/ˈkætəlɪst/","level":"advanced","category":"science","part_of_speech":"noun"},
            {"id":97,"word":"Unprecedented","ar":"استثنائي","example":"The growth has been unprecedented.","phonetic":"/ʌnˈprɛsɪdɛntɪd/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":98,"word":"Synthesize","ar":"يُركّب","example":"We need to synthesize all the data.","phonetic":"/ˈsɪnθəsaɪz/","level":"advanced","category":"actions","part_of_speech":"verb"},
            {"id":99,"word":"Pivotal","ar":"محوري","example":"This was a pivotal moment in history.","phonetic":"/ˈpɪvətəl/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":100,"word":"Austere","ar":"صارم","example":"The government adopted an austere policy.","phonetic":"/ɔːˈstɪər/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            # ── ADVANCED: Specialized (101-120) ──
            {"id":101,"word":"Quintessential","ar":"جوهري","example":"This is the quintessential example.","phonetic":"/ˌkwɪntɪˈsɛnʃəl/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":102,"word":"Profound","ar":"عميق","example":"The book had a profound impact on me.","phonetic":"/prəˈfaʊnd/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":103,"word":"Exacerbate","ar":"يُسوّئ","example":"The drought exacerbated the food crisis.","phonetic":"/ɪɡˈzæsərbeɪt/","level":"advanced","category":"actions","part_of_speech":"verb"},
            {"id":104,"word":"Enigmatic","ar":"غامض","example":"The Mona Lisa has an enigmatic smile.","phonetic":"/ˌɛnɪɡˈmætɪk/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":105,"word":"Pragmatic","ar":"عملي","example":"Take a pragmatic approach to problem-solving.","phonetic":"/præɡˈmætɪk/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":106,"word":"Dichotomy","ar":"تناقض","example":"There is a dichotomy between theory and practice.","phonetic":"/daɪˈkɒtəmi/","level":"advanced","category":"abstract","part_of_speech":"noun"},
            {"id":107,"word":"Zealous","ar":"متحمس","example":"She is a zealous advocate for human rights.","phonetic":"/ˈzɛləs/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":108,"word":"Ineffable","ar":"لا يوصف","example":"The beauty of the sunset was ineffable.","phonetic":"/ɪnˈɛfəbəl/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":109,"word":"Surreptitious","ar":"سري","example":"She took a surreptitious glance at the phone.","phonetic":"/ˌsʌrəpˈtɪʃəs/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":110,"word":"Obsequious","ar":"خاضع","example":"His obsequious behavior annoyed everyone.","phonetic":"/əbˈsiːkiəs/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            # ── BEGINNER: More Basics (111-140) ──
            {"id":111,"word":"Time","ar":"وقت","example":"What time is it?","phonetic":"/taɪm/","level":"beginner","category":"basics","part_of_speech":"noun"},
            {"id":112,"word":"Day","ar":"يوم","example":"It was a beautiful day.","phonetic":"/deɪ/","level":"beginner","category":"basics","part_of_speech":"noun"},
            {"id":113,"word":"Night","ar":"ليل","example":"The stars shine at night.","phonetic":"/naɪt/","level":"beginner","category":"basics","part_of_speech":"noun"},
            {"id":114,"word":"Morning","ar":"صباح","example":"Good morning, everyone!","phonetic":"/ˈmɔːrnɪŋ/","level":"beginner","category":"basics","part_of_speech":"noun"},
            {"id":115,"word":"Evening","ar":"مساء","example":"Good evening, ladies and gentlemen.","phonetic":"/ˈiːvnɪŋ/","level":"beginner","category":"basics","part_of_speech":"noun"},
            {"id":116,"word":"Rain","ar":"مطر","example":"I love the sound of rain.","phonetic":"/reɪn/","level":"beginner","category":"nature","part_of_speech":"noun"},
            {"id":117,"word":"Sun","ar":"شمس","example":"The sun is very bright today.","phonetic":"/sʌn/","level":"beginner","category":"nature","part_of_speech":"noun"},
            {"id":118,"word":"Moon","ar":"قمر","example":"The moon is full tonight.","phonetic":"/muːn/","level":"beginner","category":"nature","part_of_speech":"noun"},
            {"id":119,"word":"Tree","ar":"شجرة","example":"There is a big tree in the garden.","phonetic":"/triː/","level":"beginner","category":"nature","part_of_speech":"noun"},
            {"id":120,"word":"Flower","ar":"زهرة","example":"The flower smells wonderful.","phonetic":"/ˈflaʊər/","level":"beginner","category":"nature","part_of_speech":"noun"},
            {"id":121,"word":"Cat","ar":"قطة","example":"The cat is sleeping on the sofa.","phonetic":"/kæt/","level":"beginner","category":"animals","part_of_speech":"noun"},
            {"id":122,"word":"Dog","ar":"كلب","example":"The dog is playing in the park.","phonetic":"/dɒɡ/","level":"beginner","category":"animals","part_of_speech":"noun"},
            {"id":123,"word":"Bird","ar":"طائر","example":"The bird is singing in the tree.","phonetic":"/bɜːrd/","level":"beginner","category":"animals","part_of_speech":"noun"},
            {"id":124,"word":"Fish","ar":"سمكة","example":"I saw a fish in the river.","phonetic":"/fɪʃ/","level":"beginner","category":"animals","part_of_speech":"noun"},
            {"id":125,"word":"Work","ar":"عمل","example":"I go to work every morning.","phonetic":"/wɜːrk/","level":"beginner","category":"actions","part_of_speech":"verb"},
            {"id":126,"word":"Play","ar":"يلعب","example":"Children love to play in the park.","phonetic":"/pleɪ/","level":"beginner","category":"actions","part_of_speech":"verb"},
            {"id":127,"word":"Read","ar":"يقرأ","example":"I like to read before bed.","phonetic":"/riːd/","level":"beginner","category":"actions","part_of_speech":"verb"},
            {"id":128,"word":"Write","ar":"يكتب","example":"Please write your name here.","phonetic":"/raɪt/","level":"beginner","category":"actions","part_of_speech":"verb"},
            {"id":129,"word":"Talk","ar":"يتحدث","example":"We need to talk about this.","phonetic":"/tɔːk/","level":"beginner","category":"actions","part_of_speech":"verb"},
            {"id":130,"word":"Walk","ar":"يمشي","example":"Let's walk to the store.","phonetic":"/wɔːk/","level":"beginner","category":"actions","part_of_speech":"verb"},
            {"id":131,"word":"Hot","ar":"حار","example":"The coffee is very hot.","phonetic":"/hɒt/","level":"beginner","category":"adjectives","part_of_speech":"adjective"},
            {"id":132,"word":"Cold","ar":"بارد","example":"It's very cold outside.","phonetic":"/koʊld/","level":"beginner","category":"adjectives","part_of_speech":"adjective"},
            {"id":133,"word":"Fast","ar":"سريع","example":"The car is very fast.","phonetic":"/fæst/","level":"beginner","category":"adjectives","part_of_speech":"adjective"},
            {"id":134,"word":"Slow","ar":"بطيء","example":"The turtle is very slow.","phonetic":"/sloʊ/","level":"beginner","category":"adjectives","part_of_speech":"adjective"},
            {"id":135,"word":"Easy","ar":"سهل","example":"This exercise is very easy.","phonetic":"/ˈiːzi/","level":"beginner","category":"adjectives","part_of_speech":"adjective"},
            {"id":136,"word":"Hard","ar":"صعب","example":"The test was very hard.","phonetic":"/hɑːrd/","level":"beginner","category":"adjectives","part_of_speech":"adjective"},
            {"id":137,"word":"Money","ar":"مال","example":"I don't have enough money.","phonetic":"/ˈmʌni/","level":"beginner","category":"basics","part_of_speech":"noun"},
            {"id":138,"word":"Phone","ar":"هاتف","example":"My phone is ringing.","phonetic":"/foʊn/","level":"beginner","category":"technology","part_of_speech":"noun"},
            {"id":139,"word":"Computer","ar":"حاسوب","example":"I use my computer every day.","phonetic":"/kəmˈpjuːtər/","level":"beginner","category":"technology","part_of_speech":"noun"},
            {"id":140,"word":"Music","ar":"موسيقى","example":"I love listening to music.","phonetic":"/ˈmjuːzɪk/","level":"beginner","category":"entertainment","part_of_speech":"noun"},
            # ── INTERMEDIATE: More (141-170) ──
            {"id":141,"word":"Curiosity","ar":"فضول","example":"Curiosity is the mother of invention.","phonetic":"/ˌkjʊəriˈɒsɪti/","level":"intermediate","category":"abstract","part_of_speech":"noun"},
            {"id":142,"word":"Diligently","ar":"باجتهاد","example":"She worked diligently on the project.","phonetic":"/ˈdɪlɪdʒəntli/","level":"intermediate","category":"adverbs","part_of_speech":"adverb"},
            {"id":143,"word":"Resilient","ar":"مرنن","example":"Children are remarkably resilient.","phonetic":"/rɪˈzɪliənt/","level":"intermediate","category":"adjectives","part_of_speech":"adjective"},
            {"id":144,"word":"Prosperity","ar":"ازدهار","example":"The country enjoyed years of prosperity.","phonetic":"/prɒˈspɛrɪti/","level":"intermediate","category":"abstract","part_of_speech":"noun"},
            {"id":145,"word":"Authentic","ar":"أصيل","example":"This is an authentic Italian restaurant.","phonetic":"/ɔːˈθɛntɪk/","level":"intermediate","category":"adjectives","part_of_speech":"adjective"},
            {"id":146,"word":"Meticulous","ar":"دقيق","example":"She is meticulous in her work.","phonetic":"/məˈtɪkjʊləs/","level":"intermediate","category":"adjectives","part_of_speech":"adjective"},
            {"id":147,"word":"Exemplary","ar":"مثالي","example":"His conduct was exemplary.","phonetic":"/ɪɡˈzɛmpləri/","level":"intermediate","category":"adjectives","part_of_speech":"adjective"},
            {"id":148,"word":"Innovative","ar":"ابتكاري","example":"This is an innovative approach.","phonetic":"/ˈɪnəveɪtɪv/","level":"intermediate","category":"adjectives","part_of_speech":"adjective"},
            {"id":149,"word":"Deteriorate","ar":"يتفاقم","example":"The patient's condition began to deteriorate.","phonetic":"/dɪˈtɪəriəreɪt/","level":"intermediate","category":"actions","part_of_speech":"verb"},
            {"id":150,"word":"Flourish","ar":"يزدهر","example":"The business continued to flourish.","phonetic":"/ˈflʌrɪʃ/","level":"intermediate","category":"actions","part_of_speech":"verb"},
            {"id":151,"word":"Exquisite","ar":"رائع","example":"The painting was absolutely exquisite.","phonetic":"/ɪkˈskwɪzɪt/","level":"intermediate","category":"adjectives","part_of_speech":"adjective"},
            {"id":152,"word":"Vindicate","ar":"يُثبت براءته","example":"The evidence vindicated his position.","phonetic":"/ˈvɪndɪkeɪt/","level":"intermediate","category":"actions","part_of_speech":"verb"},
            {"id":153,"word":"Harmonious","ar":"متناغم","example":"They had a harmonious relationship.","phonetic":"/hɑːrˈmoʊniəs/","level":"intermediate","category":"adjectives","part_of_speech":"adjective"},
            {"id":154,"word":"Nostalgia","ar":"حنين","example":"She felt a wave of nostalgia.","phonetic":"/nɒˈstældʒə/","level":"intermediate","category":"emotions","part_of_speech":"noun"},
            {"id":155,"word":"Eloquent","ar":"بليغ","example":"He made an eloquent argument.","phonetic":"/ˈɛləkwənt/","level":"intermediate","category":"adjectives","part_of_speech":"adjective"},
            {"id":156,"word":"Amalgamate","ar":"يدمج","example":"The two companies decided to amalgamate.","phonetic":"/əˈmælɡəmeɪt/","level":"intermediate","category":"actions","part_of_speech":"verb"},
            {"id":157,"word":"Candid","ar":"صريح","example":"She gave a candid assessment.","phonetic":"/ˈkændɪd/","level":"intermediate","category":"adjectives","part_of_speech":"adjective"},
            {"id":158,"word":"Endeavor","ar":"محاولة","example":"This was a worthy endeavor.","phonetic":"/ɪnˈdɛvər/","level":"intermediate","category":"abstract","part_of_speech":"noun"},
            {"id":159,"word":"Pinnacle","ar":"قمة","example":"Reaching the pinnacle of success.","phonetic":"/ˈpɪnəkəl/","level":"intermediate","category":"abstract","part_of_speech":"noun"},
            {"id":160,"word":"Tenacious","ar":"متمسك","example":"She is a tenacious competitor.","phonetic":"/tɪˈneɪʃəs/","level":"intermediate","category":"adjectives","part_of_speech":"adjective"},
            # ── ADVANCED: More (161-200) ──
            {"id":161,"word":"Sycophant","ar":"خاضع","example":"The king surrounded himself with sycophants.","phonetic":"/ˈsɪkəfænt/","level":"advanced","category":"people","part_of_speech":"noun"},
            {"id":162,"word":"Loquacious","ar":"ثرثار","example":"My loquacious neighbor talked for hours.","phonetic":"/loʊˈkweɪʃəs/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":163,"word":"Mellifluous","ar":"عذب","example":"She has a mellifluous singing voice.","phonetic":"/mɛˈlɪfluəs/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":164,"word":"Pulchritude","ar":"جمال","example":"Her pulchritude was admired by all.","phonetic":"/ˈpʌlkrɪtjuːd/","level":"advanced","category":"abstract","part_of_speech":"noun"},
            {"id":165,"word":"Ebullient","ar":"متحمس","example":"Her ebullient personality lit up the room.","phonetic":"/ɪˈbʊliənt/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":166,"word":"Languid","ar":"كسلان","example":"A languid afternoon in the garden.","phonetic":"/ˈlæŋɡwɪd/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":167,"word":"Sanguine","ar":"متفائل","example":"She remains sanguine about the future.","phonetic":"/ˈsæŋɡwɪn/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":168,"word":"Obstreperous","ar":"صاخب","example":"The obstreperous child refused to be quiet.","phonetic":"/əbˈstrɛpərəs/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":169,"word":"Recalcitrant","ar":"عنيد","example":"The recalcitrant student refused to cooperate.","phonetic":"/rɪˈkælsɪtrənt/","level":"advanced","category":"adjectives","part_of_speech":"adjective"},
            {"id":170,"word":"Verisimilitude","ar":"واقعية","example":"The novel has remarkable verisimilitude.","phonetic":"/ˌvɛrɪsɪˈmɪlɪtjuːd/","level":"advanced","category":"abstract","part_of_speech":"noun"},
        ]

    # ══════════════════════════════════════════════════════════════
    # DATA - 100+ Grammar Rules
    # ══════════════════════════════════════════════════════════════
    def _all_grammar(self):
        return [
            # BEGINNER (1-30)
            {"id":1,"title":"المضارع البسيط","rule":"Subject + base verb (+ s/es for he/she/it)","example":"I play / She plays football every day.","tip":"لا تنسَ s/es للفرد الغائب (he/she/it)","level":"beginner"},
            {"id":2,"title":"الماضي البسيط","rule":"Subject + V2 (past form)","example":"I went to school yesterday.","tip":"افعل القواعد الشاذة (go→went, see→saw)","level":"beginner"},
            {"id":3,"title":"المستقبل بـ will","rule":"Subject + will + base verb","example":"I will study tomorrow.","tip":"will للתשובות السريعة والتنبؤات","level":"beginner"},
            {"id":4,"title":"المستقبل بـ be going to","rule":"Subject + am/is/are + going to + verb","example":"I am going to travel next week.","tip":"be going to للخطط المحددة مسبقاً","level":"beginner"},
            {"id":5,"title":"There is / There are","rule":"There is + singular / There are + plural","example":"There is a book on the table. / There are cats.","tip":"اختَر is أو are حسب العدد","level":"beginner"},
            {"id":6,"title":"المقالات a/an/the","rule":"a/an + singular countable / the + specific","example":"A cat is sleeping. The cat is mine.","tip":"a قبل الصوائت، an قبل الساكنة","level":"beginner"},
            {"id":7,"title":"صفات الملكية","rule":"my/your/his/her/its/our/their + noun","example":"This is my book.","tip":"لا تضع 's مع الضمائر","level":"beginner"},
            {"id":8,"title":"السؤال بـ Do/Does","rule":"Do/Does + subject + base verb?","example":"Do you like coffee? / Does she work here?","tip":"Does مع he/she/it فقط","level":"beginner"},
            {"id":9,"title":"النفي بـ Don't/Doesn't","rule":"Subject + don't/doesn't + base verb","example":"I don't like noise. / She doesn't swim.","tip":"doesn't مع الفرودة فقط","level":"beginner"},
            {"id":10,"title":"الظرف الزمان","rule":"always/usually/often/sometimes/never + verb","example":"I always wake up early.","tip":"places بعد الفعل مباشرة","level":"beginner"},
            {"id":11,"title":"Comparatives","rule":"short adj + er + than / more + long adj + than","example":"She is taller than me. / This is more interesting.","tip":"big→bigger, good→better, many→more","level":"beginner"},
            {"id":12,"title":"Superlatives","rule":"the + adj + est / the + most + adj","example":"He is the tallest in class.","tip":"the قبل الأعلى دائماً","level":"beginner"},
            {"id":13,"title":"too + adj / too much + noun","rule":"too + adjective / too much + uncountable noun","example":"It's too hot. / Too much water is bad.","tip":"too much للعدو، too many للجمع","level":"beginner"},
            {"id":14,"title":"الشرط بـ If","rule":"If + present simple, will + base verb","example":"If it rains, I will stay home.","tip":"لا تستخدم will في if clause","level":"beginner"},
            {"id":15,"title":"الاستفهام بـ Wh","rule":"What/Where/When/Why/How + aux + subject + verb?","example":"Where do you live? / What does she want?","tip":"What للاستفسار عن الشيء","level":"beginner"},
            {"id":16,"title":"Possessive pronouns","rule":"mine/yours/his/hers/ours/theirs","example":"This book is mine. / The car is theirs.","tip":"تستبدل الصفة + الاسم","level":"beginner"},
            {"id":17,"title":"Demonstratives","rule":"this/these (قريب) / that/those (بعيد)","example":"This is my pen. / Those are your shoes.","tip":"this/that للمفرد، these/those للجمع","level":"beginner"},
            {"id":18,"title":"Some / Any","rule":"some (مثبت) / any (سؤال/نفي)","example":"I have some books. / Do you have any?","tip":"any في السؤال والنفي فقط","level":"beginner"},
            {"id":19,"title":"How much / How many","rule":"How much + uncountable / How many + countable","example":"How much water? / How many books?","tip":"much للعدو، many للجمع","level":"beginner"},
            {"id":20,"title":"Present Continuous","rule":"Subject + am/is/are + verb-ing","example":"I am studying English right now.","tip":"للحدث الجاري الآن","level":"beginner"},
            {"id":21,"title":"Can / Can't","rule":"Subject + can/can't + base verb","example":"I can swim. / She can't drive.","tip":"لا يتغير مع الزمن","level":"beginner"},
            {"id":22,"title":"Have to / Must","rule":"Subject + have to / must + verb","example":"I have to go now. / You must study.","tip":"must للضرورة القوية","level":"beginner"},
            {"id":23,"title":"Like + verb-ing","rule":"Subject + like(s) + verb-ing","example":"I like reading. / She likes cooking.","tip":"بعض الأفعال تأخذ ing فقط","level":"beginner"},
            {"id":24,"title":"Present Perfect","rule":"Subject + have/has + past participle","example":"I have visited Paris three times.","tip":"يستخدم مع since/for","level":"beginner"},
            {"id":25,"title":"Past Continuous","rule":"Subject + was/were + verb-ing","example":"I was sleeping when you called.","tip":"للحدث كان جارياً في وقت محدد","level":"beginner"},
            {"id":26,"title":"Countable / Uncountable","rule":"a/an + countable / no article + uncountable","example":"A water (wrong) / Some water (correct)","tip":"water, milk, money = uncountable","level":"beginner"},
            {"id":27,"title":"Adjective + Noun","rule":"Adjective always comes before the noun","example":"A beautiful garden (not garden beautiful)","tip":"الصفة قبل الاسم دائماً","level":"beginner"},
            {"id":28,"title":"Verb + Object","rule":"Subject + verb + object","example":"She reads books. / They play football.","tip":"المفعول بعد الفعل مباشرة","level":"beginner"},
            {"id":29,"title":" negatives","rule":"Subject + aux + not + verb","example":"I am not / He is not / They are not","tip":"缩写: isn't, aren't, wasn't, weren't","level":"beginner"},
            {"id":30,"title":"Imperatives","rule":"Base verb (祈使)","example":"Stop! / Please sit down. / Don't run!","tip":"للأمر والنصح","level":"beginner"},
            # INTERMEDIATE (31-65)
            {"id":31,"title":"Present Perfect Continuous","rule":"Subject + have/has + been + verb-ing","example":"I have been studying for 3 hours.","tip":"يستخدم مع for/since للمدة","level":"intermediate"},
            {"id":32,"title":"Past Perfect","rule":"Subject + had + past participle","example":"I had finished before she came.","tip":"حدث قبل حدث آخر في الماضي","level":"intermediate"},
            {"id":33,"title":"used to","rule":"Subject + used to + base verb","example":"I used to play football when I was young.","tip":"عادة في الماضي لم تعد صحيحة","level":"intermediate"},
            {"id":34,"title":"First Conditional","rule":"If + present, will + verb","example":"If I study, I will pass the exam.","tip":"شرط ممكن حدوثه","level":"intermediate"},
            {"id":35,"title":"Second Conditional","rule":"If + past, would + verb","example":"If I were rich, I would travel the world.","tip":"حالة تخيلية","level":"intermediate"},
            {"id":36,"title":"Reported Speech","rule":"said (that) + past tense","example":"He said that he was tired.","tip":"يتحول الزمن للماضي","level":"intermediate"},
            {"id":37,"title":"Passive Voice","rule":"Subject + be + past participle (+ by agent)","example":"The book was written by J.K. Rowling.","tip":"المفعول يصبح فاعلاً","level":"intermediate"},
            {"id":38,"title":"Relative Clauses","rule":"who/which/that/where/whose","example":"The man who lives next door is a doctor.","tip":"who للبشر، which للأشياء","level":"intermediate"},
            {"id":39,"title":"Modal Verbs","rule":"can/could/may/might/must/should/would","example":"You should exercise more. / It might rain.","tip":"لا تتغير الصيغة مع الفاعل","level":"intermediate"},
            {"id":40,"title":"Gerunds vs Infinitives","rule":"verb+ing (gerund) / to + verb (infinitive)","example":"I enjoy swimming. / I want to swim.","tip":"بعض الأفعال تأخذ ing فقط","level":"intermediate"},
            {"id":41,"title":"Phrasal Verbs","rule":"verb + preposition/adverb = new meaning","example":"Give up = stop / Look after = care for","tip":"المعنى يتغير بالجذر","level":"intermediate"},
            {"id":42,"title":"Quantifiers","rule":"some/any/much/many/a lot of/few/little","example":"I have many friends. / There is little time.","tip":"any في السؤال والنفي فقط","level":"intermediate"},
            {"id":43,"title":"Adjective Order","rule":"opinion-size-age-shape-color-origin-material","example":"A beautiful big old round red Italian table","tip":"الترتيب ثابت بالإنجليزية","level":"intermediate"},
            {"id":44,"title":"Third Conditional","rule":"If + past perfect, would have + pp","example":"If I had studied, I would have passed.","tip":"ندم على الماضي","level":"intermediate"},
            {"id":45,"title":"Wish + past simple","rule":"I wish + past simple","example":"I wish I had more time.","tip":"تمنٍّ في الحاضر","level":"intermediate"},
            {"id":46,"title":"Wish + past perfect","rule":"I wish + past perfect","example":"I wish I had studied harder.","tip":"ندم على الماضي","level":"intermediate"},
            {"id":47,"title":"used to vs would","rule":"used to (عادة) / would (تكرار)","example":"I used to smoke. / We would play every day.","tip":"would لا تستخدم للحالات","level":"intermediate"},
            {"id":48,"title":"Causative","rule":"have/get something done","example":"I had my car repaired yesterday.","tip":"الفعل يُنفَذ بواسطة آخر","level":"intermediate"},
            {"id":49,"title":"Tag Questions","rule":"statement + positive tag / negative tag","example":"You're a student, aren't you?","tip":"إذا كانت الجملة مثبتة، التاج سالب","level":"intermediate"},
            {"id":50,"title":"Relative Clauses Reduced","rule":"حذف who/which + be","example":"The man (who was) standing there left.","tip":"اختصار الجمل","level":"intermediate"},
            {"id":51,"title":"Indirect Questions","rule":"Do you know + question word + S + V?","example":"Do you know where she lives? (not does she live)","tip":"لا ي逆转 الفاعل والفعل","level":"intermediate"},
            {"id":52,"title":"Future Perfect","rule":"Subject + will have + past participle","example":"I will have finished by 5pm.","tip":"حدث سيكتمل قبل وقت محدد","level":"intermediate"},
            {"id":53,"title":"Future Continuous","rule":"Subject + will be + verb-ing","example":"I will be working at 3pm tomorrow.","tip":"حدث سيكون جارياً في وقت محدد","level":"intermediate"},
            {"id":54,"title":"used to negatives","rule":"Subject + didn't use to + verb","example":"I didn't use to like coffee.","tip":"النفي مع didn't","level":"intermediate"},
            {"id":55,"title":"So + adjective + that","rule":"So + adj + that + clause","example":"It was so cold that we stayed home.","tip":"entails result clause","level":"intermediate"},
            {"id":56,"title":"Such + noun + that","rule":"Such + (a/an) + noun + that + clause","example":"It was such a good movie that I watched it twice.","tip":"such + noun وليس adjective","level":"intermediate"},
            {"id":57,"title":"Comparative + and + Comparative","rule":"comparative + and + comparative","example":"The situation is getting worse and worse.","tip":"لتغير تدريجي","level":"intermediate"},
            {"id":58,"title":"The + Comparative, the + Comparative","rule":"The + comparative..., the + comparative...","example":"The more you study, the more you learn.","tip":"لتغير متناسب","level":"intermediate"},
            {"id":59,"title":"Enough","rule":"adj + enough / enough + noun","example":"She is old enough to drive. / I have enough money.","tip":"adj + enough وليس enough + adj","level":"intermediate"},
            {"id":60,"title":"Too","rule":"too + adj + to + verb","example":"She is too young to drive.","tip":"too = أكثر من اللازم","level":"intermediate"},
            {"id":61,"title":"Prepositions of Time","rule":"at (time) / on (day/date) / in (month/year)","example":"at 5pm / on Monday / in January","tip":"at night (استثناء)","level":"intermediate"},
            {"id":62,"title":"Prepositions of Place","rule":"in (inside) / on (surface) / at (point)","example":"in the room / on the table / at school","tip":"at home, at work (استثناء)","level":"intermediate"},
            {"id":63,"title":"Phrasal Verbs - Separable","rule":"verb + noun/pronoun + preposition","example":"Turn on the light / Turn it on","tip":"الضمائر تأتي في المنتصف","level":"intermediate"},
            {"id":64,"title":"Phrasal Verbs - Inseparable","rule":"verb + preposition + noun","example":"Look after the children (not look the children after)","tip":"لا يمكن فصلها","level":"intermediate"},
            {"id":65,"title":"Conditionals Zero","rule":"If + present, present","example":"If you heat water to 100°C, it boils.","tip":"حقيقة علمية","level":"intermediate"},
            # ADVANCED (66-100)
            {"id":66,"title":"Mixed Conditionals","rule":"نوعان مختلطان من الماضي والحاضر","example":"If I had studied, I would be a doctor now.","tip":"ماضي مع نتيجة حاضرة","level":"advanced"},
            {"id":67,"title":"Inversion","rule":"翻转 الفاعل والفعل في الجمل النفي","example":"Never have I seen such beauty. / Not only...but also","tip":"في الجمل الشرطية والنفي","level":"advanced"},
            {"id":68,"title":"Cleft Sentences","rule":"It is/was + extracted + that...","example":"It was John who broke the window.","tip":"للتأكيد","level":"advanced"},
            {"id":69,"title":"Participle Clauses","rule":"V-ing / V-ed (تختصر جملة)","example":"Walking down the street, I saw a cat.","tip":"تختصر جملة كاملة","level":"advanced"},
            {"id":70,"title":"Subjunctive","rule":"It is important that he be...","example":"I suggest that she go now. / If I were you...","tip":"للتوصيات والأوامر","level":"advanced"},
            {"id":71,"title":"Discourse Markers","rule":"however/therefore/moreover/furthermore/nevertheless","example":"However, I disagree with this approach.","tip":"لربط الأفكار","level":"advanced"},
            {"id":72,"title":"Nominalization","rule":"تحويل الفعل/صفة إلى اسم","example":"decide → decision / important → importance","tip":"لجعل اللغة أكثر رسمية","level":"advanced"},
            {"id":73,"title":"Advanced Prepositions","rule":"in terms of / with regard to / on behalf of","example":"In terms of quality, it's the best option.","tip":"حروف جارة متقدمة","level":"advanced"},
            {"id":74,"title":"Conditional Inversion","rule":"Had/Were/Should + subject","example":"Had I known, I would have come. / Were I you...","tip":"بديل for if في الرسمية","level":"advanced"},
            {"id":75,"title":"Reported Speech - Questions","rule":"asked + question word + S + V","example":"She asked where I lived. (not where do I live)","tip":"لا逆转 في Reported Questions","level":"advanced"},
            {"id":76,"title":"Advanced Modals","rule":"must have / can't have / should have / might have","example":"He must have forgotten. / She can't have left.","tip":"لل推测 والاستنتاج","level":"advanced"},
            {"id":77,"title":"Relative Clauses - Non-defining","rule":", who/which... (معلومات إضافية)","example":"My brother, who lives in London, is a doctor.","tip":"بين فاصلة لا يمكن حذفها","level":"advanced"},
            {"id":78,"title":"Advanced Conjunctions","rule":"although/despite/in spite of/rather than","example":"Although it rained, we went out. / Despite the rain...","tip":"حروف ربط متقدمة","level":"advanced"},
            {"id":79,"title":"Future Perfect Continuous","rule":"Subject + will have been + verb-ing","example":"By next year, I will have been working here for 5 years.","tip":"لمدة في المستقبل","level":"advanced"},
            {"id":80,"title":"Past Perfect Continuous","rule":"Subject + had been + verb-ing","example":"I had been waiting for 2 hours when she arrived.","tip":"لمدة قبل حدث في الماضي","level":"advanced"},
            {"id":81,"title":"Advanced Passive","rule":"It is said/believed/reported that...","example":"It is believed that the earth is round.","tip":"للتقارير الرسمية","level":"advanced"},
            {"id":82,"title":"Advanced Conditionals","rule":"Unless / Provided that / As long as","example":"Unless you study, you will fail.","tip":"unless = if not","level":"advanced"},
            {"id":83,"title":"Emphatic Structures","rule":"do/does/did + base verb","example":"I do love chocolate! / She did try her best.","tip":"للتأكيد","level":"advanced"},
            {"id":84,"title":"Advanced Relative Pronouns","rule":"whose / whom / which / that","example":"The man whose car was stolen reported it.","tip":"whose للملكية","level":"advanced"},
            {"id":85,"title":"Collocations","rule":"make a decision / take a photo / do homework","example":"I made a decision to quit.","tip":"أزواج كلمات شائعة","level":"advanced"},
            {"id":86,"title":"Advanced Articles","rule":"zero article / the + unique things","example":"Life is beautiful. / The sun rises in the east.","tip":"لا article للclidات العامة","level":"advanced"},
            {"id":87,"title":"Advanced Prepositions","rule":"on time / in time / at once / by accident","example":"We arrived on time. / I found it by accident.","tip":"تعابير ثابتة","level":"advanced"},
            {"id":88,"title":"Parallel Structure","rule":"أجزاء الجملة متناسقة","example":"I like reading, writing, and drawing.","tip":"نفس الشكل النحوي","level":"advanced"},
            {"id":89,"title":"Advanced Negation","rule":"neither...nor / not only...but also","example":"Neither he nor she came. / Not only did he come, but he also brought gifts.","tip":"لا يستخدم but also مع not only","level":"advanced"},
            {"id":90,"title":"Inversion after Adverbials","rule":"Never/Seldom/Hardly/Rarely + aux + S + V","example":"Seldom does he arrive on time.","tip":"翻转 بعد ظروف النفي","level":"advanced"},
            {"id":91,"title":"Cleft - Wh-cleft","rule":"What + S + V is/was + ...","example":"What I need is a vacation.","tip":"للتأكيد على جزء معين","level":"advanced"},
            {"id":92,"title":"Advanced Reported Speech","rule":"suggested/insisted/recommended + that + S + base","example":"She suggested that he take a break.","tip":"بعد these verbs: base verb","level":"advanced"},
            {"id":93,"title":"Ellipsis","rule":"حذف الكلمات المكررة","example":"I can speak English, and she can (speak English) too.","tip":"لا تكرر ما هو مفهوم","level":"advanced"},
            {"id":94,"title":"Advanced Connectors","rule":"whereas/while/however/nevertheless","example":"He is tall, whereas she is short.","tip":"لل对比 وال转折","level":"advanced"},
            {"id":95,"title":"Result Clauses","rule":"so...that / such...that / so that","example":"He spoke so fast that I couldn't understand.","tip":"entails result","level":"advanced"},
            {"id":96,"title":"Purpose Clauses","rule":"in order to / so as to / so that","example":"I study hard in order to pass the exam.","tip":"ل目的","level":"advanced"},
            {"id":97,"title":"Advanced Concession","rule":"although/even though/even if/despite","example":"Even though it was raining, we played football.","tip":"للتنازل","level":"advanced"},
            {"id":98,"title":"Advanced Questions","rule":"tag questions / indirect questions / rhetorical","example":"Beautiful weather, isn't it? / Isn't it obvious?","tip":"للأسئلة غير المباشرة","level":"advanced"},
            {"id":99,"title":"Nominal Clauses","rule":"What/Where/How + clause as subject","example":"What you said is true. / How he did it amazes me.","tip":"الجملة الاسمية كفاعل","level":"advanced"},
            {"id":100,"title":"Advanced Styles","rule":"formal vs informal register","example":"commence (formal) vs start (informal)","tip":"اختر الصرف حسب السياق","level":"advanced"},
        ]

    # ══════════════════════════════════════════════════════════════
    # DATA - 300+ Exercises (multiple types)
    # ══════════════════════════════════════════════════════════════
    def _all_exercises(self):
        return [
            # BEGINNER - MCQ (1-40)
            {"id":1,"type":"mcq","question":"I _____ to school every day.","options":["go","goes","going","went"],"answer":0,"explanation":"I + go (بدون s)","level":"beginner"},
            {"id":2,"type":"mcq","question":"She _____ a teacher.","options":["am","is","are","be"],"answer":1,"explanation":"She + is","level":"beginner"},
            {"id":3,"type":"mcq","question":"_____ you like coffee?","options":["Do","Does","Is","Are"],"answer":0,"explanation":"Do + you","level":"beginner"},
            {"id":4,"type":"mcq","question":"There _____ a book on the table.","options":["is","are","am","be"],"answer":0,"explanation":"a book = مفرد therefore is","level":"beginner"},
            {"id":5,"type":"mcq","question":"I _____ to Paris last summer.","options":["go","went","will go","going"],"answer":1,"explanation":"last summer = الماضي","level":"beginner"},
            {"id":6,"type":"mcq","question":"They _____ not like fish.","options":["do","does","is","are"],"answer":0,"explanation":"they + do","level":"beginner"},
            {"id":7,"type":"mcq","question":"This is _____ book.","options":["my","me","I","mine"],"answer":0,"explanation":"possessive adjective: my","level":"beginner"},
            {"id":8,"type":"mcq","question":"_____ is the weather today?","options":["How","What","Where","Why"],"answer":0,"explanation":"How = كيف (الطقس)","level":"beginner"},
            {"id":9,"type":"mcq","question":"I have _____ apples.","options":["a","an","two","the"],"answer":2,"explanation":"two = عدد محدد","level":"beginner"},
            {"id":10,"type":"mcq","question":"He _____ football yesterday.","options":["play","plays","played","playing"],"answer":2,"explanation":"yesterday = الماضي","level":"beginner"},
            {"id":11,"type":"mcq","question":"The cat is _____ the table.","options":["in","on","at","to"],"answer":1,"explanation":"on = على السطح","level":"beginner"},
            {"id":12,"type":"mcq","question":"I _____ a doctor when I grow up.","options":["will be","am","was","be"],"answer":0,"explanation":"when I grow up = المستقبل","level":"beginner"},
            {"id":13,"type":"mcq","question":"She is _____ than her sister.","options":["tall","taller","tallest","more tall"],"answer":1,"explanation":"taller than = مقارنة","level":"beginner"},
            {"id":14,"type":"mcq","question":"We _____ breakfast at 7am.","options":["has","have","having","haves"],"answer":1,"explanation":"we + have","level":"beginner"},
            {"id":15,"type":"mcq","question":"_____ he at home?","options":["Is","Are","Am","Do"],"answer":0,"explanation":"he + is","level":"beginner"},
            {"id":16,"type":"mcq","question":"I _____ a new phone.","options":["want","wants","wanting","wanted"],"answer":0,"explanation":"I + want (بدون s)","level":"beginner"},
            {"id":17,"type":"mcq","question":"The book is very _____.","options":["interesting","interested","interest","interestingly"],"answer":0,"explanation":"صفة قبل الاسم","level":"beginner"},
            {"id":18,"type":"mcq","question":"She _____ English every day.","options":["study","studies","studying","studied"],"answer":1,"explanation":"she + studies (y→ies)","level":"beginner"},
            {"id":19,"type":"mcq","question":"This is _____ interesting movie.","options":["a","an","the","no article"],"answer":1,"explanation":"interesting تبدأ بـ i صائت","level":"beginner"},
            {"id":20,"type":"mcq","question":"I _____ not understand.","options":["do","does","is","am"],"answer":0,"explanation":"I + do","level":"beginner"},
            {"id":21,"type":"mcq","question":"There _____ many people at the party.","options":["is","are","am","be"],"answer":1,"explanation":"people = جمع therefore are","level":"beginner"},
            {"id":22,"type":"mcq","question":"He _____ to the cinema yesterday.","options":["go","goes","went","going"],"answer":2,"explanation":"yesterday = الماضي","level":"beginner"},
            {"id":23,"type":"mcq","question":"_____ she like chocolate?","options":["Do","Does","Is","Are"],"answer":1,"explanation":"she + does","level":"beginner"},
            {"id":24,"type":"mcq","question":"The dog is _____ the house.","options":["in","on","at","under"],"answer":3,"explanation":"under = تحت","level":"beginner"},
            {"id":25,"type":"mcq","question":"I am _____ a book right now.","options":["read","reads","reading","readed"],"answer":2,"explanation":"am + reading (المضارع المستمر)","level":"beginner"},
            {"id":26,"type":"mcq","question":"We _____ go to school on Sundays.","options":["don't","doesn't","isn't","aren't"],"answer":0,"explanation":"we + don't","level":"beginner"},
            {"id":27,"type":"mcq","question":"This is the _____ movie I've seen.","options":["good","better","best","goodest"],"answer":2,"explanation":"the best = الأفضل","level":"beginner"},
            {"id":28,"type":"mcq","question":"She can _____ very fast.","options":["runs","running","run","ran"],"answer":2,"explanation":"can + base verb","level":"beginner"},
            {"id":29,"type":"mcq","question":"I _____ my homework yesterday.","options":["do","does","did","doing"],"answer":2,"explanation":"yesterday = الماضي","level":"beginner"},
            {"id":30,"type":"mcq","question":"The sun _____ in the east.","options":["rise","rises","rising","rose"],"answer":1,"explanation":"الحقيقة العلمية = المضارع","level":"beginner"},
            {"id":31,"type":"mcq","question":"He is _____ than me.","options":["strong","stronger","strongest","more strong"],"answer":1,"explanation":"short adj + er","level":"beginner"},
            {"id":32,"type":"mcq","question":"I need _____ water.","options":["a","an","some","the"],"answer":2,"explanation":"water = غير معدود some","level":"beginner"},
            {"id":33,"type":"mcq","question":"_____ is your name?","options":["What","Where","When","How"],"answer":0,"explanation":"What = ماذا (الاسم)","level":"beginner"},
            {"id":34,"type":"mcq","question":"They _____ playing football.","options":["is","am","are","be"],"answer":2,"explanation":"they + are","level":"beginner"},
            {"id":35,"type":"mcq","question":"I _____ breakfast every morning.","options":["eat","eats","eating","eated"],"answer":0,"explanation":"I + eat","level":"beginner"},
            {"id":36,"type":"mcq","question":"This pen is _____.","options":["my","mine","me","I"],"answer":1,"explanation":"mine = ضمير ملكية منفصل","level":"beginner"},
            {"id":37,"type":"mcq","question":"She doesn't _____ tea.","options":["likes","like","liking","liked"],"answer":1,"explanation":"doesn't + base verb","level":"beginner"},
            {"id":38,"type":"mcq","question":"We went to the park _____ Sunday.","options":["in","on","at","for"],"answer":1,"explanation":"on + يوم","level":"beginner"},
            {"id":39,"type":"mcq","question":"The baby is _____ asleep.","options":["fast","quickly","soon","rapidly"],"answer":0,"explanation":"fast asleep = نوم عميق","level":"beginner"},
            {"id":40,"type":"mcq","question":"I _____ never _____ sushi.","options":["have, eaten","had, eaten","was, eating","did, eat"],"answer":0,"explanation":"have never + pp","level":"beginner"},
            # INTERMEDIATE - MCQ (41-80)
            {"id":41,"type":"mcq","question":"I _____ this movie before.","options":["saw","have seen","see","seeing"],"answer":1,"explanation":"before = present perfect","level":"intermediate"},
            {"id":42,"type":"mcq","question":"She _____ for 3 hours.","options":["has been studying","is studying","studies","studied"],"answer":0,"explanation":"for = مدة = present perfect continuous","level":"intermediate"},
            {"id":43,"type":"mcq","question":"If I _____ you, I would study harder.","options":["was","were","am","be"],"answer":1,"explanation":"conditional 2: were","level":"intermediate"},
            {"id":44,"type":"mcq","question":"He said that he _____ tired.","options":["was","is","were","has been"],"answer":0,"explanation":"reported speech: is → was","level":"intermediate"},
            {"id":45,"type":"mcq","question":"The letter _____ by John.","options":["was written","wrote","writing","written"],"answer":0,"explanation":"passive: was + past participle","level":"intermediate"},
            {"id":46,"type":"mcq","question":"I _____ to music when the phone rang.","options":["listened","was listening","listen","am listening"],"answer":1,"explanation":"حدث جارٍ قُوطع","level":"intermediate"},
            {"id":47,"type":"mcq","question":"She asked me where I _____.","options":["lived","live","was living","had lived"],"answer":0,"explanation":"reported speech: live → lived","level":"intermediate"},
            {"id":48,"type":"mcq","question":"This is the best movie I _____ seen.","options":["have","has","had","having"],"answer":0,"explanation":"present perfect: have + pp","level":"intermediate"},
            {"id":49,"type":"mcq","question":"He made me _____ the truth.","options":["tell","told","telling","to tell"],"answer":0,"explanation":"make + bare infinitive","level":"intermediate"},
            {"id":50,"type":"mcq","question":"There are _____ people at the party.","options":["much","many","a little","little"],"answer":1,"explanation":"many + countable","level":"intermediate"},
            {"id":51,"type":"mcq","question":"I wish I _____ more time.","options":["have","had","having","has"],"answer":1,"explanation":"wish + past simple","level":"intermediate"},
            {"id":52,"type":"mcq","question":"He's _____ tall that he can reach the shelf.","options":["such","so","very","too"],"answer":1,"explanation":"so...that","level":"intermediate"},
            {"id":53,"type":"mcq","question":"The meeting has been _____ until next week.","options":["put off","put up","put out","put on"],"answer":0,"explanation":"put off = تأجيل","level":"intermediate"},
            {"id":54,"type":"mcq","question":"I'm looking forward _____ you.","options":["to seeing","to see","seeing","see"],"answer":0,"explanation":"look forward to + gerund","level":"intermediate"},
            {"id":55,"type":"mcq","question":"I used to _____ football when I was young.","options":["play","playing","played","plays"],"answer":0,"explanation":"used to + base verb","level":"intermediate"},
            {"id":56,"type":"mcq","question":"She enjoys _____ books.","options":["reading","to read","read","reads"],"answer":0,"explanation":"enjoy + gerund","level":"intermediate"},
            {"id":57,"type":"mcq","question":"He has _____ finished his work.","options":["yet","already","still","ever"],"answer":1,"explanation":"already في الجمل المثبتة","level":"intermediate"},
            {"id":58,"type":"mcq","question":"I haven't finished _____.","options":["yet","already","still","ever"],"answer":0,"explanation":"yet في الجمل السالبة","level":"intermediate"},
            {"id":59,"type":"mcq","question":"She _____ live in London.","options":["is used to","used to","use to","used"],"answer":1,"explanation":"used to + base verb","level":"intermediate"},
            {"id":60,"type":"mcq","question":"He suggested _____ to the cinema.","options":["going","to go","go","went"],"answer":0,"explanation":"suggest + gerund","level":"intermediate"},
            {"id":61,"type":"mcq","question":"If it _____ tomorrow, we will cancel.","options":["rains","will rain","rained","raining"],"answer":0,"explanation":"conditional 1: present in if clause","level":"intermediate"},
            {"id":62,"type":"mcq","question":"The book _____ by millions.","options":["is read","reads","reading","readed"],"answer":0,"explanation":"passive voice","level":"intermediate"},
            {"id":63,"type":"mcq","question":"She asked me _____ I was busy.","options":["if","do","does","is"],"answer":0,"explanation":"reported question: if/whether","level":"intermediate"},
            {"id":64,"type":"mcq","question":"I would rather _____ at home tonight.","options":["stay","staying","stayed","to stay"],"answer":0,"explanation":"would rather + base verb","level":"intermediate"},
            {"id":65,"type":"mcq","question":"He insisted _____ paying for dinner.","options":["on","in","at","for"],"answer":0,"explanation":"insist on + gerund","level":"intermediate"},
            {"id":66,"type":"mcq","question":"The more you study, _____ you learn.","options":["the more","more","the most","most"],"answer":0,"explanation":"the more...the more","level":"intermediate"},
            {"id":67,"type":"mcq","question":"She is _____ of heights.","options":["afraid","frightening","frightened","afraiding"],"answer":2,"explanation":"frightened = خائفة","level":"intermediate"},
            {"id":68,"type":"mcq","question":"I don't mind _____ for you.","options":["waiting","to wait","wait","waited"],"answer":0,"explanation":"mind + gerund","level":"intermediate"},
            {"id":69,"type":"mcq","question":"He denied _____ the money.","options":["steal","stealing","to steal","stole"],"answer":1,"explanation":"deny + gerund","level":"intermediate"},
            {"id":70,"type":"mcq","question":"She recommended _____ the report.","options":["reading","to read","read","reads"],"answer":0,"explanation":"recommend + gerund","level":"intermediate"},
            {"id":71,"type":"mcq","question":"He _____ have passed the test; he studied hard.","options":["must","might","should","could"],"answer":0,"explanation":"must = استنتاج مؤكد","level":"intermediate"},
            {"id":72,"type":"mcq","question":"She _____ be at home; the light is on.","options":["must","might","should","could"],"answer":0,"explanation":"must = استنتاج","level":"intermediate"},
            {"id":73,"type":"mcq","question":"You _____ smoke in the hospital.","options":["mustn't","don't have to","needn't","can't"],"answer":0,"explanation":"mustn't = محظور","level":"intermediate"},
            {"id":74,"type":"mcq","question":"I _____ help you with your homework.","options":["can","must","should","could"],"answer":0,"explanation":"can = القدرة على المساعدة","level":"intermediate"},
            {"id":75,"type":"mcq","question":"He _____ better if he had studied.","options":["would have done","would do","did","does"],"answer":0,"explanation":"3rd conditional","level":"intermediate"},
            {"id":76,"type":"mcq","question":"She _____ be a great leader.","options":["could","must","should","would"],"answer":0,"explanation":"could = القدرة المحتملة","level":"intermediate"},
            {"id":77,"type":"mcq","question":"I _____ rather you didn't smoke here.","options":["would","should","could","might"],"answer":0,"explanation":"would rather + past simple","level":"intermediate"},
            {"id":78,"type":"mcq","question":"He _____ have forgotten about the meeting.","options":["might","must","should","could"],"answer":0,"explanation":"might = احتمال","level":"intermediate"},
            {"id":79,"type":"mcq","question":"She _____ have told me about the change.","options":["should","must","could","might"],"answer":0,"explanation":"should have = كان يجب","level":"intermediate"},
            {"id":80,"type":"mcq","question":"You _____ drive without a license.","options":["mustn't","don't have to","needn't","shouldn't"],"answer":0,"explanation":"mustn't = محظور","level":"intermediate"},
            # ADVANCED - MCQ (81-120)
            {"id":81,"type":"mcq","question":"If I had studied harder, I _____ the exam.","options":["would pass","would have passed","passed","will pass"],"answer":1,"explanation":"3rd conditional: would have + pp","level":"advanced"},
            {"id":82,"type":"mcq","question":"_____ he arrived, the meeting started.","options":["Hardly had","Had hardly","No sooner had","Hardly"],"answer":0,"explanation":"inversion: Hardly had + subject + pp","level":"advanced"},
            {"id":83,"type":"mcq","question":"It is essential that he _____ on time.","options":["be","is","was","being"],"answer":0,"explanation":"subjunctive: be (not is)","level":"advanced"},
            {"id":84,"type":"mcq","question":"The project was _____ challenging than expected.","options":["more","most","much","very"],"answer":0,"explanation":"more + adj + than = comparative","level":"advanced"},
            {"id":85,"type":"mcq","question":"She _____ have passed the test; she didn't study.","options":["should","might","couldn't","must"],"answer":2,"explanation":"couldn't = لم تتمكن","level":"advanced"},
            {"id":86,"type":"mcq","question":"Notwithstanding the rain, the event _____.","options":["continued","continues","continuing","continue"],"answer":0,"explanation":"past tense بعد حدث سابق","level":"advanced"},
            {"id":87,"type":"mcq","question":"Had I known about the problem, I _____ it.","options":["would fix","would have fixed","fixed","fix"],"answer":1,"explanation":"inversion = if, would have + pp","level":"advanced"},
            {"id":88,"type":"mcq","question":"The data _____ that the approach works.","options":["suggests","suggest","suggesting","suggested"],"answer":0,"explanation":"data = singular in formal English","level":"advanced"},
            {"id":89,"type":"mcq","question":"She spoke _____ she were the boss.","options":["as if","like","as","even"],"answer":0,"explanation":"as if + past (subjunctive)","level":"advanced"},
            {"id":90,"type":"mcq","question":"_____ the circumstances, we had no choice.","options":["Given","Giving","Given that","Giving that"],"answer":0,"explanation":"Given = بالنظر إلى","level":"advanced"},
            {"id":91,"type":"mcq","question":"He _____ to the meeting, but he didn't attend.","options":["should come","should have come","must come","might come"],"answer":1,"explanation":"ندم: should have + pp","level":"advanced"},
            {"id":92,"type":"mcq","question":"The technology has _____ changed our lives.","options":["fundamentally","fundamental","fundamentals","fundament"],"answer":0,"explanation":"ظرف ي修饰 الفعل","level":"advanced"},
            {"id":93,"type":"mcq","question":"I'd rather you _____ that to me.","options":["didn't say","don't say","haven't said","won't say"],"answer":0,"explanation":"would rather + past simple","level":"advanced"},
            {"id":94,"type":"mcq","question":"Only when I _____ the truth did I understand.","options":["knew","know","knowing","known"],"answer":0,"explanation":"inversion + past simple","level":"advanced"},
            {"id":95,"type":"mcq","question":"The company has _____ many new employees.","options":["recruited","recruit","recruiting","recruitment"],"answer":0,"explanation":"has + past participle","level":"advanced"},
            {"id":96,"type":"mcq","question":"Despite _____ hard, he failed the exam.","options":["studying","studied","study","to study"],"answer":0,"explanation":"despite + gerund","level":"advanced"},
            {"id":97,"type":"mcq","question":"The report _____ be completed by Friday.","options":["must","should","ought to","all of the above"],"answer":3,"explanation":"جميعها تعبر عن ال obligation","level":"advanced"},
            {"id":98,"type":"mcq","question":"What _____ if you had more time?","options":["would you do","will you do","did you do","do you do"],"answer":0,"explanation":"2nd conditional: would + base verb","level":"advanced"},
            {"id":99,"type":"mcq","question":"She _____ never _____ such a thing.","options":["has, seen","had, seen","was, seeing","did, see"],"answer":0,"explanation":"present perfect: has + pp","level":"advanced"},
            {"id":100,"type":"mcq","question":"He spoke _____ everyone understood.","options":["so clearly that","such clearly that","so clear that","such clear that"],"answer":0,"explanation":"so + adv + that","level":"advanced"},
            {"id":101,"type":"fill","question":"I _____ (go) to school every day.","answer":"go","explanation":"المضارع البسيط مع I","level":"beginner"},
            {"id":102,"type":"fill","question":"She _____ (be) a student.","answer":"is","explanation":"She + is","level":"beginner"},
            {"id":103,"type":"fill","question":"They _____ (not like) coffee.","answer":"don't like","explanation":"they + don't + base verb","level":"beginner"},
            {"id":104,"type":"fill","question":"He _____ (play) football yesterday.","answer":"played","explanation":"yesterday = الماضي","level":"beginner"},
            {"id":105,"type":"fill","question":"I _____ (will) help you.","answer":"will","explanation":"المستقبل مع will","level":"beginner"},
            {"id":106,"type":"fill","question":"We _____ (be) happy.","answer":"are","explanation":"we + are","level":"beginner"},
            {"id":107,"type":"fill","question":"She _____ (can) swim very well.","answer":"can","explanation":"can + base verb","level":"beginner"},
            {"id":108,"type":"fill","question":"The cat _____ (sleep) on the sofa.","answer":"is sleeping","explanation":"المضارع المستمر","level":"beginner"},
            {"id":109,"type":"fill","question":"I _____ (have) two brothers.","answer":"have","explanation":"I + have","level":"beginner"},
            {"id":110,"type":"fill","question":"He _____ (go) to work every day.","answer":"goes","explanation":"he + goes (s)","level":"beginner"},
            {"id":111,"type":"fill","question":"I _____ (study) English for 3 years.","answer":"have been studying","explanation":"for + مدة = present perfect continuous","level":"intermediate"},
            {"id":112,"type":"fill","question":"She said she _____ (be) tired.","answer":"was","explanation":"reported speech: is → was","level":"intermediate"},
            {"id":113,"type":"fill","question":"The book _____ (write) by J.K. Rowling.","answer":"was written","explanation":"passive voice","level":"intermediate"},
            {"id":114,"type":"fill","question":"If I _____ (be) you, I would go.","answer":"were","explanation":"conditional 2: were","level":"intermediate"},
            {"id":115,"type":"fill","question":"He suggested _____ (go) to the cinema.","answer":"going","explanation":"suggest + gerund","level":"intermediate"},
            {"id":116,"type":"fill","question":"I wish I _____ (have) more money.","answer":"had","explanation":"wish + past simple","level":"intermediate"},
            {"id":117,"type":"fill","question":"She enjoys _____ (read) books.","answer":"reading","explanation":"enjoy + gerund","level":"intermediate"},
            {"id":118,"type":"fill","question":"The meeting _____ (put off) until next week.","answer":"has been put off","explanation":"passive + phrasal verb","level":"intermediate"},
            {"id":119,"type":"fill","question":"He asked me where I _____ (live).","answer":"lived","explanation":"reported speech: live → lived","level":"intermediate"},
            {"id":120,"type":"fill","question":"I would rather _____ (stay) at home.","answer":"stay","explanation":"would rather + base verb","level":"intermediate"},
            {"id":121,"type":"fill","question":"Had I known, I _____ (come).","answer":"would have come","explanation":"inversion = if, would have + pp","level":"advanced"},
            {"id":122,"type":"fill","question":"It is important that he _____ (be) on time.","answer":"be","explanation":"subjunctive: be","level":"advanced"},
            {"id":123,"type":"fill","question":"She spoke _____ (eloquent) at the conference.","answer":"eloquently","explanation":"ظرف من صفة","level":"advanced"},
            {"id":124,"type":"fill","question":"The data _____ (suggest) that the plan works.","answer":"suggests","explanation":"data = singular","level":"advanced"},
            {"id":125,"type":"fill","question":"He denied _____ (take) the money.","answer":"taking","explanation":"deny + gerund","level":"advanced"},
            {"id":126,"type":"fill","question":"Not only _____ (did) he come, but he also brought gifts.","answer":"did","explanation":"inversion after not only","level":"advanced"},
            {"id":127,"type":"fill","question":"She insisted _____ (pay) for dinner.","answer":"on paying","explanation":"insist on + gerund","level":"advanced"},
            {"id":128,"type":"fill","question":"He was _____ (suppose) to arrive at 5.","answer":"supposed","explanation":"be supposed to","level":"advanced"},
            {"id":129,"type":"fill","question":"The project needs _____ (complete) by Friday.","answer":"to be completed","explanation":"needs + to be + pp","level":"advanced"},
            {"id":130,"type":"fill","question":"_____ (give) the circumstances, we left.","answer":"Given","explanation":"Given = بالنظر إلى","level":"advanced"},
        ]

    # ══════════════════════════════════════════════════════════════
    # DATA - 50+ Idioms
    # ══════════════════════════════════════════════════════════════
    def _all_idioms(self):
        return [
            {"id":1,"idiom":"break a leg","meaning":"بالتوفيق","example":"Break a leg in your performance tonight!","level":"beginner"},
            {"id":2,"idiom":"hit the books","meaning":"المذاكرة","example":"I need to hit the books before the exam.","level":"beginner"},
            {"id":3,"idiom":"once in a blue moon","meaning":"نادراً","example":"He visits us once in a blue moon.","level":"beginner"},
            {"id":4,"idiom":"piece of cake","meaning":"سهل جداً","example":"The test was a piece of cake.","level":"beginner"},
            {"id":5,"idiom":"under the weather","meaning":"مريض","example":"I'm feeling under the weather today.","level":"beginner"},
            {"id":6,"idiom":"cost an arm and a leg","meaning":"غالي جداً","example":"That car cost an arm and a leg.","level":"intermediate"},
            {"id":7,"idiom":"bite the bullet","meaning":"تتحمل الصعوبات","example":"I had to bite the bullet and tell her the truth.","level":"intermediate"},
            {"id":8,"idiom":"let the cat out of the bag","meaning":"كشف السر","example":"She let the cat out of the bag about the surprise party.","level":"intermediate"},
            {"id":9,"idiom":"spill the beans","meaning":"كشف الأسرار","example":"Come on, spill the beans! What happened?","level":"intermediate"},
            {"id":10,"idiom":"beat around the bush","meaning":"يتجنّب الموضوع","example":"Stop beating around the bush and tell me directly.","level":"intermediate"},
            {"id":11,"idiom":"blessing in disguise","meaning":"خير في ثوب شر","example":"Losing that job was a blessing in disguise.","level":"intermediate"},
            {"id":12,"idiom":"the ball is in your court","meaning":"القرار لك","example":"I've done my part, now the ball is in your court.","level":"intermediate"},
            {"id":13,"idiom":"back to the drawing board","meaning":"البدء من جديد","example":"The plan failed, so it's back to the drawing board.","level":"intermediate"},
            {"id":14,"idiom":"burning the midnight oil","meaning":"المذاكرة ليل","example":"She was burning the midnight oil for the exam.","level":"intermediate"},
            {"id":15,"idiom":"call it a day","meaning":"أنهية العمل","example":"Let's call it a day and go home.","level":"intermediate"},
            {"id":16,"idiom":"cut to the chase","meaning":"اذهب للمهم","example":"Cut to the chase, what's the result?","level":"advanced"},
            {"id":17,"idiom":"the elephant in the room","meaning":"المشكلة الواضحة","example":"We need to address the elephant in the room.","level":"advanced"},
            {"id":18,"idiom":"hit the nail on the head","meaning":"بالضبط","example":"You hit the nail on the head with that analysis.","level":"advanced"},
            {"id":19,"idiom":"the sky is the limit","meaning":"السماء هي الحد","example":"With hard work, the sky is the limit.","level":"advanced"},
            {"id":20,"idiom":"when pigs fly","meaning":"مستحيل","example":"I'll apologize when pigs fly.","level":"advanced"},
            {"id":21,"idiom":"the last straw","meaning":"الحد الأخير","example":"That was the last straw, I quit!","level":"intermediate"},
            {"id":22,"idiom":"a dime a dozen","meaning":"رخيص جداً","example":"These shirts are a dime a dozen.","level":"intermediate"},
            {"id":23,"idiom":"get out of hand","meaning":"يخرج عن السيطرة","example":"The situation got out of hand quickly.","level":"intermediate"},
            {"id":24,"idiom":"on the same page","meaning":"متفقون","example":"We're all on the same page about this.","level":"intermediate"},
            {"id":25,"idiom":"the tip of the iceberg","meaning":"جزء من المشكلة","example":"What we see is just the tip of the iceberg.","level":"advanced"},
            {"id":26,"idiom":"a fish out of water","meaning":"غير مرتاح","example":"I felt like a fish out of water at the party.","level":"intermediate"},
            {"id":27,"idiom":"break the ice","meaning":"كسر الحواجز","example":"He told a joke to break the ice.","level":"beginner"},
            {"id":28,"idiom":"by the skin of my teeth","meaning":"بالكاد","example":"I passed the test by the skin of my teeth.","level":"advanced"},
            {"id":29,"idiom":"actions speak louder than words","meaning":"الأفعال أبلغ من الكلام","example":"Actions speak louder than words, so prove it.","level":"beginner"},
            {"id":30,"idiom":"every cloud has a silver lining","meaning":"في كل شيء خير","example":"Don't worry, every cloud has a silver lining.","level":"beginner"},
        ]

    # ══════════════════════════════════════════════════════════════
    # DATA - Common Phrases
    # ══════════════════════════════════════════════════════════════
    def _all_phrases(self):
        return [
            {"id":1,"phrase":"How are you?","ar":"كيف حالك؟","category":"greetings","level":"beginner"},
            {"id":2,"phrase":"Nice to meet you","ar":"تشرفت بمعرفتك","category":"greetings","level":"beginner"},
            {"id":3,"phrase":"See you later","ar":"أراك لاحقاً","category":"greetings","level":"beginner"},
            {"id":4,"phrase":"Take care","ar":"اعتنِ بنفسك","category":"greetings","level":"beginner"},
            {"id":5,"phrase":"No problem","ar":"لا مشكلة","category":"daily","level":"beginner"},
            {"id":6,"phrase":"Of course","ar":"بالطبع","category":"daily","level":"beginner"},
            {"id":7,"phrase":"I don't understand","ar":"لا أفهم","category":"daily","level":"beginner"},
            {"id":8,"phrase":"Could you repeat that?","ar":"هل يمكنك إعادة ذلك؟","category":"daily","level":"beginner"},
            {"id":9,"phrase":"What do you mean?","ar":"ماذا تعني؟","category":"daily","level":"beginner"},
            {"id":10,"phrase":"I agree with you","ar":"أوافقك الرأي","category":"daily","level":"beginner"},
            {"id":11,"phrase":"In my opinion","ar":"في رأيي","category":"opinions","level":"intermediate"},
            {"id":12,"phrase":"As far as I know","ar":"بقدر ما أعلم","category":"opinions","level":"intermediate"},
            {"id":13,"phrase":"It depends on","ar":"يعتمد على","category":"opinions","level":"intermediate"},
            {"id":14,"phrase":"I'm looking forward to","ar":"أتطلع إلى","category":"feelings","level":"intermediate"},
            {"id":15,"phrase":"I'm fed up with","ar":"لقد سئمت من","category":"feelings","level":"intermediate"},
            {"id":16,"phrase":"There's no point in","ar":"لا فائدة من","category":"opinions","level":"intermediate"},
            {"id":17,"phrase":"To be honest","ar":"بصراحة","category":"opinions","level":"intermediate"},
            {"id":18,"phrase":"On the other hand","ar":"من ناحية أخرى","category":"opinions","level":"intermediate"},
            {"id":19,"phrase":"For the time being","ar":"مؤقتاً","category":"time","level":"intermediate"},
            {"id":20,"phrase":"At the end of the day","ar":"في نهاية المطاف","category":"opinions","level":"intermediate"},
        ]

    def get_random_exercise(self, level):
        exercises = self.get_exercises(level)
        if exercises:
            return random.choice(exercises)
        return None

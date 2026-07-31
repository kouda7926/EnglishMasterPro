#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EnglishMaster Pro v3.0 - Professional English Learning App
170+ Words | 100 Grammar Rules | 130 Exercises | Idioms | Phrases
"""

import os
import sys
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.core.window import Window

from database import Database
from engine import LearningEngine
from achievements import check_achievements, get_all_achievements
from sound import SoundSystem

Window.size = (400, 720)


# ══════════════════════════════════════════════════════════════
# SCREENS
# ══════════════════════════════════════════════════════════════

class SplashScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self.switch_next, 2.5)

    def switch_next(self, dt):
        self.manager.current = 'login'


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()

    def login(self):
        name = self.ids.name_input.text.strip()
        if not name:
            self.ids.error_label.text = "Please enter your name"
            return
        uid = self.app.db.add_user(name)
        self.app.current_user = uid
        self.app.sound.speak_english(f"Welcome {name}")
        self.manager.current = 'home'

    def login_existing(self, uid):
        self.app.current_user = uid
        user = self.app.db.get_user(uid)
        self.app.sound.speak_english(f"Welcome back {user['name']}")
        self.manager.current = 'home'


class HomeScreen(Screen):
    def on_enter(self):
        self.update_stats()

    def update_stats(self):
        app = App.get_running_app()
        if not app.current_user:
            return
        stats = app.db.get_stats(app.current_user)
        user = app.db.get_user(app.current_user)
        self.ids.welcome_label.text = f"Welcome, {user['name']}!"
        self.ids.level_label.text = f"Level: {stats['level'].title()}"
        self.ids.xp_label.text = f"XP: {stats['xp']}"
        self.ids.streak_label.text = f"Streak: {stats['streak']} days"
        self.ids.words_label.text = str(stats['words'])
        self.ids.grammar_label.text = str(stats['grammar'])
        self.ids.exercises_label.text = str(stats['exercises'])
        self.ids.accuracy_label.text = f"{stats['accuracy']}%"


class VocabularyScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_words = []
        self.current_index = 0
        self.showing_meaning = False

    def on_enter(self):
        app = App.get_running_app()
        level = app.db.get_level(app.current_user)
        self.current_words = app.db.get_words(level)
        self.current_index = 0
        if self.current_words:
            self.show_word()

    def show_word(self):
        if not self.current_words or self.current_index >= len(self.current_words):
            self.ids.word_area.text = "No more words!"
            return
        w = self.current_words[self.current_index]
        self.ids.word_label.text = w['word']
        self.ids.phonetic_label.text = w['phonetic']
        self.ids.meaning_label.text = "Tap to reveal"
        self.ids.example_label.text = ""
        self.ids.category_label.text = f"{w['category']} | {w['part_of_speech']}"
        self.showing_meaning = False

    def toggle_meaning(self):
        if not self.current_words or self.current_index >= len(self.current_words):
            return
        w = self.current_words[self.current_index]
        if self.showing_meaning:
            self.ids.meaning_label.text = "Tap to reveal"
            self.ids.example_label.text = ""
        else:
            self.ids.meaning_label.text = w['ar']
            self.ids.example_label.text = f"Example: {w['example']}"
            app = App.get_running_app()
            app.sound.speak_english(w['word'])
        self.showing_meaning = not self.showing_meaning

    def next_word(self):
        app = App.get_running_app()
        if self.current_words and self.current_index < len(self.current_words):
            w = self.current_words[self.current_index]
            app.db.mark_word_learned(app.current_user, w['id'])
            app.db.add_xp(app.current_user, 5)
        self.current_index += 1
        self.showing_meaning = False
        self.show_word()

    def prev_word(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.showing_meaning = False
            self.show_word()

    def hear_pronunciation(self):
        if self.current_words and self.current_index < len(self.current_words):
            w = self.current_words[self.current_index]
            App.get_running_app().sound.speak_english(w['word'])


class GrammarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.all_rules = []
        self.filter_level = 'all'

    def on_enter(self):
        self.load_rules()

    def load_rules(self):
        app = App.get_running_app()
        self.all_rules = app.db.get_grammar(self.filter_level)
        self.populate_list()

    def populate_list(self):
        self.ids.grammar_list.clear_widgets()
        for rule in self.all_rules:
            btn = CardButton(
                text=f"[b]{rule['title']}[/b]\n{rule['rule'][:60]}...",
                markup=True,
                size_hint_y=None,
                height=70
            )
            btn.bind(on_press=lambda x, r=rule: self.show_rule(r))
            self.ids.grammar_list.add_widget(btn)

    def show_rule(self, rule):
        app = App.get_running_app()
        app.db.mark_grammar_done(app.current_user, rule['id'])
        app.db.add_xp(app.current_user, 3)
        content = BoxLayout(orientation='vertical', padding=10, spacing=8)
        content.add_widget(Label(
            text=f"[b]{rule['title']}[/b]",
            markup=True, font_size='18sp',
            size_hint_y=None, height=30, color=(1,1,1,1)
        ))
        content.add_widget(Label(
            text=f"[color=#3B82F6]Rule:[/color]\n{rule['rule']}",
            markup=True, font_size='14sp',
            size_hint_y=None, height=50, color=(1,1,1,1)
        ))
        content.add_widget(Label(
            text=f"[color=#22C55E]Example:[/color]\n{rule['example']}",
            markup=True, font_size='14sp',
            size_hint_y=None, height=50, color=(1,1,1,1)
        ))
        content.add_widget(Label(
            text=f"[color=#F59E0B]Tip:[/color]\n{rule['tip']}",
            markup=True, font_size='13sp',
            size_hint_y=None, height=50, color=(1,1,1,1)
        ))
        close_btn = SecondaryButton(text="Close", on_press=lambda x: self._popup.dismiss())
        content.add_widget(close_btn)
        self._popup = Popup(
            title='', content=content,
            size_hint=(0.9, 0.7), auto_dismiss=True,
            background='', separator_color=[0.2,0.2,0.2,1]
        )
        self._popup.open()

    def filter_beginner(self):
        self.filter_level = 'beginner'
        self.load_rules()

    def filter_intermediate(self):
        self.filter_level = 'intermediate'
        self.load_rules()

    def filter_advanced(self):
        self.filter_level = 'advanced'
        self.load_rules()

    def filter_all(self):
        self.filter_level = 'all'
        self.load_rules()


class ExerciseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.exercises = []
        self.current_index = 0
        self.score = 0
        self.answered = False

    def on_enter(self):
        app = App.get_running_app()
        level = app.db.get_level(app.current_user)
        self.exercises = app.db.get_exercises(level)
        self.current_index = 0
        self.score = 0
        self.show_exercise()

    def show_exercise(self):
        self.answered = False
        self.ids.feedback_label.text = ""
        if self.current_index >= len(self.exercises):
            self.show_results()
            return
        ex = self.exercises[self.current_index]
        self.ids.question_label.text = f"[b]Q{self.current_index+1}/{len(self.exercises)}[/b]\n\n{ex['question']}"
        self.ids.options_list.clear_widgets()
        if ex['type'] == 'mcq':
            for i, opt in enumerate(ex['options']):
                btn = QuizOption(text=opt)
                btn.bind(on_press=lambda x, idx=i: self.check_answer(idx))
                self.ids.options_list.add_widget(btn)
        elif ex['type'] == 'fill':
            self.ids.fill_input.text = ""
            self.ids.fill_input.opacity = 1
            self.ids.fill_input.disabled = False
            self.ids.submit_fill.opacity = 1
            self.ids.submit_fill.disabled = False
            self.ids.options_list.opacity = 0
        else:
            self.ids.fill_input.opacity = 0
            self.ids.fill_input.disabled = True
            self.ids.submit_fill.opacity = 0
            self.ids.submit_fill.disabled = True

    def check_answer(self, selected_idx):
        if self.answered:
            return
        self.answered = True
        ex = self.exercises[self.current_index]
        correct = selected_idx == ex['answer']
        app = App.get_running_app()
        app.db.mark_exercise_done(app.current_user, ex['id'], correct)
        if correct:
            self.score += 1
            self.ids.feedback_label.text = "[color=#22C55E]Correct![/color]"
            app.db.add_xp(app.current_user, 10)
        else:
            correct_text = ex['options'][ex['answer']]
            self.ids.feedback_label.text = f"[color=#EF4444]Wrong! Answer: {correct_text}[/color]\n{ex['explanation']}"
        for child in self.ids.options_list.children:
            child.disabled = True
        Clock.schedule_once(lambda dt: self.next_exercise(), 1.5)

    def submit_fill_answer(self):
        if self.answered:
            return
        self.answered = True
        ex = self.exercises[self.current_index]
        user_answer = self.ids.fill_input.text.strip().lower()
        correct_answer = ex['answer'].lower()
        app = App.get_running_app()
        correct = user_answer == correct_answer
        app.db.mark_exercise_done(app.current_user, ex['id'], correct)
        if correct:
            self.score += 1
            self.ids.feedback_label.text = "[color=#22C55E]Correct![/color]"
            app.db.add_xp(app.current_user, 10)
        else:
            self.ids.feedback_label.text = f"[color=#EF4444]Wrong! Answer: {ex['answer']}[/color]\n{ex['explanation']}"
        self.ids.fill_input.disabled = True
        self.ids.submit_fill.disabled = True
        Clock.schedule_once(lambda dt: self.next_exercise(), 1.5)

    def next_exercise(self):
        self.current_index += 1
        self.show_exercise()

    def show_results(self):
        total = len(self.exercises)
        pct = (self.score / total * 100) if total > 0 else 0
        app = App.get_running_app()
        app.db.add_xp(app.current_user, self.score * 5)
        self.ids.question_label.text = f"[b]Quiz Complete![/b]\n\nScore: {self.score}/{total}\nAccuracy: {pct:.0f}%"
        self.ids.options_list.clear_widgets()
        self.ids.options_list.add_widget(Label(
            text="Great job!" if pct >= 70 else "Keep practicing!",
            color=(1,1,1,1), font_size='16sp'
        ))
        retry = PrimaryButton(text="Try Again", on_press=lambda x: self.on_enter())
        self.ids.options_list.add_widget(retry)


class IdiomsScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        idioms = app.db.get_idioms()
        self.ids.idioms_list.clear_widgets()
        for i in idioms:
            card = BoxLayout(
                orientation='vertical', padding=12, spacing=4,
                size_hint_y=None, height=100
            )
            card.canvas.before
            card.add_widget(Label(
                text=f"[b]{i['idiom']}[/b]",
                markup=True, font_size='15sp', color=(0.235,0.51,0.965,1),
                size_hint_y=None, height=25, halign='left', text_size=(350, None)
            ))
            card.add_widget(Label(
                text=i['meaning'],
                font_size='14sp', color=(1,1,1,1),
                size_hint_y=None, height=22, halign='left', text_size=(350, None)
            ))
            card.add_widget(Label(
                text=f"[color=#9CA3AF]{i['example']}[/color]",
                markup=True, font_size='12sp',
                size_hint_y=None, height=22, halign='left', text_size=(350, None)
            ))
            self.ids.idioms_list.add_widget(card)


class PhrasesScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        phrases = app.db.get_phrases()
        self.ids.phrases_list.clear_widgets()
        for p in phrases:
            btn = CardButton(
                text=f"[b]{p['phrase']}[/b]\n{p['ar']}",
                markup=True, size_hint_y=None, height=60
            )
            btn.bind(on_press=lambda x, ph=p: App.get_running_app().sound.speak_english(ph['phrase']))
            self.ids.phrases_list.add_widget(btn)


class ProgressScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        stats = app.db.get_stats(app.current_user)
        self.ids.progress_list.clear_widgets()
        items = [
            ("Total XP", str(stats['xp']), "#3B82F6"),
            ("Level", stats['level'].title(), "#22C55E"),
            ("Streak", f"{stats['streak']} days", "#F59E0B"),
            ("Words Learned", str(stats['words']), "#8B5CF6"),
            ("Grammar Rules", str(stats['grammar']), "#EC4899"),
            ("Exercises Done", str(stats['exercises']), "#06B6D4"),
            ("Quizzes Taken", str(stats['quizzes']), "#F97316"),
            ("Accuracy", f"{stats['accuracy']}%", "#10B981"),
            ("Flashcards", str(stats['flashcards']), "#6366F1"),
            ("Achievements", str(stats['achievements']), "#EAB308"),
        ]
        for label, value, color in items:
            row = BoxLayout(
                orientation='horizontal', padding=12, spacing=10,
                size_hint_y=None, height=44
            )
            row.add_widget(Label(
                text=label, font_size='14sp', color=(0.6,0.6,0.6,1),
                halign='left', text_size=(200, None)
            ))
            row.add_widget(Label(
                text=f"[b]{value}[/b]", markup=True, font_size='15sp',
                color=(1,1,1,1), halign='right'
            ))
            self.ids.progress_list.add_widget(row)


class AchievementsScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        achievements = get_all_achievements(app.current_user, app.db)
        self.ids.ach_list.clear_widgets()
        for a in achievements:
            status = "[color=#22C55E]Earned![/color]" if a['earned'] else "[color=#64748B]Locked[/color]"
            btn = CardButton(
                text=f"{a['icon']} {a['title']}\n{a['desc']}  {status}",
                markup=True, size_hint_y=None, height=70
            )
            self.ids.ach_list.add_widget(btn)


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        app = App.get_running_app()
        self.ids.sound_switch.active = app.sound.enabled

    def toggle_sound(self, value):
        app = App.get_running_app()
        app.sound.enabled = value

    def change_level(self, level):
        app = App.get_running_app()
        app.db.set_level(app.current_user, level)

    def logout(self):
        App.get_running_app().current_user = None
        self.manager.current = 'login'


class FlashcardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cards = []
        self.current_index = 0
        self.show_back = False

    def on_enter(self):
        app = App.get_running_app()
        level = app.db.get_level(app.current_user)
        self.cards = app.db.get_due_words(app.current_user, 10)
        self.current_index = 0
        self.show_back = False
        self.update_card()

    def update_card(self):
        if not self.cards or self.current_index >= len(self.cards):
            self.ids.card_word.text = "No more cards!"
            self.ids.card_meaning.text = "Come back later"
            self.ids.card_example.text = ""
            return
        w = self.cards[self.current_index]
        if self.show_back:
            self.ids.card_word.text = w['word']
            self.ids.card_meaning.text = w['ar']
            self.ids.card_example.text = w['example']
        else:
            self.ids.card_word.text = w['word']
            self.ids.card_meaning.text = "?"
            self.ids.card_example.text = "Tap to reveal"

    def flip_card(self):
        self.show_back = not self.show_back
        self.update_card()

    def rate_card(self, quality):
        app = App.get_running_app()
        if self.cards and self.current_index < len(self.cards):
            w = self.cards[self.current_index]
            app.db.mark_word_learned(app.current_user, w['id'], quality)
            app.db.add_xp(app.current_user, quality)
            app.db.progress[app.current_user]['flashcards_reviewed'] = \
                app.db.progress[app.current_user].get('flashcards_reviewed', 0) + 1
        self.current_index += 1
        self.show_back = False
        self.update_card()


# ══════════════════════════════════════════════════════════════
# APP
# ══════════════════════════════════════════════════════════════

class EnglishMasterProApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database(data_dir="data")
        self.engine = LearningEngine(self.db)
        self.sound = SoundSystem()
        self.current_user = None

    def build(self):
        sm = ScreenManager(transition=FadeTransition(duration=0.3))

        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(VocabularyScreen(name='vocabulary'))
        sm.add_widget(GrammarScreen(name='grammar'))
        sm.add_widget(ExerciseScreen(name='exercises'))
        sm.add_widget(IdiomsScreen(name='idioms'))
        sm.add_widget(PhrasesScreen(name='phrases'))
        sm.add_widget(ProgressScreen(name='progress'))
        sm.add_widget(AchievementsScreen(name='achievements'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(FlashcardScreen(name='flashcards'))

        sm.current = 'splash'
        return sm

    def on_stop(self):
        self.db.save_all()
        self.sound.clear_cache()


if __name__ == '__main__':
    EnglishMasterProApp().run()

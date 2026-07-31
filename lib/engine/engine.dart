import 'dart:math';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import '../models.dart';
import '../data/database.dart';

class LearningEngine {
  static final LearningEngine _instance = LearningEngine._internal();
  factory LearningEngine() => _instance;
  LearningEngine._internal();

  UserProfile profile = UserProfile();
  List<Word> words = [];
  Map<int, Map<String, dynamic>> wordProgress = {};

  Future<void> init() async {
    words = List.from(AppDatabase.words);
    await _loadProfile();
    await _loadProgress();
    _checkStreak();
  }

  void _checkStreak() {
    if (profile.lastStudyDate == null) return;
    final now = DateTime.now();
    final last = profile.lastStudyDate!;
    final diff = DateTime(now.year, now.month, now.day)
        .difference(DateTime(last.year, last.month, last.day))
        .inDays;
    if (diff > 1) profile.streak = 0;
  }

  void recordStudy() {
    final now = DateTime.now();
    if (profile.lastStudyDate == null) {
      profile.streak = 1;
    } else {
      final last = profile.lastStudyDate!;
      final diff = DateTime(now.year, now.month, now.day)
          .difference(DateTime(last.year, last.month, last.day))
          .inDays;
      if (diff == 1) {
        profile.streak++;
      } else if (diff > 1) {
        profile.streak = 1;
      }
    }
    profile.lastStudyDate = now;
    _saveProfile();
  }

  List<Word> getDueWords() {
    final now = DateTime.now();
    return words.where((w) {
      final wp = wordProgress[w.id];
      if (wp == null) return true;
      if (wp['nextReview'] == null) return true;
      return now.isAfter(DateTime.parse(wp['nextReview']));
    }).toList()
      ..sort((a, b) {
        final aP = wordProgress[a.id];
        final bP = wordProgress[b.id];
        if (aP == null) return -1;
        if (bP == null) return 1;
        final aR = aP['repetitions'] ?? 0;
        final bR = bP['repetitions'] ?? 0;
        return aR.compareTo(bR);
      });
  }

  void reviewWord(int wordId, int quality) {
    final wp = wordProgress[wordId] ?? = {
      'easeFactor': 2.5,
      'interval': 0,
      'repetitions': 0,
      'nextReview': null,
    };

    double ef = wp['easeFactor'] ?? 2.5;
    int interval = wp['interval'] ?? 0;
    int reps = wp['repetitions'] ?? 0;

    if (quality >= 3) {
      if (reps == 0) {
        interval = 1;
      } else if (reps == 1) {
        interval = 6;
      } else {
        interval = (interval * ef).round();
      }
      reps++;
    } else {
      reps = 0;
      interval = 1;
    }

    ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02));
    if (ef < 1.3) ef = 1.3;

    final nextReview = DateTime.now().add(Duration(days: interval));

    wordProgress[wordId] = {
      'easeFactor': ef,
      'interval': interval,
      'repetitions': reps,
      'nextReview': nextReview.toIso8601String(),
    };

    _saveProgress();
  }

  int calculateXP(Exercise exercise, bool correct) {
    if (!correct) return 0;
    int base = switch (exercise.level) {
      'beginner' => 10,
      'intermediate' => 20,
      'advanced' => 30,
      _ => 10,
    };
    return base;
  }

  int calculateWordXP(Word word) {
    return switch (word.level) {
      'beginner' => 10,
      'intermediate' => 20,
      'advanced' => 30,
      _ => 10,
    };
  }

  String getDifficultyLevel() {
    if (profile.totalAnswered == 0) return 'beginner';
    final acc = profile.accuracy;
    if (acc >= 0.8 && profile.totalAnswered >= 20) return 'advanced';
    if (acc >= 0.6 && profile.totalAnswered >= 10) return 'intermediate';
    return 'beginner';
  }

  List<Exercise> getAdaptiveExercises() {
    final level = getDifficultyLevel();
    final allExercises = AppDatabase.exercises;
    final levelExercises = allExercises.where((e) => e.level == level).toList();
    levelExercises.shuffle();
    return levelExercises.take(10).toList();
  }

  List<GrammarRule> getGrammarByLevel(String level) {
    return AppDatabase.grammarRules.where((r) => r.level == level).toList();
  }

  List<Word> getWordsByLevel(String level) {
    return words.where((w) => w.level == level).toList();
  }

  List<Word> getWordsByCategory(String category) {
    return words.where((w) => w.category == category).toList();
  }

  List<String> getCategories() {
    return words.map((w) => w.category).toSet().toList()..sort();
  }

  double getOverallProgress() {
    final totalWords = words.length;
    final learned = profile.wordsLearned;
    return totalWords > 0 ? learned / totalWords : 0.0;
  }

  Map<String, double> getLevelProgress() {
    final beginner = words.where((w) => w.level == 'beginner').length;
    final intermediate = words.where((w) => w.level == 'intermediate').length;
    final advanced = words.where((w) => w.level == 'advanced').length;

    final learnedBeginner = wordProgress.entries
        .where((e) => words.firstWhere((w) => w.id == e.key).level == 'beginner' && (e.value['repetitions'] ?? 0) >= 3)
        .length;
    final learnedIntermediate = wordProgress.entries
        .where((e) => words.firstWhere((w) => w.id == e.key).level == 'intermediate' && (e.value['repetitions'] ?? 0) >= 3)
        .length;
    final learnedAdvanced = wordProgress.entries
        .where((e) => words.firstWhere((w) => w.id == e.key).level == 'advanced' && (e.value['repetitions'] ?? 0) >= 3)
        .length;

    return {
      'beginner': beginner > 0 ? learnedBeginner / beginner : 0.0,
      'intermediate': intermediate > 0 ? learnedIntermediate / intermediate : 0.0,
      'advanced': advanced > 0 ? learnedAdvanced / advanced : 0.0,
    };
  }

  List<Achievement> checkAchievements() {
    final newAchievements = <Achievement>[];
    for (final a in AppDatabase.achievements) {
      if (profile.unlockedAchievements.contains(a.id)) continue;
      bool unlocked = false;
      switch (a.condition) {
        case 'lessons':
          unlocked = profile.lessonsCompleted >= a.target;
        case 'words':
          unlocked = profile.wordsLearned >= a.target;
        case 'streak':
          unlocked = profile.streak >= a.target;
        case 'exercises':
          unlocked = profile.totalAnswered >= a.target;
        case 'xp':
          unlocked = profile.xp >= a.target;
        case 'perfect':
          unlocked = profile.accuracy == 1.0 && profile.totalAnswered >= 5;
        case 'accuracy':
          unlocked = profile.accuracy * 100 >= a.target && profile.totalAnswered >= 20;
        case 'level':
          unlocked = profile.level >= a.target;
        case 'idioms':
          unlocked = profile.settings['idiomsSeen'] != null &&
              (profile.settings['idiomsSeen'] as List).length >= a.target;
        case 'phrases':
          unlocked = profile.settings['phrasesSeen'] != null &&
              (profile.settings['phrasesSeen'] as List).length >= a.target;
        case 'rules':
          unlocked = profile.settings['rulesCompleted'] != null &&
              (profile.settings['rulesCompleted'] as List).length >= a.target;
      }
      if (unlocked) {
        profile.unlockedAchievements.add(a.id);
        newAchievements.add(a);
      }
    }
    if (newAchievements.isNotEmpty) _saveProfile();
    return newAchievements;
  }

  void markIdiomSeen(int idiomId) {
    final seen = (profile.settings['idiomsSeen'] as List?) ?? [];
    if (!seen.contains(idiomId)) {
      seen.add(idiomId);
      profile.settings['idiomsSeen'] = seen;
      _saveProfile();
    }
  }

  void markPhraseSeen(int phraseId) {
    final seen = (profile.settings['phrasesSeen'] as List?) ?? [];
    if (!seen.contains(phraseId)) {
      seen.add(phraseId);
      profile.settings['phrasesSeen'] = seen;
      _saveProfile();
    }
  }

  void markRuleCompleted(int ruleId) {
    final completed = (profile.settings['rulesCompleted'] as List?) ?? [];
    if (!completed.contains(ruleId)) {
      completed.add(ruleId);
      profile.settings['rulesCompleted'] = completed;
      _saveProfile();
    }
  }

  Future<void> _loadProfile() async {
    final prefs = await SharedPreferences.getInstance();
    final data = prefs.getString('userProfile');
    if (data != null) {
      final map = jsonDecode(data);
      profile = UserProfile(
        name: map['name'] ?? 'Student',
        xp: map['xp'] ?? 0,
        streak: map['streak'] ?? 0,
        totalCorrect: map['totalCorrect'] ?? 0,
        totalAnswered: map['totalAnswered'] ?? 0,
        wordsLearned: map['wordsLearned'] ?? 0,
        lessonsCompleted: map['lessonsCompleted'] ?? 0,
        lastStudyDate: map['lastStudyDate'] != null ? DateTime.parse(map['lastStudyDate']) : null,
        unlockedAchievements: List<int>.from(map['unlockedAchievements'] ?? []),
        settings: Map<String, dynamic>.from(map['settings'] ?? {}),
      );
    }
  }

  Future<void> _saveProfile() async {
    final prefs = await SharedPreferences.getInstance();
    final map = {
      'name': profile.name,
      'xp': profile.xp,
      'streak': profile.streak,
      'totalCorrect': profile.totalCorrect,
      'totalAnswered': profile.totalAnswered,
      'wordsLearned': profile.wordsLearned,
      'lessonsCompleted': profile.lessonsCompleted,
      'lastStudyDate': profile.lastStudyDate?.toIso8601String(),
      'unlockedAchievements': profile.unlockedAchievements,
      'settings': profile.settings,
    };
    await prefs.setString('userProfile', jsonEncode(map));
  }

  Future<void> _loadProgress() async {
    final prefs = await SharedPreferences.getInstance();
    final data = prefs.getString('wordProgress');
    if (data != null) {
      final map = jsonDecode(data);
      wordProgress = map.map((k, v) => MapEntry(int.parse(k), Map<String, dynamic>.from(v)));
    }
  }

  Future<void> _saveProgress() async {
    final prefs = await SharedPreferences.getInstance();
    final map = wordProgress.map((k, v) => MapEntry(k.toString(), v));
    await prefs.setString('wordProgress', jsonEncode(map));
  }

  Future<void> updateSettings(String key, dynamic value) async {
    profile.settings[key] = value;
    await _saveProfile();
  }

  Future<void> updateName(String name) async {
    profile.name = name;
    await _saveProfile();
  }
}

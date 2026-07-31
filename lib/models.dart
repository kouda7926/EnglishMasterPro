class Word {
  final int id;
  final String word;
  final String meaningAr;
  final String meaningEn;
  final String example;
  final String level;
  final String category;
  double easeFactor;
  int interval;
  int repetitions;
  DateTime? nextReview;

  Word({
    required this.id,
    required this.word,
    required this.meaningAr,
    required this.meaningEn,
    required this.example,
    required this.level,
    required this.category,
    this.easeFactor = 2.5,
    this.interval = 0,
    this.repetitions = 0,
    this.nextReview,
  });

  Map<String, dynamic> toMap() => {
    'id': id, 'word': word, 'meaningAr': meaningAr, 'meaningEn': meaningEn,
    'example': example, 'level': level, 'category': category,
    'easeFactor': easeFactor, 'interval': interval, 'repetitions': repetitions,
    'nextReview': nextReview?.toIso8601String(),
  };

  factory Word.fromMap(Map<String, dynamic> m) => Word(
    id: m['id'], word: m['word'], meaningAr: m['meaningAr'], meaningEn: m['meaningEn'],
    example: m['example'], level: m['level'], category: m['category'],
    easeFactor: m['easeFactor'] ?? 2.5, interval: m['interval'] ?? 0,
    repetitions: m['repetitions'] ?? 0,
    nextReview: m['nextReview'] != null ? DateTime.parse(m['nextReview']) : null,
  );
}

class GrammarRule {
  final int id;
  final String title;
  final String titleAr;
  final String explanation;
  final String example;
  final String level;

  const GrammarRule({
    required this.id, required this.title, required this.titleAr,
    required this.explanation, required this.example, required this.level,
  });
}

class Exercise {
  final int id;
  final String question;
  final List<String> options;
  final int correctIndex;
  final String? fillAnswer;
  final String type;
  final int ruleId;
  final String level;

  const Exercise({
    required this.id, required this.question, required this.options,
    required this.correctIndex, this.fillAnswer, required this.type,
    required this.ruleId, required this.level,
  });
}

class Idiom {
  final int id;
  final String idiom;
  final String meaningAr;
  final String example;

  const Idiom({required this.id, required this.idiom, required this.meaningAr, required this.example});
}

class Phrase {
  final int id;
  final String phrase;
  final String meaningAr;
  final String context;

  const Phrase({required this.id, required this.phrase, required this.meaningAr, required this.context});
}

class Achievement {
  final int id;
  final String title;
  final String titleAr;
  final String description;
  final String icon;
  final String condition;
  final int target;

  const Achievement({
    required this.id, required this.title, required this.titleAr,
    required this.description, required this.icon, required this.condition, required this.target,
  });
}

class UserProfile {
  String name;
  int xp;
  int streak;
  int totalCorrect;
  int totalAnswered;
  int wordsLearned;
  int lessonsCompleted;
  DateTime? lastStudyDate;
  List<int> unlockedAchievements;
  Map<String, dynamic> settings;

  UserProfile({
    this.name = 'Student',
    this.xp = 0,
    this.streak = 0,
    this.totalCorrect = 0,
    this.totalAnswered = 0,
    this.wordsLearned = 0,
    this.lessonsCompleted = 0,
    this.lastStudyDate,
    List<int>? unlockedAchievements,
    Map<String, dynamic>? settings,
  })  : unlockedAchievements = unlockedAchievements ?? [],
        settings = settings ?? {'sound': true, 'darkMode': true, 'language': 'ar'};

  int get level => (xp / 500).floor() + 1;
  double get accuracy => totalAnswered > 0 ? totalCorrect / totalAnswered : 0.0;
}

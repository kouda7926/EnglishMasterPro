import 'package:flutter/material.dart';
import '../engine/engine.dart';
import '../data/database.dart';
import 'vocabulary_screen.dart';
import 'grammar_screen.dart';
import 'exercises_screen.dart';
import 'flashcards_screen.dart';
import 'idioms_screen.dart';
import 'phrases_screen.dart';
import 'progress_screen.dart';
import 'achievements_screen.dart';
import 'settings_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _engine = LearningEngine();
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    final p = _engine.profile;
    return Scaffold(
      body: _currentIndex == 0 ? _buildHome(p) : _buildTab(_currentIndex),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (i) => setState(() => _currentIndex = i),
        type: BottomNavigationBarType.fixed,
        backgroundColor: const Color(0xFF161B22),
        selectedItemColor: const Color(0xFF58A6FF),
        unselectedItemColor: const Color(0xFF484F58),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.trending_up), label: 'Progress'),
          BottomNavigationBarItem(icon: Icon(Icons.emoji_events), label: 'Awards'),
          BottomNavigationBarItem(icon: Icon(Icons.settings), label: 'Settings'),
        ],
      ),
    );
  }

  Widget _buildHome(UserProfile p) {
    final dueWords = _engine.getDueWords();
    return SafeArea(
      child: CustomScrollView(
        slivers: [
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      CircleAvatar(
                        radius: 28,
                        backgroundColor: const Color(0xFF58A6FF).withOpacity(0.2),
                        child: Text(p.name.isNotEmpty ? p.name[0].toUpperCase() : '?', style: const TextStyle(fontSize: 24, color: Color(0xFF58A6FF), fontWeight: FontWeight.bold)),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('مرحباً ${p.name}', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white)),
                            Text('Level ${p.level} • ${p.xp} XP', style: const TextStyle(color: Color(0xFF8B949E))),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  Row(
                    children: [
                      _statCard('🔥', '${p.streak}', 'Streak'),
                      const SizedBox(width: 12),
                      _statCard('⭐', '${p.xp}', 'XP'),
                      const SizedBox(width: 12),
                      _statCard('📝', '${p.totalCorrect}/${p.totalAnswered}', 'Score'),
                      const SizedBox(width: 12),
                      _statCard('📚', '${p.wordsLearned}', 'Words'),
                    ],
                  ),
                  const SizedBox(height: 20),
                  if (dueWords.isNotEmpty)
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(colors: [Color(0xFF238636), Color(0xFF2EA043)]),
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.replay, color: Colors.white, size: 28),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text('Review Time!', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                                Text('${dueWords.length} words need review', style: const TextStyle(color: Colors.white70)),
                              ],
                            ),
                          ),
                          ElevatedButton(
                            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const FlashcardsScreen())),
                            style: ElevatedButton.styleFrom(backgroundColor: Colors.white, foregroundColor: const Color(0xFF238636)),
                            child: const Text('Start'),
                          ),
                        ],
                      ),
                    ),
                  const SizedBox(height: 24),
                  const Text('Learning Paths', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
                  const SizedBox(height: 12),
                ],
              ),
            ),
          ),
          SliverPadding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            sliver: SliverGrid(
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 2, mainAxisSpacing: 12, crossAxisSpacing: 12, childAspectRatio: 1.2),
              delegate: SliverChildListDelegate([
                _pathCard('📖', 'Vocabulary', '${AppDatabase.words.length} words', const Color(0xFF58A6FF), () => Navigator.push(context, MaterialPageRoute(builder: (_) => const VocabularyScreen()))),
                _pathCard('📝', 'Grammar', '${AppDatabase.grammarRules.length} rules', const Color(0xFF3FB950), () => Navigator.push(context, MaterialPageRoute(builder: (_) => const GrammarScreen()))),
                _pathCard('🧠', 'Exercises', '${AppDatabase.exercises.length} questions', const Color(0xFFF0883E), () => Navigator.push(context, MaterialPageRoute(builder: (_) => const ExercisesScreen()))),
                _pathCard('🃏', 'Flashcards', 'Spaced repetition', const Color(0xFFF778BA), () => Navigator.push(context, MaterialPageRoute(builder: (_) => const FlashcardsScreen()))),
                _pathCard('💬', 'Idioms', '${AppDatabase.idioms.length} idioms', const Color(0xFFD2A8FF), () => Navigator.push(context, MaterialPageRoute(builder: (_) => const IdiomsScreen()))),
                _pathCard('🗣️', 'Phrases', '${AppDatabase.phrases.length} phrases', const Color(0xFF79C0FF), () => Navigator.push(context, MaterialPageRoute(builder: (_) => const PhrasesScreen()))),
              ]),
            ),
          ),
          const SliverToBoxAdapter(child: SizedBox(height: 20)),
        ],
      ),
    );
  }

  Widget _statCard(String emoji, String value, String label) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(color: const Color(0xFF21262D), borderRadius: BorderRadius.circular(12)),
        child: Column(children: [
          Text(emoji, style: const TextStyle(fontSize: 20)),
          const SizedBox(height: 4),
          Text(value, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white)),
          Text(label, style: const TextStyle(fontSize: 10, color: Color(0xFF8B949E))),
        ]),
      ),
    );
  }

  Widget _pathCard(String emoji, String title, String subtitle, Color color, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(emoji, style: const TextStyle(fontSize: 32)),
            const SizedBox(height: 8),
            Text(title, style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: color)),
            Text(subtitle, style: const TextStyle(fontSize: 11, color: Color(0xFF8B949E))),
          ],
        ),
      ),
    );
  }

  Widget _buildTab(int index) {
    return switch (index) {
      1 => const ProgressScreen(),
      2 => const AchievementsScreen(),
      3 => const SettingsScreen(),
      _ => const SizedBox(),
    };
  }
}

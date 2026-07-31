import 'package:flutter/material.dart';
import '../engine/engine.dart';

class ProgressScreen extends StatelessWidget {
  const ProgressScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final engine = LearningEngine();
    final p = engine.profile;
    final lp = engine.getLevelProgress();
    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('📊 Your Progress', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white)),
            const SizedBox(height: 20),
            _overviewCard(p),
            const SizedBox(height: 16),
            const Text('Level Progress', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
            const SizedBox(height: 12),
            _levelProgress('Beginner', lp['beginner'] ?? 0, const Color(0xFF3FB950)),
            _levelProgress('Intermediate', lp['intermediate'] ?? 0, const Color(0xFFF0883E)),
            _levelProgress('Advanced', lp['advanced'] ?? 0, const Color(0xFFF85149)),
            const SizedBox(height: 20),
            const Text('Statistics', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
            const SizedBox(height: 12),
            _statRow('Total Words Learned', '${p.wordsLearned}', Icons.book),
            _statRow('Lessons Completed', '${p.lessonsCompleted}', Icons.school),
            _statRow('Exercises Answered', '${p.totalAnswered}', Icons.quiz),
            _statRow('Correct Answers', '${p.totalCorrect}', Icons.check_circle),
            _statRow('Accuracy', '${(p.accuracy * 100).round()}%', Icons.bullseye),
            _statRow('Current Streak', '${p.streak} days', Icons.local_fire_department),
            _statRow('Total XP', '${p.xp}', Icons.star),
            _statRow('Level', '${p.level}', Icons.trending_up),
          ],
        ),
      ),
    );
  }

  Widget _overviewCard(UserProfile p) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(colors: [Color(0xFF58A6FF), Color(0xFF1F6FEB)]),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        children: [
          CircleAvatar(
            radius: 36,
            backgroundColor: Colors.white.withOpacity(0.2),
            child: Text(p.name.isNotEmpty ? p.name[0].toUpperCase() : '?', style: const TextStyle(fontSize: 32, color: Colors.white, fontWeight: FontWeight.bold)),
          ),
          const SizedBox(height: 12),
          Text(p.name, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white)),
          const SizedBox(height: 4),
          Text('Level ${p.level} • ${p.xp} XP', style: const TextStyle(color: Colors.white70)),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _miniStat('🔥', '${p.streak}'),
              _miniStat('⭐', '${p.xp}'),
              _miniStat('📚', '${p.wordsLearned}'),
              _miniStat('✅', '${(p.accuracy * 100).round()}%'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _miniStat(String emoji, String value) {
    return Column(children: [Text(emoji, style: const TextStyle(fontSize: 20)), Text(value, style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white))]);
  }

  Widget _levelProgress(String label, double progress, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(label, style: const TextStyle(color: Color(0xFFC9D1D9), fontSize: 14)),
              Text('${(progress * 100).round()}%', style: TextStyle(color: color, fontWeight: FontWeight.bold)),
            ],
          ),
          const SizedBox(height: 6),
          ClipRRect(
            borderRadius: BorderRadius.circular(6),
            child: LinearProgressIndicator(value: progress, minHeight: 10, backgroundColor: const Color(0xFF21262D), valueColor: AlwaysStoppedAnimation(color)),
          ),
        ],
      ),
    );
  }

  Widget _statRow(String label, String value, IconData icon) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(color: const Color(0xFF161B22), borderRadius: BorderRadius.circular(12)),
      child: Row(
        children: [
          Icon(icon, color: const Color(0xFF58A6FF), size: 20),
          const SizedBox(width: 12),
          Expanded(child: Text(label, style: const TextStyle(color: Color(0xFFC9D1D9)))),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 16)),
        ],
      ),
    );
  }
}

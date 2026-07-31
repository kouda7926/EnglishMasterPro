import 'package:flutter/material.dart';
import '../engine/engine.dart';
import '../data/database.dart';

class AchievementsScreen extends StatelessWidget {
  const AchievementsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final engine = LearningEngine();
    final unlocked = engine.profile.unlockedAchievements;
    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.emoji_events, color: Color(0xFFF0883E), size: 28),
                const SizedBox(width: 8),
                const Text('🏆 Achievements', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white)),
              ],
            ),
            const SizedBox(height: 8),
            Text('${unlocked.length}/${AppDatabase.achievements.length} unlocked', style: const TextStyle(color: Color(0xFF8B949E))),
            const SizedBox(height: 20),
            ...AppDatabase.achievements.map((a) {
              final isUnlocked = unlocked.contains(a.id);
              return _achievementCard(a, isUnlocked);
            }),
          ],
        ),
      ),
    );
  }

  Widget _achievementCard(dynamic a, bool unlocked) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: unlocked ? const Color(0xFFF0883E).withOpacity(0.1) : const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: unlocked ? const Color(0xFFF0883E).withOpacity(0.3) : const Color(0xFF21262D)),
      ),
      child: Row(
        children: [
          Container(
            width: 48, height: 48,
            decoration: BoxDecoration(
              color: unlocked ? const Color(0xFFF0883E).withOpacity(0.2) : const Color(0xFF21262D),
              shape: BoxShape.circle,
            ),
            child: Icon(unlocked ? Icons.emoji_events : Icons.lock, color: unlocked ? const Color(0xFFF0883E) : const Color(0xFF484F58), size: 24),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(a.titleAr, style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: unlocked ? Colors.white : const Color(0xFF484F58))),
                const SizedBox(height: 2),
                Text(a.description, style: TextStyle(fontSize: 12, color: unlocked ? const Color(0xFF8B949E) : const Color(0xFF30363D))),
              ],
            ),
          ),
          if (unlocked) const Icon(Icons.check_circle, color: Color(0xFF3FB950), size: 20),
        ],
      ),
    );
  }
}

import 'package:flutter/material.dart';
import '../engine/engine.dart';
import '../models.dart';

class ExercisesScreen extends StatefulWidget {
  const ExercisesScreen({super.key});

  @override
  State<ExercisesScreen> createState() => _ExercisesScreenState();
}

class _ExercisesScreenState extends State<ExercisesScreen> {
  final _engine = LearningEngine();
  late List<Exercise> _exercises;
  int _current = 0;
  int _correct = 0;
  bool _answered = false;
  int _selected = -1;
  final _fillController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _exercises = _engine.getAdaptiveExercises();
  }

  @override
  void dispose() {
    _fillController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_current >= _exercises.length) return _buildResults();
    final ex = _exercises[_current];
    return Scaffold(
      appBar: AppBar(title: Text('🧠 Exercise ${_current + 1}/${_exercises.length}')),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            LinearProgressIndicator(
              value: (_current + 1) / _exercises.length,
              backgroundColor: const Color(0xFF21262D),
              valueColor: const AlwaysStoppedAnimation(Color(0xFF58A6FF)),
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('${_correct} correct', style: const TextStyle(color: Color(0xFF3FB950))),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: ex.level == 'beginner' ? const Color(0xFF3FB950).withOpacity(0.2) :
                           ex.level == 'intermediate' ? const Color(0xFFF0883E).withOpacity(0.2) :
                           const Color(0xFFF85149).withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(ex.level, style: TextStyle(
                    color: ex.level == 'beginner' ? const Color(0xFF3FB950) :
                           ex.level == 'intermediate' ? const Color(0xFFF0883E) :
                           const Color(0xFFF85149),
                    fontSize: 12,
                  )),
                ),
              ],
            ),
            const SizedBox(height: 24),
            Text(ex.question, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
            const SizedBox(height: 24),
            if (ex.type == 'mcq') ...[
              ...List.generate(ex.options.length, (i) => _optionButton(ex, i)),
            ] else ...[
              TextField(
                controller: _fillController,
                style: const TextStyle(color: Colors.white, fontSize: 16),
                decoration: InputDecoration(
                  hintText: 'Type your answer...',
                  hintStyle: const TextStyle(color: Color(0xFF484F58)),
                  filled: true,
                  fillColor: const Color(0xFF21262D),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                  focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Color(0xFF58A6FF))),
                ),
              ),
            ],
            const Spacer(),
            if (_answered || ex.type == 'fill')
              SizedBox(
                width: double.infinity, height: 48,
                child: ElevatedButton(
                  onPressed: () => _nextExercise(ex),
                  style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF58A6FF)),
                  child: Text(_current < _exercises.length - 1 ? 'Next →' : 'See Results', style: const TextStyle(fontSize: 16, color: Colors.white)),
                ),
              ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  Widget _optionButton(Exercise ex, int i) {
    Color bgColor = const Color(0xFF21262D);
    Color textColor = const Color(0xFFC9D1D9);
    if (_answered) {
      if (i == ex.correctIndex) {
        bgColor = const Color(0xFF238636);
        textColor = Colors.white;
      } else if (i == _selected && i != ex.correctIndex) {
        bgColor = const Color(0xFFDA3633);
        textColor = Colors.white;
      }
    }
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: GestureDetector(
        onTap: _answered ? null : () => _checkAnswer(ex, i),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(color: bgColor, borderRadius: BorderRadius.circular(12)),
          child: Row(
            children: [
              Container(
                width: 28, height: 28,
                decoration: BoxDecoration(
                  color: _answered && i == ex.correctIndex ? Colors.white.withOpacity(0.2) :
                         _answered && i == _selected ? Colors.white.withOpacity(0.2) :
                         const Color(0xFF484F58).withOpacity(0.3),
                  shape: BoxShape.circle,
                ),
                child: Center(child: Text(String.fromCharCode(65 + i), style: TextStyle(color: textColor, fontWeight: FontWeight.bold, fontSize: 12))),
              ),
              const SizedBox(width: 12),
              Expanded(child: Text(ex.options[i], style: TextStyle(color: textColor, fontSize: 15))),
              if (_answered && i == ex.correctIndex) const Icon(Icons.check_circle, color: Colors.white, size: 20),
              if (_answered && i == _selected && i != ex.correctIndex) const Icon(Icons.cancel, color: Colors.white, size: 20),
            ],
          ),
        ),
      ),
    );
  }

  void _checkAnswer(Exercise ex, int index) {
    setState(() {
      _answered = true;
      _selected = index;
      final correct = index == ex.correctIndex;
      if (correct) {
        _correct++;
        _engine.profile.totalCorrect++;
      }
      _engine.profile.totalAnswered++;
      _engine.profile.xp += _engine.calculateXP(ex, correct);
      _engine.recordStudy();
    });
  }

  void _nextExercise(Exercise ex) {
    if (ex.type == 'fill') {
      final answer = _fillController.text.trim().toLowerCase();
      final correct = answer == (ex.fillAnswer?.toLowerCase() ?? '');
      setState(() {
        if (correct) {
          _correct++;
          _engine.profile.totalCorrect++;
        }
        _engine.profile.totalAnswered++;
        _engine.profile.xp += _engine.calculateXP(ex, correct);
        _engine.recordStudy();
      });
      _fillController.clear();
    }
    setState(() {
      _current++;
      _answered = false;
      _selected = -1;
    });
  }

  Widget _buildResults() {
    final total = _exercises.length;
    final percent = total > 0 ? (_correct / total * 100).round() : 0;
    final newAchievements = _engine.checkAchievements();
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(percent >= 80 ? Icons.emoji_events : percent >= 50 ? Icons.thumb_up : Icons.refresh,
                  size: 80, color: percent >= 80 ? const Color(0xFFF0883E) : percent >= 50 ? const Color(0xFF3FB950) : const Color(0xFFF85149)),
              const SizedBox(height: 20),
              Text(percent >= 80 ? 'Excellent!' : percent >= 50 ? 'Good Job!' : 'Keep Trying!',
                  style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white)),
              const SizedBox(height: 10),
              Text('$_correct/$total correct ($percent%)', style: const TextStyle(fontSize: 18, color: Color(0xFF8B949E))),
              if (newAchievements.isNotEmpty) ...[
                const SizedBox(height: 20),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(color: const Color(0xFFF0883E).withOpacity(0.1), borderRadius: BorderRadius.circular(12)),
                  child: Column(
                    children: newAchievements.map((a) => Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.emoji_events, color: Color(0xFFF0883E), size: 16),
                        const SizedBox(width: 8),
                        Text('New: ${a.titleAr}', style: const TextStyle(color: Color(0xFFF0883E))),
                      ],
                    )).toList(),
                  ),
                ),
              ],
              const SizedBox(height: 30),
              SizedBox(
                width: double.infinity, height: 48,
                child: ElevatedButton(
                  onPressed: () => Navigator.pop(context),
                  style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF58A6FF)),
                  child: const Text('Back to Home', style: TextStyle(fontSize: 16, color: Colors.white)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

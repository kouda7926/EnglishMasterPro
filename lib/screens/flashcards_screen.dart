import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';
import '../engine/engine.dart';
import '../models.dart';

class FlashcardsScreen extends StatefulWidget {
  const FlashcardsScreen({super.key});

  @override
  State<FlashcardsScreen> createState() => _FlashcardsScreenState();
}

class _FlashcardsScreenState extends State<FlashcardsScreen> {
  final _engine = LearningEngine();
  final _tts = FlutterTts();
  late List<Word> _cards;
  int _current = 0;
  bool _showFront = true;

  @override
  void initState() {
    super.initState();
    _cards = _engine.getDueWords();
    if (_cards.isEmpty) _cards = _engine.words.take(20).toList();
    _tts.setLanguage('en-US');
    _tts.setSpeechRate(0.4);
  }

  @override
  Widget build(BuildContext context) {
    if (_cards.isEmpty) return Scaffold(appBar: AppBar(title: const Text('🃏 Flashcards')), body: const Center(child: Text('No cards to review!', style: TextStyle(color: Color(0xFF8B949E)))));
    final word = _cards[_current % _cards.length];
    return Scaffold(
      appBar: AppBar(
        title: Text('🃏 Flashcard ${(_current % _cards.length) + 1}/${_cards.length}'),
        actions: [
          IconButton(icon: const Icon(Icons.volume_up), onPressed: () => _tts.speak(word.word)),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            LinearProgressIndicator(value: (_current % _cards.length + 1) / _cards.length, backgroundColor: const Color(0xFF21262D), valueColor: const AlwaysStoppedAnimation(Color(0xFF58A6FF))),
            const SizedBox(height: 24),
            GestureDetector(
              onTap: () => setState(() => _showFront = !_showFront),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 400),
                width: double.infinity,
                height: 280,
                decoration: BoxDecoration(
                  gradient: LinearGradient(colors: _showFront ? [const Color(0xFF58A6FF), const Color(0xFF1F6FEB)] : [const Color(0xFF3FB950), const Color(0xFF238636)]),
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [BoxShadow(color: (_showFront ? const Color(0xFF58A6FF) : const Color(0xFF3FB950)).withOpacity(0.3), blurRadius: 20, spreadRadius: 2)],
                ),
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(_showFront ? word.word : word.meaningAr, style: TextStyle(fontSize: _showFront ? 36 : 28, fontWeight: FontWeight.bold, color: Colors.white)),
                      const SizedBox(height: 12),
                      if (_showFront) Text(word.meaningEn, style: const TextStyle(fontSize: 16, color: Colors.white70)),
                      if (!_showFront) ...[
                        Text(word.example, style: const TextStyle(fontSize: 14, color: Colors.white70, fontStyle: FontStyle.italic), textAlign: TextAlign.center),
                        const SizedBox(height: 8),
                        Text(word.level, style: const TextStyle(fontSize: 12, color: Colors.white60)),
                      ],
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 12),
            Text('Tap card to ${_showFront ? 'reveal answer' : 'see word'}', style: const TextStyle(color: Color(0xFF8B949E), fontSize: 12)),
            const Spacer(),
            if (!_showFront)
              Row(
                children: [
                  Expanded(
                    child: _ratingButton('😓', 'Hard', const Color(0xFFF85149), () => _rate(word, 1)),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: _ratingButton('🤔', 'Good', const Color(0xFFF0883E), () => _rate(word, 3)),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: _ratingButton('😎', 'Easy', const Color(0xFF3FB950), () => _rate(word, 5)),
                  ),
                ],
              ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  Widget _ratingButton(String emoji, String label, Color color, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(color: color.withOpacity(0.15), borderRadius: BorderRadius.circular(16), border: Border.all(color: color.withOpacity(0.3))),
        child: Column(children: [Text(emoji, style: const TextStyle(fontSize: 24)), const SizedBox(height: 4), Text(label, style: TextStyle(color: color, fontWeight: FontWeight.bold))]),
      ),
    );
  }

  void _rate(Word word, int quality) {
    _engine.reviewWord(word.id, quality);
    _engine.profile.xp += _engine.calculateWordXP(word);
    _engine.recordStudy();
    setState(() {
      _showFront = true;
      _current++;
      if (_current >= _cards.length) {
        Navigator.pop(context);
      }
    });
  }
}

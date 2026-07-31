import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';
import '../engine/engine.dart';
import '../models.dart';

class VocabularyScreen extends StatefulWidget {
  const VocabularyScreen({super.key});

  @override
  State<VocabularyScreen> createState() => _VocabularyScreenState();
}

class _VocabularyScreenState extends State<VocabularyScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final _engine = LearningEngine();
  final _tts = FlutterTts();
  String _selectedCategory = 'all';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _tts.setLanguage('en-US');
    _tts.setSpeechRate(0.4);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('📖 Vocabulary'),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: const Color(0xFF58A6FF),
          tabs: const [
            Tab(text: 'Beginner'),
            Tab(text: 'Intermediate'),
            Tab(text: 'Advanced'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: ['beginner', 'intermediate', 'advanced'].map((level) => _buildWordList(level)).toList(),
      ),
    );
  }

  Widget _buildWordList(String level) {
    final words = _engine.getWordsByLevel(level);
    return Column(
      children: [
        Container(
          height: 40,
          padding: const EdgeInsets.symmetric(horizontal: 12),
          child: ListView(
            scrollDirection: Axis.horizontal,
            children: [
              _categoryChip('all'),
              ..._engine.getCategories().map((c) => _categoryChip(c)),
            ],
          ),
        ),
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.all(12),
            itemCount: words.where((w) => _selectedCategory == 'all' || w.category == _selectedCategory).length,
            itemBuilder: (ctx, i) {
              final word = words.where((w) => _selectedCategory == 'all' || w.category == _selectedCategory).toList()[i];
              return _wordCard(word);
            },
          ),
        ),
      ],
    );
  }

  Widget _categoryChip(String cat) {
    final selected = _selectedCategory == cat;
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: FilterChip(
        label: Text(cat, style: TextStyle(color: selected ? Colors.white : const Color(0xFF8B949E), fontSize: 12)),
        selected: selected,
        onSelected: (_) => setState(() => _selectedCategory = cat),
        selectedColor: const Color(0xFF58A6FF),
        backgroundColor: const Color(0xFF21262D),
        checkmarkColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 0),
        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
        visualDensity: VisualDensity.compact,
      ),
    );
  }

  Widget _wordCard(Word word) {
    final learned = (wordProgress[word.id]?['repetitions'] ?? 0) >= 3;
    return Card(
      color: const Color(0xFF161B22),
      margin: const EdgeInsets.only(bottom: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: learned ? const Color(0xFF3FB950).withOpacity(0.2) : const Color(0xFF58A6FF).withOpacity(0.2),
          child: Icon(learned ? Icons.check : Icons.book, color: learned ? const Color(0xFF3FB950) : const Color(0xFF58A6FF), size: 20),
        ),
        title: Text(word.word, style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
        subtitle: Text(word.meaningAr, style: const TextStyle(color: Color(0xFF8B949E))),
        trailing: IconButton(
          icon: const Icon(Icons.volume_up, color: Color(0xFF58A6FF)),
          onPressed: () => _tts.speak(word.word),
        ),
        onTap: () => _showWordDetail(word),
      ),
    );
  }

  Map<int, Map<String, dynamic>> get wordProgress => _engine.wordProgress;

  void _showWordDetail(Word word) {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF161B22),
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(child: Container(width: 40, height: 4, decoration: BoxDecoration(color: const Color(0xFF484F58), borderRadius: BorderRadius.circular(2)))),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(word.word, style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white)),
                      Text(word.meaningAr, style: const TextStyle(fontSize: 18, color: Color(0xFF58A6FF))),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.volume_up, color: Color(0xFF58A6FF), size: 32),
                  onPressed: () => _tts.speak(word.word),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _detailRow('Meaning', word.meaningEn),
            _detailRow('Level', word.level),
            _detailRow('Category', word.category),
            const SizedBox(height: 12),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(color: const Color(0xFF21262D), borderRadius: BorderRadius.circular(12)),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Example:', style: TextStyle(fontSize: 12, color: Color(0xFF8B949E))),
                  const SizedBox(height: 4),
                  Text(word.example, style: const TextStyle(fontSize: 16, color: Colors.white, fontStyle: FontStyle.italic)),
                ],
              ),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () {
                  _engine.reviewWord(word.id, 4);
                  _engine.profile.xp += _engine.calculateWordXP(word);
                  _engine.profile.wordsLearned++;
                  _engine.recordStudy();
                  Navigator.pop(ctx);
                  setState(() {});
                },
                icon: const Icon(Icons.check_circle),
                label: const Text('Mark as Learned'),
                style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF3FB950), padding: const EdgeInsets.symmetric(vertical: 14)),
              ),
            ),
            const SizedBox(height: 10),
          ],
        ),
      ),
    );
  }

  Widget _detailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Text('$label: ', style: const TextStyle(fontSize: 13, color: Color(0xFF8B949E))),
          Text(value, style: const TextStyle(fontSize: 13, color: Colors.white)),
        ],
      ),
    );
  }
}

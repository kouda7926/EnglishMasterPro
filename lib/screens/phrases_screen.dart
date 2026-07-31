import 'package:flutter/material.dart';
import '../engine/engine.dart';
import '../data/database.dart';

class PhrasesScreen extends StatefulWidget {
  const PhrasesScreen({super.key});

  @override
  State<PhrasesScreen> createState() => _PhrasesScreenState();
}

class _PhrasesScreenState extends State<PhrasesScreen> {
  final _engine = LearningEngine();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('🗣️ Useful Phrases')),
      body: ListView.builder(
        padding: const EdgeInsets.all(12),
        itemCount: AppDatabase.phrases.length,
        itemBuilder: (ctx, i) {
          final phrase = AppDatabase.phrases[i];
          _engine.markPhraseSeen(phrase.id);
          return Card(
            color: const Color(0xFF161B22),
            margin: const EdgeInsets.only(bottom: 10),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: ListTile(
              contentPadding: const EdgeInsets.all(16),
              leading: CircleAvatar(
                backgroundColor: const Color(0xFF79C0FF).withOpacity(0.15),
                child: Text('${phrase.id}', style: const TextStyle(color: Color(0xFF79C0FF), fontSize: 12, fontWeight: FontWeight.bold)),
              ),
              title: Text(phrase.phrase, style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 15)),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 4),
                  Text(phrase.meaningAr, style: const TextStyle(color: Color(0xFF58A6FF), fontSize: 13)),
                  const SizedBox(height: 2),
                  Text(phrase.context, style: const TextStyle(color: Color(0xFF484F58), fontSize: 11)),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

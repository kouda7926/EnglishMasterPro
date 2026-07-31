import 'package:flutter/material.dart';
import '../engine/engine.dart';
import '../data/database.dart';

class IdiomsScreen extends StatefulWidget {
  const IdiomsScreen({super.key});

  @override
  State<IdiomsScreen> createState() => _IdiomsScreenState();
}

class _IdiomsScreenState extends State<IdiomsScreen> {
  final _engine = LearningEngine();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('💬 Idioms & Expressions')),
      body: ListView.builder(
        padding: const EdgeInsets.all(12),
        itemCount: AppDatabase.idioms.length,
        itemBuilder: (ctx, i) {
          final idiom = AppDatabase.idioms[i];
          _engine.markIdiomSeen(idiom.id);
          return Card(
            color: const Color(0xFF161B22),
            margin: const EdgeInsets.only(bottom: 10),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(color: const Color(0xFFD2A8FF).withOpacity(0.15), borderRadius: BorderRadius.circular(8)),
                        child: Text('#${idiom.id}', style: const TextStyle(color: Color(0xFFD2A8FF), fontSize: 12)),
                      ),
                      const SizedBox(width: 8),
                      Expanded(child: Text(idiom.idiom, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white))),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(idiom.meaningAr, style: const TextStyle(fontSize: 15, color: Color(0xFF58A6FF))),
                  const SizedBox(height: 8),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(color: const Color(0xFF21262D), borderRadius: BorderRadius.circular(8)),
                    child: Text(idiom.example, style: const TextStyle(fontSize: 13, color: Color(0xFF8B949E), fontStyle: FontStyle.italic)),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

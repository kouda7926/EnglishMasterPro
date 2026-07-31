import 'package:flutter/material.dart';
import '../engine/engine.dart';
import '../models.dart';

class GrammarScreen extends StatefulWidget {
  const GrammarScreen({super.key});

  @override
  State<GrammarScreen> createState() => _GrammarScreenState();
}

class _GrammarScreenState extends State<GrammarScreen> {
  final _engine = LearningEngine();
  String _level = 'beginner';

  @override
  Widget build(BuildContext context) {
    final rules = _engine.getGrammarByLevel(_level);
    return Scaffold(
      appBar: AppBar(title: const Text('📝 Grammar')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: ['beginner', 'intermediate', 'advanced'].map((l) => Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4),
                  child: ElevatedButton(
                    onPressed: () => setState(() => _level = l),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _level == l ? const Color(0xFF3FB950) : const Color(0xFF21262D),
                      foregroundColor: _level == l ? Colors.white : const Color(0xFF8B949E),
                    ),
                    child: Text(l[0].toUpperCase() + l.substring(1), style: const TextStyle(fontSize: 12)),
                  ),
                ),
              )).toList(),
            ),
          ),
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              itemCount: rules.length,
              itemBuilder: (ctx, i) => _ruleCard(rules[i]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _ruleCard(GrammarRule rule) {
    final completed = (_engine.profile.settings['rulesCompleted'] as List?)?.contains(rule.id) ?? false;
    return Card(
      color: const Color(0xFF161B22),
      margin: const EdgeInsets.only(bottom: 10),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Theme(
        data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
        child: ExpansionTile(
          leading: CircleAvatar(
            backgroundColor: completed ? const Color(0xFF3FB950).withOpacity(0.2) : const Color(0xFF58A6FF).withOpacity(0.2),
            child: Text('${rule.id}', style: TextStyle(color: completed ? const Color(0xFF3FB950) : const Color(0xFF58A6FF), fontSize: 12, fontWeight: FontWeight.bold)),
          ),
          title: Text(rule.title, style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 14)),
          subtitle: Text(rule.titleAr, style: const TextStyle(color: Color(0xFF8B949E), fontSize: 12)),
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(rule.explanation, style: const TextStyle(color: Color(0xFFC9D1D9), fontSize: 14)),
                  const SizedBox(height: 12),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(color: const Color(0xFF21262D), borderRadius: BorderRadius.circular(8)),
                    child: Text('Example: ${rule.example}', style: const TextStyle(color: Color(0xFF58A6FF), fontStyle: FontStyle.italic, fontSize: 13)),
                  ),
                  const SizedBox(height: 12),
                  if (!completed)
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: () {
                          _engine.markRuleCompleted(rule.id);
                          setState(() {});
                        },
                        icon: const Icon(Icons.check),
                        label: const Text('Mark as Completed'),
                        style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF3FB950)),
                      ),
                    )
                  else
                    const Row(
                      children: [
                        Icon(Icons.check_circle, color: Color(0xFF3FB950), size: 16),
                        SizedBox(width: 8),
                        Text('Completed', style: TextStyle(color: Color(0xFF3FB950))),
                      ],
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

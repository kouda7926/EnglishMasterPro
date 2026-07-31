import 'package:flutter/material.dart';
import '../engine/engine.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _engine = LearningEngine();

  @override
  Widget build(BuildContext context) {
    final p = _engine.profile;
    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('⚙️ Settings', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white)),
            const SizedBox(height: 20),
            _section('Profile', [
              ListTile(
                leading: const Icon(Icons.person, color: Color(0xFF58A6FF)),
                title: const Text('Name', style: TextStyle(color: Colors.white)),
                subtitle: Text(p.name, style: const TextStyle(color: Color(0xFF8B949E))),
                trailing: const Icon(Icons.edit, color: Color(0xFF484F58)),
                onTap: () => _editName(),
              ),
            ]),
            _section('Preferences', [
              SwitchListTile(
                secondary: const Icon(Icons.volume_up, color: Color(0xFF58A6FF)),
                title: const Text('Sound Effects', style: TextStyle(color: Colors.white)),
                value: p.settings['sound'] ?? true,
                onChanged: (v) async {
                  await _engine.updateSettings('sound', v);
                  setState(() {});
                },
                activeColor: const Color(0xFF3FB950),
              ),
              SwitchListTile(
                secondary: const Icon(Icons.dark_mode, color: Color(0xFF58A6FF)),
                title: const Text('Dark Mode', style: TextStyle(color: Colors.white)),
                value: p.settings['darkMode'] ?? true,
                onChanged: (v) async {
                  await _engine.updateSettings('darkMode', v);
                  setState(() {});
                },
                activeColor: const Color(0xFF3FB950),
              ),
            ]),
            _section('Data', [
              ListTile(
                leading: const Icon(Icons.delete_forever, color: Color(0xFFF85149)),
                title: const Text('Reset Progress', style: TextStyle(color: Color(0xFFF85149))),
                subtitle: const Text('Delete all your progress', style: TextStyle(color: Color(0xFF8B949E))),
                onTap: () => _resetProgress(),
              ),
            ]),
            const SizedBox(height: 20),
            Center(
              child: Column(
                children: [
                  Text('English Master Pro v3.0', style: TextStyle(color: const Color(0xFF484F58), fontSize: 12)),
                  const Text('Built with Flutter', style: TextStyle(color: Color(0xFF30363D), fontSize: 11)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _section(String title, List<Widget> children) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF8B949E))),
        const SizedBox(height: 8),
        Container(
          decoration: BoxDecoration(color: const Color(0xFF161B22), borderRadius: BorderRadius.circular(16)),
          child: Column(children: children),
        ),
        const SizedBox(height: 16),
      ],
    );
  }

  void _editName() {
    final controller = TextEditingController(text: _engine.profile.name);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF161B22),
        title: const Text('Edit Name', style: TextStyle(color: Colors.white)),
        content: TextField(
          controller: controller,
          style: const TextStyle(color: Colors.white),
          decoration: InputDecoration(
            filled: true,
            fillColor: const Color(0xFF21262D),
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel', style: TextStyle(color: Color(0xFF8B949E)))),
          TextButton(
            onPressed: () async {
              await _engine.updateName(controller.text.trim());
              if (ctx.mounted) Navigator.pop(ctx);
              setState(() {});
            },
            child: const Text('Save', style: TextStyle(color: Color(0xFF58A6FF))),
          ),
        ],
      ),
    );
  }

  void _resetProgress() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF161B22),
        title: const Text('Reset Progress?', style: TextStyle(color: Color(0xFFF85149))),
        content: const Text('This will delete all your progress. This action cannot be undone.', style: TextStyle(color: Color(0xFF8B949E))),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel', style: TextStyle(color: Color(0xFF8B949E)))),
          TextButton(
            onPressed: () async {
              final engine = LearningEngine();
              engine.profile.xp = 0;
              engine.profile.streak = 0;
              engine.profile.totalCorrect = 0;
              engine.profile.totalAnswered = 0;
              engine.profile.wordsLearned = 0;
              engine.profile.lessonsCompleted = 0;
              engine.profile.unlockedAchievements = [];
              await engine.updateSettings('reset', true);
              if (ctx.mounted) Navigator.pop(ctx);
              setState(() {});
            },
            child: const Text('Reset', style: TextStyle(color: Color(0xFFF85149))),
          ),
        ],
      ),
    );
  }
}

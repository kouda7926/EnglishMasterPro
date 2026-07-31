import 'package:flutter/material.dart';
import '../engine/engine.dart';
import 'home_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _controller = TextEditingController();
  final _engine = LearningEngine();

  @override
  void initState() {
    super.initState();
    _controller.text = _engine.profile.name;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(begin: Alignment.topCenter, end: Alignment.bottomCenter, colors: [Color(0xFF0D1117), Color(0xFF161B22)]),
        ),
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(32),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.person_add, size: 80, color: Color(0xFF58A6FF)),
                  const SizedBox(height: 30),
                  Text('مرحباً بك!', style: Theme.of(context).textTheme.headlineLarge?.copyWith(fontSize: 28)),
                  const SizedBox(height: 10),
                  Text('What is your name?', style: Theme.of(context).textTheme.bodyLarge?.copyWith(fontSize: 16)),
                  const SizedBox(height: 30),
                  TextField(
                    controller: _controller,
                    style: const TextStyle(color: Colors.white, fontSize: 18),
                    textAlign: TextAlign.center,
                    decoration: InputDecoration(
                      hintText: 'أدخل اسمك...',
                      hintStyle: const TextStyle(color: Color(0xFF484F58)),
                      filled: true,
                      fillColor: const Color(0xFF21262D),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide.none),
                      focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: const BorderSide(color: Color(0xFF58A6FF), width: 2)),
                    ),
                    onSubmitted: (_) => _startLearning(),
                  ),
                  const SizedBox(height: 24),
                  SizedBox(
                    width: double.infinity, height: 52,
                    child: ElevatedButton(
                      onPressed: _startLearning,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF58A6FF),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      ),
                      child: const Text('ابدأ التعلم! 🚀', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  void _startLearning() async {
    final name = _controller.text.trim();
    if (name.isNotEmpty) {
      await _engine.updateName(name);
      if (mounted) {
        Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const HomeScreen()));
      }
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'engine/engine.dart';
import 'screens/splash_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await LearningEngine().init();
  runApp(const EnglishMasterApp());
}

class EnglishMasterApp extends StatelessWidget {
  const EnglishMasterApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'English Master Pro',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        primarySwatch: Colors.blue,
        scaffoldBackgroundColor: const Color(0xFF0D1117),
        cardColor: const Color(0xFF161B22),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF58A6FF),
          secondary: Color(0xFF3FB950),
          surface: Color(0xFF161B22),
          error: Color(0xFFF85149),
        ),
        textTheme: GoogleFonts.cairoTextTheme(ThemeData.dark().textTheme).copyWith(
          headlineLarge: GoogleFonts.cairo(color: Colors.white, fontWeight: FontWeight.bold),
          headlineMedium: GoogleFonts.cairo(color: Colors.white, fontWeight: FontWeight.w600),
          bodyLarge: GoogleFonts.cairo(color: const Color(0xFFC9D1D9)),
          bodyMedium: GoogleFonts.cairo(color: const Color(0xFF8B949E)),
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF161B22),
          elevation: 0,
          centerTitle: true,
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF58A6FF),
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          ),
        ),
      ),
      home: const SplashScreen(),
    );
  }
}

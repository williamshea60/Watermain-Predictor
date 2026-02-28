import 'package:shared_preferences/shared_preferences.dart';

import '../models/incident.dart';

class QuietHours {
  const QuietHours({required this.startHour, required this.endHour});

  final int startHour;
  final int endHour;
}

class SettingsService {
  static const _confidenceKey = 'min_confidence';
  static const _quietStartKey = 'quiet_start';
  static const _quietEndKey = 'quiet_end';

  Future<void> setMinConfidence(ConfidenceLevel confidence) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_confidenceKey, confidence.name);
  }

  Future<ConfidenceLevel> getMinConfidence() async {
    final prefs = await SharedPreferences.getInstance();
    final value = prefs.getString(_confidenceKey);
    return ConfidenceLevel.values.where((e) => e.name == value).firstOrNull ?? ConfidenceLevel.low;
  }

  Future<void> setQuietHours(QuietHours quietHours) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(_quietStartKey, quietHours.startHour);
    await prefs.setInt(_quietEndKey, quietHours.endHour);
  }

  Future<QuietHours> getQuietHours() async {
    final prefs = await SharedPreferences.getInstance();
    return QuietHours(
      startHour: prefs.getInt(_quietStartKey) ?? 22,
      endHour: prefs.getInt(_quietEndKey) ?? 7,
    );
  }
}

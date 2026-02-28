import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';

import 'repositories/incident_repository.dart';
import 'screens/home_screen.dart';
import 'services/api_service.dart';
import 'services/notification_service.dart';
import 'services/settings_service.dart';
import 'state/app_controller.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  const baseUrl = String.fromEnvironment(
    'BACKEND_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );

  final apiService = ApiService(baseUrl: baseUrl);
  final repository = IncidentRepository(apiService);
  final settingsService = SettingsService();
  final controller = AppController(repository: repository, settingsService: settingsService);

  final notifications = NotificationService(FirebaseMessaging.instance);
  await notifications.initialize();
  await controller.initialize();

  runApp(BreakWatchApp(controller: controller));
}

class BreakWatchApp extends StatelessWidget {
  const BreakWatchApp({super.key, required this.controller});

  final AppController controller;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'BreakWatch',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: HomeScreen(controller: controller),
    );
  }
}

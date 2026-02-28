import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';

class NotificationService {
  NotificationService(this._messaging);

  final FirebaseMessaging _messaging;

  Future<void> initialize() async {
    try {
      await Firebase.initializeApp();
      await _messaging.requestPermission(alert: true, badge: true, sound: true);

      FirebaseMessaging.onMessage.listen((RemoteMessage message) {
        debugPrint('Foreground FCM message received: ${message.messageId}');
      });

      FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
        debugPrint('Notification opened app: ${message.messageId}');
      });

      final token = await _messaging.getToken();
      debugPrint('FCM token (stub): $token');
      // TODO: Send token to backend registration endpoint when available.
    } on Exception catch (e) {
      debugPrint('FCM initialization skipped due to error: $e');
    }
  }
}

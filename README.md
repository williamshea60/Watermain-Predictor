# BreakWatch

BreakWatch is a Flutter mobile app for Android and iOS that visualizes watermain incidents in Toronto.

## Features

- Google Map centered on Toronto with incident pins loaded from `GET /incidents`.
- Pin colors map to confidence level (`low`, `medium`, `high`).
- Incident list below map sorted by `last_seen` descending.
- Incident detail screen with score breakdown and supporting signal links.
- Settings screen to configure minimum confidence threshold and quiet hours.
- Clean architecture layering (`services` -> `repository` -> `state` -> `screens/widgets`).
- Firebase Cloud Messaging integration stubs for push notification wiring.

## Backend base URL configuration

Set backend URL at build/runtime with dart-define:

```bash
flutter run --dart-define=BACKEND_BASE_URL=https://your-api.example.com
```

If not provided, the app defaults to `http://10.0.2.2:8000`.

## Getting started

> Requires latest stable Flutter SDK and platform toolchains.

1. Install dependencies:
   ```bash
   flutter pub get
   ```
2. Configure Firebase for each platform (for FCM):
   - Android: add `android/app/google-services.json`.
   - iOS: add `ios/Runner/GoogleService-Info.plist`.
3. Ensure Firebase platform setup is complete (`firebase_core`, `firebase_messaging`).

### Run on Android emulator

```bash
flutter emulators
flutter emulators --launch <android_emulator_id>
flutter run -d <android_device_id> --dart-define=BACKEND_BASE_URL=http://10.0.2.2:8000
```

### Run on iOS simulator

```bash
open -a Simulator
flutter devices
flutter run -d <ios_simulator_id> --dart-define=BACKEND_BASE_URL=http://localhost:8000
```

## Project structure

- `lib/services`: API, settings persistence, and FCM services.
- `lib/repositories`: business-facing data access.
- `lib/state`: app-level state management and error handling.
- `lib/screens`: home, detail, and settings screens.
- `lib/widgets`: reusable UI parts.

## Error handling notes

- API calls enforce timeout and status checks.
- malformed payloads are guarded with explicit parse exceptions.
- UI surfaces refresh failures without crashing.

## Notes

- If platform folders are missing, run:
  ```bash
  flutter create .
  ```
  Then re-run `flutter pub get`.

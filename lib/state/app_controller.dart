import 'package:flutter/foundation.dart';

import '../models/incident.dart';
import '../repositories/incident_repository.dart';
import '../services/settings_service.dart';

class AppController extends ChangeNotifier {
  AppController({required IncidentRepository repository, required SettingsService settingsService})
      : _repository = repository,
        _settingsService = settingsService;

  final IncidentRepository _repository;
  final SettingsService _settingsService;

  List<Incident> _allIncidents = [];
  bool _isLoading = false;
  String? _errorMessage;
  ConfidenceLevel _minConfidence = ConfidenceLevel.low;
  QuietHours _quietHours = const QuietHours(startHour: 22, endHour: 7);

  List<Incident> get incidents =>
      _allIncidents.where((incident) => incident.confidence.index >= _minConfidence.index).toList(growable: false);
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  ConfidenceLevel get minConfidence => _minConfidence;
  QuietHours get quietHours => _quietHours;

  Future<void> initialize() async {
    _minConfidence = await _settingsService.getMinConfidence();
    _quietHours = await _settingsService.getQuietHours();
    await refreshIncidents();
  }

  Future<void> refreshIncidents() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _allIncidents = await _repository.getIncidents();
    } on Exception catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> updateMinConfidence(ConfidenceLevel confidence) async {
    _minConfidence = confidence;
    notifyListeners();
    await _settingsService.setMinConfidence(confidence);
  }

  Future<void> updateQuietHours(QuietHours quietHours) async {
    _quietHours = quietHours;
    notifyListeners();
    await _settingsService.setQuietHours(quietHours);
  }
}

import '../models/incident.dart';
import '../services/api_service.dart';

class IncidentRepository {
  IncidentRepository(this._apiService);

  final ApiService _apiService;

  Future<List<Incident>> getIncidents() async {
    final incidents = await _apiService.fetchIncidents();
    incidents.sort((a, b) => b.lastSeen.compareTo(a.lastSeen));
    return incidents;
  }
}

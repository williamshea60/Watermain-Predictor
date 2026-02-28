import 'package:breakwatch/models/incident.dart';
import 'package:breakwatch/repositories/incident_repository.dart';
import 'package:breakwatch/services/api_service.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakeApiService extends ApiService {
  _FakeApiService(this._incidents) : super(baseUrl: 'http://localhost');

  final List<Incident> _incidents;

  @override
  Future<List<Incident>> fetchIncidents() async => _incidents;
}

void main() {
  test('repository sorts incidents by lastSeen desc', () async {
    final early = Incident.fromJson({
      'id': 'a',
      'title': 'Old',
      'description': '',
      'latitude': 0,
      'longitude': 0,
      'last_seen': '2024-01-01T01:00:00Z',
      'confidence': 'low',
      'score': 0.1,
      'score_breakdown': {},
      'signal_links': [],
    });
    final recent = Incident.fromJson({
      'id': 'b',
      'title': 'Recent',
      'description': '',
      'latitude': 0,
      'longitude': 0,
      'last_seen': '2024-02-01T01:00:00Z',
      'confidence': 'high',
      'score': 0.9,
      'score_breakdown': {},
      'signal_links': [],
    });

    final repo = IncidentRepository(_FakeApiService([early, recent]));
    final result = await repo.getIncidents();

    expect(result.first.id, 'b');
    expect(result.last.id, 'a');
  });
}

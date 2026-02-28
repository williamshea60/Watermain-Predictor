enum ConfidenceLevel { low, medium, high }

class ScoreBreakdown {
  const ScoreBreakdown({
    required this.pressure,
    required this.weather,
    required this.age,
    required this.soil,
  });

  final double pressure;
  final double weather;
  final double age;
  final double soil;

  factory ScoreBreakdown.fromJson(Map<String, dynamic> json) {
    return ScoreBreakdown(
      pressure: (json['pressure'] as num?)?.toDouble() ?? 0,
      weather: (json['weather'] as num?)?.toDouble() ?? 0,
      age: (json['age'] as num?)?.toDouble() ?? 0,
      soil: (json['soil'] as num?)?.toDouble() ?? 0,
    );
  }
}

class Incident {
  const Incident({
    required this.id,
    required this.title,
    required this.description,
    required this.latitude,
    required this.longitude,
    required this.lastSeen,
    required this.confidence,
    required this.score,
    required this.scoreBreakdown,
    required this.signalLinks,
  });

  final String id;
  final String title;
  final String description;
  final double latitude;
  final double longitude;
  final DateTime lastSeen;
  final ConfidenceLevel confidence;
  final double score;
  final ScoreBreakdown scoreBreakdown;
  final List<Uri> signalLinks;

  factory Incident.fromJson(Map<String, dynamic> json) {
    final confidenceRaw = (json['confidence'] as String? ?? 'low').toLowerCase();
    final confidence = switch (confidenceRaw) {
      'high' => ConfidenceLevel.high,
      'medium' || 'med' => ConfidenceLevel.medium,
      _ => ConfidenceLevel.low,
    };

    final linksRaw = json['signal_links'] as List<dynamic>? ?? [];

    return Incident(
      id: json['id']?.toString() ?? '',
      title: json['title'] as String? ?? 'Unknown Incident',
      description: json['description'] as String? ?? 'No details provided.',
      latitude: (json['latitude'] as num?)?.toDouble() ?? 0,
      longitude: (json['longitude'] as num?)?.toDouble() ?? 0,
      lastSeen: DateTime.tryParse(json['last_seen'] as String? ?? '') ?? DateTime.fromMillisecondsSinceEpoch(0),
      confidence: confidence,
      score: (json['score'] as num?)?.toDouble() ?? 0,
      scoreBreakdown: ScoreBreakdown.fromJson(json['score_breakdown'] as Map<String, dynamic>? ?? {}),
      signalLinks: linksRaw
          .map((e) => Uri.tryParse(e.toString()))
          .whereType<Uri>()
          .toList(growable: false),
    );
  }
}

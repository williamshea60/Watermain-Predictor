import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/incident.dart';

class ApiException implements Exception {
  ApiException(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() => 'ApiException(statusCode: $statusCode, message: $message)';
}

class ApiService {
  ApiService({http.Client? client, required this.baseUrl}) : _client = client ?? http.Client();

  final http.Client _client;
  final String baseUrl;

  Future<List<Incident>> fetchIncidents() async {
    final uri = Uri.parse('$baseUrl/incidents');

    try {
      final response = await _client.get(uri).timeout(const Duration(seconds: 15));

      if (response.statusCode != 200) {
        throw ApiException('Unexpected server response.', statusCode: response.statusCode);
      }

      final decoded = jsonDecode(response.body);
      if (decoded is! List) {
        throw ApiException('Malformed incidents payload.');
      }

      return decoded
          .whereType<Map<String, dynamic>>()
          .map(Incident.fromJson)
          .toList(growable: false);
    } on ApiException {
      rethrow;
    } on FormatException {
      throw ApiException('Failed to parse incidents response.');
    } on Exception catch (e) {
      throw ApiException('Network error fetching incidents: $e');
    }
  }

  void dispose() {
    _client.close();
  }
}

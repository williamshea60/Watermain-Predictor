import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../models/incident.dart';

class IncidentDetailScreen extends StatelessWidget {
  const IncidentDetailScreen({super.key, required this.incident});

  final Incident incident;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(incident.title)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text(incident.description, style: Theme.of(context).textTheme.bodyLarge),
          const SizedBox(height: 16),
          Text('Score: ${incident.score.toStringAsFixed(2)}'),
          const SizedBox(height: 12),
          const Text('Score Breakdown', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          _metricRow('Pressure', incident.scoreBreakdown.pressure),
          _metricRow('Weather', incident.scoreBreakdown.weather),
          _metricRow('Pipe Age', incident.scoreBreakdown.age),
          _metricRow('Soil', incident.scoreBreakdown.soil),
          const SizedBox(height: 20),
          const Text('Supporting Signals', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          ...incident.signalLinks.map(
            (link) => ListTile(
              contentPadding: EdgeInsets.zero,
              title: Text(link.toString()),
              trailing: const Icon(Icons.open_in_new),
              onTap: () => _openLink(context, link),
            ),
          ),
        ],
      ),
    );
  }

  Widget _metricRow(String name, double value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Expanded(child: Text(name)),
          Text(value.toStringAsFixed(2)),
        ],
      ),
    );
  }

  Future<void> _openLink(BuildContext context, Uri link) async {
    final ok = await launchUrl(link, mode: LaunchMode.externalApplication);
    if (!ok && context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Could not open link: $link')),
      );
    }
  }
}

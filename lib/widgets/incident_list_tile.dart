import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../models/incident.dart';

class IncidentListTile extends StatelessWidget {
  const IncidentListTile({super.key, required this.incident, required this.onTap});

  final Incident incident;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        title: Text(incident.title),
        subtitle: Text('${incident.description}\nLast seen: ${DateFormat.yMMMd().add_jm().format(incident.lastSeen.toLocal())}'),
        isThreeLine: true,
        trailing: Text(
          incident.confidence.name.toUpperCase(),
          style: TextStyle(color: _confidenceColor(incident.confidence), fontWeight: FontWeight.bold),
        ),
        onTap: onTap,
      ),
    );
  }

  Color _confidenceColor(ConfidenceLevel confidence) {
    return switch (confidence) {
      ConfidenceLevel.low => Colors.green,
      ConfidenceLevel.medium => Colors.orange,
      ConfidenceLevel.high => Colors.red,
    };
  }
}

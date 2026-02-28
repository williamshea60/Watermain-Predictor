import 'package:flutter/material.dart';

import '../models/incident.dart';
import '../services/settings_service.dart';
import '../state/app_controller.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key, required this.controller});

  final AppController controller;

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late ConfidenceLevel _confidence;
  late int _quietStart;
  late int _quietEnd;

  @override
  void initState() {
    super.initState();
    _confidence = widget.controller.minConfidence;
    _quietStart = widget.controller.quietHours.startHour;
    _quietEnd = widget.controller.quietHours.endHour;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        actions: [
          TextButton(
            onPressed: _save,
            child: const Text('Save'),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Minimum Confidence Threshold', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          SegmentedButton<ConfidenceLevel>(
            segments: const [
              ButtonSegment(value: ConfidenceLevel.low, label: Text('Low')),
              ButtonSegment(value: ConfidenceLevel.medium, label: Text('Medium')),
              ButtonSegment(value: ConfidenceLevel.high, label: Text('High')),
            ],
            selected: {_confidence},
            onSelectionChanged: (selection) {
              setState(() {
                _confidence = selection.first;
              });
            },
          ),
          const SizedBox(height: 24),
          const Text('Quiet Hours', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          _hourSelector(
            label: 'Start',
            hour: _quietStart,
            onChanged: (value) => setState(() => _quietStart = value),
          ),
          _hourSelector(
            label: 'End',
            hour: _quietEnd,
            onChanged: (value) => setState(() => _quietEnd = value),
          ),
        ],
      ),
    );
  }

  Widget _hourSelector({required String label, required int hour, required ValueChanged<int> onChanged}) {
    return Row(
      children: [
        Expanded(child: Text(label)),
        DropdownButton<int>(
          value: hour,
          items: List.generate(24, (index) => index)
              .map((h) => DropdownMenuItem(value: h, child: Text('${h.toString().padLeft(2, '0')}:00')))
              .toList(growable: false),
          onChanged: (value) {
            if (value != null) {
              onChanged(value);
            }
          },
        ),
      ],
    );
  }

  Future<void> _save() async {
    await widget.controller.updateMinConfidence(_confidence);
    await widget.controller.updateQuietHours(QuietHours(startHour: _quietStart, endHour: _quietEnd));
    if (mounted) {
      Navigator.of(context).pop();
    }
  }
}

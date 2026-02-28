import 'dart:async';

import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

import '../models/incident.dart';
import '../state/app_controller.dart';
import '../widgets/incident_list_tile.dart';
import 'incident_detail_screen.dart';
import 'settings_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key, required this.controller});

  final AppController controller;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _mapCompleter = Completer<GoogleMapController>();

  static const _torontoCenter = LatLng(43.6532, -79.3832);

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: widget.controller,
      builder: (context, _) {
        return Scaffold(
          appBar: AppBar(
            title: const Text('BreakWatch'),
            actions: [
              IconButton(
                icon: const Icon(Icons.refresh),
                onPressed: widget.controller.refreshIncidents,
              ),
              IconButton(
                icon: const Icon(Icons.settings),
                onPressed: () async {
                  await Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => SettingsScreen(controller: widget.controller),
                    ),
                  );
                },
              ),
            ],
          ),
          body: Column(
            children: [
              SizedBox(
                height: 280,
                child: GoogleMap(
                  initialCameraPosition: const CameraPosition(target: _torontoCenter, zoom: 11),
                  onMapCreated: (controller) {
                    if (!_mapCompleter.isCompleted) {
                      _mapCompleter.complete(controller);
                    }
                  },
                  markers: _buildMarkers(widget.controller.incidents),
                ),
              ),
              if (widget.controller.errorMessage != null)
                Padding(
                  padding: const EdgeInsets.all(8),
                  child: Text(
                    'Unable to refresh incidents: ${widget.controller.errorMessage}',
                    style: const TextStyle(color: Colors.red),
                  ),
                ),
              Expanded(
                child: widget.controller.isLoading
                    ? const Center(child: CircularProgressIndicator())
                    : ListView.builder(
                        itemCount: widget.controller.incidents.length,
                        itemBuilder: (context, index) {
                          final incident = widget.controller.incidents[index];
                          return IncidentListTile(
                            incident: incident,
                            onTap: () => Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (_) => IncidentDetailScreen(incident: incident),
                              ),
                            ),
                          );
                        },
                      ),
              ),
            ],
          ),
        );
      },
    );
  }

  Set<Marker> _buildMarkers(List<Incident> incidents) {
    return incidents
        .map(
          (incident) => Marker(
            markerId: MarkerId(incident.id),
            position: LatLng(incident.latitude, incident.longitude),
            infoWindow: InfoWindow(title: incident.title, snippet: incident.confidence.name),
            icon: BitmapDescriptor.defaultMarkerWithHue(
              switch (incident.confidence) {
                ConfidenceLevel.low => BitmapDescriptor.hueGreen,
                ConfidenceLevel.medium => BitmapDescriptor.hueOrange,
                ConfidenceLevel.high => BitmapDescriptor.hueRed,
              },
            ),
          ),
        )
        .toSet();
  }
}

# Changelog

All notable changes to EdgePulse-Pi5 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-02-09

### Added
- Initial release of EdgePulse-Pi5
- Real-time vital signs monitoring
  - Heart rate measurement via MAX30102
  - Blood oxygen saturation (SpO₂) measurement
  - Body temperature measurement via DS18B20
- Edge-computing architecture with no cloud dependency
- Multi-channel alert system
  - Email notifications
  - SMS alerts via Twilio
  - Local buzzer and LED indicators
- Data management
  - SQLite database for local storage
  - CSV export functionality
  - Automatic data cleanup
- Web-based dashboard
  - Real-time monitoring interface
  - Historical data visualization
  - Alert history
- Threshold-based anomaly detection
  - Configurable thresholds for all vital signs
  - Multi-level severity (info, warning, critical)
  - Trend analysis
- Command-line interface
  - Status checking
  - Data export
  - Alert testing
  - Configuration validation
- Systemd service integration
- Comprehensive documentation
  - Installation guide
  - Hardware setup instructions
  - Configuration guide
  - Troubleshooting tips
- Unit tests and pytest integration
- Setup automation script

### Features
- On-device processing with <100ms latency
- Privacy-preserving local data storage
- Configurable measurement intervals
- Alert cooldown to prevent spam
- Automatic sensor error recovery
- Low CPU and memory footprint

### Documentation
- README.md with full project documentation
- QUICKSTART.md for rapid deployment
- CONTRIBUTING.md for contributors
- LICENSE (MIT)
- Hardware wiring diagrams
- API documentation

## [Unreleased]

### Planned Features
- Mobile app integration
- Machine learning for predictive analytics
- Multi-patient support
- Integration with hospital systems (HL7/FHIR)
- Advanced arrhythmia detection algorithms
- Sleep monitoring capabilities
- Stress level analysis
- Cloud sync option (optional)
- Data encryption
- User authentication for web dashboard

---

[1.0.0]: https://github.com/yourusername/edgepulse-pi5/releases/tag/v1.0.0

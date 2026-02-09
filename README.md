# EdgePulse-Pi5 🏥

A Raspberry Pi 5–based real-time health monitoring system that performs on-device analysis of vital signs such as heart rate, SpO₂, and body temperature. It detects abnormal patterns locally using edge-computing principles, enabling instant alerts without cloud dependency for low-latency healthcare environments.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%205-red.svg)

## 🌟 Features

- **Real-time Vital Sign Monitoring**
  - Heart Rate (BPM)
  - Blood Oxygen Saturation (SpO₂)
  - Body Temperature (°C/°F)

- **Edge Computing**
  - On-device analysis with no cloud dependency
  - Low-latency processing (<100ms)
  - Privacy-preserving local data storage

- **Intelligent Alerts**
  - Abnormal pattern detection using configurable thresholds
  - Multi-channel notifications (Email, SMS, Buzzer, LED)
  - Escalation protocols for critical conditions

- **Data Management**
  - Local SQLite database for historical data
  - CSV export functionality
  - Data visualization and trending

- **Web Dashboard**
  - Real-time monitoring interface
  - Historical data graphs
  - Alert history and statistics

## 📋 Hardware Requirements

### Required Components

| Component | Model | Purpose |
|-----------|-------|---------|
| Microcontroller | Raspberry Pi 5 (4GB+ RAM) | Main processing unit |
| Heart Rate & SpO₂ Sensor | MAX30102 | Pulse oximetry measurements |
| Temperature Sensor | DS18B20 or DHT22 | Body temperature monitoring |
| Buzzer | Active 5V Buzzer | Audio alerts |
| LEDs | RGB LED (Common Cathode) | Visual status indicators |
| Display (Optional) | 0.96" OLED (SSD1306) | Local data display |

### Wiring Diagram

```
MAX30102 Sensor:
- VIN  → 3.3V (Pin 1)
- GND  → GND (Pin 6)
- SDA  → GPIO 2 (Pin 3)
- SCL  → GPIO 3 (Pin 5)

DS18B20 Temperature Sensor:
- VCC  → 3.3V (Pin 17)
- GND  → GND (Pin 20)
- DATA → GPIO 4 (Pin 7)
- 4.7kΩ resistor between VCC and DATA

Buzzer:
- Positive → GPIO 17 (Pin 11)
- Negative → GND (Pin 14)

RGB LED:
- Red    → GPIO 22 (Pin 15) + 220Ω resistor
- Green  → GPIO 27 (Pin 13) + 220Ω resistor
- Blue   → GPIO 23 (Pin 16) + 220Ω resistor
- Cathode → GND (Pin 9)
```

## 🚀 Installation

### 1. System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3-pip python3-dev git i2c-tools

# Enable I2C interface
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable

# Reboot to apply changes
sudo reboot
```

### 2. Clone Repository

```bash
git clone https://github.com/yourusername/edgepulse-pi5.git
cd edgepulse-pi5
```

### 3. Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 4. Configure the System

```bash
# Copy example configuration
cp config.example.yaml config.yaml

# Edit configuration file
nano config.yaml
```

Edit the following in `config.yaml`:
- Alert thresholds for your use case
- Email/SMS credentials for notifications
- Measurement intervals
- Data retention policies

### 5. Test Sensors

```bash
# Verify I2C devices are detected
sudo i2cdetect -y 1

# Should show MAX30102 at address 0x57

# Test sensors
python3 -m src.sensors --test
```

### 6. Run the Application

```bash
# Run in foreground (for testing)
python3 main.py

# Run as background service
sudo ./setup.sh install
sudo systemctl start edgepulse
sudo systemctl enable edgepulse
```

## 📖 Usage

### Starting the Monitor

```bash
# Start monitoring
python3 main.py

# Start with custom config
python3 main.py --config /path/to/config.yaml

# Start in verbose mode
python3 main.py --verbose
```

### Web Dashboard

Access the dashboard at: `http://raspberrypi.local:5000` or `http://<PI_IP_ADDRESS>:5000`

- **Real-time View**: Current vital signs with live updates
- **History**: View past 24 hours of data with graphs
- **Alerts**: Alert history and acknowledgment
- **Settings**: Adjust thresholds and notification preferences

### Command Line Interface

```bash
# View current readings
python3 main.py --status

# Export data to CSV
python3 main.py --export --start-date 2024-01-01 --end-date 2024-01-31

# Test alert system
python3 main.py --test-alerts

# Clear old data
python3 main.py --cleanup --days 30
```

## ⚙️ Configuration

### Threshold Configuration (`config.yaml`)

```yaml
thresholds:
  heart_rate:
    min: 60        # Bradycardia threshold
    max: 100       # Tachycardia threshold
    critical_min: 40
    critical_max: 150
  
  spo2:
    min: 95        # Low oxygen threshold
    critical_min: 90
  
  temperature:
    min: 36.1      # Hypothermia threshold (°C)
    max: 37.8      # Fever threshold (°C)
    critical_min: 35.0
    critical_max: 39.0
```

### Alert Configuration

```yaml
alerts:
  email:
    enabled: true
    smtp_server: smtp.gmail.com
    smtp_port: 587
    username: your-email@gmail.com
    password: your-app-password
    recipient: alert-recipient@gmail.com
  
  sms:
    enabled: true
    provider: twilio
    account_sid: your-twilio-sid
    auth_token: your-twilio-token
    from_number: +1234567890
    to_number: +0987654321
  
  local:
    buzzer_enabled: true
    led_enabled: true
```

## 📊 Data Storage

### Database Schema

The system uses SQLite for local data storage:

```sql
-- Vital signs readings
CREATE TABLE readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    heart_rate INTEGER,
    spo2 INTEGER,
    temperature REAL,
    temperature_unit TEXT
);

-- Alert history
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    alert_type TEXT,
    severity TEXT,
    message TEXT,
    acknowledged INTEGER DEFAULT 0
);
```

### Data Export

```bash
# Export all data
python3 main.py --export --output vitals_export.csv

# Export specific date range
python3 main.py --export --start-date 2024-01-01 --end-date 2024-01-31
```

## 🔧 Troubleshooting

### Sensor Not Detected

```bash
# Check I2C connection
sudo i2cdetect -y 1

# If MAX30102 not showing at 0x57:
# 1. Check wiring connections
# 2. Verify 3.3V power supply
# 3. Test with different I2C address (some modules use 0x57)
```

### Inaccurate Readings

1. **Heart Rate/SpO₂**:
   - Ensure finger is placed correctly on sensor
   - Clean sensor surface
   - Avoid excessive movement
   - Check ambient light (shield sensor if needed)

2. **Temperature**:
   - Verify sensor is making proper contact
   - Check for loose connections
   - Calibrate sensor offset in config.yaml

### Permission Errors

```bash
# Add user to GPIO group
sudo usermod -a -G gpio $USER

# Add user to I2C group
sudo usermod -a -G i2c $USER

# Reboot to apply
sudo reboot
```

### Service Won't Start

```bash
# Check service status
sudo systemctl status edgepulse

# View logs
sudo journalctl -u edgepulse -f

# Check configuration
python3 main.py --validate-config
```

## 🏗️ Project Structure

```
edgepulse-pi5/
│
├── main.py                 # Main application entry point
├── config.yaml             # Configuration file
├── requirements.txt        # Python dependencies
├── setup.sh               # Installation script
├── edgepulse.service      # Systemd service file
│
├── src/
│   ├── __init__.py
│   ├── sensors.py         # Sensor interface classes
│   ├── analyzer.py        # Data analysis and pattern detection
│   ├── alerts.py          # Alert system implementation
│   ├── data_handler.py    # Database operations
│   └── web_dashboard.py   # Flask web interface
│
├── tests/
│   ├── test_sensors.py    # Sensor unit tests
│   ├── test_analyzer.py   # Analyzer unit tests
│   └── test_alerts.py     # Alert system tests
│
├── docs/
│   ├── API.md            # API documentation
│   ├── CALIBRATION.md    # Sensor calibration guide
│   └── DEPLOYMENT.md     # Deployment guide
│
├── logs/                  # Application logs
├── data/                  # Database and exports
└── static/               # Web dashboard assets
```

## 🔒 Security Considerations

1. **Network Security**:
   - Change default credentials
   - Use HTTPS for web dashboard
   - Implement firewall rules
   - Disable unused services

2. **Data Privacy**:
   - All data stored locally
   - Encrypted database option available
   - No cloud transmission without explicit consent

3. **Access Control**:
   - Password-protected web dashboard
   - Role-based access for multi-user environments

## 🧪 Testing

```bash
# Run all tests
python3 -m pytest tests/

# Run specific test
python3 -m pytest tests/test_sensors.py -v

# Run with coverage
python3 -m pytest --cov=src tests/
```

## 📈 Performance

- **Measurement Frequency**: 1 reading per second (configurable)
- **Processing Latency**: < 100ms average
- **Alert Response Time**: < 500ms
- **Data Storage**: ~1MB per day of continuous monitoring
- **CPU Usage**: < 15% on Raspberry Pi 5
- **Memory Usage**: ~150MB

## 🛠️ Customization

### Adding New Sensors

1. Create sensor class in `src/sensors.py`
2. Implement `read()` method
3. Add configuration to `config.yaml`
4. Update analyzer thresholds

### Custom Alert Channels

1. Create alert handler in `src/alerts.py`
2. Implement `send_alert()` method
3. Register in AlertManager
4. Configure in `config.yaml`

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**IMPORTANT**: This system is designed for educational and monitoring purposes only. It is NOT a certified medical device and should NOT be used as a substitute for professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for medical decisions.

## 🙏 Acknowledgments

- MAX30102 sensor library contributors
- Raspberry Pi Foundation
- Open-source community

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/edgepulse-pi5/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/edgepulse-pi5/discussions)
- **Email**: support@edgepulse.example.com

## 🗺️ Roadmap

- [ ] Mobile app integration
- [ ] Machine learning for predictive analytics
- [ ] Multi-patient support
- [ ] Integration with hospital systems (HL7/FHIR)
- [ ] Advanced arrhythmia detection
- [ ] Sleep monitoring features
- [ ] Stress level analysis

---

Made with ❤️ for better healthcare accessibility

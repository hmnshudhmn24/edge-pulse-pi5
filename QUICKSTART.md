# EdgePulse-Pi5 Quick Start Guide

## 🚀 Quick Installation

### Prerequisites
- Raspberry Pi 5 (4GB+ RAM recommended)
- Raspberry Pi OS (Bullseye or newer)
- MAX30102 sensor
- DS18B20 temperature sensor
- Internet connection

### 1. Clone or Extract Files
```bash
cd ~
# If you have the files, navigate to the directory
cd edgepulse-pi5
```

### 2. Run Installation
```bash
# Make setup script executable
chmod +x setup.sh

# Run full installation (requires sudo)
sudo ./setup.sh install
```

### 3. Configure
```bash
# Edit configuration file
nano config.yaml

# Important settings to update:
# - Email/SMS credentials (if using alerts)
# - Threshold values (adjust to your needs)
```

### 4. Test Sensors
```bash
# Reboot to enable I2C and 1-Wire
sudo reboot

# After reboot, test sensors
cd ~/edgepulse-pi5
./setup.sh test
```

### 5. Run the System

**Option A: Run in foreground (for testing)**
```bash
source venv/bin/activate
python3 main.py
```

**Option B: Run as service (recommended)**
```bash
# Enable and start service
sudo systemctl enable edgepulse
sudo systemctl start edgepulse

# Check status
sudo systemctl status edgepulse

# View logs
sudo journalctl -u edgepulse -f
```

### 6. Access Web Dashboard
Open a browser and navigate to:
```
http://raspberrypi.local:5000
or
http://<YOUR_PI_IP>:5000
```

## 📊 Usage Examples

### View Current Status
```bash
python3 main.py --status
```

### Export Data
```bash
# Export all data
python3 main.py --export

# Export specific date range
python3 main.py --export --start-date 2024-01-01 --end-date 2024-01-31
```

### Test Alerts
```bash
python3 main.py --test-alerts
```

### Clean Old Data
```bash
# Remove data older than 30 days
python3 main.py --cleanup --days 30
```

## 🔧 Troubleshooting

### Sensors Not Detected
```bash
# Check I2C devices
sudo i2cdetect -y 1

# Check 1-Wire devices
ls /sys/bus/w1/devices/
```

### Service Won't Start
```bash
# Check logs
sudo journalctl -u edgepulse -n 50

# Validate configuration
python3 main.py --validate-config
```

### Permission Issues
```bash
# Add user to required groups
sudo usermod -a -G gpio,i2c $USER
sudo reboot
```

## 📝 Configuration Tips

### Adjust Thresholds
Edit `config.yaml` and modify the thresholds section:
```yaml
thresholds:
  heart_rate:
    min: 60
    max: 100
```

### Enable Email Alerts
1. Get Gmail app password (if using Gmail)
2. Edit `config.yaml`:
```yaml
alerts:
  email:
    enabled: true
    username: your-email@gmail.com
    password: your-app-password
    recipient: alert-recipient@gmail.com
```

### Enable SMS Alerts
1. Sign up for Twilio account
2. Get credentials
3. Edit `config.yaml`:
```yaml
alerts:
  sms:
    enabled: true
    account_sid: your-account-sid
    auth_token: your-auth-token
    from_number: +1234567890
    to_number: +0987654321
```

## 🆘 Getting Help

- Check the full README.md for detailed documentation
- Review logs in `logs/edgepulse.log`
- Test individual components with `python3 -m src.sensors --test`

## ⚠️ Safety Reminder

This is an educational project and NOT a certified medical device. 
Always consult healthcare professionals for medical decisions.

---

For more information, see README.md

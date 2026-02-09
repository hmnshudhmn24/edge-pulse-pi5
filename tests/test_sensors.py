"""
Unit Tests for EdgePulse-Pi5
"""

import pytest
import sys
from datetime import datetime
sys.path.insert(0, '..')

from src.sensors import SensorManager
from src.analyzer import VitalSignsAnalyzer
from src.alerts import AlertManager
from src.data_handler import DataHandler


class TestSensorManager:
    """Test sensor management"""
    
    def test_sensor_initialization(self):
        """Test sensor manager initialization"""
        config = {
            'max30102': {'red_led_current': 24, 'ir_led_current': 24},
            'ds18b20': {'calibration_offset': 0.0},
            'indicators': {}
        }
        
        manager = SensorManager(config)
        assert manager is not None
    
    def test_read_all(self):
        """Test reading all sensors"""
        config = {
            'max30102': {'red_led_current': 24, 'ir_led_current': 24},
            'ds18b20': {'calibration_offset': 0.0},
            'indicators': {}
        }
        
        manager = SensorManager(config)
        readings = manager.read_all()
        
        # Should return data (simulated if hardware not available)
        assert readings is not None
        assert 'heart_rate' in readings
        assert 'spo2' in readings
        assert 'temperature' in readings


class TestVitalSignsAnalyzer:
    """Test vital signs analysis"""
    
    def test_normal_readings(self):
        """Test that normal readings produce no alerts"""
        thresholds = {
            'heart_rate': {'min': 60, 'max': 100, 'critical_min': 40, 'critical_max': 150},
            'spo2': {'min': 95, 'critical_min': 90},
            'temperature': {'min': 36.1, 'max': 37.8, 'critical_min': 35.0, 'critical_max': 39.0}
        }
        
        analyzer = VitalSignsAnalyzer(thresholds)
        
        normal_readings = {
            'heart_rate': 75,
            'spo2': 98,
            'temperature': 36.8,
            'temperature_unit': 'C'
        }
        
        alerts = analyzer.analyze(normal_readings)
        assert len(alerts) == 0
    
    def test_abnormal_heart_rate(self):
        """Test that abnormal heart rate produces alerts"""
        thresholds = {
            'heart_rate': {'min': 60, 'max': 100, 'critical_min': 40, 'critical_max': 150},
            'spo2': {'min': 95, 'critical_min': 90},
            'temperature': {'min': 36.1, 'max': 37.8, 'critical_min': 35.0, 'critical_max': 39.0}
        }
        
        analyzer = VitalSignsAnalyzer(thresholds)
        
        abnormal_readings = {
            'heart_rate': 45,
            'spo2': 98,
            'temperature': 36.8,
            'temperature_unit': 'C'
        }
        
        alerts = analyzer.analyze(abnormal_readings)
        assert len(alerts) > 0
        assert alerts[0]['type'] == 'heart_rate'
    
    def test_critical_spo2(self):
        """Test that critical SpO2 produces critical alert"""
        thresholds = {
            'heart_rate': {'min': 60, 'max': 100, 'critical_min': 40, 'critical_max': 150},
            'spo2': {'min': 95, 'critical_min': 90},
            'temperature': {'min': 36.1, 'max': 37.8, 'critical_min': 35.0, 'critical_max': 39.0}
        }
        
        analyzer = VitalSignsAnalyzer(thresholds)
        
        critical_readings = {
            'heart_rate': 75,
            'spo2': 88,
            'temperature': 36.8,
            'temperature_unit': 'C'
        }
        
        alerts = analyzer.analyze(critical_readings)
        assert len(alerts) > 0
        assert any(alert['severity'] == 'critical' for alert in alerts)


class TestDataHandler:
    """Test data handling and storage"""
    
    def test_database_creation(self, tmp_path):
        """Test database creation"""
        db_path = tmp_path / "test.db"
        handler = DataHandler(str(db_path))
        
        assert db_path.exists()
        handler.close()
    
    def test_save_reading(self, tmp_path):
        """Test saving readings"""
        db_path = tmp_path / "test.db"
        handler = DataHandler(str(db_path))
        
        reading = {
            'heart_rate': 75,
            'spo2': 98,
            'temperature': 36.8,
            'temperature_unit': 'C'
        }
        
        result = handler.save_reading(reading)
        assert result is True
        
        # Verify data was saved
        readings = handler.get_readings(limit=1)
        assert len(readings) == 1
        assert readings[0]['heart_rate'] == 75
        
        handler.close()
    
    def test_save_alert(self, tmp_path):
        """Test saving alerts"""
        db_path = tmp_path / "test.db"
        handler = DataHandler(str(db_path))
        
        alert = {
            'type': 'heart_rate',
            'severity': 'warning',
            'message': 'Test alert',
            'value': 120,
            'threshold': 100,
            'timestamp': datetime.now()
        }
        
        result = handler.save_alert(alert)
        assert result is True
        
        # Verify alert was saved
        alerts = handler.get_alerts(limit=1)
        assert len(alerts) == 1
        assert alerts[0]['severity'] == 'warning'
        
        handler.close()


class TestAlertManager:
    """Test alert management"""
    
    def test_alert_initialization(self):
        """Test alert manager initialization"""
        config = {
            'email': {'enabled': False},
            'sms': {'enabled': False},
            'local': {'buzzer_enabled': False, 'led_enabled': False}
        }
        
        manager = AlertManager(config)
        assert manager is not None
    
    def test_alert_history(self):
        """Test alert history tracking"""
        config = {
            'email': {'enabled': False},
            'sms': {'enabled': False},
            'local': {'buzzer_enabled': False, 'led_enabled': False}
        }
        
        manager = AlertManager(config)
        
        alert = {
            'type': 'heart_rate',
            'severity': 'warning',
            'message': 'Test alert',
            'timestamp': datetime.now()
        }
        
        manager.send_alert(alert)
        
        history = manager.get_alert_history()
        assert len(history) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

"""
Vital Signs Analyzer Module
Detects abnormal patterns and generates alerts
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


class VitalSignsAnalyzer:
    """Analyzes vital signs and detects abnormalities"""
    
    def __init__(self, thresholds: Dict):
        """
        Initialize analyzer with threshold configuration
        
        Args:
            thresholds: Dictionary containing threshold values for each vital sign
        """
        self.thresholds = thresholds
        
        # Historical data for trend analysis
        self.heart_rate_history = deque(maxlen=60)  # Last 60 readings
        self.spo2_history = deque(maxlen=60)
        self.temp_history = deque(maxlen=60)
        
        # Alert cooldown to prevent spam
        self.last_alert_time = {}
        self.alert_cooldown = 300  # 5 minutes
        
        logger.info("Vital signs analyzer initialized")
    
    def analyze(self, readings: Dict) -> List[Dict]:
        """
        Analyze readings and detect abnormalities
        
        Args:
            readings: Dictionary containing vital sign values
            
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        try:
            # Update history
            if 'heart_rate' in readings:
                self.heart_rate_history.append(readings['heart_rate'])
            if 'spo2' in readings:
                self.spo2_history.append(readings['spo2'])
            if 'temperature' in readings:
                self.temp_history.append(readings['temperature'])
            
            # Analyze each vital sign
            alerts.extend(self._analyze_heart_rate(readings))
            alerts.extend(self._analyze_spo2(readings))
            alerts.extend(self._analyze_temperature(readings))
            alerts.extend(self._analyze_trends())
            
            # Filter alerts by cooldown
            alerts = self._apply_cooldown(alerts)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error analyzing readings: {e}")
            return []
    
    def _analyze_heart_rate(self, readings: Dict) -> List[Dict]:
        """Analyze heart rate for abnormalities"""
        alerts = []
        
        if 'heart_rate' not in readings:
            return alerts
        
        hr = readings['heart_rate']
        thresholds = self.thresholds.get('heart_rate', {})
        
        # Critical bradycardia
        if hr < thresholds.get('critical_min', 40):
            alerts.append({
                'type': 'heart_rate',
                'severity': 'critical',
                'message': f'Critical bradycardia detected: {hr} bpm (extremely low heart rate)',
                'value': hr,
                'threshold': thresholds.get('critical_min'),
                'timestamp': datetime.now()
            })
        
        # Critical tachycardia
        elif hr > thresholds.get('critical_max', 150):
            alerts.append({
                'type': 'heart_rate',
                'severity': 'critical',
                'message': f'Critical tachycardia detected: {hr} bpm (extremely high heart rate)',
                'value': hr,
                'threshold': thresholds.get('critical_max'),
                'timestamp': datetime.now()
            })
        
        # Warning bradycardia
        elif hr < thresholds.get('min', 60):
            alerts.append({
                'type': 'heart_rate',
                'severity': 'warning',
                'message': f'Bradycardia detected: {hr} bpm (low heart rate)',
                'value': hr,
                'threshold': thresholds.get('min'),
                'timestamp': datetime.now()
            })
        
        # Warning tachycardia
        elif hr > thresholds.get('max', 100):
            alerts.append({
                'type': 'heart_rate',
                'severity': 'warning',
                'message': f'Tachycardia detected: {hr} bpm (high heart rate)',
                'value': hr,
                'threshold': thresholds.get('max'),
                'timestamp': datetime.now()
            })
        
        return alerts
    
    def _analyze_spo2(self, readings: Dict) -> List[Dict]:
        """Analyze blood oxygen saturation for abnormalities"""
        alerts = []
        
        if 'spo2' not in readings:
            return alerts
        
        spo2 = readings['spo2']
        thresholds = self.thresholds.get('spo2', {})
        
        # Critical hypoxemia
        if spo2 < thresholds.get('critical_min', 90):
            alerts.append({
                'type': 'spo2',
                'severity': 'critical',
                'message': f'Critical hypoxemia detected: {spo2}% (dangerously low blood oxygen)',
                'value': spo2,
                'threshold': thresholds.get('critical_min'),
                'timestamp': datetime.now()
            })
        
        # Warning hypoxemia
        elif spo2 < thresholds.get('min', 95):
            alerts.append({
                'type': 'spo2',
                'severity': 'warning',
                'message': f'Low blood oxygen detected: {spo2}%',
                'value': spo2,
                'threshold': thresholds.get('min'),
                'timestamp': datetime.now()
            })
        
        return alerts
    
    def _analyze_temperature(self, readings: Dict) -> List[Dict]:
        """Analyze body temperature for abnormalities"""
        alerts = []
        
        if 'temperature' not in readings:
            return alerts
        
        temp = readings['temperature']
        unit = readings.get('temperature_unit', 'C')
        thresholds = self.thresholds.get('temperature', {})
        
        # Convert to Celsius if needed
        if unit == 'F':
            temp = (temp - 32) * 5/9
        
        # Critical hypothermia
        if temp < thresholds.get('critical_min', 35.0):
            alerts.append({
                'type': 'temperature',
                'severity': 'critical',
                'message': f'Critical hypothermia detected: {temp:.1f}°C (dangerously low temperature)',
                'value': temp,
                'threshold': thresholds.get('critical_min'),
                'timestamp': datetime.now()
            })
        
        # Critical hyperthermia
        elif temp > thresholds.get('critical_max', 39.0):
            alerts.append({
                'type': 'temperature',
                'severity': 'critical',
                'message': f'Critical hyperthermia detected: {temp:.1f}°C (dangerously high temperature)',
                'value': temp,
                'threshold': thresholds.get('critical_max'),
                'timestamp': datetime.now()
            })
        
        # Warning hypothermia
        elif temp < thresholds.get('min', 36.1):
            alerts.append({
                'type': 'temperature',
                'severity': 'warning',
                'message': f'Low body temperature detected: {temp:.1f}°C',
                'value': temp,
                'threshold': thresholds.get('min'),
                'timestamp': datetime.now()
            })
        
        # Warning fever
        elif temp > thresholds.get('max', 37.8):
            severity = 'warning' if temp < 38.5 else 'critical'
            alerts.append({
                'type': 'temperature',
                'severity': severity,
                'message': f'Fever detected: {temp:.1f}°C',
                'value': temp,
                'threshold': thresholds.get('max'),
                'timestamp': datetime.now()
            })
        
        return alerts
    
    def _analyze_trends(self) -> List[Dict]:
        """Analyze trends in vital signs over time"""
        alerts = []
        
        # Rapid heart rate increase
        if len(self.heart_rate_history) >= 10:
            recent_avg = sum(list(self.heart_rate_history)[-5:]) / 5
            older_avg = sum(list(self.heart_rate_history)[-10:-5]) / 5
            
            if recent_avg > older_avg + 20:  # Increase of >20 bpm in short time
                alerts.append({
                    'type': 'heart_rate_trend',
                    'severity': 'warning',
                    'message': f'Rapid heart rate increase detected: {older_avg:.0f} → {recent_avg:.0f} bpm',
                    'value': recent_avg - older_avg,
                    'timestamp': datetime.now()
                })
        
        # Declining SpO2 trend
        if len(self.spo2_history) >= 10:
            recent_avg = sum(list(self.spo2_history)[-5:]) / 5
            older_avg = sum(list(self.spo2_history)[-10:-5]) / 5
            
            if recent_avg < older_avg - 3:  # Decrease of >3% in short time
                alerts.append({
                    'type': 'spo2_trend',
                    'severity': 'warning',
                    'message': f'Declining blood oxygen trend detected: {older_avg:.0f}% → {recent_avg:.0f}%',
                    'value': recent_avg - older_avg,
                    'timestamp': datetime.now()
                })
        
        # Rising temperature trend
        if len(self.temp_history) >= 10:
            recent_avg = sum(list(self.temp_history)[-5:]) / 5
            older_avg = sum(list(self.temp_history)[-10:-5]) / 5
            
            if recent_avg > older_avg + 0.5:  # Increase of >0.5°C in short time
                alerts.append({
                    'type': 'temperature_trend',
                    'severity': 'info',
                    'message': f'Rising temperature trend detected: {older_avg:.1f}°C → {recent_avg:.1f}°C',
                    'value': recent_avg - older_avg,
                    'timestamp': datetime.now()
                })
        
        return alerts
    
    def _apply_cooldown(self, alerts: List[Dict]) -> List[Dict]:
        """Filter alerts based on cooldown period to prevent spam"""
        filtered_alerts = []
        current_time = datetime.now()
        
        for alert in alerts:
            alert_key = f"{alert['type']}_{alert['severity']}"
            
            # Check if enough time has passed since last alert of this type
            if alert_key in self.last_alert_time:
                time_since_last = (current_time - self.last_alert_time[alert_key]).total_seconds()
                
                if time_since_last < self.alert_cooldown:
                    # Skip this alert (cooldown period not elapsed)
                    logger.debug(f"Alert cooldown active for {alert_key}")
                    continue
            
            # Update last alert time and include alert
            self.last_alert_time[alert_key] = current_time
            filtered_alerts.append(alert)
        
        return filtered_alerts
    
    def get_statistics(self) -> Dict:
        """Get statistics from historical data"""
        stats = {}
        
        if self.heart_rate_history:
            hr_list = list(self.heart_rate_history)
            stats['heart_rate'] = {
                'current': hr_list[-1],
                'average': sum(hr_list) / len(hr_list),
                'min': min(hr_list),
                'max': max(hr_list),
                'count': len(hr_list)
            }
        
        if self.spo2_history:
            spo2_list = list(self.spo2_history)
            stats['spo2'] = {
                'current': spo2_list[-1],
                'average': sum(spo2_list) / len(spo2_list),
                'min': min(spo2_list),
                'max': max(spo2_list),
                'count': len(spo2_list)
            }
        
        if self.temp_history:
            temp_list = list(self.temp_history)
            stats['temperature'] = {
                'current': temp_list[-1],
                'average': sum(temp_list) / len(temp_list),
                'min': min(temp_list),
                'max': max(temp_list),
                'count': len(temp_list)
            }
        
        return stats
    
    def reset_history(self):
        """Clear historical data"""
        self.heart_rate_history.clear()
        self.spo2_history.clear()
        self.temp_history.clear()
        self.last_alert_time.clear()
        logger.info("Analyzer history reset")


if __name__ == '__main__':
    # Test the analyzer
    thresholds = {
        'heart_rate': {
            'min': 60,
            'max': 100,
            'critical_min': 40,
            'critical_max': 150
        },
        'spo2': {
            'min': 95,
            'critical_min': 90
        },
        'temperature': {
            'min': 36.1,
            'max': 37.8,
            'critical_min': 35.0,
            'critical_max': 39.0
        }
    }
    
    analyzer = VitalSignsAnalyzer(thresholds)
    
    # Test normal readings
    print("Testing normal readings:")
    normal_readings = {
        'heart_rate': 75,
        'spo2': 98,
        'temperature': 36.8,
        'temperature_unit': 'C'
    }
    alerts = analyzer.analyze(normal_readings)
    print(f"Alerts: {len(alerts)}")
    
    # Test abnormal readings
    print("\nTesting abnormal readings:")
    abnormal_readings = {
        'heart_rate': 45,
        'spo2': 92,
        'temperature': 38.5,
        'temperature_unit': 'C'
    }
    alerts = analyzer.analyze(abnormal_readings)
    for alert in alerts:
        print(f"  {alert['severity'].upper()}: {alert['message']}")
    
    # Get statistics
    print("\nStatistics:")
    stats = analyzer.get_statistics()
    for vital, data in stats.items():
        print(f"  {vital}: avg={data['average']:.1f}, min={data['min']}, max={data['max']}")

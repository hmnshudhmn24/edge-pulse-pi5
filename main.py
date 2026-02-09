#!/usr/bin/env python3
"""
EdgePulse-Pi5 - Real-time Health Monitoring System
Main Application Entry Point
"""

import argparse
import sys
import signal
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
import yaml

from src.sensors import SensorManager
from src.analyzer import VitalSignsAnalyzer
from src.alerts import AlertManager
from src.data_handler import DataHandler
from src.web_dashboard import create_app

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/edgepulse.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class EdgePulseMonitor:
    """Main monitoring system controller"""
    
    def __init__(self, config_path='config.yaml'):
        """Initialize the monitoring system"""
        self.running = False
        self.config = self.load_config(config_path)
        
        # Initialize components
        logger.info("Initializing EdgePulse-Pi5 monitoring system...")
        
        try:
            self.data_handler = DataHandler(self.config['database']['path'])
            self.sensor_manager = SensorManager(self.config['sensors'])
            self.analyzer = VitalSignsAnalyzer(self.config['thresholds'])
            self.alert_manager = AlertManager(self.config['alerts'])
            
            logger.info("System initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize system: {e}")
            raise
    
    def load_config(self, config_path):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML configuration: {e}")
            sys.exit(1)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Shutdown signal received")
        self.stop()
    
    def start(self):
        """Start the monitoring system"""
        self.running = True
        logger.info("Starting vital signs monitoring...")
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        measurement_interval = self.config['system']['measurement_interval']
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        try:
            while self.running:
                try:
                    # Read sensor data
                    readings = self.sensor_manager.read_all()
                    
                    if readings:
                        # Log readings
                        logger.debug(f"Readings: HR={readings.get('heart_rate')}bpm, "
                                   f"SpO2={readings.get('spo2')}%, "
                                   f"Temp={readings.get('temperature')}°C")
                        
                        # Store in database
                        self.data_handler.save_reading(readings)
                        
                        # Analyze for abnormalities
                        alerts = self.analyzer.analyze(readings)
                        
                        # Handle any alerts
                        if alerts:
                            for alert in alerts:
                                logger.warning(f"Alert: {alert['message']}")
                                self.alert_manager.send_alert(alert)
                                self.data_handler.save_alert(alert)
                        
                        # Reset error counter on successful reading
                        consecutive_errors = 0
                    
                    else:
                        consecutive_errors += 1
                        logger.warning(f"Failed to read sensors ({consecutive_errors}/{max_consecutive_errors})")
                        
                        if consecutive_errors >= max_consecutive_errors:
                            error_alert = {
                                'type': 'system_error',
                                'severity': 'critical',
                                'message': 'Sensor communication failure - multiple consecutive errors',
                                'timestamp': datetime.now()
                            }
                            self.alert_manager.send_alert(error_alert)
                            consecutive_errors = 0  # Reset to avoid spam
                    
                    # Wait for next measurement
                    time.sleep(measurement_interval)
                
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                    consecutive_errors += 1
                    time.sleep(measurement_interval)
        
        finally:
            self.cleanup()
    
    def stop(self):
        """Stop the monitoring system"""
        logger.info("Stopping monitoring system...")
        self.running = False
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up resources...")
        try:
            self.sensor_manager.cleanup()
            self.data_handler.close()
            logger.info("Cleanup complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def get_status(self):
        """Get current system status"""
        try:
            readings = self.sensor_manager.read_all()
            if readings:
                return {
                    'status': 'operational',
                    'current_readings': readings,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'sensor_error',
                    'message': 'Unable to read sensors',
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def export_data(self, start_date=None, end_date=None, output_file=None):
        """Export data to CSV"""
        try:
            if not output_file:
                output_file = f"data/export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            self.data_handler.export_to_csv(
                output_file,
                start_date=start_date,
                end_date=end_date
            )
            logger.info(f"Data exported to {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            return None
    
    def test_alerts(self):
        """Test alert system"""
        logger.info("Testing alert system...")
        
        test_alert = {
            'type': 'test',
            'severity': 'info',
            'message': 'This is a test alert from EdgePulse-Pi5',
            'timestamp': datetime.now()
        }
        
        try:
            self.alert_manager.send_alert(test_alert)
            logger.info("Test alert sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send test alert: {e}")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='EdgePulse-Pi5 - Real-time Health Monitoring System'
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Display current system status and exit'
    )
    
    parser.add_argument(
        '--export',
        action='store_true',
        help='Export data to CSV'
    )
    
    parser.add_argument(
        '--start-date',
        help='Start date for export (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--end-date',
        help='End date for export (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--output',
        help='Output file for export'
    )
    
    parser.add_argument(
        '--test-alerts',
        action='store_true',
        help='Test alert system and exit'
    )
    
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Clean up old data'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Days of data to keep (default: 30)'
    )
    
    parser.add_argument(
        '--web',
        action='store_true',
        help='Start web dashboard only'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Web dashboard port (default: 5000)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--validate-config',
        action='store_true',
        help='Validate configuration and exit'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize monitor
    try:
        monitor = EdgePulseMonitor(args.config)
    except Exception as e:
        logger.error(f"Failed to initialize monitor: {e}")
        sys.exit(1)
    
    # Handle commands
    if args.validate_config:
        logger.info("Configuration is valid")
        sys.exit(0)
    
    elif args.status:
        status = monitor.get_status()
        print("\n=== EdgePulse-Pi5 Status ===")
        print(f"Status: {status['status']}")
        if 'current_readings' in status:
            readings = status['current_readings']
            print(f"Heart Rate: {readings.get('heart_rate', 'N/A')} bpm")
            print(f"SpO2: {readings.get('spo2', 'N/A')}%")
            print(f"Temperature: {readings.get('temperature', 'N/A')}°C")
        print(f"Timestamp: {status['timestamp']}")
        print("===========================\n")
        sys.exit(0)
    
    elif args.export:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d') if args.start_date else None
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d') if args.end_date else None
        
        output_file = monitor.export_data(start_date, end_date, args.output)
        if output_file:
            print(f"Data exported to: {output_file}")
            sys.exit(0)
        else:
            sys.exit(1)
    
    elif args.test_alerts:
        success = monitor.test_alerts()
        sys.exit(0 if success else 1)
    
    elif args.cleanup:
        cutoff_date = datetime.now() - timedelta(days=args.days)
        monitor.data_handler.cleanup_old_data(cutoff_date)
        logger.info(f"Cleaned up data older than {args.days} days")
        sys.exit(0)
    
    elif args.web:
        # Start web dashboard only
        app = create_app(monitor)
        logger.info(f"Starting web dashboard on port {args.port}")
        app.run(host='0.0.0.0', port=args.port, debug=args.verbose)
    
    else:
        # Start normal monitoring
        logger.info("=" * 50)
        logger.info("EdgePulse-Pi5 - Real-time Health Monitoring System")
        logger.info("=" * 50)
        monitor.start()


if __name__ == '__main__':
    main()

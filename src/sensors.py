"""
Sensor Interface Module
Handles communication with MAX30102, DS18B20, and other sensors
"""

import time
import logging
from typing import Dict, Optional
import random

logger = logging.getLogger(__name__)

try:
    import board
    import busio
    import adafruit_max30105
    from adafruit_max30105 import MAX30105
    HAS_MAX30102 = True
except ImportError:
    logger.warning("MAX30102 library not available, using simulation mode")
    HAS_MAX30102 = False

try:
    from w1thermsensor import W1ThermSensor, Sensor
    HAS_DS18B20 = True
except ImportError:
    logger.warning("DS18B20 library not available, using simulation mode")
    HAS_DS18B20 = False

try:
    import RPi.GPIO as GPIO
    HAS_GPIO = True
except ImportError:
    logger.warning("GPIO library not available, using simulation mode")
    HAS_GPIO = False


class MAX30102Sensor:
    """MAX30102 Pulse Oximeter and Heart Rate Sensor"""
    
    def __init__(self, config: Dict):
        """Initialize MAX30102 sensor"""
        self.config = config
        self.sensor = None
        self.simulation_mode = not HAS_MAX30102
        
        if not self.simulation_mode:
            try:
                # Initialize I2C
                i2c = busio.I2C(board.SCL, board.SDA)
                
                # Initialize sensor
                self.sensor = MAX30105(i2c)
                
                # Configure sensor
                self.sensor.setup()
                self.sensor.set_mode(0x03)  # SpO2 mode
                self.sensor.set_led_current(
                    red_current=config.get('red_led_current', 24),
                    ir_current=config.get('ir_led_current', 24)
                )
                
                logger.info("MAX30102 sensor initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize MAX30102: {e}")
                logger.warning("Falling back to simulation mode")
                self.simulation_mode = True
        
        if self.simulation_mode:
            logger.info("MAX30102 running in simulation mode")
    
    def read(self) -> Optional[Dict[str, float]]:
        """
        Read heart rate and SpO2 values
        
        Returns:
            Dict with 'heart_rate' and 'spo2' keys, or None if read fails
        """
        if self.simulation_mode:
            return self._simulate_reading()
        
        try:
            # Read samples
            samples = []
            for _ in range(100):  # Collect 100 samples
                if self.sensor.available():
                    red_reading = self.sensor.pop_red_from_storage()
                    ir_reading = self.sensor.pop_ir_from_storage()
                    samples.append((red_reading, ir_reading))
                time.sleep(0.01)
            
            if not samples:
                logger.warning("No samples collected from MAX30102")
                return None
            
            # Calculate heart rate and SpO2
            heart_rate = self._calculate_heart_rate(samples)
            spo2 = self._calculate_spo2(samples)
            
            # Validate readings
            if heart_rate and 30 <= heart_rate <= 250:
                if spo2 and 70 <= spo2 <= 100:
                    return {
                        'heart_rate': int(heart_rate),
                        'spo2': int(spo2)
                    }
            
            logger.debug("Invalid MAX30102 readings detected")
            return None
            
        except Exception as e:
            logger.error(f"Error reading MAX30102: {e}")
            return None
    
    def _calculate_heart_rate(self, samples) -> Optional[float]:
        """Calculate heart rate from IR samples using peak detection"""
        if not samples:
            return None
        
        # Extract IR values
        ir_values = [ir for _, ir in samples]
        
        # Simple peak detection
        threshold = sum(ir_values) / len(ir_values)
        peaks = []
        
        for i in range(1, len(ir_values) - 1):
            if ir_values[i] > threshold:
                if ir_values[i] > ir_values[i-1] and ir_values[i] > ir_values[i+1]:
                    peaks.append(i)
        
        if len(peaks) < 2:
            return None
        
        # Calculate average time between peaks
        peak_intervals = [peaks[i+1] - peaks[i] for i in range(len(peaks)-1)]
        avg_interval = sum(peak_intervals) / len(peak_intervals)
        
        # Convert to BPM (100 samples = ~1 second)
        heart_rate = 60 / (avg_interval * 0.01)
        
        return heart_rate if 30 <= heart_rate <= 250 else None
    
    def _calculate_spo2(self, samples) -> Optional[float]:
        """Calculate SpO2 from red and IR samples"""
        if not samples:
            return None
        
        # Extract values
        red_values = [red for red, _ in samples]
        ir_values = [ir for _, ir in samples]
        
        # Calculate AC and DC components
        red_ac = max(red_values) - min(red_values)
        red_dc = sum(red_values) / len(red_values)
        ir_ac = max(ir_values) - min(ir_values)
        ir_dc = sum(ir_values) / len(ir_values)
        
        # Avoid division by zero
        if red_dc == 0 or ir_dc == 0 or ir_ac == 0:
            return None
        
        # Calculate R value
        r = (red_ac / red_dc) / (ir_ac / ir_dc)
        
        # Empirical formula for SpO2
        spo2 = 110 - 25 * r
        
        return spo2 if 70 <= spo2 <= 100 else None
    
    def _simulate_reading(self) -> Dict[str, float]:
        """Simulate sensor readings for testing"""
        # Generate realistic simulated values with some variation
        base_hr = 75
        base_spo2 = 97
        
        heart_rate = base_hr + random.randint(-5, 5)
        spo2 = base_spo2 + random.randint(-2, 2)
        
        return {
            'heart_rate': heart_rate,
            'spo2': spo2
        }


class DS18B20Sensor:
    """DS18B20 Digital Temperature Sensor"""
    
    def __init__(self, config: Dict):
        """Initialize DS18B20 sensor"""
        self.config = config
        self.sensor = None
        self.simulation_mode = not HAS_DS18B20
        
        if not self.simulation_mode:
            try:
                # Initialize 1-Wire sensor
                self.sensor = W1ThermSensor()
                logger.info(f"DS18B20 sensor initialized: {self.sensor.id}")
                
            except Exception as e:
                logger.error(f"Failed to initialize DS18B20: {e}")
                logger.warning("Falling back to simulation mode")
                self.simulation_mode = True
        
        if self.simulation_mode:
            logger.info("DS18B20 running in simulation mode")
    
    def read(self) -> Optional[Dict[str, float]]:
        """
        Read temperature value
        
        Returns:
            Dict with 'temperature' and 'temperature_unit' keys
        """
        if self.simulation_mode:
            return self._simulate_reading()
        
        try:
            # Read temperature in Celsius
            temp_celsius = self.sensor.get_temperature()
            
            # Apply calibration offset if configured
            offset = self.config.get('calibration_offset', 0.0)
            temp_celsius += offset
            
            # Validate reading
            if 30.0 <= temp_celsius <= 42.0:  # Valid body temperature range
                return {
                    'temperature': round(temp_celsius, 1),
                    'temperature_unit': 'C'
                }
            else:
                logger.warning(f"Invalid temperature reading: {temp_celsius}°C")
                return None
                
        except Exception as e:
            logger.error(f"Error reading DS18B20: {e}")
            return None
    
    def _simulate_reading(self) -> Dict[str, float]:
        """Simulate temperature reading for testing"""
        base_temp = 36.8
        temperature = base_temp + random.uniform(-0.3, 0.3)
        
        return {
            'temperature': round(temperature, 1),
            'temperature_unit': 'C'
        }


class StatusIndicators:
    """LED and Buzzer status indicators"""
    
    def __init__(self, config: Dict):
        """Initialize GPIO pins for indicators"""
        self.config = config
        self.simulation_mode = not HAS_GPIO
        
        if not self.simulation_mode:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
                
                # Setup LED pins
                self.led_red = config.get('led_red_pin', 22)
                self.led_green = config.get('led_green_pin', 27)
                self.led_blue = config.get('led_blue_pin', 23)
                
                GPIO.setup(self.led_red, GPIO.OUT)
                GPIO.setup(self.led_green, GPIO.OUT)
                GPIO.setup(self.led_blue, GPIO.OUT)
                
                # Setup buzzer pin
                self.buzzer = config.get('buzzer_pin', 17)
                GPIO.setup(self.buzzer, GPIO.OUT)
                
                # Initialize all off
                self.set_led('off')
                GPIO.output(self.buzzer, GPIO.LOW)
                
                logger.info("Status indicators initialized")
                
            except Exception as e:
                logger.error(f"Failed to initialize GPIO: {e}")
                logger.warning("Falling back to simulation mode")
                self.simulation_mode = True
        
        if self.simulation_mode:
            logger.info("Status indicators running in simulation mode")
    
    def set_led(self, color: str):
        """Set LED color (red, green, blue, yellow, cyan, magenta, white, off)"""
        if self.simulation_mode:
            logger.debug(f"[SIM] LED color: {color}")
            return
        
        colors = {
            'off': (0, 0, 0),
            'red': (1, 0, 0),
            'green': (0, 1, 0),
            'blue': (0, 0, 1),
            'yellow': (1, 1, 0),
            'cyan': (0, 1, 1),
            'magenta': (1, 0, 1),
            'white': (1, 1, 1)
        }
        
        if color in colors:
            r, g, b = colors[color]
            GPIO.output(self.led_red, r)
            GPIO.output(self.led_green, g)
            GPIO.output(self.led_blue, b)
    
    def beep(self, duration: float = 0.2, count: int = 1):
        """Sound buzzer"""
        if self.simulation_mode:
            logger.debug(f"[SIM] Buzzer: {count} beep(s)")
            return
        
        for _ in range(count):
            GPIO.output(self.buzzer, GPIO.HIGH)
            time.sleep(duration)
            GPIO.output(self.buzzer, GPIO.LOW)
            time.sleep(duration)
    
    def cleanup(self):
        """Cleanup GPIO"""
        if not self.simulation_mode:
            GPIO.cleanup()


class SensorManager:
    """Manages all sensors and indicators"""
    
    def __init__(self, config: Dict):
        """Initialize all sensors"""
        self.config = config
        
        # Initialize sensors
        self.max30102 = MAX30102Sensor(config.get('max30102', {}))
        self.ds18b20 = DS18B20Sensor(config.get('ds18b20', {}))
        self.indicators = StatusIndicators(config.get('indicators', {}))
        
        logger.info("Sensor manager initialized")
    
    def read_all(self) -> Optional[Dict]:
        """Read all sensors and return combined data"""
        try:
            # Read heart rate and SpO2
            pulse_ox_data = self.max30102.read()
            
            # Read temperature
            temp_data = self.ds18b20.read()
            
            # Combine data
            if pulse_ox_data and temp_data:
                readings = {**pulse_ox_data, **temp_data}
                readings['timestamp'] = time.time()
                
                # Update status LED (green = normal)
                self.indicators.set_led('green')
                
                return readings
            else:
                logger.warning("Failed to read one or more sensors")
                self.indicators.set_led('red')
                return None
                
        except Exception as e:
            logger.error(f"Error reading sensors: {e}")
            self.indicators.set_led('red')
            return None
    
    def cleanup(self):
        """Cleanup all sensors"""
        logger.info("Cleaning up sensors")
        self.indicators.cleanup()


def test_sensors():
    """Test sensor functionality"""
    print("Testing EdgePulse-Pi5 Sensors\n")
    
    config = {
        'max30102': {'red_led_current': 24, 'ir_led_current': 24},
        'ds18b20': {'calibration_offset': 0.0},
        'indicators': {
            'led_red_pin': 22,
            'led_green_pin': 27,
            'led_blue_pin': 23,
            'buzzer_pin': 17
        }
    }
    
    manager = SensorManager(config)
    
    print("Reading sensors for 10 seconds...\n")
    
    for i in range(10):
        readings = manager.read_all()
        if readings:
            print(f"Reading {i+1}:")
            print(f"  Heart Rate: {readings.get('heart_rate')} bpm")
            print(f"  SpO2: {readings.get('spo2')}%")
            print(f"  Temperature: {readings.get('temperature')}°C")
            print()
        else:
            print(f"Reading {i+1}: Failed\n")
        
        time.sleep(1)
    
    print("Testing status indicators...")
    manager.indicators.set_led('red')
    time.sleep(1)
    manager.indicators.set_led('green')
    time.sleep(1)
    manager.indicators.set_led('blue')
    time.sleep(1)
    manager.indicators.beep(count=3)
    
    manager.cleanup()
    print("\nSensor test complete")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Sensor module testing')
    parser.add_argument('--test', action='store_true', help='Run sensor tests')
    args = parser.parse_args()
    
    if args.test:
        test_sensors()

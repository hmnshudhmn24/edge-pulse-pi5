"""
Alert Management Module
Handles multi-channel notifications (Email, SMS, Local alerts)
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from twilio.rest import Client as TwilioClient
    HAS_TWILIO = True
except ImportError:
    logger.warning("Twilio library not available, SMS alerts disabled")
    HAS_TWILIO = False


class EmailAlert:
    """Email notification handler"""
    
    def __init__(self, config: Dict):
        """Initialize email alert system"""
        self.config = config
        self.enabled = config.get('enabled', False)
        
        if self.enabled:
            self.smtp_server = config.get('smtp_server')
            self.smtp_port = config.get('smtp_port', 587)
            self.username = config.get('username')
            self.password = config.get('password')
            self.recipient = config.get('recipient')
            self.from_addr = config.get('from_address', self.username)
            
            logger.info("Email alerts enabled")
        else:
            logger.info("Email alerts disabled")
    
    def send(self, alert: Dict) -> bool:
        """Send email alert"""
        if not self.enabled:
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"EdgePulse Alert: {alert['severity'].upper()} - {alert['type']}"
            msg['From'] = self.from_addr
            msg['To'] = self.recipient
            
            # Create email body
            text_body = self._create_text_body(alert)
            html_body = self._create_html_body(alert)
            
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email alert sent to {self.recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
    
    def _create_text_body(self, alert: Dict) -> str:
        """Create plain text email body"""
        timestamp = alert.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
        
        body = f"""
EdgePulse-Pi5 Health Monitoring Alert

SEVERITY: {alert['severity'].upper()}
TYPE: {alert['type']}
TIME: {timestamp}

MESSAGE:
{alert['message']}
"""
        
        if 'value' in alert:
            body += f"\nCurrent Value: {alert['value']}"
        
        if 'threshold' in alert:
            body += f"\nThreshold: {alert['threshold']}"
        
        body += "\n\n---\nThis is an automated message from EdgePulse-Pi5 monitoring system."
        
        return body
    
    def _create_html_body(self, alert: Dict) -> str:
        """Create HTML email body"""
        timestamp = alert.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
        
        # Color based on severity
        severity_colors = {
            'critical': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8'
        }
        color = severity_colors.get(alert['severity'], '#6c757d')
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .alert-box {{
                    border-left: 5px solid {color};
                    padding: 15px;
                    background-color: #f8f9fa;
                    margin: 20px 0;
                }}
                .severity {{ 
                    color: {color};
                    font-weight: bold;
                    font-size: 18px;
                }}
                .message {{
                    font-size: 16px;
                    margin: 10px 0;
                }}
                .details {{
                    color: #6c757d;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <h2>🏥 EdgePulse-Pi5 Health Monitoring Alert</h2>
            <div class="alert-box">
                <div class="severity">{alert['severity'].upper()} ALERT</div>
                <div class="details">Type: {alert['type']} | Time: {timestamp}</div>
                <div class="message">{alert['message']}</div>
        """
        
        if 'value' in alert:
            html += f"<div class='details'>Current Value: <strong>{alert['value']}</strong></div>"
        
        if 'threshold' in alert:
            html += f"<div class='details'>Threshold: {alert['threshold']}</div>"
        
        html += """
            </div>
            <p style="color: #6c757d; font-size: 12px;">
                This is an automated message from EdgePulse-Pi5 monitoring system.
            </p>
        </body>
        </html>
        """
        
        return html


class SMSAlert:
    """SMS notification handler using Twilio"""
    
    def __init__(self, config: Dict):
        """Initialize SMS alert system"""
        self.config = config
        self.enabled = config.get('enabled', False) and HAS_TWILIO
        
        if self.enabled:
            provider = config.get('provider', 'twilio')
            
            if provider == 'twilio':
                self.account_sid = config.get('account_sid')
                self.auth_token = config.get('auth_token')
                self.from_number = config.get('from_number')
                self.to_number = config.get('to_number')
                
                try:
                    self.client = TwilioClient(self.account_sid, self.auth_token)
                    logger.info("SMS alerts enabled (Twilio)")
                except Exception as e:
                    logger.error(f"Failed to initialize Twilio: {e}")
                    self.enabled = False
            else:
                logger.warning(f"Unknown SMS provider: {provider}")
                self.enabled = False
        else:
            logger.info("SMS alerts disabled")
    
    def send(self, alert: Dict) -> bool:
        """Send SMS alert"""
        if not self.enabled:
            return False
        
        try:
            # Create SMS message
            message = self._create_sms_message(alert)
            
            # Send via Twilio
            self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=self.to_number
            )
            
            logger.info(f"SMS alert sent to {self.to_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS alert: {e}")
            return False
    
    def _create_sms_message(self, alert: Dict) -> str:
        """Create SMS message text"""
        severity_emoji = {
            'critical': '🚨',
            'warning': '⚠️',
            'info': 'ℹ️'
        }
        emoji = severity_emoji.get(alert['severity'], '📢')
        
        message = f"{emoji} EdgePulse Alert\n"
        message += f"{alert['severity'].upper()}: {alert['message']}"
        
        if 'value' in alert:
            message += f"\nValue: {alert['value']}"
        
        return message[:160]  # SMS length limit


class LocalAlert:
    """Local buzzer and LED alert handler"""
    
    def __init__(self, config: Dict, indicators=None):
        """Initialize local alert system"""
        self.config = config
        self.buzzer_enabled = config.get('buzzer_enabled', True)
        self.led_enabled = config.get('led_enabled', True)
        self.indicators = indicators
        
        logger.info(f"Local alerts - Buzzer: {self.buzzer_enabled}, LED: {self.led_enabled}")
    
    def send(self, alert: Dict) -> bool:
        """Trigger local alert"""
        if not self.indicators:
            logger.debug("No indicators available for local alert")
            return False
        
        try:
            severity = alert['severity']
            
            # Set LED color based on severity
            if self.led_enabled:
                led_colors = {
                    'critical': 'red',
                    'warning': 'yellow',
                    'info': 'blue'
                }
                color = led_colors.get(severity, 'white')
                self.indicators.set_led(color)
            
            # Sound buzzer based on severity
            if self.buzzer_enabled:
                beep_patterns = {
                    'critical': (0.5, 3),  # Long beeps, 3 times
                    'warning': (0.2, 2),   # Short beeps, 2 times
                    'info': (0.1, 1)       # Single short beep
                }
                duration, count = beep_patterns.get(severity, (0.1, 1))
                self.indicators.beep(duration=duration, count=count)
            
            logger.info(f"Local alert triggered: {severity}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to trigger local alert: {e}")
            return False


class AlertManager:
    """Manages all alert channels"""
    
    def __init__(self, config: Dict, indicators=None):
        """Initialize alert manager"""
        self.config = config
        
        # Initialize alert handlers
        self.email_alert = EmailAlert(config.get('email', {}))
        self.sms_alert = SMSAlert(config.get('sms', {}))
        self.local_alert = LocalAlert(config.get('local', {}), indicators)
        
        # Alert history
        self.alert_history = []
        self.max_history = 1000
        
        logger.info("Alert manager initialized")
    
    def send_alert(self, alert: Dict):
        """Send alert through all enabled channels"""
        logger.info(f"Processing alert: {alert['type']} ({alert['severity']})")
        
        # Add to history
        self.alert_history.append(alert)
        if len(self.alert_history) > self.max_history:
            self.alert_history.pop(0)
        
        # Send through each channel
        results = {
            'email': False,
            'sms': False,
            'local': False
        }
        
        # Determine which channels to use based on severity
        severity = alert['severity']
        
        if severity == 'critical':
            # Send through all channels for critical alerts
            results['email'] = self.email_alert.send(alert)
            results['sms'] = self.sms_alert.send(alert)
            results['local'] = self.local_alert.send(alert)
        
        elif severity == 'warning':
            # Email and local for warnings
            results['email'] = self.email_alert.send(alert)
            results['local'] = self.local_alert.send(alert)
        
        else:  # info
            # Local only for info
            results['local'] = self.local_alert.send(alert)
        
        # Log results
        sent_channels = [ch for ch, success in results.items() if success]
        if sent_channels:
            logger.info(f"Alert sent via: {', '.join(sent_channels)}")
        else:
            logger.warning("Alert not sent through any channel")
        
        return results
    
    def get_alert_history(self, count: int = 10) -> list:
        """Get recent alert history"""
        return self.alert_history[-count:]
    
    def clear_history(self):
        """Clear alert history"""
        self.alert_history.clear()
        logger.info("Alert history cleared")


if __name__ == '__main__':
    # Test alert system
    config = {
        'email': {
            'enabled': False,  # Disable for testing
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': 'test@example.com',
            'password': 'password',
            'recipient': 'recipient@example.com'
        },
        'sms': {
            'enabled': False,  # Disable for testing
            'provider': 'twilio',
            'account_sid': 'ACxxxx',
            'auth_token': 'xxxx',
            'from_number': '+1234567890',
            'to_number': '+0987654321'
        },
        'local': {
            'buzzer_enabled': True,
            'led_enabled': True
        }
    }
    
    manager = AlertManager(config)
    
    # Test alert
    test_alert = {
        'type': 'heart_rate',
        'severity': 'warning',
        'message': 'Test alert: Heart rate above threshold',
        'value': 120,
        'threshold': 100,
        'timestamp': datetime.now()
    }
    
    print("Sending test alert...")
    results = manager.send_alert(test_alert)
    print(f"Results: {results}")
    
    # Show history
    print("\nAlert history:")
    for alert in manager.get_alert_history():
        print(f"  {alert['timestamp']}: {alert['message']}")

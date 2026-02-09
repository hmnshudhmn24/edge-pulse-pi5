"""
Web Dashboard Module
Flask-based web interface for real-time monitoring
"""

import logging
from flask import Flask, render_template_string, jsonify, request
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def create_app(monitor):
    """Create Flask application"""
    app = Flask(__name__)
    app.config['monitor'] = monitor
    
    @app.route('/')
    def index():
        """Main dashboard page"""
        return render_template_string(HTML_TEMPLATE)
    
    @app.route('/api/current')
    def get_current():
        """Get current readings"""
        try:
            readings = monitor.sensor_manager.read_all()
            if readings:
                return jsonify({
                    'success': True,
                    'data': readings
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to read sensors'
                }), 500
        except Exception as e:
            logger.error(f"API error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/history')
    def get_history():
        """Get historical data"""
        try:
            hours = int(request.args.get('hours', 24))
            start_date = datetime.now() - timedelta(hours=hours)
            
            readings = monitor.data_handler.get_readings(
                start_date=start_date,
                limit=1000
            )
            
            return jsonify({
                'success': True,
                'data': readings
            })
        except Exception as e:
            logger.error(f"API error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/alerts')
    def get_alerts():
        """Get recent alerts"""
        try:
            hours = int(request.args.get('hours', 24))
            start_date = datetime.now() - timedelta(hours=hours)
            
            alerts = monitor.data_handler.get_alerts(
                start_date=start_date,
                limit=100
            )
            
            return jsonify({
                'success': True,
                'data': alerts
            })
        except Exception as e:
            logger.error(f"API error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/statistics')
    def get_statistics():
        """Get statistics"""
        try:
            hours = int(request.args.get('hours', 24))
            start_date = datetime.now() - timedelta(hours=hours)
            
            stats = monitor.data_handler.get_statistics(start_date=start_date)
            
            return jsonify({
                'success': True,
                'data': stats
            })
        except Exception as e:
            logger.error(f"API error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return app


# HTML Template for dashboard
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EdgePulse-Pi5 Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }
        
        .card-title {
            font-size: 1.2em;
            color: #333;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .metric {
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }
        
        .unit {
            font-size: 0.5em;
            color: #666;
            margin-left: 5px;
        }
        
        .status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 500;
        }
        
        .status-normal {
            background: #d4edda;
            color: #155724;
        }
        
        .status-warning {
            background: #fff3cd;
            color: #856404;
        }
        
        .status-critical {
            background: #f8d7da;
            color: #721c24;
        }
        
        .timestamp {
            color: #999;
            font-size: 0.9em;
            margin-top: 10px;
        }
        
        .alerts-section {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }
        
        .alert-item {
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid;
        }
        
        .alert-critical {
            background: #f8d7da;
            border-left-color: #dc3545;
        }
        
        .alert-warning {
            background: #fff3cd;
            border-left-color: #ffc107;
        }
        
        .alert-info {
            background: #d1ecf1;
            border-left-color: #17a2b8;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .updating {
            animation: pulse 1s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏥 EdgePulse-Pi5</h1>
            <div class="subtitle">Real-time Health Monitoring Dashboard</div>
        </header>
        
        <div class="dashboard">
            <div class="card">
                <div class="card-title">❤️ Heart Rate</div>
                <div class="metric" id="heart-rate">--<span class="unit">bpm</span></div>
                <div class="status status-normal" id="hr-status">Normal</div>
                <div class="timestamp" id="hr-time">--</div>
            </div>
            
            <div class="card">
                <div class="card-title">🫁 Blood Oxygen</div>
                <div class="metric" id="spo2">--<span class="unit">%</span></div>
                <div class="status status-normal" id="spo2-status">Normal</div>
                <div class="timestamp" id="spo2-time">--</div>
            </div>
            
            <div class="card">
                <div class="card-title">🌡️ Temperature</div>
                <div class="metric" id="temperature">--<span class="unit">°C</span></div>
                <div class="status status-normal" id="temp-status">Normal</div>
                <div class="timestamp" id="temp-time">--</div>
            </div>
        </div>
        
        <div class="alerts-section">
            <h2 style="margin-bottom: 20px;">Recent Alerts</h2>
            <div id="alerts-container">
                <div class="loading">Loading alerts...</div>
            </div>
        </div>
    </div>
    
    <script>
        // Update interval (milliseconds)
        const UPDATE_INTERVAL = 2000;
        
        // Fetch current readings
        async function updateReadings() {
            try {
                const response = await fetch('/api/current');
                const result = await response.json();
                
                if (result.success) {
                    const data = result.data;
                    
                    // Update heart rate
                    if (data.heart_rate) {
                        document.getElementById('heart-rate').innerHTML = 
                            data.heart_rate + '<span class="unit">bpm</span>';
                        updateStatus('hr', data.heart_rate, 60, 100, 40, 150);
                    }
                    
                    // Update SpO2
                    if (data.spo2) {
                        document.getElementById('spo2').innerHTML = 
                            data.spo2 + '<span class="unit">%</span>';
                        updateStatus('spo2', data.spo2, 95, 100, 90, 100);
                    }
                    
                    // Update temperature
                    if (data.temperature) {
                        document.getElementById('temperature').innerHTML = 
                            data.temperature.toFixed(1) + '<span class="unit">°C</span>';
                        updateStatus('temp', data.temperature, 36.1, 37.8, 35.0, 39.0);
                    }
                    
                    // Update timestamp
                    const now = new Date().toLocaleTimeString();
                    document.getElementById('hr-time').textContent = 'Updated: ' + now;
                    document.getElementById('spo2-time').textContent = 'Updated: ' + now;
                    document.getElementById('temp-time').textContent = 'Updated: ' + now;
                }
            } catch (error) {
                console.error('Error fetching readings:', error);
            }
        }
        
        // Update status indicator
        function updateStatus(prefix, value, min, max, criticalMin, criticalMax) {
            const statusEl = document.getElementById(prefix + '-status');
            
            if (value < criticalMin || value > criticalMax) {
                statusEl.className = 'status status-critical';
                statusEl.textContent = 'Critical';
            } else if (value < min || value > max) {
                statusEl.className = 'status status-warning';
                statusEl.textContent = 'Warning';
            } else {
                statusEl.className = 'status status-normal';
                statusEl.textContent = 'Normal';
            }
        }
        
        // Fetch recent alerts
        async function updateAlerts() {
            try {
                const response = await fetch('/api/alerts?hours=24');
                const result = await response.json();
                
                if (result.success) {
                    const container = document.getElementById('alerts-container');
                    
                    if (result.data.length === 0) {
                        container.innerHTML = '<div class="loading">No recent alerts</div>';
                        return;
                    }
                    
                    container.innerHTML = result.data
                        .slice(0, 10)
                        .map(alert => `
                            <div class="alert-item alert-${alert.severity}">
                                <strong>${alert.severity.toUpperCase()}</strong>: ${alert.message}
                                <div style="color: #666; font-size: 0.9em; margin-top: 5px;">
                                    ${new Date(alert.timestamp).toLocaleString()}
                                </div>
                            </div>
                        `)
                        .join('');
                }
            } catch (error) {
                console.error('Error fetching alerts:', error);
            }
        }
        
        // Initial load
        updateReadings();
        updateAlerts();
        
        // Set up auto-refresh
        setInterval(updateReadings, UPDATE_INTERVAL);
        setInterval(updateAlerts, UPDATE_INTERVAL * 5);
    </script>
</body>
</html>
"""

"""
Data Handler Module
Manages database operations and data export
"""

import sqlite3
import csv
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class DataHandler:
    """Handles data storage and retrieval"""
    
    def __init__(self, db_path: str = 'data/edgepulse.db'):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        
        self._create_tables()
        logger.info(f"Database initialized: {db_path}")
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Readings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                heart_rate INTEGER,
                spo2 INTEGER,
                temperature REAL,
                temperature_unit TEXT DEFAULT 'C'
            )
        """)
        
        # Alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                value REAL,
                threshold REAL,
                acknowledged INTEGER DEFAULT 0
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_readings_timestamp 
            ON readings(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_timestamp 
            ON alerts(timestamp)
        """)
        
        self.conn.commit()
        logger.debug("Database tables created/verified")
    
    def save_reading(self, readings: Dict) -> bool:
        """
        Save vital signs reading to database
        
        Args:
            readings: Dictionary containing vital sign values
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                INSERT INTO readings (heart_rate, spo2, temperature, temperature_unit)
                VALUES (?, ?, ?, ?)
            """, (
                readings.get('heart_rate'),
                readings.get('spo2'),
                readings.get('temperature'),
                readings.get('temperature_unit', 'C')
            ))
            
            self.conn.commit()
            logger.debug(f"Reading saved: HR={readings.get('heart_rate')}, SpO2={readings.get('spo2')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save reading: {e}")
            return False
    
    def save_alert(self, alert: Dict) -> bool:
        """
        Save alert to database
        
        Args:
            alert: Dictionary containing alert information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                INSERT INTO alerts (timestamp, alert_type, severity, message, value, threshold)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                alert.get('timestamp', datetime.now()),
                alert.get('type'),
                alert.get('severity'),
                alert.get('message'),
                alert.get('value'),
                alert.get('threshold')
            ))
            
            self.conn.commit()
            logger.debug(f"Alert saved: {alert.get('type')} ({alert.get('severity')})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save alert: {e}")
            return False
    
    def get_readings(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Retrieve readings from database
        
        Args:
            start_date: Start datetime for filtering
            end_date: End datetime for filtering
            limit: Maximum number of readings to return
            
        Returns:
            List of reading dictionaries
        """
        try:
            cursor = self.conn.cursor()
            
            query = "SELECT * FROM readings WHERE 1=1"
            params = []
            
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            readings = [dict(row) for row in rows]
            return readings
            
        except Exception as e:
            logger.error(f"Failed to retrieve readings: {e}")
            return []
    
    def get_alerts(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Retrieve alerts from database
        
        Args:
            start_date: Start datetime for filtering
            end_date: End datetime for filtering
            severity: Filter by severity level
            limit: Maximum number of alerts to return
            
        Returns:
            List of alert dictionaries
        """
        try:
            cursor = self.conn.cursor()
            
            query = "SELECT * FROM alerts WHERE 1=1"
            params = []
            
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)
            
            if severity:
                query += " AND severity = ?"
                params.append(severity)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            alerts = [dict(row) for row in rows]
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to retrieve alerts: {e}")
            return []
    
    def get_latest_reading(self) -> Optional[Dict]:
        """Get the most recent reading"""
        readings = self.get_readings(limit=1)
        return readings[0] if readings else None
    
    def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Calculate statistics from readings
        
        Args:
            start_date: Start datetime for filtering
            end_date: End datetime for filtering
            
        Returns:
            Dictionary containing statistical information
        """
        try:
            cursor = self.conn.cursor()
            
            query = """
                SELECT 
                    COUNT(*) as count,
                    AVG(heart_rate) as avg_hr,
                    MIN(heart_rate) as min_hr,
                    MAX(heart_rate) as max_hr,
                    AVG(spo2) as avg_spo2,
                    MIN(spo2) as min_spo2,
                    MAX(spo2) as max_spo2,
                    AVG(temperature) as avg_temp,
                    MIN(temperature) as min_temp,
                    MAX(temperature) as max_temp
                FROM readings
                WHERE 1=1
            """
            params = []
            
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)
            
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Failed to calculate statistics: {e}")
            return {}
    
    def export_to_csv(
        self,
        output_file: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> bool:
        """
        Export readings to CSV file
        
        Args:
            output_file: Path to output CSV file
            start_date: Start datetime for filtering
            end_date: End datetime for filtering
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all readings
            cursor = self.conn.cursor()
            
            query = "SELECT * FROM readings WHERE 1=1"
            params = []
            
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)
            
            query += " ORDER BY timestamp ASC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            if not rows:
                logger.warning("No data to export")
                return False
            
            # Write to CSV
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow(['Timestamp', 'Heart Rate (bpm)', 'SpO2 (%)', 'Temperature', 'Unit'])
                
                # Write data
                for row in rows:
                    writer.writerow([
                        row['timestamp'],
                        row['heart_rate'],
                        row['spo2'],
                        row['temperature'],
                        row['temperature_unit']
                    ])
            
            logger.info(f"Exported {len(rows)} readings to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export to CSV: {e}")
            return False
    
    def cleanup_old_data(self, cutoff_date: datetime) -> int:
        """
        Delete data older than cutoff date
        
        Args:
            cutoff_date: Delete data before this date
            
        Returns:
            Number of records deleted
        """
        try:
            cursor = self.conn.cursor()
            
            # Delete old readings
            cursor.execute("""
                DELETE FROM readings WHERE timestamp < ?
            """, (cutoff_date,))
            readings_deleted = cursor.rowcount
            
            # Delete old alerts
            cursor.execute("""
                DELETE FROM alerts WHERE timestamp < ?
            """, (cutoff_date,))
            alerts_deleted = cursor.rowcount
            
            self.conn.commit()
            
            total_deleted = readings_deleted + alerts_deleted
            logger.info(f"Deleted {total_deleted} old records (readings: {readings_deleted}, alerts: {alerts_deleted})")
            
            # Vacuum database to reclaim space
            cursor.execute("VACUUM")
            
            return total_deleted
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return 0
    
    def acknowledge_alert(self, alert_id: int) -> bool:
        """
        Mark an alert as acknowledged
        
        Args:
            alert_id: ID of the alert to acknowledge
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                UPDATE alerts SET acknowledged = 1 WHERE id = ?
            """, (alert_id,))
            
            self.conn.commit()
            logger.debug(f"Alert {alert_id} acknowledged")
            return True
            
        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


if __name__ == '__main__':
    # Test data handler
    print("Testing DataHandler...\n")
    
    handler = DataHandler('data/test_edgepulse.db')
    
    # Test saving readings
    print("Saving test readings...")
    for i in range(5):
        reading = {
            'heart_rate': 75 + i,
            'spo2': 97 + i % 3,
            'temperature': 36.8 + (i * 0.1),
            'temperature_unit': 'C'
        }
        handler.save_reading(reading)
    
    # Test retrieving readings
    print("\nRetrieving readings...")
    readings = handler.get_readings(limit=5)
    for reading in readings:
        print(f"  {reading['timestamp']}: HR={reading['heart_rate']}, SpO2={reading['spo2']}, Temp={reading['temperature']}°C")
    
    # Test saving alerts
    print("\nSaving test alert...")
    alert = {
        'type': 'heart_rate',
        'severity': 'warning',
        'message': 'Test alert',
        'value': 120,
        'threshold': 100,
        'timestamp': datetime.now()
    }
    handler.save_alert(alert)
    
    # Test retrieving alerts
    print("\nRetrieving alerts...")
    alerts = handler.get_alerts(limit=5)
    for alert in alerts:
        print(f"  {alert['timestamp']}: {alert['severity']} - {alert['message']}")
    
    # Test statistics
    print("\nCalculating statistics...")
    stats = handler.get_statistics()
    print(f"  Count: {stats.get('count')}")
    print(f"  Avg HR: {stats.get('avg_hr'):.1f} bpm")
    print(f"  Avg SpO2: {stats.get('avg_spo2'):.1f}%")
    
    # Test export
    print("\nExporting to CSV...")
    handler.export_to_csv('data/test_export.csv')
    
    handler.close()
    print("\nTest complete")

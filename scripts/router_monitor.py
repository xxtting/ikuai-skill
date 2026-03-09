#!/usr/bin/env python3
"""
Router Monitor for iKuai Routers

Real-time router monitoring with threshold-based alerting and historical logging.
"""

import time
import json
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from ikuai_api_client import IkuaiAPIClient


class RouterMonitor:
    """Monitor for iKuai router status and alerts."""
    
    def __init__(
        self,
        client: IkuaiAPIClient,
        dev_id: str,
        log_file: str = "router_monitor.log"
    ):
        """
        Initialize router monitor.
        
        Args:
            client: IkuaiAPIClient instance
            dev_id: Device ID of the router
            log_file: Path to log file
        """
        self.client = client
        self.dev_id = dev_id
        self.log_file = log_file
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Alert thresholds
        self.thresholds = {
            'cpu_percent': 90,
            'memory_percent': 90,
            'temperature_celsius': 75,
            'online_users': 100,
            'bandwidth_mbps': 500
        }
        
        # Alert callbacks
        self.alert_callbacks = []
        
        # Monitoring state
        self.monitoring = False
        self.interval = 60  # Default interval: 60 seconds
        self.history = []
        self.max_history = 1000  # Max historical records to keep
        
        # Previous state for comparison
        self.prev_status = None
    
    def set_thresholds(self, **kwargs):
        """
        Set alert thresholds.
        
        Args:
            cpu_percent: CPU usage threshold (percentage)
            memory_percent: Memory usage threshold (percentage)
            temperature_celsius: Temperature threshold (Celsius)
            online_users: Online users count threshold
            bandwidth_mbps: Bandwidth usage threshold (Mbps)
        """
        for key, value in kwargs.items():
            if key in self.thresholds:
                self.thresholds[key] = value
                self.logger.info(f"Updated threshold {key}: {value}")
    
    def set_interval(self, seconds: int):
        """
        Set monitoring interval.
        
        Args:
            seconds: Interval in seconds
        """
        self.interval = seconds
        self.logger.info(f"Monitoring interval set to {seconds} seconds")
    
    def add_alert_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """
        Add callback function for alerts.
        
        Args:
            callback: Function to call when alert is triggered
                     Receives (alert_type, alert_data) as arguments
        """
        self.alert_callbacks.append(callback)
        self.logger.info("Alert callback added")
    
    def _trigger_alert(self, alert_type: str, alert_data: Dict[str, Any]):
        """
        Trigger alert callbacks.
        
        Args:
            alert_type: Type of alert
            alert_data: Alert data
        """
        self.logger.warning(f"ALERT: {alert_type} - {json.dumps(alert_data, ensure_ascii=False)}")
        
        for callback in self.alert_callbacks:
            try:
                callback(alert_type, alert_data)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {str(e)}")
    
    def _check_thresholds(self, status: Dict[str, Any]):
        """
        Check status against thresholds and trigger alerts.
        
        Args:
            status: Router status data
        """
        data = status.get('data', {})
        
        # Check CPU usage
        cpu = data.get('cpu', 0)
        if cpu > self.thresholds['cpu_percent']:
            self._trigger_alert('HIGH_CPU', {
                'current': cpu,
                'threshold': self.thresholds['cpu_percent']
            })
        
        # Check memory usage
        memory = data.get('mem', 0)
        if memory > self.thresholds['memory_percent']:
            self._trigger_alert('HIGH_MEMORY', {
                'current': memory,
                'threshold': self.thresholds['memory_percent']
            })
        
        # Check temperature
        temp = data.get('temp', 0)
        if temp > self.thresholds['temperature_celsius']:
            self._trigger_alert('HIGH_TEMPERATURE', {
                'current': temp,
                'threshold': self.thresholds['temperature_celsius']
            })
        
        # Check online users
        online_users = data.get('online_users', 0)
        if online_users > self.thresholds['online_users']:
            self._trigger_alert('HIGH_ONLINE_USERS', {
                'current': online_users,
                'threshold': self.thresholds['online_users']
            })
        
        # Check bandwidth
        bandwidth = data.get('bandwidth', 0)
        if bandwidth > self.thresholds['bandwidth_mbps']:
            self._trigger_alert('HIGH_BANDWIDTH', {
                'current': bandwidth,
                'threshold': self.thresholds['bandwidth_mbps']
            })
    
    def _record_status(self, status: Dict[str, Any]):
        """
        Record status to history.
        
        Args:
            status: Router status data
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'status': status
        }
        
        self.history.append(record)
        
        # Trim history if needed
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current router status.
        
        Returns:
            Router status data
        """
        try:
            status = self.client.get_router_status(self.dev_id)
            
            if status.get('errno') == 0:
                self.logger.info("Status retrieved successfully")
                return status
            else:
                self.logger.error(f"Failed to get status: {status.get('errmsg')}")
                return status
                
        except Exception as e:
            self.logger.error(f"Error getting status: {str(e)}")
            return {'errno': -1, 'errmsg': str(e)}
    
    def get_online_users(self) -> Dict[str, Any]:
        """
        Get current online users.
        
        Returns:
            Online users data
        """
        try:
            result = self.client.get_online_users(self.dev_id)
            
            if result.get('errno') == 0:
                data = result.get('data', [])
                self.logger.info(f"Online users: {len(data)}")
            else:
                self.logger.error(f"Failed to get online users: {result.get('errmsg')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting online users: {str(e)}")
            return {'errno': -1, 'errmsg': str(e)}
    
    def check_once(self):
        """Perform a single status check."""
        self.logger.info("Performing status check...")
        
        status = self.get_status()
        
        if status.get('errno') == 0:
            self._check_thresholds(status)
            self._record_status(status)
            
            # Display summary
            data = status.get('data', {})
            self.logger.info(
                f"Status: CPU={data.get('cpu', 0)}%, "
                f"Memory={data.get('mem', 0)}%, "
                f"Temp={data.get('temp', 0)}°C, "
                f"Online={data.get('online_users', 0)}"
            )
    
    def start_monitoring(self, interval: int = None):
        """
        Start continuous monitoring.
        
        Args:
            interval: Monitoring interval in seconds (optional)
        """
        if self.monitoring:
            self.logger.warning("Monitoring already running")
            return
        
        if interval:
            self.set_interval(interval)
        
        self.monitoring = True
        self.logger.info(f"Starting monitoring (interval: {self.interval}s)")
        
        try:
            while self.monitoring:
                self.check_once()
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
            self.stop_monitoring()
        except Exception as e:
            self.logger.error(f"Monitoring error: {str(e)}")
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        self.monitoring = False
        self.logger.info("Monitoring stopped")
    
    def get_history(self, limit: int = 100) -> list:
        """
        Get historical status records.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of historical records
        """
        return self.history[-limit:]
    
    def export_history(self, file_path: str):
        """
        Export history to JSON file.
        
        Args:
            file_path: Path to output file
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
            self.logger.info(f"History exported to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to export history: {str(e)}")
    
    def get_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Calculate statistics from historical data.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Statistics dictionary
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_records = [
            record for record in self.history
            if datetime.fromisoformat(record['timestamp']) > cutoff_time
        ]
        
        if not recent_records:
            return {'error': 'No data available for specified period'}
        
        cpu_values = [r['status'].get('data', {}).get('cpu', 0) for r in recent_records]
        memory_values = [r['status'].get('data', {}).get('mem', 0) for r in recent_records]
        temp_values = [r['status'].get('data', {}).get('temp', 0) for r in recent_records]
        
        stats = {
            'period_hours': hours,
            'record_count': len(recent_records),
            'cpu': {
                'avg': sum(cpu_values) / len(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values)
            },
            'memory': {
                'avg': sum(memory_values) / len(memory_values),
                'max': max(memory_values),
                'min': min(memory_values)
            },
            'temperature': {
                'avg': sum(temp_values) / len(temp_values),
                'max': max(temp_values),
                'min': min(temp_values)
            }
        }
        
        return stats
    
    def print_statistics(self, hours: int = 24):
        """
        Print statistics summary.
        
        Args:
            hours: Number of hours to analyze
        """
        stats = self.get_statistics(hours)
        
        if 'error' in stats:
            self.logger.error(stats['error'])
            return
        
        print(f"\n=== Statistics (Last {hours} hours) ===")
        print(f"Records: {stats['record_count']}")
        print(f"\nCPU Usage:")
        print(f"  Average: {stats['cpu']['avg']:.1f}%")
        print(f"  Maximum: {stats['cpu']['max']:.1f}%")
        print(f"  Minimum: {stats['cpu']['min']:.1f}%")
        print(f"\nMemory Usage:")
        print(f"  Average: {stats['memory']['avg']:.1f}%")
        print(f"  Maximum: {stats['memory']['max']:.1f}%")
        print(f"  Minimum: {stats['memory']['min']:.1f}%")
        print(f"\nTemperature:")
        print(f"  Average: {stats['temperature']['avg']:.1f}°C")
        print(f"  Maximum: {stats['temperature']['max']:.1f}°C")
        print(f"  Minimum: {stats['temperature']['min']:.1f}°C")


def webhook_alert_callback(webhook_url: str):
    """
    Create a webhook alert callback.
    
    Args:
        webhook_url: URL to send webhook to
        
    Returns:
        Callback function
    """
    import requests
    
    def callback(alert_type: str, alert_data: Dict[str, Any]):
        payload = {
            'alert_type': alert_type,
            'alert_data': alert_data,
            'router_dev_id': None,  # Will be set by monitor
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            print(f"✓ Webhook sent: {webhook_url}")
        except Exception as e:
            print(f"✗ Webhook failed: {str(e)}")
    
    return callback


def main():
    """Example usage."""
    APP_ID = "your_app_id"
    APP_SECRET = "your_app_secret"
    DEV_ID = "your_device_id"
    
    # Initialize client and monitor
    client = IkuaiAPIClient(APP_ID, APP_SECRET)
    client.get_access_token()
    
    monitor = RouterMonitor(client, DEV_ID)
    
    # Configure thresholds
    monitor.set_thresholds(
        cpu_percent=80,
        memory_percent=85,
        temperature_celsius=70
    )
    
    # Add webhook alert (optional)
    # monitor.add_alert_callback(webhook_alert_callback("https://your-webhook-url.com"))
    
    # Custom alert callback example
    def custom_alert(alert_type: str, alert_data: Dict[str, Any]):
        print(f"\n🚨 ALERT TRIGGERED!")
        print(f"Type: {alert_type}")
        print(f"Data: {json.dumps(alert_data, indent=2)}")
        print()
    
    monitor.add_alert_callback(custom_alert)
    
    try:
        # Single check
        print("=== Single Status Check ===")
        monitor.check_once()
        
        # Continuous monitoring
        print("\n=== Starting Continuous Monitoring ===")
        print("Press Ctrl+C to stop\n")
        monitor.start_monitoring(interval=30)
        
    except KeyboardInterrupt:
        print("\nMonitoring stopped")
    finally:
        # Export history before exit
        monitor.export_history('router_history.json')
        
        # Print statistics
        monitor.print_statistics(hours=1)
        
        client.close()


if __name__ == "__main__":
    main()

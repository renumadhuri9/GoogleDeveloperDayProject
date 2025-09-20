import numpy as np
from datetime import datetime, timedelta

class TrafficSimulator:
    def __init__(self, base_flow=100, variance=20):
        """
        Initialize traffic simulator with Hyderabad traffic patterns
        
        Args:
            base_flow (int): Base number of vehicles per minute
            variance (int): Maximum variance in vehicle count
        """
        self.base_flow = base_flow
        self.variance = variance
        
        # Typical Hyderabad traffic patterns
        self.peak_hours = {
            'morning': (8, 11),    # Morning rush: 8 AM - 11 AM
            'evening': (16, 20)    # Evening rush: 4 PM - 8 PM
        }
        
        # Traffic multipliers for different conditions
        self.multipliers = {
            'peak_hour': 2.0,      # Peak hour traffic multiplier
            'off_peak': 0.7,       # Off-peak traffic multiplier
            'weekend': 0.8,        # Weekend traffic reduction
            'rain': 1.3,           # Rain impact on traffic
            'high_temp': 1.2       # High temperature impact (people prefer vehicles)
        }
        
    def _is_peak_hour(self, hour):
        """Check if current hour is during peak traffic"""
        morning_start, morning_end = self.peak_hours['morning']
        evening_start, evening_end = self.peak_hours['evening']
        
        return (morning_start <= hour < morning_end) or (evening_start <= hour < evening_end)
    
    def _get_time_based_multiplier(self, timestamp):
        """Calculate traffic multiplier based on time patterns"""
        hour = timestamp.hour
        is_weekend = timestamp.weekday() >= 5
        
        multiplier = 1.0
        
        # Apply weekend reduction
        if is_weekend:
            multiplier *= self.multipliers['weekend']
        
        # Apply peak/off-peak multipliers
        if self._is_peak_hour(hour):
            multiplier *= self.multipliers['peak_hour']
        elif hour >= 23 or hour <= 5:  # Late night/early morning
            multiplier *= self.multipliers['off_peak']
        
        return multiplier
        
    def generate_traffic_pattern(self, timestamp=None):
        """
        Generate simulated traffic data based on Hyderabad patterns
        
        Args:
            timestamp (datetime, optional): Specific timestamp to generate data for.
                                         If None, uses current time.
        
        Returns:
            tuple: (timestamp, count)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Get base multiplier from time patterns
        multiplier = self._get_time_based_multiplier(timestamp)
        
        # Add some randomness to base flow
        base_count = self.base_flow * multiplier
        variance = self.variance * multiplier
        count = base_count + np.random.normal(0, variance/2)
        
        # Add some periodic variation
        hour_fraction = timestamp.hour + timestamp.minute / 60.0
        periodic_variation = np.sin(2 * np.pi * hour_fraction / 24) * 0.2 * base_count
        
        count += periodic_variation
        
        return timestamp, max(0, int(count))  # Ensure count is not negative and integer
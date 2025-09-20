import numpy as np
from datetime import datetime, timedelta

class TemperatureSimulator:
    def __init__(self):
        """
        Initialize temperature simulator with Hyderabad-like patterns
        
        Hyderabad typically has:
        - Daily temp range: 20-35°C
        - Peak temperature around 2-3 PM
        - Lowest temperature around 5-6 AM
        - Seasonal variations (we'll simplify this for demo)
        """
        self.base_temp = 27.0  # Base temperature
        self.daily_amplitude = 7.0  # Temperature variation throughout the day
        self.noise_amplitude = 1.0  # Random variations
        
    def get_current_temperature(self) -> float:
        """
        Get current simulated temperature
        
        Returns:
            float: Current temperature in Celsius
        """
        current_time = datetime.now()
        return self._calculate_temperature(current_time)
    
    def get_forecast(self, hours=3):
        """
        Get temperature forecast for next few hours
        
        Args:
            hours (int): Number of hours to forecast
            
        Returns:
            list: List of (datetime, temperature) tuples
        """
        current_time = datetime.now()
        forecast_data = []
        
        for i in range(hours):
            future_time = current_time + timedelta(hours=i)
            temp = self._calculate_temperature(future_time)
            forecast_data.append((future_time, temp))
        
        return forecast_data
    
    def _calculate_temperature(self, timestamp: datetime) -> float:
        """
        Calculate temperature based on time of day
        
        Args:
            timestamp (datetime): Time to calculate temperature for
            
        Returns:
            float: Temperature in Celsius
        """
        # Convert time to hour fraction (0-24)
        hour = timestamp.hour + timestamp.minute / 60.0
        
        # Temperature follows a sine wave pattern with:
        # - Peak at 14:00 (2 PM)
        # - Trough at 5:00 (5 AM)
        phase_shift = (14 - 5) * (2 * np.pi / 24)  # Shift peak to 2 PM
        temp = self.base_temp + self.daily_amplitude * np.sin(
            2 * np.pi * (hour - 5) / 24 - phase_shift
        )
        
        # Add some random noise
        noise = np.random.normal(0, self.noise_amplitude)
        
        return round(temp + noise, 1)
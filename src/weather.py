import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class WeatherAPI:
    def __init__(self):
        """Initialize WeatherAPI with Hitech City coordinates"""
        self.api_key = os.getenv('WEATHER_API_KEY')
        if not self.api_key:
            raise ValueError("WEATHER_API_KEY not found in environment variables")
        
        # Coordinates for Hitech City, Hyderabad
        self.latitude = "17.4435"
        self.longitude = "78.3772"
        self.base_url = "http://api.weatherapi.com/v1"
        
    def get_current_temperature(self):
        """
        Get current temperature for Hitech City
        
        Returns:
            float: Current temperature in Celsius
        """
        try:
            url = f"{self.base_url}/current.json"
            params = {
                'key': self.api_key,
                'q': f"{self.latitude},{self.longitude}"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data['current']['temp_c']
            
        except requests.RequestException as e:
            print(f"Error fetching weather data: {e}")
            # Return None or a default value in case of error
            return None
            
    def get_forecast(self, hours=3):
        """
        Get temperature forecast for next few hours
        
        Args:
            hours (int): Number of hours to forecast
            
        Returns:
            list: List of (datetime, temperature) tuples
        """
        try:
            url = f"{self.base_url}/forecast.json"
            params = {
                'key': self.api_key,
                'q': f"{self.latitude},{self.longitude}",
                'hours': hours
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            forecast_data = []
            
            for hour in data['forecast']['forecastday'][0]['hour']:
                time = datetime.strptime(hour['time'], "%Y-%m-%d %H:%M")
                temp = hour['temp_c']
                forecast_data.append((time, temp))
                
            return forecast_data
            
        except requests.RequestException as e:
            print(f"Error fetching forecast data: {e}")
            return []
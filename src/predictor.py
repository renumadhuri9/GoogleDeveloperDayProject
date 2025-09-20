import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from temperature_sim import TemperatureSimulator

class TrafficPredictor:
    def __init__(self, window_size=30):
        """
        Initialize traffic predictor
        
        Args:
            window_size (int): Number of historical points to use for prediction
        """
        self.window_size = window_size
        self.model = LinearRegression()
        self.history_times = []
        self.history_counts = []
        self.history_temps = []
        self.temp_simulator = TemperatureSimulator()
        
    def add_datapoint(self, timestamp: datetime, count: int, temperature=None):
        """
        Add a new datapoint to the prediction model
        
        Args:
            timestamp (datetime): Time of measurement
            count (int): Vehicle count
            temperature (float, optional): Temperature in Celsius. If None, will use simulator
        """
        if temperature is None:
            temperature = self.temp_simulator.get_current_temperature()
        
        self.history_times.append(timestamp)
        self.history_counts.append(count)
        self.history_temps.append(temperature)
        
        # Keep only recent history
        if len(self.history_times) > self.window_size:
            self.history_times = self.history_times[-self.window_size:]
            self.history_counts = self.history_counts[-self.window_size:]
            self.history_temps = self.history_temps[-self.window_size:]
    
    def predict_next(self, minutes_ahead=15):
        """
        Predict traffic for the next N minutes using time and temperature
        
        Args:
            minutes_ahead (int): Number of minutes to predict ahead
            
        Returns:
            tuple: (future_times, predictions, future_temps)
        """
        if len(self.history_times) < 5:  # Need minimum data points
            return [], [], []
            
        # Convert times to minutes from start for numerical prediction
        base_time = self.history_times[0]
        time_features = np.array([(t - base_time).total_seconds() / 60 for t in self.history_times])
        
        # Combine time and temperature features
        X = np.column_stack((time_features, self.history_temps))
        y = np.array(self.history_counts)
        
        # Fit model
        self.model.fit(X, y)
        
        # Generate future timestamps
        last_time = self.history_times[-1]
        future_times = [last_time + timedelta(minutes=i+1) for i in range(minutes_ahead)]
        
        # Get temperature forecast
        forecast_data = self.temp_simulator.get_forecast(hours=int((minutes_ahead + 59) / 60))
        future_temps = []
        
        # Match forecast temperatures with prediction times
        for future_time in future_times:
            # Find the closest forecast time
            closest_forecast = min(forecast_data, key=lambda x: abs(x[0] - future_time))
            future_temps.append(closest_forecast[1])
        
        # Create feature matrix for prediction
        future_time_features = np.array([(t - base_time).total_seconds() / 60 for t in future_times])
        X_future = np.column_stack((future_time_features, future_temps))
        
        # Predict
        predictions = self.model.predict(X_future)
        
        return future_times, predictions.astype(int), future_temps
        
    def check_congestion(self, threshold=150):
        """
        Check if predicted traffic indicates congestion
        
        Args:
            threshold (int): Vehicle count threshold for congestion
            
        Returns:
            bool: True if congestion predicted
        """
        _, predictions, _ = self.predict_next(minutes_ahead=5)
        return any(count > threshold for count in predictions)
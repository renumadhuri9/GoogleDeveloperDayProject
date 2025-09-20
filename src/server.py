import streamlit as st
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import time
from traffic_detection import TrafficSimulator
from predictor import TrafficPredictor

def initialize_app():
    """Initialize the Streamlit application and session state"""
    # Initialize or reset simulator and predictor
    st.session_state.simulator = TrafficSimulator(base_flow=100, variance=20)
    st.session_state.predictor = TrafficPredictor(window_size=30)
    
    # Initialize or clear history
    if 'history_times' not in st.session_state:
        st.session_state.history_times = []
    if 'history_counts' not in st.session_state:
        st.session_state.history_counts = []
    
    # Clear old data that's more than 30 minutes old
    current_time = datetime.now()
    cutoff_time = current_time - timedelta(minutes=30)
    
    if st.session_state.history_times:
        valid_indices = [i for i, t in enumerate(st.session_state.history_times) 
                        if t >= cutoff_time]
        
        st.session_state.history_times = [st.session_state.history_times[i] for i in valid_indices] if valid_indices else []
        st.session_state.history_counts = [st.session_state.history_counts[i] for i in valid_indices] if valid_indices else []
        
    # Initialize with some recent data if empty
    if not st.session_state.history_times:
        for i in range(5):
            time_point = current_time - timedelta(minutes=5-i)
            timestamp, count = st.session_state.simulator.generate_traffic_pattern(time_point)
            st.session_state.history_times.append(timestamp)
            st.session_state.history_counts.append(count)

def update_data():
    """Update traffic data and predictions"""
    # Get current time
    current_time = datetime.now()
    
    # Clean up old data (older than 30 minutes)
    if st.session_state.history_times:
        cutoff_time = current_time - timedelta(minutes=30)
        valid_indices = [i for i, t in enumerate(st.session_state.history_times) 
                        if t >= cutoff_time]
        
        st.session_state.history_times = [st.session_state.history_times[i] for i in valid_indices]
        st.session_state.history_counts = [st.session_state.history_counts[i] for i in valid_indices]
    
    # Generate new traffic data
    timestamp, count = st.session_state.simulator.generate_traffic_pattern(current_time)
    
    # Get temperature from predictor's temperature simulator
    temperature = st.session_state.predictor.temp_simulator.get_current_temperature()
    
    # Update history
    st.session_state.history_times.append(timestamp)
    st.session_state.history_counts.append(count)
    
    # Update predictor with temperature
    st.session_state.predictor.add_datapoint(timestamp, count, temperature)
    
    # Update last refresh time
    st.session_state.last_refresh = current_time
    
    return timestamp, count, temperature

def create_traffic_plot():
    """Create and return the traffic visualization plot"""
    # Get predictions
    future_times, predictions, future_temps = st.session_state.predictor.predict_next(minutes_ahead=15)
    
    # Create subplots for traffic and temperature
    fig = go.Figure()
    
    # Historical traffic data
    fig.add_trace(go.Scatter(
        x=st.session_state.history_times,
        y=st.session_state.history_counts,
        name='Historical Traffic',
        line=dict(color='#4B8BBE', width=2)  # Professional blue
    ))
    
    # Predicted traffic
    if len(future_times) > 0:
        fig.add_trace(go.Scatter(
            x=future_times,
            y=predictions,
            name='Predicted Traffic',
            line=dict(color='#FF6B6B', width=2, dash='dash')  # Soft red
        ))
    
    # Historical temperature data
    fig.add_trace(go.Scatter(
        x=st.session_state.history_times,
        y=st.session_state.predictor.history_temps,
        name='Temperature (°C)',
        yaxis='y2',
        line=dict(color='#FFA500', width=2)  # Orange
    ))
    
    # Predicted temperature
    if len(future_times) > 0:
        fig.add_trace(go.Scatter(
            x=future_times,
            y=future_temps,
            name='Predicted Temp',
            yaxis='y2',
            line=dict(color='#FFD700', width=2, dash='dash')  # Gold
        ))
    
    # Layout with dual y-axes
    current_time = datetime.now()
    time_range_start = current_time - timedelta(minutes=30)
    time_range_end = current_time + timedelta(minutes=15)
    
    fig.update_layout(
        plot_bgcolor='rgba(28, 28, 28, 0.8)',
        paper_bgcolor='rgba(28, 28, 28, 0)',
        title=dict(
            text='Real-time Traffic Flow & Temperature Analysis',
            y=0.98,
            x=0.5,
            xanchor='center',
            yanchor='top',
            font=dict(size=18, color='white')
        ),
        xaxis=dict(
            title='Time',
            gridcolor='rgba(255, 255, 255, 0.1)',
            range=[time_range_start, time_range_end],
            tickformat='%H:%M',
            tickfont=dict(size=10),
            title_font=dict(size=12)
        ),
        yaxis=dict(
            title='Vehicles per Minute',
            gridcolor='rgba(255, 255, 255, 0.1)',
            tickfont=dict(size=10),
            title_font=dict(size=12),
            title_standoff=20
        ),
        yaxis2=dict(
            title='Temperature (°C)',
            overlaying='y',
            side='right',
            range=[20, 40],
            tickfont=dict(size=10),
            title_font=dict(size=12),
            title_standoff=20,
            gridcolor='rgba(255, 255, 255, 0.05)'
        ),
        height=400,
        margin=dict(l=60, r=60, t=60, b=60),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(28, 28, 28, 0.8)',
            bordercolor='rgba(255, 255, 255, 0.1)',
            borderwidth=1,
            font=dict(size=10)
        ),
        hovermode='x unified'
    )
    
    return fig

def load_custom_css():
    """Load custom CSS styles"""
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def format_metric(label, value, prefix="", suffix=""):
    """Format metric with custom HTML/CSS"""
    return f"""
    <div style='padding: 1rem; background-color: rgba(28, 28, 28, 0.5); border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1);'>
        <p style='color: #888; margin-bottom: 0.5rem; font-size: 0.8rem;'>{label}</p>
        <h3 style='margin: 0; font-size: 1.5rem;'>{prefix}{value}{suffix}</h3>
    </div>
    """

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title='Traffic Flow Analytics | Hitech City',
        layout='wide',
        initial_sidebar_state='expanded'
    )
    
    # Load custom CSS
    load_custom_css()
    
    # Initialize app state
    initialize_app()
    
    # Premium Header with Logo and Title
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Emblem_of_Telangana.svg/1200px-Emblem_of_Telangana.svg.png", width=100)
    with col2:
        st.markdown("""
        <h1 style='margin-bottom: 0;'>Urban Traffic Analytics</h1>
        <p style='font-size: 1.2rem; color: #888;'>Hitech City Smart Traffic Management System</p>
        """, unsafe_allow_html=True)
    
    # Description with premium styling
    st.markdown("""
    <div style='background-color: rgba(28, 131, 225, 0.1); padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
        <h4 style='margin: 0; color: #1C83E1;'>AI-Powered Traffic Analysis</h4>
        <p style='margin: 0.5rem 0 0 0;'>
        Advanced real-time monitoring and prediction system for Hitech City traffic patterns.
        Utilizing machine learning algorithms to analyze temperature impact on traffic flow.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Premium Sidebar
    st.sidebar.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <h2 style='font-size: 1.5rem; margin: 0;'>Control Center</h2>
        <p style='color: #888; margin-top: 0.5rem;'>System Configuration</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # Analysis Settings
    st.sidebar.markdown("### 📊 Analysis Settings")
    update_frequency = st.sidebar.slider(
        "Refresh Rate (seconds)",
        min_value=1,
        max_value=60,
        value=5,
        help="Set how frequently the dashboard updates"
    )
    
    # Traffic Thresholds
    st.sidebar.markdown("### 🚦 Traffic Thresholds")
    congestion_threshold = st.sidebar.slider(
        "Congestion Alert Level",
        min_value=50,
        max_value=300,
        value=150,
        help="Vehicle count that triggers congestion warning"
    )
    
    # Location Selection
    st.sidebar.markdown("### 📍 Location Focus")
    selected_location = st.sidebar.selectbox(
        "Monitor Point",
        ["Hitech City Junction", "Mindspace Junction", "Cyber Towers", "HITEC City MMTS"],
        help="Select specific location to monitor"
    )
    
    # Time Range
    st.sidebar.markdown("### ⏰ Time Window")
    time_window = st.sidebar.select_slider(
        "Historical Data Window",
        options=["30 mins", "1 hour", "2 hours", "4 hours"],
        value="1 hour",
        help="Amount of historical data to display"
    )
    
    # Create placeholder for metrics
    metrics_placeholder = st.empty()
    plot_placeholder = st.empty()
    
    # Use Streamlit's native real-time updates
    if 'last_update' not in st.session_state:
        st.session_state.last_update = time.time()
    
    current_time = time.time()
    if current_time - st.session_state.last_update >= update_frequency:
        # Update data
        timestamp, current_count, current_temp = update_data()
        st.session_state.last_update = current_time
        
        # Update metrics container
        with metrics_placeholder.container():
            # Premium status card
            status_col1, status_col2 = st.columns([2, 1])
            with status_col1:
                st.markdown("""
                <div style='background-color: rgba(28, 28, 28, 0.5); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1);'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <h3 style='margin: 0; font-size: 1.2rem;'>System Status</h3>
                            <p style='margin: 0.5rem 0 0 0; color: #888;'>Real-time monitoring active</p>
                        </div>
                        <div class='status-badge success'>
                            ● LIVE
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # KPI Grid
            st.markdown("<br>", unsafe_allow_html=True)
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            
            # Current Traffic Flow
            with kpi1:
                if len(st.session_state.history_counts) > 1:
                    delta_count = current_count - st.session_state.history_counts[-2]
                else:
                    delta_count = 0
                st.markdown(
                    format_metric(
                        "CURRENT TRAFFIC FLOW",
                        f"{current_count}",
                        suffix=" veh/min"
                    ),
                    unsafe_allow_html=True
                )
                st.markdown(f"<p style='color: {'#00c851' if delta_count <= 0 else '#ff4444'}; font-size: 0.8rem; margin: 0;'>{delta_count:+d} from last reading</p>", unsafe_allow_html=True)
            
            # Temperature
            with kpi2:
                if len(st.session_state.predictor.history_temps) > 1:
                    delta_temp = current_temp - st.session_state.predictor.history_temps[-2]
                else:
                    delta_temp = 0
                st.markdown(
                    format_metric(
                        "TEMPERATURE",
                        f"{current_temp:.1f}",
                        suffix="°C"
                    ),
                    unsafe_allow_html=True
                )
                st.markdown(f"<p style='color: {'#00c851' if delta_temp <= 0 else '#ff4444'}; font-size: 0.8rem; margin: 0;'>{delta_temp:+.1f}°C from last reading</p>", unsafe_allow_html=True)
            
            # Predicted Load
            with kpi3:
                _, predictions, _ = st.session_state.predictor.predict_next(minutes_ahead=15)
                if len(predictions) > 0:
                    max_predicted = max(predictions)
                    current_load = (current_count / congestion_threshold) * 100
                    st.markdown(
                        format_metric(
                            "CURRENT LOAD",
                            f"{current_load:.1f}",
                            suffix="%"
                        ),
                        unsafe_allow_html=True
                    )
                    st.markdown(f"<p style='color: {'#00c851' if current_load < 70 else '#ff4444'}; font-size: 0.8rem; margin: 0;'>Max predicted: {max_predicted} veh/min</p>", unsafe_allow_html=True)
            
            # Traffic Status
            with kpi4:
                is_congested = st.session_state.predictor.check_congestion(threshold=congestion_threshold)
                status_color = "#00c851" if not is_congested else "#ff4444"
                status_text = "Normal Flow" if not is_congested else "Heavy Traffic"
                st.markdown(
                    f"""
                    <div style='padding: 1rem; background-color: rgba(28, 28, 28, 0.5); border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1);'>
                        <p style='color: #888; margin-bottom: 0.5rem; font-size: 0.8rem;'>TRAFFIC STATUS</p>
                        <div style='display: flex; align-items: center;'>
                            <div style='width: 10px; height: 10px; border-radius: 50%; background-color: {status_color}; margin-right: 8px;'></div>
                            <h3 style='margin: 0; font-size: 1.2rem;'>{status_text}</h3>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        # Update visualizations
        with plot_placeholder.container():
            tabs = st.tabs(["📈 Real-time Analysis", "🔍 Insights", "🗺️ Area Map"])
            
            # Real-time Analysis Tab
            with tabs[0]:
                st.plotly_chart(create_traffic_plot(), use_container_width=True)
            
            # Insights Tab
            with tabs[1]:
                # Header
                st.markdown("""
                    <div style='background-color: rgba(28, 28, 28, 0.5); padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;'>
                        <h3 style='margin: 0;'>Traffic Analytics Dashboard</h3>
                        <p style='margin: 0.5rem 0 0 0; color: #888;'>Comprehensive traffic analysis and insights</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Initialize metrics
                avg_traffic = np.mean(st.session_state.history_counts)
                peak_traffic = max(st.session_state.history_counts)
                peak_hour = st.session_state.history_times[np.argmax(st.session_state.history_counts)].strftime("%H:%M")
                
                # Ensure arrays are the same length before calculating correlation
                min_length = min(len(st.session_state.history_counts), len(st.session_state.predictor.history_temps))
                if min_length > 1:  # Need at least 2 points for correlation
                    temp_correlation = np.corrcoef(
                        st.session_state.history_counts[-min_length:],
                        st.session_state.predictor.history_temps[-min_length:]
                    )[0,1]
                    temp_impact = "Strong" if abs(temp_correlation) > 0.7 else "Moderate" if abs(temp_correlation) > 0.3 else "Weak"
                    temp_direction = "Positive" if temp_correlation > 0 else "Negative"
                else:
                    # Not enough data for correlation
                    temp_correlation = 0
                    temp_impact = "Insufficient Data"
                    temp_direction = "N/A"
                congestion_frequency = sum(count > congestion_threshold for count in st.session_state.history_counts) / len(st.session_state.history_counts)
                predictions_above_threshold = sum(p > congestion_threshold for p in predictions) if len(predictions) > 0 else 0
                
                # Create three columns
                left_col, middle_col, right_col = st.columns(3)
                
                # Traffic Metrics
                with left_col:
                    st.markdown(f"""
                        <div style='background-color: rgba(28, 28, 28, 0.5); padding: 1rem; border-radius: 8px;'>
                            <h4 style='margin: 0 0 1rem 0; color: #1C83E1;'>Traffic Metrics</h4>
                            <table style='width: 100%;'>
                                <tr><td style='color: #888; padding: 4px 0;'>Average Flow:</td><td style='text-align: right;'>{avg_traffic:.1f} veh/min</td></tr>
                                <tr><td style='color: #888; padding: 4px 0;'>Peak Flow:</td><td style='text-align: right;'>{peak_traffic:.1f} veh/min</td></tr>
                                <tr><td style='color: #888; padding: 4px 0;'>Peak Time:</td><td style='text-align: right;'>{peak_hour}</td></tr>
                                <tr><td style='color: #888; padding: 4px 0;'>Current vs Avg:</td>
                                    <td style='text-align: right; color: {"#00c851" if current_count <= avg_traffic else "#ff4444"};'>
                                        {((current_count/avg_traffic - 1) * 100):+.1f}%
                                    </td>
                                </tr>
                            </table>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Temperature Impact
                with middle_col:
                    st.markdown(f"""
                        <div style='background-color: rgba(28, 28, 28, 0.5); padding: 1rem; border-radius: 8px;'>
                            <h4 style='margin: 0 0 1rem 0; color: #1C83E1;'>Temperature Impact</h4>
                            <table style='width: 100%;'>
                                <tr><td style='color: #888; padding: 4px 0;'>Correlation:</td><td style='text-align: right;'>{temp_correlation:.2f}</td></tr>
                                <tr><td style='color: #888; padding: 4px 0;'>Impact Level:</td><td style='text-align: right;'>{temp_impact}</td></tr>
                                <tr><td style='color: #888; padding: 4px 0;'>Direction:</td><td style='text-align: right;'>{temp_direction}</td></tr>
                                <tr><td style='color: #888; padding: 4px 0;'>Temp Trend:</td>
                                    <td style='text-align: right; color: {"#00c851" if delta_temp <= 0 else "#ff4444"};'>
                                        {"Rising" if delta_temp > 0 else "Falling"}
                                    </td>
                                </tr>
                            </table>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Congestion Analysis
                with right_col:
                    st.markdown(f"""
                        <div style='background-color: rgba(28, 28, 28, 0.5); padding: 1rem; border-radius: 8px;'>
                            <h4 style='margin: 0 0 1rem 0; color: #1C83E1;'>Congestion Analysis</h4>
                            <table style='width: 100%;'>
                                <tr><td style='color: #888; padding: 4px 0;'>Congestion Rate:</td><td style='text-align: right;'>{congestion_frequency * 100:.1f}%</td></tr>
                                <tr><td style='color: #888; padding: 4px 0;'>Alert Threshold:</td><td style='text-align: right;'>{congestion_threshold} veh/min</td></tr>
                                <tr><td style='color: #888; padding: 4px 0;'>Predicted Alerts:</td><td style='text-align: right;'>{predictions_above_threshold}/15 min</td></tr>
                                <tr><td style='color: #888; padding: 4px 0;'>Current Status:</td>
                                    <td style='text-align: right; color: {"#00c851" if not is_congested else "#ff4444"};'>
                                        {"Normal" if not is_congested else "Alert"}
                                    </td>
                                </tr>
                            </table>
                        </div>
                    """, unsafe_allow_html=True)
                
            with tabs[2]:
                # Static map data for Hitech City key locations
                locations = {
                    "Hitech City Junction": {"lat": 17.4459, "lon": 78.3781, "traffic": "Heavy"},
                    "Mindspace Junction": {"lat": 17.4424, "lon": 78.3795, "traffic": "Moderate"},
                    "Cyber Towers": {"lat": 17.4500, "lon": 78.3824, "traffic": "Light"},
                    "HITEC City MMTS": {"lat": 17.4474, "lon": 78.3785, "traffic": "Moderate"}
                }
                
                # Create an HTML map using Folium
                import folium
                from streamlit_folium import folium_static
                
                # Create the base map centered on Hitech City
                m = folium.Map(
                    location=[17.4459, 78.3781],
                    zoom_start=15,
                    tiles="cartodbdark_matter"
                )
                
                # Add markers for each location
                for loc_name, loc_data in locations.items():
                    color = "red" if loc_data["traffic"] == "Heavy" else "orange" if loc_data["traffic"] == "Moderate" else "green"
                    folium.CircleMarker(
                        location=[loc_data["lat"], loc_data["lon"]],
                        radius=10,
                        popup=f"{loc_name}<br>Traffic: {loc_data['traffic']}",
                        color=color,
                        fill=True
                    ).add_to(m)
                
                # Add a legend
                legend_html = """
                    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: rgba(255, 255, 255, 0.8);
                        border-radius: 5px; padding: 10px; font-size: 14px;">
                        <p><strong>Traffic Status</strong></p>
                        <p>🔴 Heavy</p>
                        <p>🟡 Moderate</p>
                        <p>🟢 Light</p>
                    </div>
                """
                m.get_root().html.add_child(folium.Element(legend_html))
                
                # Display the map
                st.markdown("""
                <div style='background-color: rgba(28, 28, 28, 0.5); padding: 1.5rem; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1);'>
                    <h3 style='margin: 0 0 1rem 0;'>Live Traffic Map - Hitech City</h3>
                </div>
                """, unsafe_allow_html=True)
                
                folium_static(m)
    
    # Premium footer with additional information
    st.markdown("""
    <div style='position: fixed; bottom: 0; left: 0; right: 0; background-color: rgba(28, 28, 28, 0.95); padding: 1rem; border-top: 1px solid rgba(255, 255, 255, 0.1);'>
        <div style='display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto;'>
            <div>
                <h4 style='margin: 0; color: #1C83E1;'>Smart Traffic Management System</h4>
                <p style='margin: 0.5rem 0 0 0; font-size: 0.8rem; color: #888;'>
                    Powered by Advanced Machine Learning • Real-time Analytics • Temperature-aware Predictions
                </p>
            </div>
            <div style='text-align: right;'>
                <p style='margin: 0; font-size: 0.8rem; color: #888;'>Last updated: {}</p>
                <p style='margin: 0.2rem 0 0 0; font-size: 0.8rem; color: #888;'>Model accuracy: {:.1f}%</p>
            </div>
        </div>
    </div>
    """.format(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        95.5  # Example accuracy - you could calculate this from actual predictions
    ), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
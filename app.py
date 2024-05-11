import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import time
import os
import requests


st.title('Daily Temperature Tracker 3-Weieren')

# Function to load temperature data
def load_temperature_data():
    url = 'https://raw.githubusercontent.com/szeni23/runnerPublic/main/temperature_data.csv'
    try:
        data = pd.read_csv(url, dayfirst=True)
        data['Date'] = pd.to_datetime(data['Date'], format='%d.%m.%Y')
        # Ensure each date has only one data point, for safety
        data = data.drop_duplicates(subset='Date', keep='first')
        return data.sort_values(by='Date')
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load the temperature data
data = load_temperature_data()

# Initialize or update the last update time in session state
if 'last_update' not in st.session_state or time.time() - st.session_state['last_update'] > 300:
    st.session_state['last_update'] = time.time()
    st.rerun()

if not data.empty:
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))
    
    sns.lineplot(x='Date', y='Temp', data=data, marker='o', color='dodgerblue', label='Daily Temperature')
    plt.fill_between(data['Date'], data['Temp'] - 1, data['Temp'] + 1, color='dodgerblue', alpha=0.3)
    plt.axhline(17, color='red', lw=2, ls='--', label="Rico's comfort water temperature line")
    
    today = datetime.now().date()
    todays_data = data[data['Date'].dt.date == today]
    if not todays_data.empty:
        todays_temp = todays_data['Temp'].values[0]
        st.subheader(f"Weather in St.Gallen:")
        st.write(f"**Today's water temperature is:** {todays_temp} °C")

    else:
        st.markdown("**Today's water temperature is not available.**")

    def fetch_weather_data(api_key, city):
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric'
        }
        response = requests.get(base_url, params=params)
        return response.json()
    
    city = 'St. Gallen'
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        st.error('API key not found. Please set the OPENWEATHER_API_KEY environment variable.')
        st.stop()
        
    weather_data = fetch_weather_data(api_key, city)
    
    if 'main' in weather_data:
        st.write(f"**Temperature:** {weather_data['main']['temp']} °C")
        st.write(f"**Weather:** {weather_data['weather'][0]['description']}")
        st.write(f"**Humidity:** {weather_data['main']['humidity']}%")
        st.write(f"**Wind Speed:** {weather_data['wind']['speed']} m/s")
    else:
        if 'message' in weather_data:
            st.error(f"Error fetching weather data: {weather_data['message']}")
        else:
            st.error("Error fetching weather data. Please check your API key and the city name.")
    
    
    plt.title('Water Temperature Trend at 3-Weihern', fontsize=16)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Temperature (°C)', fontsize=14)
    plt.xticks(data['Date'], data['Date'].dt.strftime('%d %b %Y'), rotation=45)
    plt.ylim(0, 30)
    plt.legend()
    plt.tight_layout()
    
    st.pyplot(plt)

    window_size = 7  # 7-day moving average
    data['Moving Average'] = data['Temp'].rolling(window=window_size, min_periods=1).mean()

    # Set the style for plots
    sns.set_theme(style="whitegrid")
    
    # Create the Moving Average plot
    plt.figure(figsize=(12, 6))
    plt.plot(data['Date'], data['Temp'], marker='o', linestyle='', color='dodgerblue', label='Daily Temperature')
    plt.plot(data['Date'], data['Moving Average'], color='red', label=f'{window_size}-Day Moving Average')

    plt.title('Water Temperature Trend with Moving Average', fontsize=16)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Temperature (°C)', fontsize=14)
    plt.xticks(data['Date'], data['Date'].dt.strftime('%d %b %Y'), rotation=45)
    plt.ylim(0, 30)
    plt.legend()
    plt.tight_layout()
    st.pyplot(plt)

    data['Month'] = data['Date'].dt.month_name()
    data['Day'] = data['Date'].dt.day
    heat_data = data.pivot_table(index='Month', columns='Day', values='Temp', aggfunc='mean')
    
    plt.figure(figsize=(20, 6))
    sns.heatmap(heat_data, cmap='coolwarm', linewidths=.5, annot=True, fmt=".1f",
                cbar_kws={'label': 'Temperature (°C)'}, vmin=0, vmax=30)
    plt.title('Heat Map of Daily Water Temperatures by Month', fontsize=16)
    plt.xlabel('Day of Month', fontsize=14)
    plt.ylabel('Month', fontsize=14)
    plt.yticks(rotation=0)
    plt.tight_layout()
    st.pyplot(plt)

    
else:
    st.markdown("No data available to display.")


    
st.markdown(
    "For more detailed information, visit "
    "[Tagesaktuelle Öffnungszeiten und Temperaturen der Freibäder]"
    "(https://www.sport.stadt.sg.ch/news/stsg_sport/2024/05/freibaeder--tagesaktuelle-oeffnungszeiten-und-temperaturen.html)."
)

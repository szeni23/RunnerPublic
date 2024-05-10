import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import time

st.title('Daily Temperature Tracker 3-Weihern')

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
    st.experimental_rerun()

if not data.empty:
    # Set the style
    sns.set_theme(style="whitegrid")

    # Create the plot
    plt.figure(figsize=(10, 6))
    sns.lineplot(x='Date', y='Temp', data=data, marker='o', color='dodgerblue', label='Daily Temperature')
    plt.axhline(17, color='red', lw=2, ls='--', label="Rico's convenience water temp line")
    
    plt.title('Temperature Trend at 3-Weihern', fontsize=16)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Temperature (°C)', fontsize=14)
    plt.xticks(rotation=45)
    plt.ylim(0, 30)
    plt.legend()
    plt.tight_layout()
    
    st.pyplot(plt)

    # Find today's date and the corresponding temperature
    today = datetime.now().date()
    todays_data = data[data['Date'].dt.date == today]

    if not todays_data.empty:
        todays_temp = todays_data['Temp'].values[0]
        st.markdown(f"**Today's water temperature is: {todays_temp} °C**")
    else:
        st.markdown("**Today's water temperature is not available.**")

    st.markdown(
        "For more detailed information, visit "
        "[Tagesaktuelle Öffnungszeiten und Temperaturen der Freibäder]"
        "(https://www.sport.stadt.sg.ch/news/stsg_sport/2024/05/freibaeder--tagesaktuelle-oeffnungszeiten-und-temperaturen.html)."
    )
else:
    st.markdown("No data available to display.")

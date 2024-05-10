import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import time

st.title('Daily Temperature Tracker 3-Weihern')

# Set the style of seaborn
sns.set_theme(style="whitegrid")

# Function to load temperature data
def load_temperature_data():
    url = 'https://raw.githubusercontent.com/szeni23/runnerPublic/main/temperature_data.csv'
    try:
        data = pd.read_csv(url, dayfirst=True)
        data['Date'] = pd.to_datetime(data['Date'], format='%d.%m.%Y')
        data = data.sort_values(by='Date')
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load the temperature data
data = load_temperature_data()

# Initialize or update the last update time in session state
if 'last_update' not in st.session_state:
    st.session_state['last_update'] = time.time()

# Check if it's time to reload data (automatically every 300 seconds / 5 minutes)
current_time = time.time()
if current_time - st.session_state['last_update'] > 300:
    st.session_state['last_update'] = current_time
    st.experimental_rerun()

if not data.empty:
    # Plot the data using Matplotlib and Seaborn
    plt.figure(figsize=(10, 6))
    
    # Plotting the temperature trend
    sns.lineplot(x='Date', y='Temp', data=data, marker='o', color='dodgerblue', label='Daily Temperature')
    
    # Adding a horizontal line for Rico's convenience water temp line
    plt.axhline(17, color='red', lw=2, ls='--', label="Rico's convenience water temp line")
    
    # Enhancing the plot with titles, labels, and a legend
    plt.title('Temperature Trend at 3-Weihern', fontsize=16)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Temperature (°C)', fontsize=14)
    plt.xticks(rotation=45)
    plt.ylim(0, 30)
    plt.legend()
    
    # Tight layout for better spacing
    plt.tight_layout()
    
    # Display the plot
    st.pyplot(plt)

    st.markdown(
        "For more detailed information, visit "
        "[Tagesaktuelle Öffnungszeiten und Temperaturen der Freibäder]"
        "(https://www.sport.stadt.sg.ch/news/stsg_sport/2024/05/freibaeder--tagesaktuelle-oeffnungszeiten-und-temperaturen.html)."
    )
else:
    st.markdown("No data available to display.")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from datetime import datetime, timedelta
import time

st.title('Daily Temperature Tracker 3-Weihern')

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

# Button for manual data refresh
if st.button('Reload Data'):
    st.rerun()

# Initialize or update the last update time in session state
if 'last_update' not in st.session_state:
    st.session_state['last_update'] = time.time()

# Check if it's time to reload data (automatically every 300 seconds / 5 minutes)
current_time = time.time()
if current_time - st.session_state['last_update'] > 300:
    st.session_state['last_update'] = current_time
    rerun()

if not data.empty:
    # Plot the data
    fig = px.line(data, x='Date', y='Temp',
                  title='Temperature Trend',
                  labels={'Temp': 'Temperature (°C)', 'Date': 'Date'},
                  markers=True)

    fig.update_layout(
        autosize=True,
        margin=dict(l=50, r=50, t=50, b=50),
        template="plotly_white",
        yaxis=dict(range=[0, 30]),
        xaxis=dict(
            tickformat="%d %b %Y",
            dtick="D1",
            tickangle=-45,
        ),
        shapes=[
            go.layout.Shape(
                type="line",
                x0=data['Date'].min(),
                y0=17,
                x1=data['Date'].max(),
                y1=17,
                line=dict(
                    color="Red",
                    width=2,
                    dash="dot",
                ),
            )
        ]
    )

    fig.add_annotation(
        x=data['Date'].max(),
        y=17,
        text="Rico's convenience water temp line",
        showarrow=True,
        arrowhead=1,
        ax=0,
        ay=-40
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "For more detailed information, visit "
        "[Tagesaktuelle Öffnungszeiten und Temperaturen der Freibäder]"
        "(https://www.sport.stadt.sg.ch/news/stsg_sport/2024/05/freibaeder--tagesaktuelle-oeffnungszeiten-und-temperaturen.html)."
    )
else:
    st.markdown("No data available to display.")

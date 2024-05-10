import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from datetime import datetime, time, timedelta
import pytz

st.title('Daily Temperature Tracker 3-Weihern')

def load_temperature_data():
    # URL to the raw CSV file in the GitHub repository
    url = 'https://raw.githubusercontent.com/szeni23/runnerPublic/main/temperature_data.csv'
    try:
        data = pd.read_csv(url, dayfirst=True)
        data['Date'] = pd.to_datetime(data['Date'], format='%d.%m.%Y')
        # Sort the data by date to ensure the newest date is last
        data = data.sort_values(by='Date')
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

data = load_temperature_data()

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
        x=data['Date'].max(),  # Update to use the maximum (most recent) date
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

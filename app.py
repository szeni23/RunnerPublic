import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from datetime import datetime, time, timedelta
import pytz


st.title('Daily Temperature Tracker 3-Weihern ')

def is_time_to_update():
    zurich = pytz.timezone('Europe/Zurich')
    current_time = datetime.now(zurich).time()
    target_time = time(13, 20)
    return current_time >= target_time and current_time <= (datetime.combine(datetime.today(), target_time) + timedelta(minutes=1)).time()
    
@st.cache_data
def load_data():
    url = 'https://raw.githubusercontent.com/szeni23/RunnerPublic/main/temperature_data.csv'
    data = pd.read_csv(url, dayfirst=True)
    data['Date'] = pd.to_datetime(data['Date'], format='%d.%m.%Y')
    return data

data = load_data()

if st.button('Update Data Now'):
    st.experimental_rerun()

if is_time_to_update():
    st.experimental_rerun()

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
    x=data['Date'].min(),
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


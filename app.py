from __future__ import annotations

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

from data_source import DATASET_TABLE_URL, fetch_bath_data

st.set_page_config(
    page_title="St.Gallen Bäder Dashboard",
    layout="wide",
)

st.title("St.Gallen Bäder Dashboard")
st.caption(
    "Live data source: "
    f"[Bäder Aktualisierung der Webseite]({DATASET_TABLE_URL})"
)


@st.cache_data(ttl=900, show_spinner=False)
def load_data() -> pd.DataFrame:
    return fetch_bath_data()


with st.spinner("Loading latest bath data..."):
    try:
        data = load_data()
    except requests.RequestException as error:
        st.error(f"Could not load data from the city dataset API: {error}")
        st.stop()

if data.empty:
    st.warning("No data available from the source API.")
    st.stop()

all_baths = sorted(data["bath"].dropna().unique())
date_min = data["date"].min().date()
date_max = data["date"].max().date()

st.sidebar.header("Filters")
selected_baths = st.sidebar.multiselect(
    "Baths",
    options=all_baths,
    default=all_baths,
)

date_range = st.sidebar.date_input(
    "Date range",
    value=(date_min, date_max),
    min_value=date_min,
    max_value=date_max,
)

include_missing_temperatures = st.sidebar.checkbox(
    "Include rows without water temperature",
    value=False,
)

if st.sidebar.button("Refresh data"):
    st.cache_data.clear()
    st.rerun()

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
elif isinstance(date_range, list) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = date_min, date_max

if not selected_baths:
    st.info("Select at least one bath in the sidebar.")
    st.stop()

filtered = data[data["bath"].isin(selected_baths)].copy()
filtered = filtered[(filtered["date"].dt.date >= start_date) & (filtered["date"].dt.date <= end_date)]

if not include_missing_temperatures:
    filtered = filtered[filtered["water_temperature_c"].notna()]

if filtered.empty:
    st.warning("No records match your filter settings.")
    st.stop()

latest_update = filtered["updated_at"].max()
latest_update_local = latest_update.tz_convert("Europe/Zurich") if pd.notna(latest_update) else None

latest_by_bath = (
    filtered.sort_values(["bath", "date", "updated_at"], ascending=[True, False, False])
    .drop_duplicates(subset=["bath"], keep="first")
    .reset_index(drop=True)
)
latest_temps = latest_by_bath.dropna(subset=["water_temperature_c"]).copy()

if latest_temps.empty:
    warmest_label = "n/a"
    warmest_value = "-"
    mean_value = "-"
else:
    warmest_row = latest_temps.loc[latest_temps["water_temperature_c"].idxmax()]
    warmest_label = warmest_row["bath"]
    warmest_value = f"{warmest_row['water_temperature_c']:.1f} °C"
    mean_value = f"{latest_temps['water_temperature_c'].mean():.1f} °C"

metric_col1, metric_col2, metric_col3 = st.columns(3)
metric_col1.metric("Latest dataset update", latest_update_local.strftime("%Y-%m-%d %H:%M") if latest_update_local else "n/a")
metric_col2.metric("Warmest current bath", warmest_label, warmest_value)
metric_col3.metric("Average current temperature", mean_value)

st.subheader("Latest status by bath")
status_table = latest_by_bath[
    [
        "bath",
        "date",
        "water_temperature_c",
        "status",
        "opening_time",
        "closing_time",
        "bath_bus",
        "message",
        "updated_at",
    ]
].copy()

status_table = status_table.rename(
    columns={
        "bath": "Bath",
        "date": "Date",
        "water_temperature_c": "Water Temp (°C)",
        "status": "Status",
        "opening_time": "Opening",
        "closing_time": "Closing",
        "bath_bus": "Bäderbus",
        "message": "Message",
        "updated_at": "Updated",
    }
)
status_table["Date"] = status_table["Date"].dt.strftime("%Y-%m-%d")
status_table["Updated"] = status_table["Updated"].dt.tz_convert("Europe/Zurich").dt.strftime("%Y-%m-%d %H:%M")
status_table["Water Temp (°C)"] = status_table["Water Temp (°C)"].map(
    lambda value: f"{value:.1f}" if pd.notna(value) else ""
)

st.dataframe(status_table, hide_index=True, use_container_width=True)

st.subheader("Temperature trend")
chart_data = filtered.dropna(subset=["water_temperature_c"]).sort_values(["date", "bath"])

if chart_data.empty:
    st.info("No temperature values available for the selected filters.")
else:
    trend_fig = px.line(
        chart_data,
        x="date",
        y="water_temperature_c",
        color="bath",
        markers=True,
        labels={
            "date": "Date",
            "water_temperature_c": "Water Temperature (°C)",
            "bath": "Bath",
        },
    )
    trend_fig.update_layout(
        hovermode="x unified",
        legend_title_text="Bath",
        margin=dict(l=20, r=20, t=30, b=20),
    )
    st.plotly_chart(trend_fig, use_container_width=True)

if len(latest_temps) > 1:
    st.subheader("Current temperature comparison")
    comparison_fig = px.bar(
        latest_temps.sort_values("water_temperature_c", ascending=False),
        x="bath",
        y="water_temperature_c",
        color="bath",
        labels={
            "bath": "Bath",
            "water_temperature_c": "Water Temperature (°C)",
        },
    )
    comparison_fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(comparison_fig, use_container_width=True)

with st.expander("Show filtered raw data"):
    raw = filtered.sort_values(["date", "bath"])
    raw = raw.rename(
        columns={
            "record_id": "Record ID",
            "date": "Date",
            "bath": "Bath",
            "water_temperature_c": "Water Temp (°C)",
            "status": "Status",
            "opening_time": "Opening",
            "closing_time": "Closing",
            "bath_bus": "Bäderbus",
            "message": "Message",
            "updated_at": "Updated",
        }
    )
    st.dataframe(raw, hide_index=True, use_container_width=True)

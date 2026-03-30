# St.Gallen Bäder Dashboard

A Streamlit dashboard for current and historical water temperatures in St.Gallen public baths.

The app now reads directly from the official Open Data API instead of scraping HTML pages or relying on committed CSV snapshots.

## Data source

- Dataset page: <https://daten.stadt.sg.ch/explore/dataset/baeder-aktualisierung-der-webseite/table/?sort=fertigstellungszeit>
- API endpoint: <https://daten.stadt.sg.ch/api/explore/v2.1/catalog/datasets/baeder-aktualisierung-der-webseite/records>

## Features

- Live API ingestion with pagination and deduplication
- Filter by bath and date range
- Latest status table per bath
- Interactive trend and comparison charts
- Raw data view for verification

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Project layout

- `app.py`: Streamlit UI and filtering logic
- `data_source.py`: API client and data cleaning

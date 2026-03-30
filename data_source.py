from __future__ import annotations

import re
from html import unescape

import pandas as pd
import requests

DATASET_NAME = "baeder-aktualisierung-der-webseite"
DATASET_TABLE_URL = (
    "https://daten.stadt.sg.ch/explore/dataset/"
    f"{DATASET_NAME}/table/?sort=fertigstellungszeit"
)
API_URL = (
    "https://daten.stadt.sg.ch/api/explore/v2.1/catalog/datasets/"
    f"{DATASET_NAME}/records"
)
API_PAGE_SIZE = 100

_COLUMN_MAP = {
    "id": "record_id",
    "fertigstellungszeit": "updated_at",
    "datum": "date",
    "bad": "bath",
    "baederbus": "bath_bus",
    "pegelstand": "water_level",
    "wassertemperatur": "water_temperature_c",
    "badstatus": "status",
    "schliessung": "closing_time",
    "mitteilungen": "message",
    "oeffnung": "opening_time",
}


def _strip_html(value: str | None) -> str:
    if value is None:
        return ""

    text = unescape(str(value))
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _fetch_page(offset: int) -> dict:
    response = requests.get(
        API_URL,
        params={"limit": API_PAGE_SIZE, "offset": offset},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def _prepare_dataframe(raw: pd.DataFrame) -> pd.DataFrame:
    data = raw.rename(columns=_COLUMN_MAP)

    for _, target in _COLUMN_MAP.items():
        if target not in data.columns:
            data[target] = pd.NA

    data["date"] = pd.to_datetime(data["date"], errors="coerce").dt.normalize()
    data["updated_at"] = pd.to_datetime(data["updated_at"], errors="coerce", utc=True)
    data["water_temperature_c"] = pd.to_numeric(data["water_temperature_c"], errors="coerce")

    for text_col in ["bath", "status", "bath_bus", "opening_time", "closing_time"]:
        data[text_col] = data[text_col].fillna("").astype(str).str.strip()

    data["message"] = data["message"].map(_strip_html)

    # Keep only the latest update per date and bath.
    data = data.sort_values(
        by=["date", "bath", "updated_at"],
        ascending=[True, True, False],
    ).drop_duplicates(subset=["date", "bath"], keep="first")

    data = data.sort_values(by=["date", "bath"]).reset_index(drop=True)
    return data


def fetch_bath_data() -> pd.DataFrame:
    rows: list[dict] = []
    offset = 0
    total_count = None

    while total_count is None or offset < total_count:
        payload = _fetch_page(offset)
        total_count = int(payload.get("total_count", 0))
        batch = payload.get("results", [])

        if not batch:
            break

        rows.extend(batch)
        offset += API_PAGE_SIZE

    if not rows:
        return pd.DataFrame(columns=list(_COLUMN_MAP.values()))

    raw = pd.DataFrame(rows)
    return _prepare_dataframe(raw)

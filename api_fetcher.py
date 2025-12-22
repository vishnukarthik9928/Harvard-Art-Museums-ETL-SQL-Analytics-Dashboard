# api/fetcher.py

import requests
import time
import streamlit as st
from config import API_KEY, BASE_URL, PAGE_SIZE, TARGET_PER_CLASS

def fetch_objects(classification):
    objects = []
    page = 1
    progress = st.progress(0, text=f"Fetching {classification}...")

    while len(objects) < TARGET_PER_CLASS:
        params = {
            "apikey": API_KEY,
            "classification": classification,
            "size": PAGE_SIZE,
            "page": page,
            "hasimage": 1,
        }

        r = requests.get(BASE_URL, params=params)
        if r.status_code != 200:
            break

        data = r.json()
        records = data.get("records", [])
        if not records:
            break

        objects.extend(records)
        progress.progress(min(len(objects) / TARGET_PER_CLASS, 1.0))

        if not data.get("info", {}).get("next"):
            break

        page += 1
        time.sleep(0.15)

    progress.empty()
    return objects[:TARGET_PER_CLASS]

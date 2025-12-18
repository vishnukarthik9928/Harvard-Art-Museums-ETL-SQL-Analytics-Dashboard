# 🏛 Harvard Art Museums ETL & SQL Analytics Dashboard

An **end-to-end data engineering and analytics project** built using the **Harvard Art Museums API**, **MySQL/TiDB**, and **Streamlit**.

This project demonstrates how to:

- Extract large-scale cultural data from a public REST API  
- Normalize nested JSON into relational SQL tables  
- Perform advanced SQL analytics (**25+ queries**)  
- Build an interactive dashboard with safe database controls  

---

## 📌 Project Overview

The **Harvard Art Museums API** provides rich metadata for artworks across classifications such as **Paintings, Prints, Drawings, Photographs, and Sculpture**.

This application implements a complete **ETL pipeline**:

- **Extract** artifacts from the API (2,500 per classification)  
- **Transform** nested JSON into structured tables  
- **Load** data into a relational SQL database  
- **Analyze** data using classification-aware SQL queries  
- **Visualize & explore** results using Streamlit  

---

## 🧱 Tech Stack

| Layer | Technology |
|------|-----------|
| Language | Python |
| API | Harvard Art Museums API |
| Database | MySQL / TiDB |
| UI | Streamlit |
| Data Processing | Pandas |
| HTTP Client | Requests |

---

## 📂 Database Schema

### 🏺 Table 1: `artifact_metadata`
Stores descriptive and historical information.

| Column | Description |
|------|------------|
| id | Artifact ID (Primary Key) |
| title | Artifact title |
| culture | Cultural origin |
| period | Historical period |
| century | Century |
| medium | Material / medium |
| dimensions | Physical dimensions |
| description | Description |
| department | Museum department |
| classification | Paintings / Prints / Sculpture etc. |
| accessionyear | Year acquired |
| accessionmethod | Acquisition method |

---

### 🖼️ Table 2: `artifact_media`
Stores media-related details.

| Column | Description |
|------|------------|
| objectid | Artifact ID (FK) |
| imagecount | Number of images |
| mediacount | Media count |
| colorcount | Number of detected colors |
| media_rank | Ranking metric |
| datebegin | Creation start year |
| dateend | Creation end year |

---

### 🎨 Table 3: `artifact_colors`
Stores color composition.

| Column | Description |
|------|------------|
| objectid | Artifact ID (FK) |
| color | Color |
| spectrum | Spectrum |
| hue | Hue |
| percent | Coverage percentage |
| css3 | CSS color name |

---

## 🔄 ETL Pipeline

### 1️⃣ Extract
- Fetches artifacts using:
  - `classification`
  - `hasimage = 1`
- Uses pagination (`size = 100`)
- Collects **up to 2,500 records per classification**

### 2️⃣ Transform
- Handles missing and inconsistent metadata  
- Normalizes nested fields (colors, media)  
- Limits colors per artifact for performance  
- Handles sparse fields (`culture`, `period`, `century`)  

### 3️⃣ Load
- Batch inserts using `executemany`  
- Optimized commits  
- Data persists across runs  
- Duplicate-safe inserts using primary keys  

---

## 🖥️ Streamlit Dashboard Features

### 🎛 Classification Selector
Choose one of:
- Paintings
- Prints
- Drawings
- Photographs
- Sculpture  

All table views and analytics dynamically adapt to the selected classification.

---

### 📥 Data Collection
- Collects API data per classification  
- Displays a progress bar  
- Stores results in Streamlit session state  

---

### 📤 Insert into SQL
- Inserts data into:
  - `artifact_metadata`
  - `artifact_media`
  - `artifact_colors`
- Shows loading spinner  
- Uses batch inserts for performance  

---

### 📊 View SQL Tables (Filtered)
- View any of the three tables  
- Automatically filtered by selected classification  
- Adjustable row limit  

---

## 🔍 SQL Analytics (25 Queries)

### 🏺 Artifact Metadata Queries
- 11th Century Byzantine Artifacts  
- Unique Cultures  
- Archaic Period Artifacts  
- Titles by Accession Year  
- Artifacts per Department  

### 🖼️ Artifact Media Queries
- Artifacts with >1 Image  
- Average Media Rank  
- Colorcount > Mediacount  
- Artifacts from 1500–1600  
- Artifacts with No Media  

### 🎨 Artifact Colors Queries
- Distinct Hues  
- Top 5 Colors  
- Average Coverage per Hue  
- Total Color Entries  
- Colors per Artifact  

### 🔗 Join-Based Queries
- Byzantine Titles & Hues  
- Titles with Hues  
- Titles, Culture & Media Rank  
- Top 10 Grey Artifacts  
- Artifacts per Classification (Global)  

### ⭐ Bonus Queries
- Top 5 Cultures by Count  
- Average Images per Classification  
- Most Colorful Artifacts  
- Artifacts Without Colors  
- Oldest Artifacts  

---

## ⚠️ Why Some Queries Return No Results

Some queries may return empty results due to **data reality**, not errors:

- `culture`, `period`, and `century` are sparsely populated in the API  
- `hasimage = 1` filter removes artifacts without media  
- Certain cultures (e.g., Byzantine) rarely exist in some classifications (e.g., Prints)  

This behavior is **expected and correct**.

---

## 🗑️ Database Reset (Danger Zone)

A protected database reset feature is provided:

- Small **top-right “Reset DB” button**
- Double confirmation required
- Safe `TRUNCATE` order:
  1. `artifact_colors`
  2. `artifact_media`
  3. `artifact_metadata`
- Clears Streamlit session state
- Automatically reloads the UI  

This mimics **production-grade safety patterns**.

---

## 🧠 Key Design Decisions

- Persistent SQL storage (no auto-deletes)  
- Classification-filtered views instead of separate tables  
- Flexible SQL handling for inconsistent metadata  
- Explicit handling of empty results  
- Streamlit session-state management for stability  

---

## 🎤 Viva / Interview One-Liner

> *“This project implements an end-to-end ETL pipeline using a public museum API, normalizes the data into relational tables, and provides classification-aware analytics through an interactive Streamlit dashboard.”*

---

## 🚀 How to Run

```bash
pip install streamlit pandas requests mysql-connector-python
streamlit run app.py

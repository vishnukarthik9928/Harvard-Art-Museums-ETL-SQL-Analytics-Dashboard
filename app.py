import streamlit as st
import pandas as pd

from config import CLASSIFICATIONS
from tables import create_tables
from api_fetcher import fetch_objects
from services import insert_metadata, insert_media, insert_colors
from queries import queries
from connection import get_conn

# --------------------------------------------------
# UI TITLE
# --------------------------------------------------
st.title("🏛 Harvard’s Artifacts Collection")

# --------------------------------------------------
# CREATE TABLES
# --------------------------------------------------
create_tables()

# --------------------------------------------------
# SESSION STATE INITIALIZATION
# --------------------------------------------------
if "objects" not in st.session_state:
    st.session_state.objects = []

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame()

if "insert_done" not in st.session_state:
    st.session_state.insert_done = False

# --------------------------------------------------
# CLASSIFICATION SELECTION
# --------------------------------------------------
classification = st.selectbox("Select Classification", CLASSIFICATIONS)

# --------------------------------------------------
# COLLECT DATA FROM API
# --------------------------------------------------
if st.button("Collect Data"):
    objs = fetch_objects(classification)
    st.session_state.objects = objs
    st.session_state.df = pd.DataFrame(objs)
    st.session_state.insert_done = False
    st.success(f"Collected {len(objs)} records")

# --------------------------------------------------
# INSERT DATA INTO DATABASE
# --------------------------------------------------
if st.button("Insert into SQL"):
    df = st.session_state.df

    if df.empty:
        st.warning("No data to insert")
    else:
        # -------- METADATA --------
        meta_cols = [
            "id", "title", "culture", "period", "century",
            "medium", "dimensions", "description", "department",
            "classification", "accessionyear", "accessionmethod"
        ]

        for col in meta_cols:
            if col not in df.columns:
                df[col] = None

        insert_metadata(df[meta_cols])

        # -------- MEDIA --------
        df_media = pd.DataFrame({
            "objectid": df["id"],
            "imagecount": df.get("imagecount", 0),
            "mediacount": df.get("imagecount", 0),
            "colorcount": df.get("colors").apply(
                lambda x: len(x) if isinstance(x, list) else 0
            ),
            "media_rank": 0,
            "datebegin": df.get("datebegin"),
            "dateend": df.get("dateend")
        })

        insert_media(df_media)

        # -------- COLORS --------
        color_rows = []
        for obj in st.session_state.objects:
            for c in (obj.get("colors") or [])[:5]:
                color_rows.append({
                    "objectid": obj["id"],
                    "color": c.get("color"),
                    "spectrum": c.get("spectrum"),
                    "hue": c.get("hue"),
                    "percent": c.get("percent"),
                    "css3": c.get("css3"),
                })

        if color_rows:
            insert_colors(pd.DataFrame(color_rows))

        st.session_state.insert_done = True
        st.success("✅ Data inserted successfully")

# --------------------------------------------------
# VIEW SQL TABLES (FILTERED BY CLASSIFICATION)
# --------------------------------------------------
if st.session_state.insert_done:
    st.subheader("📊 View SQL Tables")

    table = st.selectbox(
        "Select Table",
        ["artifact_metadata", "artifact_media", "artifact_colors"]
    )

    limit = st.number_input("Rows", 10, 500, 50)

    if st.button("Show Table Data"):
        conn = get_conn()

        if table == "artifact_metadata":
            query = f"""
                SELECT *
                FROM artifact_metadata
                WHERE classification = %s
                LIMIT {limit}
            """
            df_view = pd.read_sql(query, conn, params=(classification,))

        elif table == "artifact_media":
            query = f"""
                SELECT m.*
                FROM artifact_media m
                JOIN artifact_metadata md ON m.objectid = md.id
                WHERE md.classification = %s
                LIMIT {limit}
            """
            df_view = pd.read_sql(query, conn, params=(classification,))

        else:  # artifact_colors
            query = f"""
                SELECT c.*
                FROM artifact_colors c
                JOIN artifact_metadata md ON c.objectid = md.id
                WHERE md.classification = %s
                LIMIT {limit}
            """
            df_view = pd.read_sql(query, conn, params=(classification,))

        conn.close()

        if df_view.empty:
            st.warning("No records found.")
        else:
            st.dataframe(df_view)

# --------------------------------------------------
# SQL ANALYTICS QUERIES
# --------------------------------------------------
st.subheader("🔍 SQL Analytics Queries")

query_name = st.selectbox("Select a query", list(queries.keys()))


if st.button("Run Query"):
    conn = get_conn()
    df_q = pd.read_sql(
        queries[query_name],
        conn,
        params={"cls": classification}
    )
    conn.close()

    if df_q.empty:
        st.warning("No results for this classification.")
    else:
        st.success(f"{len(df_q)} rows returned for {classification}")
        st.dataframe(df_q)

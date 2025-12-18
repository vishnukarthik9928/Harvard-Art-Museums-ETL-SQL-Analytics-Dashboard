import requests
import pandas as pd
import streamlit as st
import mysql.connector
import time

# ---------- CONFIG ----------
API_KEY = "0b1f2e28-e2f0-4da3-9ee5-e5ac310a8da3"
BASE_URL = "https://api.harvardartmuseums.org/object"

CLASSIFICATIONS = ["Paintings", "Prints", "Drawings", "Photographs", "Sculpture"]
TARGET_PER_CLASS = 2500
PAGE_SIZE = 100

DB_CONFIG = {
    "host": "gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
    "port": 4000,
    "user": "39yNB9h2CfXsH3f.root",
    "password": "si6tbz8owWRyvMjg",
    "database": "Harvard_art",
}

# ---------- DB HELPERS ----------
def get_conn():
    conn = mysql.connector.connect(**DB_CONFIG)
    conn.autocommit = False
    return conn


def create_tables():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS artifact_metadata (
            id INT PRIMARY KEY,
            title TEXT,
            culture TEXT,
            period TEXT,
            century TEXT,
            medium TEXT,
            dimensions TEXT,
            description TEXT,
            department TEXT,
            classification TEXT,
            accessionyear INT,
            accessionmethod TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS artifact_media (
            objectid INT,
            imagecount INT,
            mediacount INT,
            colorcount INT,
            media_rank INT,
            datebegin INT,
            dateend INT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS artifact_colors (
            objectid INT,
            color TEXT,
            spectrum TEXT,
            hue TEXT,
            percent DOUBLE,
            css3 TEXT
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


# ---------- API FETCH ----------
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


# ---------- INSERT FUNCTIONS ----------
def insert_metadata(df, batch_size=500):
    conn = get_conn()
    cur = conn.cursor()

    sql = """
        INSERT INTO artifact_metadata
        (id,title,culture,period,century,medium,dimensions,
         description,department,classification,accessionyear,accessionmethod)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            title=VALUES(title),
            culture=VALUES(culture),
            period=VALUES(period)
    """

    for i in range(0, len(df), batch_size):
        cur.executemany(sql, df.iloc[i:i+batch_size].values.tolist())

    conn.commit()
    cur.close()
    conn.close()


def insert_media(df, batch_size=500):
    conn = get_conn()
    cur = conn.cursor()

    sql = """
        INSERT INTO artifact_media
        (objectid,imagecount,mediacount,colorcount,media_rank,datebegin,dateend)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """

    for i in range(0, len(df), batch_size):
        cur.executemany(sql, df.iloc[i:i+batch_size].values.tolist())

    conn.commit()
    cur.close()
    conn.close()


def insert_colors(df, batch_size=1000):
    conn = get_conn()
    cur = conn.cursor()

    sql = """
        INSERT INTO artifact_colors
        (objectid,color,spectrum,hue,percent,css3)
        VALUES (%s,%s,%s,%s,%s,%s)
    """

    for i in range(0, len(df), batch_size):
        cur.executemany(sql, df.iloc[i:i+batch_size].values.tolist())

    conn.commit()
    cur.close()
    conn.close()


# ---------- STREAMLIT UI ----------
st.title("🏛 Harvard’s Artifacts Collection")

create_tables()

classification = st.selectbox("Select Classification", CLASSIFICATIONS)

if "objects" not in st.session_state:
    st.session_state.objects = []
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame()
if "insert_done" not in st.session_state:
    st.session_state.insert_done = False

# ---------- COLLECT ----------
if st.button("Collect Data"):
    objs = fetch_objects(classification)
    st.session_state.objects = objs
    st.session_state.df = pd.DataFrame(objs)
    st.session_state.insert_done = False
    st.success(f"Collected {len(objs)} records")

# ---------- INSERT ----------
if st.button("Insert into SQL"):
    df = st.session_state.df
    if df.empty:
        st.warning("No data to insert")
    else:
        with st.spinner("⏳ Inserting data into SQL tables..."):
            if "department" not in df.columns and "division" in df.columns:
                df["department"] = df["division"]

            meta_cols = [
                "id","title","culture","period","century",
                "medium","dimensions","description","department",
                "classification","accessionyear","accessionmethod"
            ]
            for c in meta_cols:
                if c not in df.columns:
                    df[c] = None

            insert_metadata(df[meta_cols])

            df_media = pd.DataFrame({
                "objectid": df["id"],
                "imagecount": df.get("imagecount", 0),
                "mediacount": df.get("imagecount", 0),
                "colorcount": df.get("colors").apply(
                    lambda x: len(x) if isinstance(x, list) else 0),
                "media_rank": 0,
                "datebegin": df.get("datebegin"),
                "dateend": df.get("dateend")
            })

            insert_media(df_media)

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

# ---------- VIEW SQL TABLES (FILTERED BY CLASSIFICATION) ----------
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
        st.dataframe(df_view)
# ================= SQL ANALYTICS  =================
st.subheader("🔍 SQL Analytics Queries")

queries = {
    # ===== artifact_metadata =====
    "1)11th Century Byzantine Artifacts":
        """SELECT *
           FROM artifact_metadata
           WHERE century = '11th century'
             AND culture = 'Byzantine'
             AND classification = %(cls)s;""",

    "2)Unique Cultures":
        """SELECT DISTINCT culture
           FROM artifact_metadata
           WHERE culture IS NOT NULL
             AND classification = %(cls)s;""",

    "3)Archaic Period Artifacts":
        """SELECT *
           FROM artifact_metadata
           WHERE (period = 'Archaic Period' or period ='Archaic')
             AND classification = %(cls)s;""",

    "4)Titles by Accession Year":
        """SELECT title, accessionyear
           FROM artifact_metadata
           WHERE classification = %(cls)s
           ORDER BY accessionyear DESC;""",

    "5)Artifacts per Department":
        """SELECT department, COUNT(*) AS artifact_count
           FROM artifact_metadata
           WHERE classification = %(cls)s
           GROUP BY department;""",

    # ===== artifact_media =====
    "6)Artifacts with >1 Image":
        """SELECT m.*
           FROM artifact_media m
           JOIN artifact_metadata md ON m.objectid = md.id
           WHERE m.imagecount > 1
             AND md.classification = %(cls)s;""",

    "7)Average Media Rank":
        """SELECT AVG(m.media_rank) AS avg_rank
           FROM artifact_media m
           JOIN artifact_metadata md ON m.objectid = md.id
           WHERE md.classification = %(cls)s;""",

    "8)Colorcount > Mediacount":
        """SELECT m.*
           FROM artifact_media m
           JOIN artifact_metadata md ON m.objectid = md.id
           WHERE m.colorcount > m.mediacount
             AND md.classification = %(cls)s;""",

    "9)Artifacts (1500–1600)":
        """SELECT m.*
           FROM artifact_media m
           JOIN artifact_metadata md ON m.objectid = md.id
           WHERE m.datebegin >= 1500
             AND m.dateend <= 1600
             AND md.classification = %(cls)s;""",

    "10)Artifacts with No Media":
        """SELECT m.*
           FROM artifact_media m
           JOIN artifact_metadata md ON m.objectid = md.id
           WHERE (m.mediacount = 0 OR m.mediacount IS NULL)
             AND md.classification = %(cls)s;""",

    # ===== artifact_colors =====
    "11)Distinct Hues":
        """SELECT DISTINCT c.hue
           FROM artifact_colors c
           JOIN artifact_metadata md ON c.objectid = md.id
           WHERE c.hue IS NOT NULL
             AND md.classification = %(cls)s;""",

    "12)Top 5 Colors":
        """SELECT c.color, COUNT(*) AS frequency
           FROM artifact_colors c
           JOIN artifact_metadata md ON c.objectid = md.id
           WHERE md.classification = %(cls)s
           GROUP BY c.color
           ORDER BY frequency DESC
           LIMIT 5;""",

    "13)Average Coverage per Hue":
        """SELECT c.hue, AVG(c.percent) AS avg_coverage
           FROM artifact_colors c
           JOIN artifact_metadata md ON c.objectid = md.id
           WHERE md.classification = %(cls)s
           GROUP BY c.hue;""",

    "14)Total Color Entries":
        """SELECT COUNT(*) AS total_colors
           FROM artifact_colors c
           JOIN artifact_metadata md ON c.objectid = md.id
           WHERE md.classification = %(cls)s;""",

    "15)Colors for Each Artifact":
        """SELECT md.title, c.color, c.hue
           FROM artifact_metadata md
           JOIN artifact_colors c ON md.id = c.objectid
           WHERE md.classification = %(cls)s;""",

    # ===== JOIN-BASED QUERIES =====
    "16)Byzantine Titles & Hues":
        """SELECT md.title, c.hue
           FROM artifact_metadata md
           JOIN artifact_colors c ON md.id = c.objectid
           WHERE md.culture = 'Byzantine'
             AND md.classification = %(cls)s;""",

    "17)Titles with Hues":
        """SELECT md.title, c.hue
           FROM artifact_metadata md
           JOIN artifact_colors c ON md.id = c.objectid
           WHERE md.classification = %(cls)s;""",

    "18)Titles, Culture & Media Rank":
        """SELECT md.title, md.culture, m.media_rank
           FROM artifact_metadata md
           JOIN artifact_media m ON md.id = m.objectid
           WHERE md.period IS NOT NULL
             AND md.classification = %(cls)s;""",

    "19)Top 10 Grey Artifacts":
        """SELECT DISTINCT md.title, m.media_rank
           FROM artifact_metadata md
           JOIN artifact_media m ON md.id = m.objectid
           JOIN artifact_colors c ON md.id = c.objectid
           WHERE c.hue = 'Grey'
             AND md.classification = %(cls)s
           ORDER BY m.media_rank DESC
           LIMIT 10;""",

    "20)Artifacts per Classification (Global)":
        """SELECT md.classification,
                  COUNT(*) AS artifact_count,
                  AVG(m.mediacount) AS avg_media_count
           FROM artifact_metadata md
           JOIN artifact_media m ON md.id = m.objectid
           GROUP BY md.classification;""",

    # ===== EXTRA (BONUS – MORE MARKS) =====
    "21)Top 5 Cultures by Count":
        """SELECT culture, COUNT(*) AS cnt
           FROM artifact_metadata
           WHERE classification = %(cls)s
           GROUP BY culture
           ORDER BY cnt DESC
           LIMIT 5;""",

    "22)Average Images per Classification (Global)":
        """SELECT md.classification, AVG(m.imagecount) AS avg_images
           FROM artifact_metadata md
           JOIN artifact_media m ON md.id = m.objectid
           GROUP BY md.classification;""",

    "23)Most Colorful Artifacts":
        """SELECT m.objectid, m.colorcount
           FROM artifact_media m
           JOIN artifact_metadata md ON m.objectid = md.id
           WHERE md.classification = %(cls)s
           ORDER BY m.colorcount DESC
           LIMIT 10;""",

    "24)Artifacts Without Colors":
        """SELECT m.*
           FROM artifact_media m
           JOIN artifact_metadata md ON m.objectid = md.id
           WHERE m.colorcount = 0
             AND md.classification = %(cls)s;""",

    "25)Oldest Artifacts":
        """SELECT m.*
           FROM artifact_media m
           JOIN artifact_metadata md ON m.objectid = md.id
           WHERE md.classification = %(cls)s
           ORDER BY m.datebegin ASC
           LIMIT 10;"""
}

query_name = st.selectbox("Select a query", list(queries.keys()))

if st.button("Run Query"):
    conn = get_conn()
    df_q = pd.read_sql(queries[query_name], conn, params={"cls": classification})
    conn.close()

    if df_q.empty:
        st.warning("No results for this classification.")
    else:
        st.success(f"{len(df_q)} rows returned for {classification}")
        st.dataframe(df_q)
# ================= RESET DATABASE (TOP-RIGHT MINI BUTTON) =================

col_left, col_right = st.columns([9, 1])

# Initialize state
if "show_reset_confirm" not in st.session_state:
    st.session_state.show_reset_confirm = False

with col_right:
    if st.button("🗑️ Reset DB", key="reset_db_btn"):
        st.session_state.show_reset_confirm = True

# Confirmation UI
if st.session_state.show_reset_confirm:
    with st.expander("⚠️ Confirm Database Reset", expanded=True):
        st.warning(
            "This action will permanently delete ALL data from:\n"
            "- artifact_metadata\n"
            "- artifact_media\n"
            "- artifact_colors\n\n"
            "**This cannot be undone.**"
        )

        confirm_reset = st.checkbox(
            "I understand this will permanently delete all data",
            key="confirm_reset_checkbox"
        )

        if confirm_reset:
            if st.button("🔥 CONFIRM & TRUNCATE", key="confirm_truncate_btn"):
                with st.spinner("Resetting database..."):
                    conn = get_conn()
                    cur = conn.cursor()

                    try:
                        # Child → Parent order
                        cur.execute("TRUNCATE TABLE artifact_colors;")
                        cur.execute("TRUNCATE TABLE artifact_media;")
                        cur.execute("TRUNCATE TABLE artifact_metadata;")
                        conn.commit()

                        # Clear ALL Streamlit state
                        st.session_state.clear()

                        st.success("✅ Database reset successfully.")

                        # Force UI refresh
                        st.rerun()

                    except Exception as e:
                        conn.rollback()
                        st.error(f"❌ Error while truncating tables: {e}")

                    finally:
                        cur.close()
                        conn.close()

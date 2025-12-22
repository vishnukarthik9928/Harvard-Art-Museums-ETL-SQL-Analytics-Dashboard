# services/db_inserts.py

from connection import get_conn

# --------------------------------------------------
# Insert ARTIFACT METADATA
# --------------------------------------------------
def insert_metadata(df, batch_size=500):
    conn = get_conn()
    cur = conn.cursor()

    sql = """
        INSERT INTO artifact_metadata
        (id, title, culture, period, century, medium, dimensions,
         description, department, classification, accessionyear, accessionmethod)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            title = VALUES(title),
            culture = VALUES(culture),
            period = VALUES(period)
    """

    for i in range(0, len(df), batch_size):
        cur.executemany(
            sql,
            df.iloc[i:i + batch_size].values.tolist()
        )

    conn.commit()
    cur.close()
    conn.close()


# --------------------------------------------------
# Insert ARTIFACT MEDIA
# --------------------------------------------------
def insert_media(df, batch_size=500):
    conn = get_conn()
    cur = conn.cursor()

    sql = """
        INSERT INTO artifact_media
        (objectid, imagecount, mediacount, colorcount,
         media_rank, datebegin, dateend)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """

    for i in range(0, len(df), batch_size):
        cur.executemany(
            sql,
            df.iloc[i:i + batch_size].values.tolist()
        )

    conn.commit()
    cur.close()
    conn.close()


# --------------------------------------------------
# Insert ARTIFACT COLORS
# --------------------------------------------------
def insert_colors(df, batch_size=1000):
    conn = get_conn()
    cur = conn.cursor()

    sql = """
        INSERT INTO artifact_colors
        (objectid, color, spectrum, hue, percent, css3)
        VALUES (%s,%s,%s,%s,%s,%s)
    """

    for i in range(0, len(df), batch_size):
        cur.executemany(
            sql,
            df.iloc[i:i + batch_size].values.tolist()
        )

    conn.commit()
    cur.close()
    conn.close()

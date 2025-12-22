from connection import get_conn

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

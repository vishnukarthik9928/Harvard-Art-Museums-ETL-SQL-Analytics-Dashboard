

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


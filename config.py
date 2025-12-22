# config.py

API_KEY = "0b1f2e28-e2f0-4da3-9ee5-e5ac310a8da3"
BASE_URL = "https://api.harvardartmuseums.org/object"

CLASSIFICATIONS = [
    "Paintings", "Prints", "Drawings", "Photographs", "Sculpture"
]

TARGET_PER_CLASS = 2500
PAGE_SIZE = 100

DB_CONFIG = {
    "host": "gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
    "port": 4000,
    "user": "39yNB9h2CfXsH3f.root",
    "password": "si6tbz8owWRyvMjg",
    "database": "Harvard_art",
}

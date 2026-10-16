import os
import sys
import time

import duckdb
import requests

BASE_URL = "https://search.dip.bundestag.de/api/v1/"
ENDPOINT = "plenarprotokoll-text"
API_KEY = os.environ.get("DIP_API_KEY", "R2BZaee.DjdCyihKZMf8AOjtScubP2EVydegzjmBIQ")
DB_PATH = "data/database.duckdb"

def fetch_page(params):
    for attempt in range(5):
        response = requests.get(BASE_URL + ENDPOINT, params=params, timeout=60)
        if response.status_code in (429, 500, 502, 503, 504):
            time.sleep(2 ** attempt)
            continue
        response.raise_for_status()
        return response.json()
    response.raise_for_status()


def main():
    params = {"apikey": API_KEY}
    con = duckdb.connect(DB_PATH)
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    con.execute("CREATE SCHEMA IF NOT EXISTS cur")
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw.protokolle (
            id VARCHAR PRIMARY KEY,
            dokument_art VARCHAR, typ VARCHAR, wahlperiode VARCHAR,
            text VARCHAR, titel VARCHAR, date TIMESTAMP
        )""")
    con.execute("CREATE TABLE IF NOT EXISTS fetch_state (cursor VARCHAR)")
    row = con.execute("SELECT cursor FROM fetch_state").fetchone()
    cursor = row[0] if row else ""

    done = False
    while not done:
        if cursor:
            params["cursor"] = cursor
        d = fetch_page(params)

        rows = [
            (x.get("id"), x.get("dokumentart"), x.get("typ"), x.get("wahlperiode"),
             x.get("text"), x.get("titel"), x.get("datum"))
            for x in d.get("documents", [])
        ]
        new_cursor = d.get("cursor", cursor)
        done = new_cursor == cursor
        cursor = new_cursor

        con.begin()
        if rows:
            con.executemany("INSERT OR IGNORE INTO raw.protokolle VALUES (?,?,?,?,?,?,?)", rows)
        con.execute("DELETE FROM fetch_state")
        con.execute("INSERT INTO fetch_state VALUES (?)", [cursor])
        con.commit()

        n = con.execute("SELECT count(*) FROM raw.protokolle").fetchone()[0]
        print(f"{n} documents in table", flush=True)

    con.execute("DELETE FROM fetch_state")  # success: clear resume state
    con.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\ninterrupted; rerun to resume from the saved cursor", file=sys.stderr)
        sys.exit(130)
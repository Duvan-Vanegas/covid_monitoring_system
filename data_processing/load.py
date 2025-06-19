"""Loading transformed data into a SQLite database."""

import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text

# Directories
DB_PATH = "data/covid.db"
PROCESSED_DIR = "data/processed"


def create_connection(db_path):
    """
    Creates a connection to the SQLite database using SQLAlchemy and sqlite3.
    """
    engine = create_engine(f"sqlite:///{db_path}")
    raw_conn = sqlite3.connect(db_path)
    return engine, raw_conn


def create_tables(engine):
    """
    Creates the current_data and historical_data tables if they do not exist.
    """
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS current_data (
                country VARCHAR(50) PRIMARY KEY,
                cases INTEGER,
                active INTEGER,
                deaths INTEGER,
                recovered INTEGER,
                updated TIMESTAMP,
                lat REAL,
                long REAL
            );
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS historical_data (
                date DATE,
                country VARCHAR(50),
                cases INTEGER,
                deaths INTEGER,
                PRIMARY KEY (date, country)
            );
        """))


def load_data_to_db(raw_conn):
    """
    Loads transformed CSV files and inserts into the SQLite DB.
    """
    cursor = raw_conn.cursor()

    # Load current_data from CSV
    df_current = pd.read_csv(os.path.join(
        PROCESSED_DIR, "current_data.csv"), parse_dates=["updated"])
    for _, row in df_current.iterrows():
        updated_str = pd.to_datetime(row["updated"]).isoformat()

        cursor.execute("SELECT updated FROM current_data WHERE country = ?", (row["country"],))
        existing = cursor.fetchone()
        if existing is None or pd.to_datetime(updated_str) > pd.to_datetime(existing[0]):
            cursor.execute("""
                INSERT OR REPLACE INTO current_data 
                (country, cases, active, deaths, recovered, updated, lat, long)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["country"],
                row["cases"],
                row["active"],
                row["deaths"],
                row["recovered"],
                updated_str,
                row["lat"],
                row["long"]
            ))

    # Load historical_data from CSV
    df_historical = pd.read_csv(os.path.join(
        PROCESSED_DIR, "historical_data.csv"), parse_dates=["date"])
    for _, row in df_historical.iterrows():
        date_str = pd.to_datetime(row["date"]).date().isoformat()

        cursor.execute("""
            SELECT 1 FROM historical_data WHERE date = ? AND country = ?
        """, (date_str, row["country"]))
        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO historical_data (date, country, cases, deaths)
                VALUES (?, ?, ?, ?)
            """, (date_str, row["country"], row["cases"], row["deaths"]))

    raw_conn.commit()
    print("Datos insertados correctamente en SQLite.")


def run():
    """
    Runs the full load process: connection, table creation, data loading.
    """
    os.makedirs("data", exist_ok=True)

    print("Conectando a la base de datos...")
    engine, raw_conn = create_connection(DB_PATH)

    print("Creando tablas si no existen...")
    create_tables(engine)

    print("Cargando archivos procesados en la base de datos...")
    load_data_to_db(raw_conn)

    raw_conn.close()
    print("Carga completada!")

if __name__ == "__main__":
    run()

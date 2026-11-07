
import os
import pandas as pd

from sqlalchemy import create_engine, text, URL

# ----------------------------------
# 1. DATABASE CONNECTION
# ----------------------------------

db_url = URL.create(
    drivername="postgresql+psycopg",
    username="postgres",
    password=2110
    host="localhost",
    port=5432,
    database="distasense"
)

engine = create_engine(db_url)

# ----------------------------------
# 2. FILE PATH
# ----------------------------------

PROCESSED_FILE = "Data/Processed/data.csv"

# ----------------------------------
# 3. DATABASE INSERT FUNCTION
# ----------------------------------

def store_sensor_readings():

    try:
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        print("PostgreSQL connected successfully!")

        # Read processed CSV
        df = pd.read_csv(PROCESSED_FILE)

        if df.empty:
            print("No sensor readings available.")
            return

        # Validate columns
        required_columns = [
            "Timestamp",
            "Distance_cm",
            "Distance_Change_cm"
        ]

        if not all(col in df.columns for col in required_columns):
            raise ValueError("Required CSV columns are missing.")

        # Convert data types
        df["Timestamp"] = pd.to_datetime(
            df["Timestamp"], errors="coerce"
        )

        df["Distance_cm"] = pd.to_numeric(
            df["Distance_cm"], errors="coerce"
        )

        df["Distance_Change_cm"] = pd.to_numeric(
            df["Distance_Change_cm"], errors="coerce"
        )

        # Remove invalid rows
        df.dropna(
            subset=required_columns,
            inplace=True
        )

        # Remove duplicate timestamps in current CSV
        df.drop_duplicates(
            subset=["Timestamp"],
            keep="last",
            inplace=True
        )

        # Prepare records
        records = []

        for row in df.itertuples(index=False):
            records.append({
                "timestamp": row.Timestamp.to_pydatetime(),
                "distance_cm": float(row.Distance_cm),
                "distance_change_cm": float(
                    row.Distance_Change_cm
                )
            })

        if not records:
            print("No valid readings to insert.")
            return

        # Insert only new records
        insert_query = text("""
            INSERT INTO sensor_readings
            (timestamp, distance_cm, distance_change_cm)
            VALUES
            (:timestamp, :distance_cm, :distance_change_cm)
            ON CONFLICT (timestamp) DO NOTHING
        """)

        with engine.begin() as conn:
            result = conn.execute(insert_query, records)

        inserted = result.rowcount
        skipped = len(records) - inserted

        print("--------------------------------")
        print("SENSOR DATABASE UPDATE")
        print("--------------------------------")
        print("Processed records:", len(records))
        print("New records inserted:", inserted)
        print("Existing records skipped:", skipped)
        print("Database storage completed!")
        print("--------------------------------")

    except Exception as e:
        print("Database operation failed:", e)


# ----------------------------------
# 4. EXECUTION
# ----------------------------------

if __name__ == "__main__":
    store_sensor_readings()

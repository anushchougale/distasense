# Distance Monitoring Dashboard

Streamlit dashboard for the PostgreSQL database `distasense` and table `sensor_readings`.

## Expected PostgreSQL columns

- `id`
- `timestamp`
- `distance_cm`
- `distance_change_cm`

## Install

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configure PostgreSQL password (PowerShell)

```powershell
$env:DB_PASSWORD="your_postgres_password"
```

Optional environment variables:

```powershell
$env:DB_USER="postgres"
$env:DB_HOST="localhost"
$env:DB_PORT="5432"
$env:DB_NAME="distasense"
```

## Run

From the project root:

```powershell
streamlit run Dashboard/app.py
```

The dashboard reads from PostgreSQL only. It does not collect sensor readings or insert rows.
Your existing workflow remains responsible for:
1. Collecting live sensor readings into `Data/Raw/distance_readings.csv`
2. Running `Processing/process.py` to create `Data/Processed/data.csv`
3. Running your database synchronization script to insert new rows into PostgreSQL

The dashboard refreshes its displayed database data every 5 seconds when Auto-refresh is enabled.
This does not make the sensor-to-database pipeline automatic; the collection, processing, and database sync scripts must still run.

## Important

The dashboard assumes the table already exists and the timestamp column is unique as configured for `ON CONFLICT (timestamp) DO NOTHING` in your database sync script.

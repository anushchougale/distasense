
import serial
import time
import csv
import os
import re
from datetime import datetime

collection_interval = 1 # seconds same with the ESP32 code as write in delay().

# ESP32 Configuration
SERIAL_PORT = "COM13"
BAUD_RATE = 115200

# Dataset location
Dataset = os.path.join("Data", "Raw")
os.makedirs(Dataset, exist_ok=True)

csv_file = os.path.join(Dataset, "distance_readings.csv")

def create_csv():
    if not os.path.exists(csv_file):
        with open(csv_file, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "Timestamp",
                "Distance_cm"
            ])

def collect_data():
    create_csv()

    print("=" * 45)
    print("       DISTASENSE AI - DATA COLLECTION")
    print("=" * 45)

    esp32 = None

    try:
        esp32 = serial.Serial(
            SERIAL_PORT,
            BAUD_RATE,
            timeout=2
        )

        time.sleep(2)

        print(f"Connected to ESP32 on {SERIAL_PORT}")
        print("Collecting distance readings...")
        print("Press CTRL+C to stop.\n")

        # Get the existing number of records
        with open(csv_file, "r", newline="") as file:
            count = sum(1 for row in csv.reader(file)) - 1
        print(f"Last saved record number: {count}\n")

        with open(csv_file, "a", newline="") as file:
            writer = csv.writer(file)

            while True:
                line = esp32.readline().decode(
                    "utf-8", errors="ignore"
                ).strip()

                if not line:
                    continue

                match = re.search(
                    r"Distance\s*:\s*(-?\d+(?:\.\d+)?)",
                    line,
                    re.IGNORECASE
                )

                if match:
                    distance = float(match.group(1))

                    if distance <= 0 or distance > 400:
                        print("Invalid reading:", distance)
                        continue

                    timestamp = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                    writer.writerow([timestamp, distance])
                    file.flush()

                    count += 1

                    print(
                        f"{timestamp} | "
                        f"Distance: {distance:.2f} cm | "
                        f"Records: {count}"
                    )

                    time.sleep(collection_interval)

    except serial.SerialException as error:
        print("Serial connection error:", error)

    except KeyboardInterrupt:
        print("\nData collection stopped.")

    finally:
        if esp32 is not None and esp32.is_open:
            esp32.close()
            print("ESP32 connection closed.")

if __name__ == "__main__":
    collect_data()

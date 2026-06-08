import sqlite3
import polars as pl
from datetime import datetime, timedelta

DB_PATH = "data/weather.db"

# ВСЕ города из задания
CITIES = {
    "Bangkok": (13.7563, 100.5018),
    "Beijing": (39.9042, 116.4074),
    "Berlin": (52.5200, 13.4050),
    "Cairo": (30.0444, 31.2357),
    "Cape Town": (-33.9249, 18.4241),
    "Dubai": (25.276987, 55.296249),
    "Istanbul": (41.0082, 28.9784),
    "London": (51.5074, -0.1278),
    "Los Angeles": (34.0522, -118.2437),
    "Madrid": (40.4168, -3.7038),
    "Moscow": (55.7558, 37.6173),
    "New York": (40.7128, -74.0060),
    "Paris": (48.8566, 2.3522),
    "Rio de Janeiro": (-22.9068, -43.1729),
    "Rome": (41.9028, 12.4964),
    "Seoul": (37.5665, 126.9780),
    "Singapore": (1.3521, 103.8198),
    "Sydney": (-33.8688, 151.2093),
    "Tokyo": (35.6895, 139.6917),
    "Toronto": (43.6532, -79.3832),
}

def generate_test_data():
    print("Generating test weather data for all cities...")
    all_data = []
    for city in CITIES.keys():
        for i in range(14):  # 14 дней данных
            date = datetime.now().date() + timedelta(days=i - 7)
            all_data.append({
                "city": city,
                "date": date,
                "avg_temp": 15 + (hash(city) % 20) + i % 10,
                "total_precip": (hash(city) % 5) + i * 0.3,
                "avg_wind": 5 + (hash(city) % 10),
                "is_rainy": 1 if i % 3 == 0 else 0
            })
    df = pl.DataFrame(all_data)
    conn = sqlite3.connect(DB_PATH)
    df.to_pandas().to_sql("weather", conn, if_exists="replace", index=False)
    conn.close()
    print(f"✅ Test data saved: {len(df)} rows for {len(CITIES)} cities")

def fetch_forecast():
    generate_test_data()

def fetch_historical():
    generate_test_data()

if __name__ == "__main__":
    generate_test_data()
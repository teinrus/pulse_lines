import aiofiles

import os
import json
from datetime import datetime

import asyncpg
import asyncio


# ----------- Асинхронное сохранение в JSON -----------

async def save_runtime_to_json(sensor_name: str, minutes: int, folder: str = "data"):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{sensor_name}_runtime.json")
    data = {
        "sensor": sensor_name,
        "runtime_minutes": minutes,
        "updated_at": datetime.now().isoformat()
    }
    async with aiofiles.open(path, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(data, indent=4, ensure_ascii=False))


async def load_runtime_from_json(sensor_name: str, folder: str = "data") -> float:
    path = os.path.join(folder, f"{sensor_name}_runtime.json")
    if not os.path.exists(path):
        return 0.0
    async with aiofiles.open(path, 'r', encoding='utf-8') as f:
        content = await f.read()
        data = json.loads(content)
        return float(data.get("runtime_minutes", 0.0))
    


# ----------- Подключение к PostgreSQL -----------
DB_CONFIG = {
    "user": "postgres",
    "password": "12345",
    "database": "temruk",
    "host": "192.168.88.232",
    "port": 5432
}

# ----------- Загрузка наработки -----------




async def load_runtime_from_db(sensor_name: str, retry_delay: int = 5) -> float:
    """
    Загружает наработку из БД с повторами до получения данных.
    """
    while True:
        try:
            conn = await asyncpg.connect(**DB_CONFIG)
            try:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS temruk_sensorruntime (
                        sensor TEXT PRIMARY KEY,
                        runtime_minutes REAL,
                        updated_at TIMESTAMP
                    )
                """)
                row = await conn.fetchrow(
                    "SELECT runtime_minutes FROM temruk_sensorruntime WHERE sensor = $1",
                    sensor_name
                )
                if row:
                    return float(row["runtime_minutes"])
                else:
                    print(f"⏳ [{sensor_name}] Данные не найдены, повтор через {retry_delay} сек...")
            finally:
                await conn.close()

        except Exception as e:
            print(f"❗ Ошибка подключения к БД для {sensor_name}: {e}")

        await asyncio.sleep(retry_delay)


# ----------- Сохранение наработки -----------
async def save_runtime_to_db(sensor_name: str, minutes: float):
    conn = await asyncpg.connect(**DB_CONFIG)
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS temruk_sensorruntime (
                sensor TEXT PRIMARY KEY,
                runtime_minutes REAL,
                updated_at TIMESTAMP
            )
        """)
        await conn.execute("""
            INSERT INTO temruk_sensorruntime (sensor, runtime_minutes, updated_at)
            VALUES ($1, $2, $3)
            ON CONFLICT (sensor) DO UPDATE SET
                runtime_minutes = EXCLUDED.runtime_minutes,
                updated_at = EXCLUDED.updated_at
        """, sensor_name, minutes, datetime.now())
    finally:
        await conn.close()

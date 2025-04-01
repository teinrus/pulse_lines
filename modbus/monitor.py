import asyncio
from datetime import datetime
from modbus.client import check_sensor_bit_async
from utils.storage import save_runtime_to_json, save_runtime_to_db,load_runtime_from_db

async def monitor_runtime_async(
    params: dict,
    interval: int = 60,
    total_minutes: int = 0,
    sensor_name: str = "Датчик"
):
    """
    Асинхронный мониторинг времени работы датчика по Modbus.

    :param params: Параметры для check_sensor_bit (host, port, и т.д.)
    :param interval: Интервал опроса в секундах
    :param minutes: Время итервала
    :param sensor_name: Название/идентификатор датчика
    """
    print(f"▶️ [{sensor_name}] Запущен мониторинг...")
    try:
        while True:
            state = await check_sensor_bit_async(**params)
            if state == 1:
                print(sensor_name,state)
                total_minutes = await load_runtime_from_db(sensor_name)
                if not total_minutes:
                    return False
                await save_runtime_to_json(sensor_name, total_minutes+1)
                await save_runtime_to_db(sensor_name, total_minutes+1)
            elif state == 0:
                print(f"[{datetime.now()}] ⏸ [{sensor_name}] не активен.")
            else:
                print(f"[{datetime.now()}] ❌ [{sensor_name}] ошибка чтения.")
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        print(f"🛑 [{sensor_name}] Мониторинг остановлен")
        return total_minutes

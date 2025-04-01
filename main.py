import asyncio
from modbus.monitor import monitor_runtime_async
import config

async def main():
    # Список параметров для разных датчиков
    sensors = [
        {
            "name": "Линия 2",
            "params": {
                "host": config.MODBUS_HOST,
                "port": config.MODBUS_PORT,
                "register_address": 4,
                "unit_id": 1,
                "bit_number": 3,
                "register_type": "input"
            }
        },
        {
            "name": "Линия 3",
            "params": {
                "host": config.MODBUS_HOST,
                "port": config.MODBUS_PORT,
                "register_address": 4,
                "unit_id": 1,
                "bit_number": 2,
                "register_type": "input"
            }
        },
        {
            "name": "Линия 4",
            "params": {
                "host": config.MODBUS_HOST,
                "port": config.MODBUS_PORT,
                "register_address": 4,
                "unit_id": 1,
                "bit_number": 1,
                "register_type": "input"
            }
        },
        {
            "name": "Линия 5",
            "params": {
                "host": config.MODBUS_HOST,
                "port": config.MODBUS_PORT,
                "register_address": 4,
                "unit_id": 1,
                "bit_number": 0,
                "register_type": "input"
            }
        }
    ]

    # Создаём асинхронные задачи для каждого датчика
    tasks = [
        monitor_runtime_async(sensor["params"], interval=60,  sensor_name=sensor["name"])
        for sensor in sensors
    ]

    # Запускаем все задачи параллельно
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Остановка мониторинга по Ctrl+C")

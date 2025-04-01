from pymodbus.client import AsyncModbusTcpClient

async def check_sensor_bit_async(
    host: str,
    port: int,
    register_address: int,
    unit_id: int,
    bit_number: int,
    register_type: str = "input"
) -> int | None:
    client = AsyncModbusTcpClient(host=host, port=port)

    if client is None:
        print(f"❌ Не удалось создать клиента для {host}:{port}")
        return None

    try:
        await client.connect()
        if register_type == "input":
            result = await client.read_input_registers(address=register_address, count=1, slave=unit_id)
        else:
            result = await client.read_holding_registers(address=register_address, count=1, slave=unit_id)

        if not result.isError():
            value = result.registers[0]
            return (value >> bit_number) & 1
        else:
            print(f"⚠️ Ошибка чтения регистра с устройства {host}")
            return None
    except Exception as e:
        print(f"❗ Ошибка в Modbus-клиенте {host}: {e}")
        return None
    finally:
        if client:
            try:
                await client.close()
            except Exception:
                pass

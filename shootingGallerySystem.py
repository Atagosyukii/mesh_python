import asyncio
from bleak import BleakClient, discover
from struct import pack

# UUID
CORE_INDICATE_UUID = ('72c90005-57a9-4d40-b746-534e22ec9f9e')
CORE_NOTIFY_UUID = ('72c90003-57a9-4d40-b746-534e22ec9f9e')
CORE_WRITE_UUID = ('72c90004-57a9-4d40-b746-534e22ec9f9e')

# Constant values
MESSAGE_TYPE_INDEX = 0
EVENT_TYPE_INDEX = 1
STATE_INDEX = 2
MESSAGE_TYPE_ID = 1
EVENT_TYPE_ID = 3

# Callback
# 動きブロックから通知を受け取り、なんかするメソッド
async def on_receive_notify(_, data: bytearray, clientLED):
    if data[MESSAGE_TYPE_INDEX] != MESSAGE_TYPE_ID:  # Message Type ID のチェック
        return
    if data[EVENT_TYPE_INDEX] != EVENT_TYPE_ID:  # Event Type ID のチェック
        return
    if data[STATE_INDEX] == 3 or data[STATE_INDEX] == 4:  # 的が倒れたことを判定する
        print('Fell Over.')
        await control_led(clientLE, duration=1500, on=1500, off=0, pattern=1, red=70, green=0, blue=0)
        return
    if data[STATE_INDEX] == 1 or data[STATE_INDEX] == 6:  # 的が起き上がったことを判定する
        print('Stand Up.')
        await control_led(clientLE, duration=2500, on=250, off=250, pattern=1, red=50, green=50, blue=0)
        return

def on_receive(_, data: bytearray):
    data = bytes(data)
    print(data)

def on_receive_indicate(_, data: bytearray):
    data = bytes(data)
    print('[indicate] ',data)

# LEDブロックを光らせるメソッド    
async def control_led(client, duration, on, off, pattern, red, green, blue):
    # print(client)
    messagetype = 1
    command = pack('<BBBBBBBHHHB', messagetype, 0, red, 0, green, 0, blue, duration, on, off, pattern)
    checksum = 0
    for x in command:
        checksum += x
    command += pack('B', checksum & 0xFF)  # Add check sum to byte array

    try:
        await client.write_gatt_char(CORE_WRITE_UUID, command, response=True)
        await asyncio.sleep(duration / 1000)
    except Exception as e:
        print('Error', e)

# ブロックと通信するメソッド
async def connect_and_operate(device, callback, blockType):
    async with BleakClient(device.address, timeout=None) as client:
        # Initialize
        await client.start_notify(CORE_NOTIFY_UUID, callback)
        # await client.start_notify(CORE_NOTIFY_UUID, simple_callback)
        await client.start_notify(CORE_INDICATE_UUID, callback)
        await client.write_gatt_char(CORE_WRITE_UUID, pack('<BBBB', 0, 2, 1, 3), response=True)
        print('Connected', device.name)
        await client.get_services()

        if blockType == 'LE':
            global clientLE
            clientLE = client

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            pass

async def scan(prefix='MESH-100'):
    while True:
        print('scan...')
        try:
            return next(d for d in await discover() if d.name and d.name.startswith(prefix))
        except StopIteration:
            continue

async def main():
    # Scan device
    deviceAC = await scan('MESH-100AC')
    print('found', deviceAC.name, deviceAC.address)
    deviceLE = await scan('MESH-100LE')
    print('found', deviceLE.name, deviceLE.address)
    
    # Connect and Operate
    await asyncio.gather(
        connect_and_operate(deviceAC, on_receive_notify, blockType='AC'),
        connect_and_operate(deviceLE, on_receive, blockType='LE')
    )
        
# Initialize event loop
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
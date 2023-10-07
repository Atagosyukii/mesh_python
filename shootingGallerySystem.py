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
def on_receive_notify(sender, data: bytearray):
    if data[MESSAGE_TYPE_INDEX] != MESSAGE_TYPE_ID:  # Message Type ID のチェック
        return
    if data[EVENT_TYPE_INDEX] != EVENT_TYPE_ID:  # Event Type ID のチェック
        return
    if data[STATE_INDEX] == 3 or data[STATE_INDEX] == 4:  # 的が倒れたことを判定する
        print('Fell Over.')
        return
    if data[STATE_INDEX] == 1:
        print('Left Side.')
        return
    if data[STATE_INDEX] == 6:  # 的が起き上がったことを判定する
        print('Right Side.')
        return

def on_receive(sender, data: bytearray):
    data = bytes(data)
    print(data)

def on_receive_indicate(sender, data: bytearray):
    data = bytes(data)
    print('[indicate] ',data)

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
    

    # Connect device
    # Connect AC Block
    async with BleakClient(deviceAC, timeout=None) as client:
        # Initialize
        await client.start_notify(CORE_NOTIFY_UUID, on_receive_notify)
        await client.start_notify(CORE_INDICATE_UUID, on_receive_indicate)
        await client.write_gatt_char(CORE_WRITE_UUID, pack('<BBBB', 0, 2, 1, 3), response=True)
        print('connected')

        await asyncio.sleep(30)

        # Finish
    
    # Connect LE Block
    # async with BleakClient(deviceLE, timeout=None) as client:
        # Initialize
        await client.start_notify(CORE_NOTIFY_UUID, on_receive)
        await client.start_notify(CORE_INDICATE_UUID, on_receive)
        await client.write_gatt_char(CORE_WRITE_UUID, pack('<BBBB', 0, 2, 1, 3), response=True)
        print('connected')

        # Generate command
        messagetype = 1
        red = 2
        green = 8
        blue = 32
        duration = 3000 # 3,000[ms]
        on = 500 # 500[ms]
        off = 500 # 500[ms]
        pattern = 2 # 1:blink, 2:firefly
        command = pack('<BBBBBBBHHHB', messagetype, 0, red, 0, green, 0, blue, duration, on, off, pattern)
        checksum = 0
        for x in command:
            checksum += x
        command = command + pack('B', checksum & 0xFF) # Add check sum to byte array
        print('command ',command)
        
        try:
            # Write command
            await client.write_gatt_char(CORE_WRITE_UUID, command, response=True)
        except Exception as e:
            print('error', e)
            return
        
        await asyncio.sleep(duration / 1000)

        # Finish
        
# Initialize event loop
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
import asyncio
from bleak import BleakClient, discover
from struct import pack

CORE_INDICATE_UUID = ('72c90005-57a9-4d40-b746-534e22ec9f9e')
CORE_NOTIFY_UUID = ('72c90003-57a9-4d40-b746-534e22ec9f9e')
CORE_WRITE_UUID = ('72c90004-57a9-4d40-b746-534e22ec9f9e')

# Callback
def on_receive(sender, data: bytearray):
    data = bytes(data)
    print(data)

async def scan(prefix = 'MESH-100'):
    while True:
        print('scan...')
        try:
            return next(d for d in await discover() if d.name and d.name.startswith(prefix))
        except StopIteration:
            continue

async def main():
    # Scan device
    device = await scan('MESH-100LE')
    print('found', device.name, device.address)
    
    # Connect device
    async with BleakClient(device, timeout=None) as client:
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
        duration = 5 * 1000 # 5,000[ms]
        on = 1 * 1000 # 1,000[ms]
        off = 500 # 500[ms]
        pattern = 1 # 1:blink, 2:firefly
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
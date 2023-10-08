import asyncio
from bleak import BleakClient, discover
from struct import pack
from functools import partial

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

# MESHブロックの状態管理クラス
class BlockManager:
    def __init__(self):
        self._ac_client = None
        self._le_client = None

    def set_ac_client(self, client):
        self._ac_client = client

    def get_ac_client(self):
        return self._ac_client
    
    def set_le_client(self, client):
        self._le_client = client

    def get_le_client(self):
        return self._le_client

# Callback
# 動きブロックから通知を受け取り、なんかするメソッド
async def on_receive_notify(blockManager, _, data: bytearray):
    if data[MESSAGE_TYPE_INDEX] != MESSAGE_TYPE_ID:  # Message Type ID のチェック
        return
    if data[EVENT_TYPE_INDEX] != EVENT_TYPE_ID:  # Event Type ID のチェック
        return
    if data[STATE_INDEX] == 3 or data[STATE_INDEX] == 4:  # 的が倒れたことを判定する
        print('Fell Over.')
        await control_led(blockManager.get_le_client(), duration=1500, on=1500, off=0, pattern=1, red=70, green=0, blue=0)
        return
    if data[STATE_INDEX] == 1 or data[STATE_INDEX] == 6 or data[STATE_INDEX] == 2 or data[STATE_INDEX] == 5:  # 的が起き上がったことを判定する
        print('Stand Up.')
        await control_led(blockManager.get_le_client(), duration=2000, on=250, off=250, pattern=1, red=50, green=50, blue=0)
        return

def on_receive(_, data: bytearray):
    data = bytes(data)
    print(data)

def on_receive_indicate(_, data: bytearray):
    data = bytes(data)
    print('[indicate] ',data)

# LEDブロックを光らせるメソッド    
async def control_led(client, duration, on, off, pattern, red, green, blue):
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
async def connect_and_operate(device, blockManager):
    async with BleakClient(device.address, timeout=None) as client:
        print(device.name)
        # Initialize
        if device.name.startswith('MESH-100AC'):  # 動きブロックの場合
            await client.start_notify(CORE_NOTIFY_UUID, partial(on_receive_notify, blockManager))
            await client.start_notify(CORE_INDICATE_UUID, on_receive_indicate)
            blockManager.set_ac_client(client)
        else:  # LEDブロックの場合
            await client.start_notify(CORE_NOTIFY_UUID, on_receive)
            await client.start_notify(CORE_INDICATE_UUID, on_receive)
            blockManager.set_le_client(client)

        await client.write_gatt_char(CORE_WRITE_UUID, pack('<BBBB', 0, 2, 1, 3), response=True)
        print('Connected', device.name)
        await client.get_services()  # そのうち無くなるメソッド

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
    # BlockManager のインスタンス生成
    blockManager = BlockManager()
    # Scan device
    deviceAC = await scan('MESH-100AC')
    print('found', deviceAC.name, deviceAC.address)
    deviceLE = await scan('MESH-100LE')
    print('found', deviceLE.name, deviceLE.address)
    
    # Connect and Operate
    await asyncio.gather(
        connect_and_operate(deviceAC, blockManager),
        connect_and_operate(deviceLE, blockManager)
    )
        
# Initialize event loop
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
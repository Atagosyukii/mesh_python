import asyncio
from bleak import BleakClient, BleakScanner
from struct import pack
from functools import partial
import pygame
import threading
import configparser

# 設定ファイルの読み込み
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

TARGET_DEVICES = dict(config['MESH_DEVICES'])
TARGET_DEVICES = {key: value for key, value in TARGET_DEVICES.items() if value and value.strip()}

print(TARGET_DEVICES)

# UUID
CORE_INDICATE_UUID = ('72c90005-57a9-4d40-b746-534e22ec9f9e')
CORE_NOTIFY_UUID = ('72c90003-57a9-4d40-b746-534e22ec9f9e')
CORE_WRITE_UUID = ('72c90004-57a9-4d40-b746-534e22ec9f9e')

# システムを動かすためのフラグ
operation_signal = True  # True:動作中, False:停止中

# MESHブロックの状態管理クラス
class BlockManager:
    def __init__(self, total_devices):
        self._ac_client = None
        self._le_client = None
        self._gp_client1 = None
        self._gp_client2 = None
        self._bu_client = None
        self._connected_devices = 0
        self.total_devices = total_devices

    async def mark_connected(self):
        self._connected_devices += 1
        if self._connected_devices == self.total_devices:
            await self.all_devices_connected()

    async def all_devices_connected(self):
        print('All devices connected.')
        await control_led(self._le_client, duration=3000, on=500, off=500, pattern=1, red=0, green=127, blue=0)

    def set_ac_client(self, client):
        self._ac_client = client

    def get_ac_client(self):
        return self._ac_client
    
    def set_le_client(self, client):
        self._le_client = client

    def get_le_client(self):
        return self._le_client
    
    def set_gp_client1(self, client):
        self._gp_client1 = client

    def get_gp_client1(self):
        return self._gp_client1
    
    def set_gp_client2(self, client):
        self._gp_client2 = client

    def get_gp_client2(self):
        return self._gp_client2
    
    def set_bu_client(self, client):
        self._bu_client = client

    def get_bu_client(self):
        return self._bu_client
    

# Callback
# 動きブロックから通知を受け取り、なんかするメソッド
async def on_receive_notify_AC(blockManager, _, data: bytearray):
    # Constant values
    MESSAGE_TYPE_INDEX = 0
    EVENT_TYPE_INDEX = 1
    STATE_INDEX = 2
    MESSAGE_TYPE_ID = 1
    EVENT_TYPE_ID = 3

    if data[MESSAGE_TYPE_INDEX] != MESSAGE_TYPE_ID:  # Message Type ID のチェック
        return
    if data[EVENT_TYPE_INDEX] != EVENT_TYPE_ID:  # Event Type ID のチェック
        return
    if data[STATE_INDEX] == 3 or data[STATE_INDEX] == 4:  # 的が倒れたことを判定する
        print('Fell Over.')
        await asyncio.gather(
            play_sound_thread("sound_effect/Phrase02-1.mp3"),
            control_led(blockManager.get_le_client(), duration=1500, on=1500, off=0, pattern=1, red=127, green=0, blue=0),
            control_gpio_output_power(blockManager.get_gp_client1(), power_state=1),
            control_gpio_output_power(blockManager.get_gp_client2(), power_state=1)
        )
        return
    
    if data[STATE_INDEX] == 1 or data[STATE_INDEX] == 6 or data[STATE_INDEX] == 2 or data[STATE_INDEX] == 5:  # 的が起き上がったことを判定する
        print('Stand Up.')
        await asyncio.gather(
            control_led(blockManager.get_le_client(), duration=1500, on=250, off=250, pattern=1, red=84, green=56, blue=0),
            control_gpio_output_power(blockManager.get_gp_client1(), power_state=2),
            control_gpio_output_power(blockManager.get_gp_client2(), power_state=2)
        )
        return

# ボタンブロックから通知を受け取り、なんかするメソッド    
async def on_receive_notify_BU(blockManager, _, data: bytearray):
    # Constant values
    MESSAGE_TYPE_INDEX = 0
    EVENT_TYPE_INDEX = 1
    STATE_INDEX = 2
    MESSAGE_TYPE_ID = 1
    EVENT_TYPE_ID = 0
    
    if data[MESSAGE_TYPE_INDEX] != MESSAGE_TYPE_ID:  # Message Type ID のチェック
        return
    if data[EVENT_TYPE_INDEX] != EVENT_TYPE_ID:  # Event Type ID のチェック
        return
    if data[STATE_INDEX] == 3:  # ボタンが2回押されたことを判定する
        print('State Reset.')
        await asyncio.gather(
            control_led(blockManager.get_le_client(), duration=1500, on=1500, off=0, pattern=1, red=0, green=0, blue=127),
            control_gpio_output_power(blockManager.get_gp_client1(), power_state=2),
            control_gpio_output_power(blockManager.get_gp_client2(), power_state=2)
        )
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

# GPIOブロックの電源出力を操作するメソッド
async def control_gpio_output_power(client, power_state):
    # クライアントが存在しない場合は処理を終了する
    if client is None: return

    # Constant values
    MESSAGE_TYPE_ID = 1
    EVENT_TYPE_ID = 1

    command = pack('<BBBBBBBBBB', MESSAGE_TYPE_ID, EVENT_TYPE_ID, 0, 0, 0, 0, power_state, 0, 0, 0)
    checksum = 0
    for x in command:
        checksum += x
    command += pack('B', checksum & 0xFF)  # Add check sum to byte array

    try:
        await client.write_gatt_char(CORE_WRITE_UUID, command, response=True)
        print('GPIO output power state: ', power_state)
    except Exception as e:
        print('Error', e)

# Windowsでサウンドを再生するメソッド
def play_sound(file_path):
    pygame.mixer.init()
    sound = pygame.mixer.Sound(file_path)
    sound.play()

# 上記のメソッドを別スレッドで再生する
async def play_sound_thread(file_path):
    thread = threading.Thread(target=play_sound, args=(file_path,))
    thread.start()

# ブロックと通信するメソッド
async def connect_and_operate(device, blockManager):
    async with BleakClient(device.address, timeout=None) as client:
        # Initialize
        if device.name == TARGET_DEVICES.get('mesh-100ac'):  # 動きブロックの場合 
            await client.start_notify(CORE_NOTIFY_UUID, partial(on_receive_notify_AC, blockManager))
            await client.start_notify(CORE_INDICATE_UUID, on_receive_indicate)
            blockManager.set_ac_client(client)
        elif device.name == TARGET_DEVICES.get('mesh-100bu'):  # ボタンブロックの場合
            await client.start_notify(CORE_NOTIFY_UUID, partial(on_receive_notify_BU, blockManager))
            await client.start_notify(CORE_INDICATE_UUID, on_receive_indicate)
            blockManager.set_bu_client(client)
        elif device.name == TARGET_DEVICES.get('mesh-100gp1'):  # GPIOブロック1の場合 (今後通知を受け取るかもしれないので、条件分岐しています。)
            await client.start_notify(CORE_NOTIFY_UUID, on_receive)
            await client.start_notify(CORE_INDICATE_UUID, on_receive)
            blockManager.set_gp_client1(client)
        elif device.name == TARGET_DEVICES.get('mesh-100gp2'):  # GPIOブロック2の場合 (今後通知を受け取るかもしれないので、条件分岐しています。)
            await client.start_notify(CORE_NOTIFY_UUID, on_receive)
            await client.start_notify(CORE_INDICATE_UUID, on_receive)
            blockManager.set_gp_client2(client)
        elif device.name == TARGET_DEVICES.get('mesh-100le'):  # LEDブロックの場合
            await client.start_notify(CORE_NOTIFY_UUID, on_receive)
            await client.start_notify(CORE_INDICATE_UUID, on_receive)
            blockManager.set_le_client(client)

        await client.write_gatt_char(CORE_WRITE_UUID, pack('<BBBB', 0, 2, 1, 3), response=True)
        client.services
        print('[Connected]', device.name, device.address)
        await blockManager.mark_connected()

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            pass

async def scan(device_type):
    print(f"Scanning for device_type: {device_type}")
    target_name = TARGET_DEVICES[device_type]
    while True:
        print('scan...')
        try:
            device = next(d for d in await BleakScanner.discover() if d.name and d.name == target_name)
            print('found', device.name, device.address)
            return device
        except StopIteration:
            continue

async def main():
   # BlockManager のインスタンス生成
    devices_to_connect = list(TARGET_DEVICES.keys())
    blockManager = BlockManager(len(devices_to_connect))
    
    # Scan devices
    scanned_devices = await asyncio.gather(*(scan(device) for device in devices_to_connect))
    
    # MESHブロックとの接続を確立し、通信を開始する  
    await asyncio.gather(*(connect_and_operate(device, blockManager) for device in scanned_devices))
        
# Initialize event loop
if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print('Program stopped by user.')
    finally:
        loop.close()
    
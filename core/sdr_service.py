'''
sdr_service.py
Captures live raw IQ data from an SDR (Software Defined Radio) device and returns it as a raw data stream.
'''

import redis
import numpy as np
import asyncio
import websockets

#first WS is best / fast
WS_URL = "wss://3.radiorubka.org/~~stream?v=11"             # add all of these in a DS (list/dict) and rotate periodically, maybe base it on geoloc and switch to whichever one is on daytime
#WS_URL = "wss://eshail.batc.org.uk/~~stream?v=11"          # figure out a way to change frequency
#WS_URL = "wss://80m.radiorubka.org/~~stream?v=11"          # also some bands are better during daytime, research more on this
#WS_URL = "ws://sdr.r9a.ru/~~stream?v=11"                  ----> this doesnt work. idk why

r = redis.Redis(host='localhost', port=6379, db=0)

async def websocket_client():
    async with websockets.connect(WS_URL) as websocket:
        await websocket.send("Hello, server!")
        while True:
            response = await websocket.recv()
            if isinstance(response, bytes):
                # Send raw bytes to Redis stream
                r.xadd('sdr_data_stream', {'iq': response})
                binary_str = ''.join(f'{byte:08b}' for byte in response)
                integer_value = int.from_bytes(response, byteorder='big')
                print(f"Binary: {binary_str[:64]}...")  # Print first 64 bits
                print(f"Integer: {integer_value}")
            else:
                print(f"Received: {response}")

if __name__ == "__main__":
    asyncio.run(websocket_client())
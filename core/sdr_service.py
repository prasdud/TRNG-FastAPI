'''
sdr_service.py
Captures live raw IQ data from an SDR (Software Defined Radio) device and returns it as a raw data stream.
'''

import redis
import asyncio
import websockets
from utils.logger import logger as log


#first WS is best / fast
WS_URL = "wss://3.radiorubka.org/~~stream?v=11"             # add all of these in a DS (list/dict) and rotate periodically, maybe base it on geoloc and switch to whichever one is on daytime
#WS_URL = "wss://eshail.batc.org.uk/~~stream?v=11"          # figure out a way to change frequency
#WS_URL = "wss://80m.radiorubka.org/~~stream?v=11"          # also some bands are better during daytime, research more on this
#WS_URL = "ws://sdr.r9a.ru/~~stream?v=11"                  ----> this doesnt work. idk why

r = redis.Redis(host='localhost', port=6379, db=0)

RECONNECT_DELAY = 5  # seconds to wait before reconnecting
MAX_RECONNECT_ATTEMPTS = None  # None for infinite retries

async def websocket_client():
    """Connect to WebSocket and process incoming data with auto-reconnect."""
    reconnect_count = 0
    
    while True:
        try:
            log.info(f"Connecting to {WS_URL}...")
            async with websockets.connect(
                WS_URL,
                ping_interval=20,      # Send ping every 20 seconds
                ping_timeout=60,       # Wait up to 60 seconds for pong response
                close_timeout=10,      # Wait up to 10 seconds for close handshake
                max_size=10 * 1024 * 1024  # 10MB max message size
            ) as websocket:
                log.info("WebSocket connected successfully!")
                reconnect_count = 0  # Reset counter on successful connection
                
                await websocket.send("Hello, server!")
                
                while True:
                    try:
                        response = await websocket.recv()
                        if isinstance(response, bytes):
                            # Send raw bytes to Redis stream with MAXLEN to prevent memory explosion
                            r.xadd('sdr_data_stream', {'iq': response}, maxlen=100, approximate=True)
                            binary_str = ''.join(f'{byte:08b}' for byte in response)
                            integer_value = int.from_bytes(response, byteorder='big')
                            log.info(f"Binary: {binary_str[:64]}...")  # Print first 64 bits
                            log.info(f"Integer: {integer_value}")
                        else:
                            log.info(f"Received: {response}")
                    except asyncio.TimeoutError:
                        log.warning("Timeout receiving data, continuing...")
                        continue
                        
        except websockets.exceptions.ConnectionClosedError as e:
            reconnect_count += 1
            log.error(f"WebSocket connection closed: {e}")
            if MAX_RECONNECT_ATTEMPTS and reconnect_count >= MAX_RECONNECT_ATTEMPTS:
                log.error(f"Max reconnection attempts ({MAX_RECONNECT_ATTEMPTS}) reached. Exiting.")
                break
            log.info(f"Reconnecting in {RECONNECT_DELAY} seconds... (attempt {reconnect_count})")
            await asyncio.sleep(RECONNECT_DELAY)
            
        except websockets.exceptions.WebSocketException as e:
            reconnect_count += 1
            log.error(f"WebSocket error: {e}")
            if MAX_RECONNECT_ATTEMPTS and reconnect_count >= MAX_RECONNECT_ATTEMPTS:
                log.error(f"Max reconnection attempts ({MAX_RECONNECT_ATTEMPTS}) reached. Exiting.")
                break
            log.info(f"Reconnecting in {RECONNECT_DELAY} seconds... (attempt {reconnect_count})")
            await asyncio.sleep(RECONNECT_DELAY)
            
        except asyncio.TimeoutError as e:
            reconnect_count += 1
            log.error(f"Connection timeout: {e}")
            if MAX_RECONNECT_ATTEMPTS and reconnect_count >= MAX_RECONNECT_ATTEMPTS:
                log.error(f"Max reconnection attempts ({MAX_RECONNECT_ATTEMPTS}) reached. Exiting.")
                break
            log.info(f"Reconnecting in {RECONNECT_DELAY} seconds... (attempt {reconnect_count})")
            await asyncio.sleep(RECONNECT_DELAY)
            
        except Exception as e:
            reconnect_count += 1
            log.error(f"Unexpected error: {e}", exc_info=True)
            if MAX_RECONNECT_ATTEMPTS and reconnect_count >= MAX_RECONNECT_ATTEMPTS:
                log.error(f"Max reconnection attempts ({MAX_RECONNECT_ATTEMPTS}) reached. Exiting.")
                break
            log.info(f"Reconnecting in {RECONNECT_DELAY} seconds... (attempt {reconnect_count})")
            await asyncio.sleep(RECONNECT_DELAY)

async def main():
    """Main entry point for the WebSocket client."""
    try:
        await websocket_client()
    except KeyboardInterrupt:
        log.info("Received shutdown signal, closing gracefully...")

if __name__ == "__main__":
    asyncio.run(main())
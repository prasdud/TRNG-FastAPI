import asyncio
import websockets

WS_URL = "wss://3.radiorubka.org/~~stream?v=11"

async def websocket_client():
    async with websockets.connect(WS_URL) as websocket:
        await websocket.send("Hello, server!")
        while True:
            response = await websocket.recv()
            if isinstance(response, bytes):
                binary_str = ''.join(f'{byte:08b}' for byte in response)
                integer_value = int.from_bytes(response, byteorder='big')
                print(f"Binary: {binary_str[:64]}...")  # Print first 64 bits
                print(f"Integer: {integer_value}")
            else:
                print(f"Received: {response}")

if __name__ == "__main__":
    asyncio.run(websocket_client())
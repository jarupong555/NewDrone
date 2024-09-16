import asyncio
import websockets
import subprocess
import time

async def handle_message(message):
    if message.startswith("Message: "):
        message = message[len("Message: "):]

    try:
        if message == "offcamera":
            result = subprocess.run(
                ["sudo", "systemctl", "stop", "camera.service"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("Camera service stopped.")
            print("Output:", result.stdout.decode())
            print("Error:", result.stderr.decode())
        elif message == "oncamera":
            result = subprocess.run(
                ["sudo", "systemctl", "start", "camera.service"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("Camera service started.")
            print("Output:", result.stdout.decode())
            print("Error:", result.stderr.decode())
        else:
            print(f"Unknown message: {message}")
    except subprocess.CalledProcessError as e:
        print(f"Subprocess error: {e}")
        print("Error output:", e.stderr.decode())

async def connect():
    uri = "ws://10.8.8.56:8081"  # Replace with your WebSocket server address
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print("Connected to WebSocket server.")
                while True:
                    message = await websocket.recv()
                    await handle_message(message)
        except websockets.ConnectionClosed:
            print("Connection closed. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Error: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(connect())

import time
import asyncio
import websockets
import socket
import binascii

# WebSocket and UDP configuration
websocket_url = "ws://10.8.8.56:8080"
UDP_IP = "192.168.144.25"
UDP_PORT = 37260

# Predefined UDP commands
up_step = binascii.unhexlify('55660102000000070064d308')
stop_step = binascii.unhexlify("55660102000000070000f124")
down_step = binascii.unhexlify("5566010200000007009cc466")
center_command = binascii.unhexlify("556601010000000801d112")
sleep_step = 0.1

# Function to send UDP message
def send_udp_message(message):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"Sending message: {message.hex()}")
        sock.sendto(message, (UDP_IP, UDP_PORT))
        sock.close()
    except Exception as e:
        print(f"An error occurred: {e}")

# Function to control the servo using UDP commands
def control_servo(command):
    if command == "up":
        send_udp_message(up_step)
        time.sleep(sleep_step)
        send_udp_message(stop_step)
    elif command == "stop":
        send_udp_message(stop_step)
    elif command == "down":
        send_udp_message(down_step)
        time.sleep(sleep_step)
        send_udp_message(stop_step)
    elif command == "center":
        send_udp_message(center_command)
        time.sleep(sleep_step)
        send_udp_message(stop_step)
    elif command == "upmax":
        send_udp_message(up_step)
    elif command == "downmax":
        send_udp_message(down_step)
    else:
        print("Unknown command")

# WebSocket handling function
async def process_websocket():
    async with websockets.connect(websocket_url) as websocket:
        print(f"Connected to WebSocket server at {websocket_url}")
        while True:
            try:
                message = await websocket.recv()
                print(f"Received: {message}")

                if message.startswith("Message:"):
                    command = message.strip().replace("Message: ", "")
                    print(f"Received command: {command}")

                    # Handle UDP-based commands
                    control_servo(command)

            except websockets.ConnectionClosed as e:
                print(f"WebSocket connection closed: {e}")
                break

# Run the combined WebSocket and UDP handling
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(process_websocket())

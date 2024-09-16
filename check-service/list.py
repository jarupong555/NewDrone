import asyncio
import websockets
import json
import subprocess

# WebSocket configuration
websocket_url = "ws://10.8.8.56:8081"

# Function to check the status of services
def check_services():
    with open('services.json', 'r') as f:
        services_data = json.load(f)

    services = services_data['services']
    status_result = {}

    for service in services:
        result = subprocess.run(['systemctl', 'is-active', service], stdout=subprocess.PIPE, text=True)
        status = result.stdout.strip()

        if status == "active":
            status_result[service] = "Active and Running"
        else:
            status_result[service] = "Not Active"
    
    return status_result

# WebSocket handling function
async def process_websocket():
    async with websockets.connect(websocket_url) as websocket:
        print(f"Connected to WebSocket server at {websocket_url}")
        while True:
            try:
                message = await websocket.recv()
                print(f"Received: {message}")

                # Check if the message starts with "Message: listservice"
                if message.startswith("Message: listservice"):
                    print("Received 'listservice' command. Checking services status...")
                    status_result = check_services()
                    await websocket.send(json.dumps(status_result))
                    print("Sent status result to WebSocket server.")
                else:
                    print("Received non-listservice message.")

            except websockets.ConnectionClosed as e:
                print(f"WebSocket connection closed: {e}")
                break

# Run the WebSocket handling
if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(process_websocket())
    except KeyboardInterrupt:
        print("Exiting...")

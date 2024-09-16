import json
import websocket
import subprocess
import time

websocket_url = "ws://10.8.8.56:8081"
data_sent = False  # Flag to control data sending

def read_services_from_json(filename="services.json"):
    with open(filename, "r") as json_file:
        services = json.load(json_file)
    return services

def control_service(service_name, action):
    if action not in ['start', 'stop']:
        return f"Invalid action: {action}. Use 'start' or 'stop'."
    
    result = subprocess.run(['sudo', 'systemctl', action, service_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if result.returncode == 0:
        return f"{action.capitalize()}ed {service_name} successfully."
    else:
        return result.stderr.decode()

def get_service_status():
    services = read_services_from_json()
    status_list = [
        f"{service['name']}: load={service['load']}, active={service['active']}, sub={service['sub']}"
        for service in services
    ]
    
    # Check if any service status matches the stopping condition
    for status in status_list:
        if "load=show" in status and "active=all" in status and "sub=installed" in status:
            global data_sent
            data_sent = True
            break
    
    return "\n".join(status_list)

def on_open(ws):
    global data_sent
    print("WebSocket connection opened")
    
    if not data_sent:
        service_status = get_service_status()
        try:
            ws.send(f"service_list\n{service_status}")
            print("Sent service list")
            data_sent = True
        except Exception as e:
            print(f"Failed to send data: {e}")

def on_message(ws, message):
    global data_sent
    print(f"Received raw message: {message}")

    if not message:
        error_msg = "Received an empty message"
        ws.send(error_msg)
        print(error_msg)
        return

    try:
        message_data = json.loads(message)
        command = message_data.get("command")
        service_name = message_data.get("service_name")
        action = message_data.get("action")

        if command == "control_service" and service_name and action:
            result = control_service(service_name, action)
            ws.send(f"Result: {result}")
            print(result)
            data_sent = False  # Reset flag to allow new data to be sent

        elif command == "list_services":
            if not data_sent:  # Send service status if not already sent
                service_status = get_service_status()
                try:
                    ws.send(f"service_list\n{service_status}")
                    print("Sent service list")
                    data_sent = True
                except Exception as e:
                    print(f"Failed to send data: {e}")

        else:
            error_msg = "Invalid command or missing parameters"
            ws.send(error_msg)
            print(error_msg)

    except json.JSONDecodeError as e:
        error_msg = f"Failed to decode JSON message: {e}"
        ws.send(error_msg)
        print(error_msg)

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"WebSocket closed: {close_msg}")

def close_websocket(ws):
    try:
        if ws and ws.sock and ws.sock.connected:
            ws.close()
    except Exception as e:
        print(f"Failed to close WebSocket: {e}")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(websocket_url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    
    # Run WebSocket client in a separate thread or use an event loop to handle connection
    ws_thread = websocket.WebSocketApp(websocket_url,
                                       on_open=on_open,
                                       on_message=on_message,
                                       on_error=on_error,
                                       on_close=on_close)
    
    ws_thread.run_forever()
    
    # Close WebSocket after a delay (for example, after 10 seconds)
    time.sleep(10)
    close_websocket(ws_thread)

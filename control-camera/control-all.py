import time
import asyncio
import websockets
import socket
import binascii
import RPi.GPIO as GPIO

# GPIO configuration for the servo
SERVO_PIN = 17  # GPIO pin connected to the servo signal
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Set up PWM on the servo pin with a frequency of 50Hz
pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz is standard for servos
pwm.start(0)  # Start PWM with 0% duty cycle

# Define initial servo position
current_angle = 0  # Start at 0 degrees

# WebSocket and UDP configuration
websocket_url = "ws://10.8.8.56:8081"
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

# Function to smoothly set the servo to a specific angle within a given duration
def set_servo_angle(target_angle, duration=0.1):
    global current_angle
    steps = int(duration / 0.05)  # Calculate the number of steps for the given duration
    step_angle = (target_angle - current_angle) / steps  # Calculate the angle change per step
    for _ in range(steps):
        current_angle += step_angle
        duty = current_angle / 18 + 2  # Calculate the duty cycle for the current angle
        duty = max(2, min(12, duty))  # Ensure duty cycle is within valid range
        pwm.ChangeDutyCycle(duty)
        time.sleep(0.05)  # Small delay for smooth transition

    # Set final duty cycle to the exact angle
    duty = target_angle / 18 + 2
    duty = max(2, min(12, duty))
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.1)  # Hold position for a brief moment to ensure stability
    pwm.ChangeDutyCycle(0)  # Stop PWM to avoid jitter

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
        set_servo_angle(0)  # Initialize servo to 0 degrees at startup
        while True:
            try:
                message = await websocket.recv()
                print(f"Received: {message}")

                if message.startswith("Message:"):
                    command = message.strip().replace("Message: ", "")
                    print(f"Received command: {command}")

                    # Handle servo control commands
                    if command == "on":
                        print("ON command received for servo")
                        set_servo_angle(100, duration=0.05)  # Move servo to 150 degrees smoothly in 0.5 seconds
                    elif command == "off":
                        print("OFF command received for servo")
                        set_servo_angle(70, duration=0.05)  # Move servo to 0 degrees smoothly in 0.5 seconds
                    else:
                        # Handle other UDP-based commands
                        control_servo(command)

            except websockets.ConnectionClosed as e:
                print(f"WebSocket connection closed: {e}")
                break

# Run the combined WebSocket and UDP handling
if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(process_websocket())
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        pwm.stop()
        GPIO.cleanup()

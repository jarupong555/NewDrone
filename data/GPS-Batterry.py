import serial
import time
import pynmea2
import asyncio
import websockets
from datetime import datetime
import spidev

gps_port = '/dev/ttyUSB1'
at_port = '/dev/ttyUSB2'

websocket_url = "ws://0.0.0.0:8080"

gps_ser = serial.Serial(gps_port, 115200, timeout=5)
at_ser = serial.Serial(at_port, 115200, timeout=5)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

vout_values = [3.29, 3.26, 3.26, 3.24, 3.21, 3.20]

max_voltage = 4.2
min_voltage = 3.5

last_gps_data = {"latitude": 0.0, "longitude": 0.0}

def send_at_command(ser, command, delay=1):
    ser.write(command.encode() + b'\r\n')
    time.sleep(delay)
    response = ser.read_until(b'OK\r\n').decode().strip()
    return response

def read_gps_data():
    global last_gps_data
    if gps_ser.in_waiting > 0:
        line = gps_ser.readline().decode('utf-8').strip()
        print(f"Raw GPS data: {line}")  # Debug statement
        if line.startswith('$GPGGA'):
            try:
                msg = pynmea2.parse(line)
                last_gps_data['latitude'] = msg.latitude
                last_gps_data['longitude'] = msg.longitude
                print(f"Latitude: {last_gps_data['latitude']}, Longitude: {last_gps_data['longitude']}")
            except pynmea2.ParseError as e:
                print(f"Parse error: {e}")
    return last_gps_data

def read_cellular_data():
    data = {}
    at_ser.write(b'AT+QENG="servingcell"\r')
    response = at_ser.read_until(b'OK').decode('utf-8')
    print(f"Raw cellular data: {response}")  # Debug statement
    for line in response.splitlines():
        if line.startswith('+QENG: "servingcell"'):
            cellular_data = line.split(',')
            data.update({
                "mcc": int(cellular_data[4]),
                "mnc": int(cellular_data[5]),
                "cellID": cellular_data[6],
                "pcid": int(cellular_data[7]),
                "earfcn": int(cellular_data[8]),
                "freq_band_ind": int(cellular_data[9]),
                "ul_bandwidth": float(cellular_data[10]),
                "dl_bandwidth": float(cellular_data[11]),
                "tac": cellular_data[12],
                "rsrp": float(cellular_data[13]),
                "rsrq": float(cellular_data[14]),
                "rssi": float(cellular_data[15]),
                "sinr": float(cellular_data[16])
            })
            break
    return data

def calculate_battery_percentage(cell_voltage, min_voltage, max_voltage):
    percentage = (cell_voltage - min_voltage) / (max_voltage - min_voltage) * 100
    return min(max(percentage, 0), 100)  # Limit percentage between 0-100%

def read_adc(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

def convert_to_voltage(adc_value, vout):
    return (adc_value * vout) / 1023.0

def map_voltage_to_4_2v(voltage, vout):
    return (voltage / vout) * 4.2

async def read_and_send_to_websocket():
    async with websockets.connect(websocket_url) as websocket:
        while True:
            gps_data = read_gps_data()  
            cellular_data = read_cellular_data()

            total_voltage = 0  
            battery_data = [] 

            for i in range(6):  
                adc_value = read_adc(i)
                print(f"Cell {i + 1} ADC Value: {adc_value}") 

                raw_voltage = convert_to_voltage(adc_value, vout_values[i])
                mapped_voltage = map_voltage_to_4_2v(raw_voltage, vout_values[i])
                percentage = calculate_battery_percentage(mapped_voltage, min_voltage, max_voltage)

                total_voltage += mapped_voltage

                cell_data = {
                    'cell': i + 1,
                    'voltage': round(mapped_voltage, 2),
                    'percentage': round(percentage, 2)
                }
                battery_data.append(cell_data)

                print(f"Cell {i + 1}: {mapped_voltage:.2f} V, {percentage:.2f}%")

            total_voltage_percentage = calculate_battery_percentage(total_voltage, min_voltage * 6, max_voltage * 6)

            print(f"Total Voltage: {total_voltage:.2f} V")
            print(f"Total Voltage Percentage: {total_voltage_percentage:.2f}%")

            data = {
                **cellular_data,
                **gps_data,
                'battery': battery_data,
                'total_voltage': round(total_voltage, 2),
                'total_voltage_percentage': round(total_voltage_percentage, 2),
                'time': datetime.utcnow().isoformat()
            }

            print(f"Data to send: {data}")

            await websocket.send(str(data))
            print("Data sent to WebSocket server.")

            await asyncio.sleep(2)  

try:
    print("Sending AT command to check modem response...")
    basic_response = send_at_command(at_ser, 'AT')
    if basic_response:
        print("Basic AT command response:")
        print(basic_response)
    else:
        print("No response to basic AT command. Check connection and power to the modem.")

    print("Enabling GPS...")
    gps_enable_response = send_at_command(at_ser, 'AT+QGPS=1', delay=2)
    if gps_enable_response:
        print("GPS enabled successfully.")
    else:
        print("No response to GPS enable command.")

    print("Waiting for GPS and modem to initialize...")
    time.sleep(2)  

    asyncio.run(read_and_send_to_websocket())

finally:
    gps_ser.close()
    at_ser.close()
    spi.close()

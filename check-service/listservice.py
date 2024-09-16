import json
import subprocess

# อ่านไฟล์ JSON
with open('services.json', 'r') as f:
    services_data = json.load(f)

# ดึงรายชื่อ services
services = services_data['services']

for service in services:
    # ใช้คำสั่ง systemctl status
    result = subprocess.run(['systemctl', 'is-active', service], stdout=subprocess.PIPE, text=True)
    status = result.stdout.strip()

    if status == "active":
        print(f"{service}: Active and Running")
    else:
        print(f"{service}: Not Active")

import subprocess
import json

def list_services():
    try:
        result = subprocess.run(['systemctl', 'list-units', '--type=service', '--all'], 
                                stdout=subprocess.PIPE, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing systemctl: {e}")
        return ""

def generate_services_json():
    services_output = list_services()
    services = []
    lines = services_output.splitlines()

    # เช็คหัวของตาราง
    if lines:
        headers = lines[0].split()
        for line in lines[1:]:
            if not line.strip():
                continue

            parts = line.split()
            if len(parts) < 5:
                continue

            service_name = parts[0]
            load = parts[1]
            active = parts[2]
            sub = parts[3]
            description = " ".join(parts[4:])

            services.append({
                'name': service_name,
                'load': load,
                'active': active,
                'sub': sub,
                'description': description
            })

    with open('services.json', 'w') as json_file:
        json.dump(services, json_file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    generate_services_json()

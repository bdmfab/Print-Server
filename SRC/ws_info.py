# main.py -- main application
from web_server import run_server
import params

print("=" * 50)
print("ESP32 Configuration Web Server (Ethernet)")
print("=" * 50)
print("\nCurrent Configuration:")
print(f"Server IP: {params.serve_config[0]}")
print(f"Subnet: {params.serve_config[1]}")
print(f"Gateway: {params.serve_config[2]}")
print(f"DNS: {params.serve_config[3]}")
print(f"Stations configured: {len(params.sta)}")
print(f"ZPL lists configured: {len(params.zpl) - 1}")
print("")
# Start the web server
run_server(host=params.serve_config[0], port=80)

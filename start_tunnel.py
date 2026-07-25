import subprocess
import threading
import time
import re
import sys
import os

print("Starting Pinggy tunnel for port 8000...")
p = subprocess.Popen(
    ['ssh', '-p', '443', '-R0:localhost:8000', '-o', 'StrictHostKeyChecking=no', 'a.pinggy.io'], 
    stdout=subprocess.PIPE, 
    stderr=subprocess.STDOUT, 
    text=True
)

url_found = False

def read_output():
    global url_found
    for line in p.stdout:
        line = line.strip()
        print("[PINGGY]", line)
        if "http" in line and ".pinggy" in line and not url_found:
            # Extract URL, ignore dashboard
            if "dashboard.pinggy.io" not in line:
                match = re.search(r'(https://[a-zA-Z0-9.-]+\.pinggy[a-zA-Z0-9.-]+)', line)
                if match:
                    url = match.group(1)
                    print(f"--- EXTRACTED URL: {url} ---")
                    with open("tunnel_url.txt", "w") as f:
                        f.write(url)
                    url_found = True

t = threading.Thread(target=read_output)
t.daemon = True
t.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    p.kill()
    if os.path.exists("tunnel_url.txt"):
        os.remove("tunnel_url.txt")

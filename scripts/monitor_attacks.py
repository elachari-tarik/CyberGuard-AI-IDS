#!/usr/bin/env python3
import subprocess
import time

def monitor_network():
    """Surveille le trafic réseau entrant"""
    print("🔍 Surveillance du trafic réseau...")
    
    # Utiliser tcpdump pour voir le trafic en temps réel
    cmd = ["sudo", "tcpdump", "-i", "eth0", "-n", "host", "172.23.64.1"]
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE, text=True)
        
        for line in process.stdout:
            print(f"📦 {line.strip()}")
            
    except KeyboardInterrupt:
        print("🛑 Surveillance arrêtée")
        process.terminate()

if __name__ == "__main__":
    monitor_network()

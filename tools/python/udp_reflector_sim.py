import socket
import argparse
import time
import random
import sys

# Educational UDP Reflection & Spoofing Simulator
# This tool demonstrates how reflection attacks utilize spoofed source IPs.
# IMPORTANT: Modern Windows restricted raw sockets. This simulates the logic
# by communicating with a 'reflector' that logs the spoofed source.

def simulate_reflection(target_ip, reflector_ip, reflector_port):
    print(f"\n[*] CONCEPT: UDP Reflection Attack Simulation")
    print(f"[*] Target (Victim): {target_ip}")
    print(f"[*] Reflector: {reflector_ip}:{reflector_port}")
    print("-" * 50)
    
    print(f"[!] Step 1: Crafting UDP packet...")
    print(f"    - Destination: {reflector_ip}:{reflector_port}")
    print(f"    - SPROOED Source IP: {target_ip}")
    print(f"    - Payload: DNS QUERY (Type ANY)")
    
    # In a real attack, we would use a raw socket here:
    # s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    # On Windows, this requires Npcap/WinPcap.
    
    print(f"\n[!] Step 2: Sending request to Reflector...")
    time.sleep(1)
    
    # We use a standard UDP socket for the demo to show it 'hitting' a reflector
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        # Note: We can't actually spoof the source IP with a standard socket bind
        # because the OS will only allow binding to local interfaces.
        msg = f"REFLECT TO:{target_ip}|PAYLOAD:AMPLICFIED_DATA_X50"
        s.sendto(msg.encode(), (reflector_ip, reflector_port))
        print(f"[+] Packet sent to Reflector.")
    except Exception as e:
        print(f"[!] Error: {e}")

    print(f"\n[!] Step 3: Reflection & Amplification")
    print(f"    - The Reflector receives the packet.")
    print(f"    - It 'thinks' {target_ip} requested the data.")
    print(f"    - It sends a LARGE response (e.g., 50x size) back to {target_ip}.")
    print(f"[+] Simulation Complete. The Victim ({target_ip}) is now receiving unsolicited traffic.")

def main():
    parser = argparse.ArgumentParser(description="Educational UDP Reflection Simulator")
    parser.add_argument("target", help="The Victim's IP (The Spoofed Source)")
    parser.add_argument("reflector", help="The Reflector's IP (e.g., Open DNS resolver)")
    parser.add_argument("-p", "--port", type=int, default=53, help="Reflector Port (Default 53 for DNS)")
    
    args = parser.parse_args()
    
    simulate_reflection(args.target, args.reflector, args.port)

if __name__ == "__main__":
    main()

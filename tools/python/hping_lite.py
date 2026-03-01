import socket
import sys
import time
import random
import argparse

def probe_tcp(host, port, source_ip=None):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        if source_ip:
            s.bind((source_ip, 0))
        start = time.time()
        s.connect((host, port))
        end = time.time()
        s.close()
        msg = f"[+] TCP Probe: Connected to {host}:{port} in {(end-start)*1000:.2f}ms"
        if source_ip:
            msg += f" (Source: {source_ip})"
        return msg
    except Exception as e:
        return f"[!] TCP Probe: Failed to connect to {host}:{port} - {e}"

def probe_udp(host, port, source_ip=None):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        if source_ip:
            s.bind((source_ip, 0))
        s.sendto(b"HELO", (host, port))
        # Since UDP is connectionless, we can't easily confirm receipt without a response
        msg = f"[*] UDP Probe: Packet sent to {host}:{port} (Educational Simulation)"
        if source_ip:
            msg += f" (Source: {source_ip})"
        return msg
    except Exception as e:
        return f"[!] UDP Probe: Failed - {e}"

def main():
    parser = argparse.ArgumentParser(description="Educational hping-lite simulation")
    parser.add_argument("host", help="Target host")
    parser.add_argument("port", type=int, help="Target port")
    parser.add_argument("mode", choices=["tcp", "udp"], help="Probe mode")
    parser.add_argument("--ips", help="Comma-separated source IP pool")
    parser.add_argument("--continuous", action="store_true", help="Enable 1s interval rotation")
    parser.add_argument("--flood", action="store_true", help="Enable high-frequency flood")

    args = parser.parse_args()

    host = args.host
    port = args.port
    mode = args.mode
    source_ips = args.ips.split(",") if args.ips else []
    continuous = args.continuous
    flood = args.flood

    print(f"[*] Starting educational probe on {host}:{port} ({mode.upper()})", flush=True)
    if source_ips:
        print(f"[*] Using source IP pool: {source_ips}", flush=True)
    if continuous:
        print(f"[*] Continuous Rotation Mode: Active (1s interval)", flush=True)
    if flood:
        print(f"[*] FLOOD MODE: ACTIVE (Maximum Frequency)", flush=True)
    
    i = 0
    try:
        while True:
            source_ip = source_ips[i % len(source_ips)] if source_ips else None
            if mode == 'tcp':
                result = probe_tcp(host, port, source_ip)
            else:
                result = probe_udp(host, port, source_ip)
            
            print(result, flush=True)
            i += 1
            
            if not continuous and not flood and i >= 5:
                break
                
            if not flood:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Stopping probe sequence...")

if __name__ == "__main__":
    main()

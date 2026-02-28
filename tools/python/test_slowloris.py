import unittest
import socket
import threading
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from slowloris_sim import init_socket

class TestSlowloris(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a tiny mock server
        cls.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cls.server_socket.bind(('127.0.0.1', 0))
        cls.port = cls.server_socket.getsockname()[1]
        cls.server_socket.listen(5)
        cls.running = True
        
        def mock_server():
            while cls.running:
                try:
                    conn, addr = cls.server_socket.accept()
                    data = conn.recv(1024) # Receive headers
                    conn.close()
                except:
                    break
        
        cls.server_thread = threading.Thread(target=mock_server)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.running = False
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('127.0.0.1', cls.port))
        cls.server_socket.close()

    def test_init_socket(self):
        s = init_socket('127.0.0.1', self.port)
        self.assertIsNotNone(s)
        s.close()

if __name__ == "__main__":
    unittest.main()

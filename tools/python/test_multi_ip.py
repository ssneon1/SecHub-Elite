import unittest
from unittest.mock import patch, MagicMock
import socket
import sys
import os

# Add tools/python to path
sys.path.append(os.path.join(os.getcwd(), "tools", "python"))
import slowloris_sim
import hping_lite

class TestMultiIP(unittest.TestCase):
    @patch('socket.socket')
    def test_slowloris_bind(self, mock_socket):
        mock_instance = MagicMock()
        mock_socket.return_value = mock_instance
        
        # Test with source IP
        slowloris_sim.init_socket("1.1.1.1", 80, source_ip="2.2.2.2")
        
        # Verify bind was called with source_ip
        mock_instance.bind.assert_called_with(("2.2.2.2", 0))

    @patch('socket.socket')
    def test_hping_tcp_bind(self, mock_socket):
        mock_instance = MagicMock()
        mock_socket.return_value = mock_instance
        
        hping_lite.probe_tcp("1.1.1.1", 80, source_ip="2.2.2.2")
        
        mock_instance.bind.assert_called_with(("2.2.2.2", 0))

    @patch('socket.socket')
    def test_hping_udp_bind(self, mock_socket):
        mock_instance = MagicMock()
        mock_socket.return_value = mock_instance
        
        hping_lite.probe_udp("1.1.1.1", 80, source_ip="3.3.3.3")
        
        mock_instance.bind.assert_called_with(("3.3.3.3", 0))

if __name__ == "__main__":
    unittest.main()

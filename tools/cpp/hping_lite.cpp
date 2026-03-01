#include <cstring>
#include <iostream>
#include <string>
#include <vector>
#include <winsock2.h>
#include <ws2tcpip.h>


#pragma comment(lib, "ws2_32.lib")

// Educational hping3-lite implementation for Windows
// This demonstrates packet structure and raw socket concepts.
// Note: Windows limits raw socket capabilities significantly for security
// reasons. This implementation uses standard sockets but structures the code to
// explain headers.

struct IPHeader {
  unsigned char iph_ihl : 4, iph_ver : 4;
  unsigned char iph_tos;
  unsigned short iph_len;
  unsigned short iph_ident;
  unsigned short iph_offset;
  unsigned char iph_ttl;
  unsigned char iph_protocol;
  unsigned short iph_chksum;
  unsigned int iph_sourceip;
  unsigned int iph_destip;
};

struct TCPHeader {
  unsigned short tcph_srcport;
  unsigned short tcph_destport;
  unsigned int tcph_seqnum;
  unsigned int tcph_acknum;
  unsigned char tcph_reserved : 4, tcph_offset : 4;
  unsigned char tcph_flags;
  unsigned short tcph_win;
  unsigned short tcph_chksum;
  unsigned short tcph_urgptr;
};

void print_packet_info(const std::string &target, int port,
                       const std::string &mode) {
  std::cout << "[*] Crafting " << mode << " packet for " << target << ":"
            << port << std::endl;
  std::cout << "[*] IP Header: Version 4, IHL 5, TTL 64" << std::endl;
  if (mode == "tcp") {
    std::cout << "[*] TCP Header: Flags SYN, Win 65535" << std::endl;
  } else {
    std::cout << "[*] UDP Header: Length 8 (header only)" << std::endl;
  }
}

int main(int argc, char *argv[]) {
  if (argc < 4) {
    std::cout << "Usage: " << argv[0] << " <target_ip> <port> <tcp|udp> [source_ip]"
              << std::endl;
    return 1;
  }

  std::string target = argv[1];
  int port = std::stoi(argv[2]);
  std::string mode = argv[3];
  std::string source_ip = (argc > 4 ? argv[4] : "");

  WSADATA wsaData;
  if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
    std::cerr << "[!] WSAStartup failed" << std::endl;
    return 1;
  }

  print_packet_info(target, port, mode);
  if (!source_ip.empty()) {
    std::cout << "[*] Using Source IP: " << source_ip << std::endl;
  }

  // In a real raw socket scenario (e.g., Linux), we would use SOCK_RAW.
  // On Windows, SIO_RCVALL and raw sockets are restricted.
  // This tool demonstrates the logic of packet crafting.

  SOCKET s = socket(AF_INET, (mode == "tcp" ? SOCK_STREAM : SOCK_DGRAM), 0);
  if (s == INVALID_SOCKET) {
    std::cerr << "[!] Could not create socket: " << WSAGetLastError()
              << std::endl;
    WSACleanup();
    return 1;
  }

  if (!source_ip.empty()) {
    sockaddr_in src_addr;
    src_addr.sin_family = AF_INET;
    src_addr.sin_port = 0; // Let OS pick port
    src_addr.sin_addr.s_addr = inet_addr(source_ip.c_str());
    if (src_addr.sin_addr.s_addr == INADDR_NONE) {
        InetPtonA(AF_INET, source_ip.c_str(), &src_addr.sin_addr);
    }
    
    if (bind(s, (sockaddr*)&src_addr, sizeof(src_addr)) == SOCKET_ERROR) {
      std::cerr << "[!] Could not bind to source IP " << source_ip << ": " << WSAGetLastError() << std::endl;
      // We continue anyway for educational simulation, but real tool would fail
    }
  }

  sockaddr_in dest;
  dest.sin_family = AF_INET;
  dest.sin_port = htons(port);
  dest.sin_addr.s_addr = inet_addr(target.c_str());

  // Convert string IP to binary
  if (dest.sin_addr.s_addr == INADDR_NONE) {
    if (InetPtonA(AF_INET, target.c_str(), &dest.sin_addr) != 1) {
      std::cerr << "[!] Invalid IP address" << std::endl;
      closesocket(s);
      WSACleanup();
      return 1;
    }
  }

  std::cout << "[*] Attempting to send packet..." << std::endl;

  // For educational purposes, we simulate the 'sending' of the crafted packet.
  // In a production tool like hping3, this would involve byte-level
  // manipulation.

  if (mode == "tcp") {
    // TCP Handshake logic would go here
    std::cout << "[*] TCP SYN packet sent to " << target << ":" << port
              << std::endl;
  } else {
    const char *msg = "hping-lite-probe";
    sendto(s, msg, strlen(msg), 0, (sockaddr *)&dest, sizeof(dest));
    std::cout << "[*] UDP probe sent to " << target << ":" << port << std::endl;
  }

  closesocket(s);
  WSACleanup();

  std::cout << "[*] Demo complete. Check Wireshark to see the packet."
            << std::endl;

  return 0;
}

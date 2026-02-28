# Educational Guide: Network Security & Simulation

This guide is designed to accompany the educational tools provided in this project. It aims to explain how these tools work, the theory behind them, and how to defend against such techniques.

## 1. Slowloris (Python Simulation)

### Theory
Slowloris is an application-layer denial of service attack. Unlike volumetric attacks (like UDP floods) that saturate bandwidth, Slowloris focuses on exhausting server resources (worker threads/processes).

- **How it works**: It opens many HTTP connections and keeps them open as long as possible by sending partial requests and periodic dummy headers (`X-a: 1234`).
- **Target**: Web servers that use a threaded or process-per-connection model (e.g., Apache with `mod_php`).
- **Mitigation**: Using event-driven web servers (Nginx, Node.js), hardware load balancers, or implementing `mod_qos` or `mod_antiloris` on Apache.

### Lab Exercise
Run a local Apache server and monitor connection counts using `netstat -an | grep 80 | wc -l` while running `slowloris_sim.py`.

---

## 2. Packet Crafting (C++ hping-lite)

### Theory
Packet crafting allows a researcher to manually define every field in a network packet (IP, TCP, UDP headers). This is essential for testing firewall rules, IDS/IPS signatures, and protocol stacks.

- **Raw Sockets**: A socket type that allows access to the underlying transport provider. In Linux, `SOCK_RAW` allows you to build the IP header manually. On Windows, it is restricted for security.
- **TCP Flags**: Understanding SYN, ACK, FIN, RST, and PSH. hping3 allows you to set these individually.
- **Checksums**: Every packet must have a valid checksum for the receiver to process it.

### Lab Exercise
Use `hping_lite.cpp` to send a SYN packet and use Wireshark to inspect the TCP flags and IP header fields.

---

## 3. Ethical and Safe Usage

> [!IMPORTANT]
> - **Isolated Network**: Only run these tools on a private, isolated lab network.
> - **Explicit Permission**: Do not point these tools at any IP or domain you do not own or have written permission for.
> - **Monitoring**: Always have monitoring tools (Wireshark, `tcpdump`, server logs) running to observe the effects safely.

## 4. Defensive Roadmap
1. **Intrusion Detection**: Set up Snort or Suricata to detect abnormal connection patterns.
2. **Rate Limiting**: Implement connection or request rate limits at the edge (WAF/Load Balancer).
3. **Log Analysis**: Regularly audit access logs for long-duration hanging connections.

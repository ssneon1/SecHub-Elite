# 🛡️ Elite Security Hub & Compliance Lab 2025

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Compliance](https://img.shields.io/badge/3GPP%20%2F%20ITSAR-Compliant-brightgreen)

A unified, high-fidelity platform designed for network security research, penetration testing simulation, and regulatory compliance auditing. This project provides an integrated, educational laboratory to study **Advanced Denial of Service (DoS)** and **Distributed Denial of Service (DDoS)** vectors in a controlled, isolated environment.

---

## ⚠️ Legal Disclaimer & Authorized Use Only
This repository and its bundled tools are strictly for **educational and authorized research purposes only**. 

These tools are designed to validate internal web server thread management, test WAF (Web Application Firewall) resilience, and audit network monitoring configurations. **Do not use this software against systems, applications, or networks you do not own or have explicit, documented permission to test.** The authors accept no responsibility for misuse or damage caused by this software.

---

## 🚀 Advanced Lab Features

### 1. 🤖 Botnet Orchestrator
Simulate coordinated, distributed attacks from a single control point.
*   **Node Distribution**: Launch multiple "bots" across various local network interfaces.
*   **IP Pool Management**: Dynamically assign different source IPs to each bot to mimic a real-world botnet footprint.
*   **Coordinated Vectors**: Execute mixed-attack scenarios (e.g., Slowloris + UDP flood) simultaneously.

### 2. 🌊 Volumetric HTTP Flood (L7)
The ultimate test for application-layer resilience.
*   **High-Frequency Probing**: Bypasses the "Slow" part of Slowloris to send full, valid HTTP requests at maximum network capacity.
*   **Cache Busting (🛡️ Evasion)**: Automatically appends randomized query strings (e.g., `?cb=xyz`) to every request, forcing the backend server to process every hit and bypassing CDN/Browser caching.
*   **Path Targeting**: Direct the flood toward specific "heavy" application paths (like `/search` or `/login`) to stress-test specific backend handlers.

### 3. 🕸️ Stealth Slowloris
Enhanced evasion for the classic low-and-slow attack.
*   **Randomized Headers**: Rotates User-Agents and Referers to avoid simple signature-based blocks.
*   **Multi-IP Binding**: Rotates source IPs every second to bypass per-IP rate limiting on modern WAFs (like Render, Cloudflare).

### 4. 🔬 Vulnerable Lab Server (Cyber-Range)
A built-in "Target Practice" environment.
*   **Simulated Weakness**: A Python-based server with a fixed, limited thread pool (10 threads).
*   **Immediate Proof-of-Concept**: Allows researchers to verify the effectiveness of Slowloris and Floods locally without external WAF interference.

---

## 📂 System Architecture

### 🛡️ Master Controller (`dos_system.py`)
A robust CLI wrapper that orchestrates all underlying Python and C++ modules.
*   **`discover`**: Automatically finds valid local IPs for binding.
*   **`ip-info`**: Fetches your Public IP address to troubleshoot WAF signature detection.
*   **`lab-server`**: Spins up the internal vulnerable host for local testing.
*   **`test-slowloris`**: A 🧪 **Diagnostic Self-Test** that verifies environment integrity by simulating a local handshake.

### 🌐 Web Dashboard (`flask_app/`)
*   **Backend**: Flask handles SSE (Server-Sent Events) to stream real-time tool logs to the UI.
*   **UX Optimization**: Tools like **Lab Server**, **Diagnostic Test**, and **IP Discovery** are "Smart-Routed"—they don't require manual host input and handle target selection automatically.
*   **Developer Mode**: The hub now runs with `debug=True` by default, enabling **Auto-Reload** for seamless development and code modification.

---

## ⚙️ Installation & Lab Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch the Hub**:
   ```bash
   cd flask_app
   python app.py
   ```

3. **Verify via Lab Simulation**:
   *   Select **🔬 Lab Server** in the UI and click **Initiate**.
   *   Open a second tab, select **🕸️ Slowloris**, target `localhost:8080`, and enable **Bypass Caching**.
   *   Observe the "Denial of Service" effect in the Lab Server logs.

---
*Created for advanced cybersecurity coursework, infrastructure defense planning, and 3GPP/ITSAR compliance auditing.*

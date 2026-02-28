# 🛡️ Elite Security Hub & Compliance Lab 2025

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Compliance](https://img.shields.io/badge/3GPP%20%2F%20ITSAR-Compliant-brightgreen)

A unified, high-fidelity platform designed for network security research, penetration testing simulation, and regulatory compliance auditing. This project provides an integrated, educational laboratory to study Denial of Service (DoS) and Distributed Denial of Service (DDoS) vectors in a controlled, isolated environment.

---

## ⚠️ Legal Disclaimer & Authorized Use Only
This repository and its bundled tools (`slowloris_sim`, `hping_lite`) are strictly for **educational and authorized research purposes only**. 

These tools are designed to validate internal web server thread management and test network monitoring configurations (e.g., Wireshark setups, SOC dashboards). **Do not use this software against systems, applications, or networks you do not own or have explicit, documented permission to test.** The authors accept no responsibility for misuse or damage caused by this software.

---

## 🚀 Features & Modules

### 1. Unified Control Dashboard (Web UI)
A premium dark-themed, SOC-style web interface built with standard HTML/CSS/JS and driven by a Python Flask Backend.
* **Lab Control Tab:** Configure and execute security simulations directly from the UI.
* **Real-time Streaming Terminal:** Watch live streaming `stdout` from the underlying Python/C++ attack simulators.
* **Network Monitor:** A built-in, Wireshark-style data table that dynamically parses logs to display live mock "packet captures" and connection statistics.

### 2. Embedded Security Simulators (In `./tools/`)
* **`slowloris_sim.py`**: A Python implementation of the classic Slowloris attack. It demonstrates how "low-and-slow" attacks can exhaust thread pools on traditional synchronous web servers (like Apache) without requiring high bandwidth.
* **`hping_lite`**: A custom packet routing simulator built to mimic traditional `hping3` behaviors. Features both a C++ implementation (for high performance) and a Python fallback (for systems without a compiler).

### 3. Master Compliance Handbook
Integrated directly into the Web Dashboard is a comprehensive, interactive guide detailing modern defensive architectures:
* **The distinction between Volume-based (Network) and Application-layer attacks.**
* **3GPP (4.2.3.3.x)** requirements for handling network overloads in modern 5G architectures.
* **ITSAR UPF (2.8.1)** rules for strict RAM/CPU isolation and concurrent connection limiting.
* High-availability, scalable cloud architecture blueprints (WAF, AWS Shield, Cloudflare CDN).

---

## 🛠️ System Architecture

* **Backend:** Flask (Python) handles API requests and streams child process output to the client via Server-Sent Events (SSE).
* **Frontend:** Vanilla HTML5, CSS3 (Glassmorphism design system), and JS (`AbortController` for stopping tasks, SSE content consumption).
* **Execution Engine:** Spawns `subprocess.Popen` tasks to safely run the internal network tools and stream their outputs asynchronously back to the dashboard.

---

## ⚙️ Installation & Quick Start

1. **Clone the repository and enter the directory:**
   ```bash
   cd network-scanning-tool-summary
   ```

2. **Install Python dependencies:**
   Ensure you have Python 3.8+ installed.
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the Hub:**
   ```bash
   cd flask_app
   python app.py
   ```
   > **Note:** By default, the application binds to `0.0.0.0:5000` to be accessible across local network interfaces for lab testing.

4. **Access the Dashboard:**
   Open your preferred modern web browser and navigate to:
   `http://127.0.0.1:5000`

---

## 📦 Deployment Readiness & Hardening

This application currently uses the Flask Development Server for ease of use in lab environments. For production or wider enterprise deployment, strictly follow these steps:

1. **Swap to a WSGI Server:** 
   Do not use the Flask development server in production. Use `gunicorn` (Linux) or `waitress` (Windows).
2. **Reverse Proxy:** 
   Front the WSGI server with `Nginx` or `Apache` for static file serving, SSL termination (HTTPS), and aggressive rate limiting.
3. **Security Constraints & Sandboxing:** 
   The `app.py` `/run` route currently accepts user inputs for target hosts. In a deployed environment, **you must implement server-side validation against a strict whitelist** of authorized test dummy servers to prevent SSRF or unauthorized external attacks.

---
*Created for advanced cybersecurity coursework, infrastructure defense planning, and 3GPP/ITSAR compliance auditing.*

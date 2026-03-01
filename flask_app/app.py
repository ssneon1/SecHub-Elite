from flask import Flask, render_template, request, Response, stream_with_context
import subprocess
import os
import sys
import json
import time
import socket
import requests

app = Flask(__name__)

# Paths to tools
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(os.path.dirname(BASE_DIR), "tools")
SLOWLORIS_PATH = os.path.join(TOOLS_DIR, "python", "slowloris_sim.py")
SLOWLORIS_TEST_PATH = os.path.join(TOOLS_DIR, "python", "test_slowloris.py")
HPING_PY_PATH = os.path.join(TOOLS_DIR, "python", "hping_lite.py")
BOTNET_PATH = os.path.join(TOOLS_DIR, "python", "botnet_sim.py")
REFLECTION_PATH = os.path.join(TOOLS_DIR, "python", "udp_reflector_sim.py")
DOS_SYSTEM_PATH = os.path.join(TOOLS_DIR, "dos_system.py")
HPING_PATH = os.path.join(TOOLS_DIR, "cpp", "hping_lite.exe")

@app.route('/check', methods=['POST'])
def check_target():
    data = request.json
    host = data.get('host')
    port = data.get('port', 80)
    
    if not host:
        return {"error": "Target host is required"}, 400
    
    results = {"http": "UNKNOWN", "tcp": "UNKNOWN"}
    
    # TCP Check
    try:
        with socket.create_connection((host, int(port)), timeout=3):
            results["tcp"] = "REACHABLE"
    except Exception:
        results["tcp"] = "UNREACHABLE"
        
    # HTTP Check
    try:
        url = f"http://{host}:{port}" if ":" not in host else host
        if not url.startswith("http"): url = f"http://{url}"
        r = requests.get(url, timeout=3, verify=False)
        results["http"] = f"REACHABLE ({r.status_code})"
    except Exception as e:
        results["http"] = f"UNREACHABLE"
        
    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_tool():
    data = request.json
    tool = data.get('tool')
    host = data.get('host')
    port = data.get('port', '80')
    extra = data.get('extra', '') # Can be sockets, bot count, or reflector IP
    ips = data.get('ips', '')
    rotate = data.get('rotate', False)
    flood = data.get('flood', False)
    path = data.get('path', '/')
    cache_bust = data.get('cache_bust', False)

    if not host and tool in ['discover', 'lab-server', 'ip-info', 'test-slowloris']:
        host = 'localhost' if tool in ['lab-server', 'test-slowloris'] else 'system'
        
    if not host and tool not in ['discover', 'lab-server', 'ip-info', 'test-slowloris']:
        return {"error": "Target host is required"}, 400

    def generate_output():
        cmd = []
        if tool == 'slowloris':
            # Run slowloris via dos_system.py with -y flag
            cmd = [sys.executable, DOS_SYSTEM_PATH, '-y', 'slowloris', host, '-p', str(port), '-s', str(extra or 150)]
            if ips: cmd.extend(['--ips', ips])
            if path: cmd.extend(['--path', path])
            if cache_bust: cmd.append('--cache-bust')
            if flood: cmd.append('--flood')
        elif tool == 'botnet':
            # Run botnet simulation with target, port, and bot count
            cmd = [sys.executable, DOS_SYSTEM_PATH, '-y', 'botnet', host, '-p', str(port), '-b', str(extra or 3), '--ips', ips]
            if rotate: cmd.append('--rotate')
            if flood: cmd.append('--flood')
        elif tool == 'reflection':
            # Run reflection via dos_system.py with -y flag
            cmd = [sys.executable, DOS_SYSTEM_PATH, '-y', 'reflection', host, extra, '-p', str(port)]
        elif tool == 'discover':
            cmd = [sys.executable, DOS_SYSTEM_PATH, '-y', 'discover']
        elif tool == 'ip-info':
            cmd = [sys.executable, DOS_SYSTEM_PATH, '-y', 'ip-info']
        elif tool == 'lab-server':
            cmd = [sys.executable, DOS_SYSTEM_PATH, '-y', 'lab-server']
        elif tool == 'site-check':
            yield f"data: {json.dumps({'text': f'[*] Running connectivity check on {host}:{port}...', 'color': 'info'})}\n\n"
            # Simulate the check results in the log stream
            try:
                with socket.create_connection((host, int(port)), timeout=3):
                    yield f"data: {json.dumps({'text': '[+] TCP Connectivity: REACHABLE', 'color': 'success'})}\n\n"
            except:
                yield f"data: {json.dumps({'text': '[!] TCP Connectivity: UNREACHABLE', 'color': 'error'})}\n\n"
            return
        elif tool == 'test-slowloris':
            cmd = [sys.executable, SLOWLORIS_TEST_PATH]
        elif tool == 'hping':
            # Check if C++ utility exists
                if not os.path.exists(HPING_PATH):
                    cpp_src = os.path.join(TOOLS_DIR, "cpp", "hping_lite.cpp")
                    try:
                        yield f"data: {json.dumps({'text': '[*] Attempting to compile C++ utility...', 'color': 'info'})}\n\n"
                        subprocess.run(["g++", cpp_src, "-o", HPING_PATH, "-lws2_32"], check=True, capture_output=True)
                        cmd = [HPING_PATH, host, str(port), extra or 'tcp']
                        if ips: cmd.append(ips.split(',')[0])
                    except Exception:
                        yield f"data: {json.dumps({'text': '[!] C++ Compiler (g++) not found. Falling back to Python module...', 'color': 'warning'})}\n\n"
                        cmd = [sys.executable, "-u", HPING_PY_PATH, host, str(port), extra or 'tcp']
                        if ips: cmd.append(ips)
                        if rotate: cmd.append("--continuous")
                else:
                    # Prefer Python for rotation/flood features
                    if rotate or flood:
                        cmd = [sys.executable, "-u", HPING_PY_PATH, host, str(port), extra or 'tcp']
                        if ips: cmd.extend(["--ips", ips])
                        if rotate: cmd.append("--continuous")
                        if flood: cmd.append("--flood")
                    else:
                        cmd = [HPING_PATH, host, str(port), extra or 'tcp']
                        if ips: cmd.append(ips.split(',')[0])
        else:
            yield f"data: {json.dumps({'text': '[!] Unknown tool requested.', 'color': 'error'})}\n\n"
            return

        yield f"data: {json.dumps({'text': f'[*] Initiating {tool} against {host}:{port}...', 'color': 'info', 'bold': True})}\n\n"
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            for line in process.stdout:
                if line.strip():
                    log_data = {'text': line.strip(), 'timestamp': time.strftime("%H:%M:%S")}
                    # Basic coloring logic
                    if "[+]" in line: log_data['color'] = 'success'
                    elif "[!]" in line: log_data['color'] = 'error'
                    elif "[*]" in line: log_data['color'] = 'info'
                    
                    yield f"data: {json.dumps(log_data)}\n\n"

            process.wait()
            rc = process.returncode
            if rc == 0:
                yield f"data: {json.dumps({'text': '[*] Process completed successfully.', 'color': 'success'})}\n\n"
            else:
                yield f"data: {json.dumps({'text': f'[!] Process exited with return code {rc}.', 'color': 'error'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'text': f'[!] Execution error: {str(e)}', 'color': 'error'})}\n\n"

    return Response(stream_with_context(generate_output()), mimetype='text/event-stream')

if __name__ == '__main__':
    # Ensure the tools directory exists relative to this app
    if not os.path.exists(TOOLS_DIR):
        print(f"[!] Critical Error: Tools directory not found at {TOOLS_DIR}")
        sys.exit(1)
    
    # Optional: Run self-test on startup to verify environment
    print("="*50)
    print("      Elite Security Hub | Startup Sequence")
    print("="*50)
    print("[*] Running system diagnostics...")
    try:
        subprocess.run([sys.executable, SLOWLORIS_TEST_PATH], check=True, capture_output=True, text=True)
        print("[+] Environment Integrity: VERIFIED")
    except Exception as e:
        print(f"[!] Warning: Diagnostic sequence interrupted: {e}")

    # For production, you'd want to use a real WSGI server like Gunicorn
    port = int(os.environ.get("PORT", 5000))
    print(f"[*] Hub Uplink Established: http://127.0.0.1:{port}")
    print("="*50)
    app.run(host='0.0.0.0', port=port, debug=True)

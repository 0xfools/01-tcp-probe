#!/usr/bin/env python3
"""
probe.py - Minimal TCP Service & Banner Prober
Zero third-party dependencies. Pure Python standard library socket implementation.

Author: 0xfools
GitHub: https://github.com/0xfools
"""

import socket
import sys

def probe_port(target_ip: str, port: int, timeout: float = 1.0):
    """
    Probes a TCP port on target_ip.
    Uses s.connect_ex() to return POSIX errno directly without crashing.
    Captures initial service banner on connection success.
    """
    # AF_INET = IPv4 address family, SOCK_STREAM = TCP byte stream
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    
    try:
        # 3-Way Handshake: SYN -> SYN-ACK -> ACK
        # Returns 0 on success; returns C errno (e.g. 111 ECONNREFUSED) on failure
        result = s.connect_ex((target_ip, port))
        
        if result == 0:
            print(f"[+] Port {port:<5} is OPEN")
            
            # Attempt banner grab: send probe to trigger service response
            try:
                s.sendall(b"\r\n")
                banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
                if banner:
                    print(f"    └── Banner: {banner}")
                else:
                    print("    └── Banner: [Connected, but no immediate banner sent]")
            except (socket.timeout, socket.error):
                print("    └── Banner: [Timed out waiting for banner response]")
        else:
            print(f"[-] Port {port:<5} is CLOSED (errno {result})")
            
    except socket.gaierror:
        print(f"[!] Hostname resolution failed for: {target_ip}")
        sys.exit(1)
    finally:
        s.close()

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "scanme.nmap.org"
    ports = [22, 80, 443, 9999]
    
    print(f"[*] 0xfools TCP Probe initializing against: {target}")
    print("-" * 55)
    for p in ports:
        probe_port(target, p)
    print("-" * 55)

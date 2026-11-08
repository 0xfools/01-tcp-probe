# 01-tcp-probe: Raw TCP Service & Banner Prober

A zero-dependency TCP port probe and banner grabber written in pure Python.

Built as part of the **`0xfools`** systems and offensive engineering journal. Rather than relying on black-box scanners, this tool directly interfaces with the Linux Berkeley sockets API to interrogate services and extract application banners.

---

## Technical Overview

### 1. The TCP 3-Way Handshake
To determine whether an application is actively listening on a port, the client operating system kernel initiates a TCP 3-way handshake:
1. **Client -> Server (`SYN`):** Client requests connection.
2. **Server -> Client (`SYN-ACK` or `RST`):** 
   - If port is **OPEN**: Server returns `SYN-ACK`.
   - If port is **CLOSED**: Kernel immediately replies with `RST` (Reset/Refused).
3. **Client -> Server (`ACK`):** Client establishes connection (`ESTABLISHED` state).

```
   Client (0xfools)                 Target Server
          │                               │
          │────── [SYN] (Port 22) ───────>│
          │<───── [SYN-ACK] ──────────────│  (Port is OPEN)
          │────── [ACK] ─────────────────>│
          │                               │
          │====== 3-Way Handshake Done ===│
          │                               │
          │<───── Service Banner ─────────│  ("SSH-2.0-OpenSSH_6.6.1p1")
```

### 2. Why `connect_ex()` instead of `connect()`?
In Python's standard `socket` module:
- `connect((host, port))` raises an unhandled `ConnectionRefusedError` or `socket.timeout` exception on failure, demanding heavy `try/except` overhead for every scanned port.
- `connect_ex((host, port))` directly mirrors the underlying C POSIX `connect()` system call:
  - Returns `0` on success.
  - Returns POSIX error numbers (`errno`, e.g., `111` for `ECONNREFUSED`, `110` for `ETIMEDOUT`) on failure without interrupting execution flow.

### 3. Service Banner Grabbing
Once a connection is established, network services (SSH, FTP, SMTP, raw TCP listeners) frequently broadcast their software version string immediately to identify the protocol implementation to the client. Sending a carriage return (`\r\n`) stimulates interactive daemons into emitting their version before authenticating.

---

## Usage

```bash
# Default probe against legal scanning testbed (scanme.nmap.org)
python3 probe.py

# Probe custom target host or IP
python3 probe.py 10.10.10.X
```

### Sample Output
```text
[*] 0xfools TCP Probe initializing against: scanme.nmap.org
-------------------------------------------------------
[+] Port 22    is OPEN
    └── Banner: SSH-2.0-OpenSSH_6.6.1p1 Ubuntu-2ubuntu2.13
[+] Port 80    is OPEN
    └── Banner: [Connected, but no immediate banner sent]
[-] Port 443   is CLOSED (errno 111)
[-] Port 9999  is CLOSED (errno 111)
-------------------------------------------------------
```

---

## Engineering Notes
- **Language:** Python 3 (Standard Library only)
- **Key System Calls:** `socket(AF_INET, SOCK_STREAM)`, `connect_ex()`, `sendall()`, `recv()`
- **Next Evolution:** Multi-threading with `concurrent.futures.ThreadPoolExecutor` to eliminate sequential network I/O latency.

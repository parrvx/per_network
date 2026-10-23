# 🌐 per_network - Unix-Legendary Network Analysis & Data Environment

A high-performance environment tailored for network traffic analysis, packet inspection, and network data engineering using a reproducibility-first approach with **Nix Flakes**, **Python 3.13**, **Polars**, **DuckDB**, and legendary Unix network diagnostic tools.

---

## 🚀 How to Activate the Environment

You can activate the development shell in two ways: using **`direnv`** (recommended for automatic loading) or directly via **`nix develop`**.

### Prerequisites
Ensure you have [Nix](https://nixos.org/) installed with Flakes enabled, along with [direnv](https://direnv.net/) for automatic shell loading.

---

### Option 1: Automatic Activation via `direnv` (Recommended)

When entering the project directory, allow `direnv` to automatically load the environment variables and dependencies specified in `.envrc`:

```bash
direnv allow
```

> **Note:** Upon activation, the Nix dev shell is loaded and the `src/` directory is automatically exported to your `PYTHONPATH`.

---

### Option 2: Manual Activation via Dev Shell (`nix develop`)

If you don't use `direnv`, you can enter the isolated shell manually at any time by running:

```bash
nix develop
```

Upon entering the shell (via either method), a summary of installed versions for key data and network tools will be displayed in your terminal.

---

## 📊 Running the Network Diagnostic Report (`analysis.py`)

The repository includes an automated Python script (`analysis.py`) that executes a suite of network diagnostic tests and compiles the results into a PDF report using the **Typst** markup engine.

### Steps to Run:

1. Ensure your shell environment is activated (`direnv` or `nix develop`).


2. Execute the main script:

```bash
python analysis.py
```

### What the Script Performs:

* **Interface & Topology Mapping:** Gathers local network interfaces and assigned IPv4 addresses using `iproute2`.
* **DNS Resolution Benchmark:** Measures query latency across providers (Cloudflare, Google, Quad9, Local) using `dnspython`.
* **Route Path Analysis:** Performs continuous traceroute and path latency checks (`mtr`) to `1.1.1.1`.
* **Throughput Testing:** Measures single-stream HTTP download speed via `curl`.
* **Report Compilation:** Writes the output into a Typst markup file (`output/network_report.typ`) and compiles it into a structured PDF document (`output/network_report.pdf`).

---

## 🛠️ Tool Summary & Included Capabilities

This environment comes pre-equipped with a full Python data engine, document generation utilities, and standard Unix network diagnostic binaries.

### 🐍 Python 3.13 & Data Science Toolkit

* **`polars`**: High-performance DataFrame library for fast data manipulation.
* **`duckdb`**: In-process analytical database engine (OLAP).
* **`httpx`**: Modern, asynchronous HTTP client for Python.
* **`scapy`**: Low-level packet crafting, manipulation, and scanning.
* **`pyshark`**: Python wrapper for programmatic `tshark` packet inspection.
* **`dnspython`**: Native DNS toolkit for Python queries and record processing.
* **`ruff`**: Extremely fast Python linter and code formatter.
* **`typst`**: Modern markup-based typesetting system for generating PDF reports.

---

### 🌐 Legendary Unix Network Toolkit

#### 1. DNS & Name Resolution

* **`bind` (`dig`, `host`, `nslookup`)**: Official utilities for DNS record querying, tracing, and debugging.

#### 2. Local Interface & Socket Inspection

* **`iproute2` (`ip`, `ss`)**: Native Linux networking utilities to inspect interface states, IP routes, and open sockets.
* **`ethtool`**: Low-level physical NIC settings, speed configuration, and hardware statistics.

#### 3. Network Discovery & Connectivity

* **`nmap`**: Industry-standard network exploration tool and port scanner.
* **`netcat-openbsd` (`nc`)**: Flexible TCP/UDP socket reading and writing.
* **`socat`**: Multipurpose relay for bidirectional data transfer across sockets, TCP, and UDP.
* **`curl`**: Universal tool for transferring data via HTTP/HTTPS/FTP protocols.

#### 4. Route Path & Quality Analysis

* **`mtr`**: Combines `traceroute` and `ping` into a live, continuous path jitter and loss analyzer.
* **`traceroute`**: Classic route path tracing utility.

#### 5. Packet Capture & Traffic Inspection

* **`tcpdump`**: Lightweight command-line packet analyzer powered by BPF filters.
* **`tshark`**: Terminal-based Wireshark engine for deep packet extraction.
* **`wireshark`**: Graphical user interface (GUI) for detailed packet analysis.

#### 6. Bandwidth & Performance Testing

* **`iperf3`**: Network throughput benchmark tool for TCP, UDP, and SCTP.
* **`iftop`**: Real-time interface bandwidth utilization breakdown by connection.

---

## 🔒 Privileges Note

Capturing raw packets (`tcpdump`, `tshark`) or modifying physical interface parameters (`ethtool`) requires elevated network capabilities (`CAP_NET_RAW`, `CAP_NET_ADMIN`). Ensure you run those specific commands with `sudo` or configure appropriate capabilities on your host machine.

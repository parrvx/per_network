import json
import os
import re
import subprocess
import time
import dns.resolver


def run_cmd(cmd: list[str] | str) -> str:
    """Helper to run system commands safely, merging stdout and stderr."""
    try:
        if isinstance(cmd, str):
            res = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, check=False
            )
        else:
            res = subprocess.run(
                cmd, capture_output=True, text=True, check=False
            )
        # Combina stdout e stderr para evitar perder dados de ferramentas CLI
        output = (res.stdout + "\n" + res.stderr).strip()
        return output
    except Exception as e:
        return f"Error executing command: {e}"


def get_network_interfaces() -> list[dict]:
    """Retrieve network interfaces and IP topology using iproute2."""
    out = run_cmd(["ip", "-j", "addr"])
    try:
        data = json.loads(out)
        interfaces = []
        for iface in data:
            ifname = iface.get("ifname", "unknown")
            operstate = iface.get("operstate", "UNKNOWN")

            if operstate == "UNKNOWN":
                operstate = (
                    "UP (Virtual)" if "UP" in iface.get("flags", []) else "UP"
                )

            ip_addrs = [
                addr.get("local")
                for addr in iface.get("addr_info", [])
                if addr.get("family") == "inet"
            ]
            primary_ip = ip_addrs[0] if ip_addrs else "No IPv4"
            interfaces.append(
                {
                    "interface": ifname,
                    "state": operstate,
                    "ip_address": primary_ip,
                }
            )
        return interfaces
    except Exception:
        return []


def run_dns_benchmark(domain: str = "google.com") -> list[dict]:
    """Benchmarking DNS resolution timing using native dnspython module."""
    providers = [
        ("Default/Local", None),
        ("Cloudflare", "1.1.1.1"),
        ("Google", "8.8.8.8"),
        ("Quad9", "9.9.9.9"),
    ]
    results = []

    for name, ip in providers:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 2.0
        resolver.lifetime = 2.0

        if ip:
            resolver.nameservers = [ip]

        start_time = time.time()
        try:
            resolver.resolve(domain, "A")
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
        except Exception:
            elapsed_ms = None

        results.append({"provider": name, "query_time_ms": elapsed_ms})

    return results


def run_mtr_analysis(target: str = "1.1.1.1") -> list[dict]:
    """Parse MTR report output into structured route hops cleanly."""
    out = run_cmd(["mtr", "--report", "--report-cycles", "5", "--raw", target])
    hops = {}

    if not out or "Error" in out or "not found" in out:
        out = run_cmd(["mtr", "--report", "--report-cycles", "5", target])
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 6 and parts[0].replace(".", "").isdigit():
                hop_num = int(parts[0].replace(".", ""))
                host = parts[1]
                loss_pct = float(parts[2].replace("%", ""))
                avg_ms = float(parts[5])
                stdev = float(parts[7]) if len(parts) > 7 else 0.0
                hops[hop_num] = {
                    "hop": hop_num,
                    "host": host,
                    "loss_pct": loss_pct,
                    "avg_ms": avg_ms,
                    "stdev": stdev,
                }
        return list(hops.values())

    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 3:
            msg_type, hop_idx = parts[0], parts[1]
            if hop_idx.isdigit():
                hop_num = int(hop_idx) + 1
                if hop_num not in hops:
                    hops[hop_num] = {
                        "hop": hop_num,
                        "host": "???",
                        "loss_pct": 0.0,
                        "avg_ms": 0.0,
                        "stdev": 0.0,
                        "_pings": [],
                    }

                if msg_type == "h":
                    hops[hop_num]["host"] = parts[2]
                elif msg_type == "p":
                    ping_ms = float(parts[2]) / 1000.0
                    hops[hop_num]["_pings"].append(ping_ms)

    result_hops = []
    for h_num in sorted(hops.keys()):
        h_data = hops[h_num]
        pings = h_data["_pings"]
        if pings:
            h_data["avg_ms"] = round(sum(pings) / len(pings), 2)
            h_data["loss_pct"] = 0.0
        else:
            h_data["loss_pct"] = 100.0
            h_data["avg_ms"] = 0.0
        del h_data["_pings"]
        result_hops.append(h_data)

    return result_hops


def run_throughput_test() -> dict:
    """Measure single-stream HTTP download speed."""
    url = "https://speed.cloudflare.com/__down?bytes=25000000"
    start = time.time()
    out = run_cmd(
        ["curl", "-o", "/dev/null", "-s", "-w", "%{speed_download}", url]
    )
    duration = time.time() - start

    try:
        # Pega a última linha caso haja qualquer lixo de saída
        clean_out = [line for line in out.splitlines() if line.strip()][-1]
        bytes_per_sec = float(clean_out.strip())
        download_mbps = round((bytes_per_sec * 8) / 1_000_000, 2)
    except (ValueError, IndexError):
        download_mbps = 0.0

    return {"download_mbps": download_mbps, "time_sec": round(duration, 2)}


def generate_typst_report(
    interfaces: list[dict],
    dns_bench: list[dict],
    mtr_hops: list[dict],
    speed: dict,
):
    """Render structured data into Typst document markup and compile to PDF."""
    os.makedirs("output", exist_ok=True)

    if_rows = ""
    for iface in interfaces:
        if_rows += f"    [{iface['interface']}], [{iface['state']}], [{iface['ip_address']}],\n"

    dns_rows = ""
    for dns_res in dns_bench:
        latency = (
            f"{dns_res['query_time_ms']} ms"
            if dns_res["query_time_ms"] is not None
            else "Timeout / Blocked"
        )
        dns_rows += f"    [{dns_res['provider']}], [{latency}],\n"

    mtr_rows = ""
    for hop in mtr_hops:
        mtr_rows += f"    [{hop['hop']}], [{hop['host']}], [{hop['loss_pct']}%], [{hop['avg_ms']} ms], [{hop['stdev']}],\n"

    typst_content = f"""
#set page(paper: "a4", margin: (x: 2cm, y: 2.5cm))
#set text(size: 10pt)

#align(center)[
  #text(18pt, weight: "bold", fill: rgb("#1d3557"))[🌐 Automated Network Diagnostic Report]
  #v(2mm)
  #text(10pt, fill: gray)[Generated using Nix, Python & Typst]
]

#v(5mm)

== 1. Network Interfaces & Topology
#table(
  columns: (1fr, 1.2fr, 2fr),
  fill: (x, y) => if y == 0 {{ rgb("#f1faee") }} else {{ none }},
  stroke: 0.5pt + gray,
  [*Interface*], [*State*], [*IPv4 Address*],
{if_rows}
)

== 2. Internet Throughput Test
#rect(width: 100%, fill: rgb("#f8f9fa"), radius: 4pt, inset: 10pt)[
  *HTTP Single-Stream Download Benchmark*
  - *Speed:* #{speed['download_mbps']} Mbps
  - *Duration:* #{speed['time_sec']} seconds
]

== 3. DNS Resolution Benchmark
#table(
  columns: (2fr, 1fr),
  fill: (x, y) => if y == 0 {{ rgb("#f1faee") }} else {{ none }},
  stroke: 0.5pt + gray,
  [*DNS Provider*], [*Query Latency*],
{dns_rows}
)

== 4. Route Path & Latency Analysis (MTR to 1.1.1.1)
#table(
  columns: (0.5fr, 3fr, 1fr, 1fr, 1fr),
  fill: (x, y) => if y == 0 {{ rgb("#f1faee") }} else {{ none }},
  stroke: 0.5pt + gray,
  [*Hop*], [*Host*], [*Loss %*], [*Avg Latency*], [*StDev*],
{mtr_rows}
)

#v(1cm)
#line(length: 100%, stroke: 0.5pt + gray)
#align(center)[
  #text(8pt, fill: gray)[Report compiled via Typst Engine]
]
"""

    typst_path = "output/network_report.typ"
    pdf_path = "output/network_report.pdf"

    with open(typst_path, "w") as f:
        f.write(typst_content)

    print(f"📄 Typst template saved to {typst_path}")
    print("⏳ Compiling Typst document to PDF...")

    comp_res = run_cmd(["typst", "compile", typst_path, pdf_path])

    if os.path.exists(pdf_path):
        print(f"🎉 Report successfully compiled to {pdf_path}")
    else:
        print(f"❌ Failed to generate PDF:\n{comp_res}")


def main():
    print("🚀 Starting Automated Network Diagnostics...")

    print("🔍 Gathering local interface topology...")
    interfaces = get_network_interfaces()

    print("🌐 Benchmarking DNS providers...")
    dns_bench = run_dns_benchmark()

    print("📍 Running MTR path analysis to Cloudflare (1.1.1.1)...")
    mtr_hops = run_mtr_analysis()

    print("⚡ Running HTTP Throughput Benchmark...")
    speed = run_throughput_test()

    print("📝 Generating Typst Markup...")
    generate_typst_report(interfaces, dns_bench, mtr_hops, speed)


if __name__ == "__main__":
    main()

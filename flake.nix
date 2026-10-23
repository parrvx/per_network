{
  description = "Unix-Legendary Network Analysis & Data Environment";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };

      # Python environment configured for high-performance data processing
      # and programmatic network packet inspection
      pythonEnv = pkgs.python313.withPackages (ps: with ps; [
        polars        # High-performance DataFrames
        duckdb        # In-process analytical database engine
        httpx         # Asynchronous HTTP client for Python
        scapy         # Low-level packet crafting and manipulation
        pyshark       # Python wrapper for tshark packet analysis
        dnspython     # Structured DNS queries directly in Python
      ]);
    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          # --- Core Python & Analytics Tools ---
          pythonEnv
          pkgs.duckdb
          pkgs.typst
          pkgs.ruff

          # --- Legendary Unix Network Toolkit ---
          pkgs.curl           # Universal data transfer tool (HTTP, FTP, etc.)
          pkgs.bind           # Official BIND utilities: dig, host, nslookup
          pkgs.tcpdump        # Lightweight, BPF-powered packet analyzer
          pkgs.tshark         # Terminal-based Wireshark packet analyzer
          pkgs.wireshark      # Graphical packet inspection (GUI)
          pkgs.socat          # Multipurpose relay for TCP/UDP/Sockets
          pkgs.netcat-openbsd # Arbitrary TCP/UDP connections and scans (nc)
          pkgs.iproute2       # Native Linux network management (ip, ss)
          pkgs.ethtool        # Low-level physical NIC settings and stats
          pkgs.mtr            # Combined traceroute and continuous ping
          pkgs.traceroute     # Classic route path tracing utility
          pkgs.iftop          # Real-time bandwidth usage by connection
          pkgs.iperf3         # Network throughput testing tool
          pkgs.nmap           # Industry-standard network discovery & security scanner
        ];

        shellHook = ''
          echo "🌐 Unix-Legendary Network Analysis Environment"
          echo "  🐍 Python:     $(python --version 2>&1 | cut -d' ' -f2)"
          echo "  🦆 DuckDB:     $(duckdb --version | awk '{print $1}')"
          echo "  🧊 Polars:     $(python -c 'import polars as pl; print(pl.__version__)')"
          echo "  ⚡ Ruff:       $(ruff --version | awk '{print $2}')"
          echo "  📝 Typst:      $(typst --version | awk '{print $2}')"
          echo "  🌐 Curl:       $(curl --version | head -n1 | awk '{print $2}')"
          echo "  🔍 Dig (BIND): $(dig -v | head -n1 | awk '{print $2}')"
          echo "  🦈 TShark:     $(tshark --version | head -n1 | awk '{print $3}')"
          echo "  📦 TCPDump:    $(tcpdump --version 2>&1 | head -n1 | awk '{print $3}')"
          echo "  🛠️  IPRoute2:   $(ip -V | awk '{print $3}')"
          echo "  🔌 Ethtool:    $(ethtool --version | awk '{print $3}')"
          echo "  🗺️  MTR:        $(mtr --version | awk '{print $2}')"
          echo "  📍 Traceroute: $(traceroute --version | awk '{print $3}')"
          echo "  🚀 IPerf3:     $(iperf3 --version | head -n1 | awk '{print $2}')"
          echo "  🎯 Nmap:       $(nmap --version | head -n1 | awk '{print $3}')"
          echo "  🔗 Socat:      $(socat -V | head -n1 | awk '{print $3}')"
        '';
      };
    };
}

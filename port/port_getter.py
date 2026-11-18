import nmap

def Get_Open_Ports(IP):
    open_ports = []
    #Timeout is currently set to vague number, will need to be redefined
    scan_time_out = 300

    try:
        scanner = nmap.PortScanner()
    except nmap.PortScannerError as exc:
        raise RuntimeError("Could not start Nmap. Check that it is installed and available on PATH.") from exc

    try:
        scanner.scan(hosts = IP, ports = "1-65535", arguments="-sT -sV", timeout=scan_time_out)
    except nmap.PortScannerTimeout as exc:
        raise RuntimeError(f"Nmap scan for {IP} timed out after 300 seconds") from exc
    except nmap.PortScannerError as exc:
        raise RuntimeError(f"Nmap could not complete the scan for {IP}") from exc
    if IP not in scanner.all_hosts():
        raise RuntimeError(f"Nmap returned no host result for {IP}")

    host_state = scanner[IP].state()
    if host_state != "up":
        raise RuntimeError(f"Nmap reported {IP} as {host_state!r}. Open ports could not be determined")

    
    for host in scanner.all_hosts():
        for port in scanner[host].all_tcp():
            if scanner[host]["tcp"][port]["state"] == "open":
                port_info = {
                    "port": port,
                    "service": scanner[host]["tcp"][port].get("name", ""),
                    "product": scanner[host]["tcp"][port].get("product", ""),
                    "version": scanner[host]["tcp"][port].get("version", "")
                }
                open_ports.append(port_info)

    return open_ports




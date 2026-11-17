import nmap

def Get_Open_Ports(IP):
    open_ports = []
    scanner = nmap.PortScanner()
    scanner.scan(hosts = IP, ports = "1-65535", arguments="-sT -sV")
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




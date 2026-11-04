import nmap

def Port_Checker(IP):
    n_map = nmap.PortScanner()
    result = n_map.scan(IP, '21')
    return result

#Library Imports

import socket
import sys 
from urllib.parse import urlsplit
from concurrent.futures import ThreadPoolExecutor, as_completed

#Scripts
import port.port_getter as port_getter
import port.port_analyzer as port_analyzer
#import port_getter
#import port_analyzer
from tls_certificate_retriever import GetCertificate
from tls_vulnerability_analyzer import Analyze_Certificate  
from vulnerable_localhost import main as Start_Test_Website  

import time


def Get_IP(URL):
    hostname = urlsplit(URL).hostname
    ip = socket.gethostbyname(hostname)
    return ip

def Port_Analyzer(IP):
    port_range = "1-65535"

    start_time = time.perf_counter()
    open_ports = port_getter.Get_Open_Ports(IP, str(port_range))
    end_time = time.perf_counter()
    for port in open_ports:
        print(port)
    print(f"Time took: {end_time - start_time} seconds")

    port_analysis = port_analyzer.Analyze_Ports(open_ports)

    for analysis in port_analysis:
        print(analysis)


def TLS_Analyzer(URL):
    certificate = GetCertificate(URL)
    analysis = Analyze_Certificate(certificate)
    return analysis


def main(URL):    
    print("Running...")
    ip = Get_IP(URL)

    results = {}
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        scans = {
            executor.submit(Port_Analyzer, str(ip)): "ports",
            executor.submit(TLS_Analyzer, str(URL)): "tls",
        }

    for future in as_completed(scans):
        scan_name = scans[future]

        try:
            results[scan_name] = future.result()
            print(f"{scan_name} scan completed")
        except Exception as error:
            results[scan_name] = {"error": str(error)}
            print(f"{scan_name} scan failed: {error}")

    print(results)


if __name__ == "__main__":  
    if len(sys.argv) > 1 and sys.argv[1] == "--test-server":  
        Start_Test_Website()  
    else:  
        URL = sys.argv[1] if len(sys.argv) > 1 else "https://localhost:8443"  
        main(URL)  

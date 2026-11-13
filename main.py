import socket
import sys 
from urllib.parse import urlsplit

import port_getter
import port_analyzer
from tls_certificate_retriever import GetCertificate
from tls_vulnerability_analyzer import Analyze_Certificate  
from vulnerable_localhost import main as Start_Test_Website  

import time


def Get_IP(URL):
    hostname = urlsplit(URL).hostname
    ip = socket.gethostbyname(hostname)
    return ip


def main(URL):
    print("Running...")
    print(f"Target URL: {URL}")

    print("\nTLS Certificate")

    try:
        certificate = GetCertificate(URL)
        analysis = Analyze_Certificate(certificate)

    except (ValueError, RuntimeError) as error:
        print(f"Certificate retrieval failed: {error}")

    port_range = "1-65535"

    start_time = time.perf_counter()
    open_ports = port_getter.Get_Open_Ports("127.0.0.1", str(port_range))
    end_time = time.perf_counter()
    for port in open_ports:
        print(port)
    print(f"Time took: {end_time - start_time} seconds")

    port_analysis = port_analyzer.Analyze_Ports(open_ports)

    for analysis in port_analysis:
        print(analysis)


#neenerneenerneener
if __name__ == "__main__":  
    if len(sys.argv) > 1 and sys.argv[1] == "--test-server":  
        Start_Test_Website()  
    else:  
        URL = sys.argv[1] if len(sys.argv) > 1 else "https://localhost:8443"  
        main(URL)

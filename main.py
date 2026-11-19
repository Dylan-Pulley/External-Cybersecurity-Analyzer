
#Library Imports
import socket
import sys 
from urllib.parse import urlsplit
from concurrent.futures import ThreadPoolExecutor, as_completed

#Scripts
import port.port_getter as port_getter
import port.port_analyzer as port_analyzer
from tls.tls_certificate_retriever import GetCertificate
from tls.tls_vulnerability_analyzer import Analyze_Certificate

#Test Imports
import time


def Get_IP(URL):
    hostname = urlsplit(URL if "://" in URL else "https://" + URL).hostname  #need to find http in url
    ip = socket.gethostbyname(hostname)
    return ip

def Port_Analyzer(IP):
    start_time = time.perf_counter()
    open_ports = port_getter.Get_Open_Ports(IP)
    end_time = time.perf_counter()
    for port in open_ports:
        print(port)
    print(f"Time took: {end_time - start_time} seconds")

    port_analysis = port_analyzer.Analyze_Ports(open_ports)

    for analysis in port_analysis:
        print(analysis)
    return port_analysis


def TLS_Analyzer(URL):
    certificate = GetCertificate(URL)
    if certificate is None:  #checking for tls validity on either http or https
        hostname = urlsplit(URL).hostname  
        return {  
            "check": "tls_certificate_expiration",  
            "status": "HTTPS_UNAVAILABLE",  
            "is_expired": None,  
            "message": f"HTTP does not use TLS. No HTTPS certificate was available at {hostname}:443."  
        }  #added ends here
    analysis = Analyze_Certificate(certificate)
    return analysis

def main(URL):
    print("Running...")
    ip = Get_IP(URL)

    with ThreadPoolExecutor(max_workers=2) as executor:
        scans = {
            executor.submit(Port_Analyzer, str(ip)): "ports",
            executor.submit(TLS_Analyzer, str(URL)): "tls",
        }

        for future in as_completed(scans):
            scan_name = scans[future]

            try:
                result = future.result()
                print(f"{scan_name} scan completed")
            except Exception as error:
                result = {"error": str(error)}
                print(f"{scan_name} scan failed: {error}")

            yield {
                "scan": scan_name,
                "result": result
            }

#Hosted Movie Website Address "http://127.0.0.1:5000"
if __name__ == "__main__":  
    #main(sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5000")  #for test site

    
    main("http://scanme.nmap.org")

    
    '''
    if len(sys.argv) > 1 and sys.argv[1] == "--test-server":  
        Start_Test_Website()  
    else:  
        URL = sys.argv[1] if len(sys.argv) > 1 else "https://localhost:8443" 
        main(URL)
    '''

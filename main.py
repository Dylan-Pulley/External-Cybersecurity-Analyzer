import socket
from urllib.parse import urlsplit

#Scripts
import port.port_getter as port_getter
import port.port_analyzer as port_analyzer

#Test
import time

def Get_IP(URL):
    hostname = urlsplit(URL).hostname
    ip = socket.gethostbyname(hostname)
    return ip

def Port_Analyzer():
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


def main(URL):    
    print("Running...")
    Port_Analyzer()





main("http://127.0.0.1:5000")
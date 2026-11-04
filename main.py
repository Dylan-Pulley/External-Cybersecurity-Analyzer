import socket
from urllib.parse import urlsplit

#Scripts
import port_analyzer

def Get_IP(URL):
    hostname = urlsplit(URL).hostname
    ip = socket.gethostbyname(hostname)
    return ip

def main(URL):
    current_ip = Get_IP(URL)
    
    port_result = port_analyzer.Port_Checker(current_ip)
    
    print(f"Current IP: {current_ip}\nPort Result: {port_result}")



main("http://127.0.0.1:5000")
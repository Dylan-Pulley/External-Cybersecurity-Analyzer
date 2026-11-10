import json
from pathlib import Path

SENSITIVE_SERVICE_PATH = (Path(__file__).resolve().parent.parent/ "config"/ "ports"/ "sensitive_services.json")
FALLBACK_PATH = (Path(__file__).resolve().parent.parent/ "config"/ "ports"/ "port_fallbacks.json")

def Load_Rules():
    with open(SENSITIVE_SERVICE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)

def Load_Fallback_Rules():
    with open(FALLBACK_PATH, "r", encoding="utf-8") as file:
            return json.load(file)

def Analyze_Ports(OPEN_PORTS):
    rules = Load_Rules()
    fallback = Load_Fallback_Rules()
    analyzed_results = []
    for port in OPEN_PORTS:
        if port["service"].lower() in rules:
            analyzed_port_object = {
                "port": port["port"],
                "service": port["service"],
                **rules[port["service"]]
            }
        else:
            analyzed_port_object = {
                "port": port["port"],
                "service": "empty_service",
                **fallback["empty_service"]
            }
        
        analyzed_results.append(analyzed_port_object)
    return(analyzed_results)
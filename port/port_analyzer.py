import json
from pathlib import Path
import port.load_iana_ports as iana_ports 

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
    iana_port_list = iana_ports.load_iana_ports()
    analyzed_results = []

    for port in OPEN_PORTS:
        number = int(port["port"])
        scanner_service = (port.get("service") or "").strip()
        service_key = scanner_service.lower()
        result = {"port": number, "service": scanner_service}

        if service_key in rules:
             result.update(rules[service_key])

        elif service_key and service_key != "unknown":
             result.update(fallback["no_matching_rule"])

        else:
            iana_names = iana_port_list.get((number, "tcp"))

            if iana_names:
                likely_service = ", ".join(sorted(iana_names))
                result.update(
                    service=likely_service,
                    service_source="iana",
                    status="informational",
                    severity="unknown",
                    description=f"IANA lists {likely_service} for TCP port {number}.",
                    recommendation="Verify which application is listening and whether access is intended",
                )
            else:
                result["service"] = "empty_service"
                result.update(fallback["empty_service"])
            
        analyzed_results.append(result)
    return(analyzed_results)
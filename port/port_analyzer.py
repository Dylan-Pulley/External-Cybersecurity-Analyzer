import json
from pathlib import Path
import port.load_iana_ports as iana_ports 

SENSITIVE_SERVICE_PATH = (Path(__file__).resolve().parent.parent/ "config"/ "ports"/ "sensitive_services.json")
FALLBACK_PATH = (Path(__file__).resolve().parent.parent/ "config"/ "ports"/ "port_fallbacks.json")

def Load_Json_Object(path):
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except OSError as exc:
        raise ValueError(f"Could not read {path.name}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path.name} must be encoded as UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{path.name}, line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a JSON object")

    return data

def Load_Rules():
    return Load_Json_Object(SENSITIVE_SERVICE_PATH)

def Load_Fallback_Rules():
    return Load_Json_Object(FALLBACK_PATH)

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
                    severity="unknown",
                    description=f"IANA lists {likely_service} for TCP port {number}.",
                    recommendation="Verify which application is listening and whether access is intended",
                )
            else:
                result["service"] = "empty_service"
                result.update(fallback["empty_service"])
            
        analyzed_results.append(result)
    return(analyzed_results)
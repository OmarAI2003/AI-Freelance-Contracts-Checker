import json

def handler(event):
    return {
        "risk_level": "HIGH",
        "contract_type": "service_agreement",
        "risks": [{
            "clause": "Payment Terms",
            "issue": "Upfront payment detected",
            "severity": "HIGH"
        }],
        "scam_indicators": ["Upfront payment requirement"],
        "status": "Container working"
    }
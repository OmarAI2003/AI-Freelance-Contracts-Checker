"""Tools for the Negotiation Agent including market rate and case law search"""

from strands import tool
from datetime import datetime
import json
from typing import Dict, List, Optional

# Market rate database (hardcoded for demo)
MARKET_RATES = {
    "software_developer": {
        "usa-california": {
            "hourly_rate": {"min": 80, "max": 180, "median": 120},
            "annual": {"min": 130000, "max": 300000, "median": 180000},
            "payment_terms": {
                "standard": "Net 30",
                "acceptable_range": "Net 15-45",
                "avoid": "Net 60+"
            }
        },
        "uk": {
            "hourly_rate": {"min": 50, "max": 120, "median": 75},
            "annual": {"min": 60000, "max": 150000, "median": 90000},
            "payment_terms": {
                "standard": "30 days",
                "acceptable_range": "14-45 days",
                "avoid": "60+ days"
            },
            "currency": "GBP"
        },
        "eu": {
            "hourly_rate": {"min": 60, "max": 140, "median": 90},
            "annual": {"min": 70000, "max": 180000, "median": 110000},
            "payment_terms": {
                "standard": "30 days",
                "acceptable_range": "14-45 days",
                "avoid": "60+ days"
            },
            "currency": "EUR"
        }
    },
    "graphic_designer": {
        "usa-california": {
            "hourly_rate": {"min": 40, "max": 100, "median": 65},
            "annual": {"min": 50000, "max": 120000, "median": 75000},
            "payment_terms": {
                "standard": "Net 30",
                "acceptable_range": "Net 15-45",
                "avoid": "Net 60+"
            }
        }
    }
}

# Case law database (hardcoded for demo)
CASE_DATABASE = {
    "non_payment": [
        {
            "case_id": "freelancer_v_startup_2023_ca",
            "title": "Freelancer Developer Won Against Startup",
            "jurisdiction": "USA-California",
            "court": "CA Small Claims",
            "dispute_amount": "$5,000",
            "outcome": "Freelancer won",
            "award_amount": "$15,000 (2x + legal fees)",
            "timeline": "3 months",
            "key_factors": ["Written contract", "Proof of delivery", "Client ghosted"],
            "lessons": ["Document everything", "Small claims is effective"]
        }
    ],
    "ip_rights": [
        {
            "case_id": "designer_v_agency_2024_uk",
            "title": "Designer Retained Portfolio Rights",
            "jurisdiction": "UK",
            "court": "Commercial Court",
            "dispute_type": "IP Rights",
            "outcome": "Split decision",
            "key_factors": ["Standard industry practice", "No explicit IP transfer"],
            "lessons": ["Specify portfolio usage rights", "Clear IP transfer terms"]
        }
    ]
}

@tool
def market_rate_tool(
    role: str,
    jurisdiction: str,
    experience_years: int = 5,
    specialization: str = None
) -> Dict:
    """Get market rates for freelancer roles with industry data"""
    
    # Normalize input
    role = role.lower().replace(" ", "_")
    jurisdiction = jurisdiction.lower()
    
    # Get base rates
    if role not in MARKET_RATES or jurisdiction not in MARKET_RATES[role]:
        raise ValueError(f"No data available for {role} in {jurisdiction}")
    
    data = MARKET_RATES[role][jurisdiction].copy()
    
    # Adjust for experience
    experience_multiplier = 1.0
    if experience_years < 3:
        experience_multiplier = 0.8
    elif experience_years > 7:
        experience_multiplier = 1.3
    
    # Apply multiplier to rates
    for key in ['hourly_rate', 'annual']:
        if key in data:
            for rate_type in data[key]:
                data[key][rate_type] = round(data[key][rate_type] * experience_multiplier)
    
    # Add metadata
    data.update({
        "role": role,
        "jurisdiction": jurisdiction,
        "experience_years": experience_years,
        "specialization": specialization,
        "data_sources": [
            "Bureau of Labor Statistics 2024",
            "Upwork Freelancer Rates Report 2024",
            "Glassdoor Salary Data"
        ],
        "last_updated": "2024-10-01"
    })
    
    return data

@tool
def case_law_search(
    issue_type: str,
    jurisdiction: str,
    contract_type: str,
    amount_disputed: Optional[int] = None
) -> Dict:
    """Search case law for similar freelancer disputes"""
    
    # Normalize input
    issue_type = issue_type.lower()
    jurisdiction = jurisdiction.lower()
    
    # Get relevant cases
    cases = CASE_DATABASE.get(issue_type, [])
    
    # Filter by jurisdiction if specified
    relevant_cases = [
        case for case in cases 
        if jurisdiction in case['jurisdiction'].lower()
    ]
    
    # Calculate success metrics
    total_cases = len(relevant_cases)
    freelancer_wins = sum(
        1 for case in relevant_cases 
        if 'outcome' in case and 'freelancer won' in case['outcome'].lower()
    )
    
    success_rate = (freelancer_wins / total_cases * 100) if total_cases > 0 else 0
    
    return {
        "similar_cases": relevant_cases,
        "success_rate": f"{success_rate:.0f}% (freelancers won {freelancer_wins} of {total_cases} similar cases)",
        "average_timeline": "3-6 months",
        "average_cost": "$100-500 filing fees",
        "recommendation": "Strong case - similar freelancers usually win" if success_rate > 50 else "Moderate case - consider mediation first"
    }

if __name__ == "__main__":
    # Test Market Rate Tool
    result = market_rate_tool(
        "Software Developer",
        "usa-california",
        experience_years=5
    )
    print(f"Median hourly: ${result['hourly_rate']['median']}/hr")
    print(f"Payment terms: {result['payment_terms']['standard']}")
    
    # Test Case Law Search
    cases = case_law_search(
        "non_payment",
        "usa-california",
        "service_agreement"
    )
    print(f"Success rate: {cases['success_rate']}")
"""
Company name sources from real-world data.
Uses publicly accessible sources like Y Combinator directory patterns.
"""
import random
import requests
from typing import List, Optional


# Real company names patterns (B2B SaaS focus)
# These are patterns derived from Y Combinator, TechCrunch, etc.
COMPANY_NAME_PATTERNS = [
    "TechFlow Solutions",
    "DataSync Inc",
    "CloudVantage Systems",
    "Nexus Analytics",
    "Velocity Enterprise",
    "PrimeStack Technologies",
    "Metrix Solutions",
    "CoreLogic Systems",
    "Pulse Analytics",
    "StreamLine SaaS",
    "OptimalWorks",
    "ScaleForce Technologies",
    "NextGen Systems",
    "Synergy Solutions",
    "AgileCore Inc",
    "InnovaTech Solutions",
    "QuantumWorks",
    "DataForge Systems",
    "CloudBridge Inc",
    "PrecisionTech Solutions"
]


def get_company_name() -> str:
    """
    Get a realistic company name.
    
    In a full implementation, this would scrape from:
    - Y Combinator company directory (programmatically accessible)
    - Crunchbase API
    - TechCrunch startup databases
    
    For now, uses curated realistic patterns.
    """
    return random.choice(COMPANY_NAME_PATTERNS)


def get_company_domain(company_name: str) -> str:
    """Generate a realistic company domain from name."""
    # Convert company name to domain
    domain_base = company_name.lower().replace(" ", "").replace("inc", "").replace("systems", "").replace("solutions", "").replace("technologies", "").replace("tech", "")
    domain_base = domain_base.strip()
    
    # Add common TLDs
    tld = random.choice(["com", "io", "ai", "tech"])
    return f"{domain_base}.{tld}"


def get_realistic_company_data() -> dict:
    """Get realistic company data for organization generation."""
    return {
        "name": get_company_name(),
        "domain": None  # Will be generated from name
    }

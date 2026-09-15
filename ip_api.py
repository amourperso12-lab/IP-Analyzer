import os
import requests
from dotenv import load_dotenv

load_dotenv()

ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY")


def analyser_ip(ip_address):
    """Interroge AbuseIPDB pour récupérer la réputation d'une IP."""

    if not ABUSEIPDB_API_KEY:
        return {
            "success": False,
            "error": "Clé API AbuseIPDB manquante dans le fichier .env."
        }

    url = "https://api.abuseipdb.com/api/v2/check"

    headers = {
        "Accept": "application/json",
        "Key": ABUSEIPDB_API_KEY
    }

    params = {
        "ipAddress": ip_address,
        "maxAgeInDays": 90
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json().get("data", {})

        return {
            "success": True,
            "ip_address": data.get("ipAddress"),
            "country": data.get("countryCode"),
            "organization": data.get("isp") or data.get("domain"),
            "ip_type": data.get("usageType") or "Inconnu",
            "abuse_score": data.get("abuseConfidenceScore", 0),
            "total_reports": data.get("totalReports", 0)
        }

    except requests.RequestException as e:
        return {
            "success": False,
            "error": f"Erreur AbuseIPDB : {e}"
        }
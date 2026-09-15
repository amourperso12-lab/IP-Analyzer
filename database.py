import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Variables Supabase manquantes dans le fichier .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def enregistrer_recherche(ip_data):
    """Enregistre une analyse IP dans Supabase."""

    donnees = {
        "ip_address": ip_data["ip_address"],
        "country": ip_data.get("country"),
        "organization": ip_data.get("organization"),
        "ip_type": ip_data.get("ip_type"),
        "risk_score": ip_data.get("risk_score"),
        "risk_status": ip_data.get("risk_status"),
    }

    return supabase.table("ip_searches").insert(donnees).execute()


def obtenir_historique():
    """Récupère les dernières recherches IP."""

    return (
        supabase
        .table("ip_searches")
        .select("*")
        .order("analysis_date", desc=True)
        .execute()
    )
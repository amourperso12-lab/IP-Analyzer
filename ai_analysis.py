import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY absente du fichier .env")

client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options=types.HttpOptions(
        timeout=20000
    )
)

MODELES_GEMINI = [
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
]


def analyser_avec_ia(ip_data, score, statut, nombre_signalements=0):
    """
    Utilise Gemini pour analyser les résultats de l'analyse IP.
    Si le premier modèle échoue ou dépasse 10 secondes,
    le deuxième modèle est automatiquement utilisé.
    """

    prompt = f"""
Tu es un assistant de cybersécurité intégré à une application appelée IP Analyzer.

Analyse uniquement les informations fournies ci-dessous.
Ne fabrique aucune information et ne prétends pas avoir effectué une analyse supplémentaire.

Adresse IP : {ip_data.get("ip_address", "Inconnue")}
Pays : {ip_data.get("country", "Inconnu")}
Organisation : {ip_data.get("organization", "Inconnue")}
Type : {ip_data.get("ip_type", "Inconnu")}
Score de risque AbuseIPDB : {score}/100
Statut : {statut}
Nombre de signalements : {nombre_signalements}

Rédige une analyse courte et professionnelle en français.

Explique :
1. Ce que signifie le score obtenu.
2. Ce que peuvent indiquer les signalements.
3. Le rôle de l'organisation et du type d'adresse IP.
4. Les précautions ou vérifications de sécurité recommandées.

Important :
- Un score élevé n'est pas une preuve absolue de comportement malveillant.
- Un score faible ne garantit pas qu'une IP est totalement sûre.
- Présente les résultats comme des indicateurs.
- N'invente aucune donnée.
"""

    for modele in MODELES_GEMINI:

        try:
            print(f"Gemini : tentative avec {modele}")

            response = client.models.generate_content(
                model=modele,
                contents=prompt
            )

            if response.text:
                print(f"Gemini : succès avec {modele}")
                return response.text.strip()

            print(f"Gemini : aucun résultat avec {modele}")

        except Exception as e:
            print(f"Gemini : échec avec {modele} : {e}")
            continue

    print("Gemini : tous les modèles sont indisponibles.")

    return (
        "L'analyse IA est temporairement indisponible. "
        "Les résultats techniques de l'adresse IP restent disponibles."
    )


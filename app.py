from flask import Flask, render_template, request, jsonify
from ipaddress import ip_address
from datetime import datetime
import threading

from ip_api import analyser_ip
from risk import calculer_risque
from database import enregistrer_recherche, obtenir_historique
from ai_analysis import analyser_avec_ia


app = Flask(__name__)

# Stockage temporaire des analyses IA
analyses_ia = {}


def lancer_analyse_ia(ip_address_value, resultat_api, score, statut, total_reports):
    """Lance Gemini en arrière-plan sans bloquer Flask."""

    try:
        analyse = analyser_avec_ia(
            resultat_api,
            score,
            statut,
            total_reports
        )

        analyses_ia[ip_address_value] = {
            "status": "completed",
            "analysis": analyse
        }

    except Exception as e:
        print(f"Erreur analyse IA : {e}")

        analyses_ia[ip_address_value] = {
            "status": "error",
            "analysis": (
                "L'analyse IA est temporairement indisponible. "
                "Les résultats techniques restent disponibles."
            )
        }


@app.route("/", methods=["GET", "POST"])
def index():
    resultat = None
    erreur = None

    if request.method == "POST":
        ip_saisie = request.form.get("ip", "").strip()

        # Validation de l'adresse IP
        try:
            ip_address(ip_saisie)

        except ValueError:
            erreur = "Adresse IP invalide."

        else:
            # Analyse AbuseIPDB
            resultat_api = analyser_ip(ip_saisie)

            if not resultat_api.get("success"):
                erreur = resultat_api.get(
                    "error",
                    "Impossible d'analyser cette adresse IP."
                )

            else:
                # Calcul du risque
                score, statut = calculer_risque(resultat_api)

                total_reports = resultat_api.get("total_reports", 0)

                resultat = {
                    **resultat_api,
                    "risk_score": score,
                    "risk_status": statut,
                    "total_reports": total_reports,
                    "analysis_date": datetime.now().strftime(
                        "%d/%m/%Y %H:%M:%S"
                    ),
                    "ai_analysis": (
                        "Analyse IA en cours..."
                    )
                }

                # Préparation du statut IA
                analyses_ia[ip_saisie] = {
                    "status": "processing",
                    "analysis": "Analyse IA en cours..."
                }

                # Lancement de Gemini en arrière-plan
                thread = threading.Thread(
                    target=lancer_analyse_ia,
                    args=(
                        ip_saisie,
                        resultat_api,
                        score,
                        statut,
                        total_reports
                    ),
                    daemon=True
                )

                thread.start()

                # Enregistrement Supabase
                try:
                    enregistrer_recherche(resultat)

                except Exception as e:
                    print(f"Erreur Supabase : {e}")

    # Récupération de l'historique
    try:
        historique = obtenir_historique().data

    except Exception as e:
        print(f"Erreur historique Supabase : {e}")
        historique = []

    return render_template(
        "index.html",
        resultat=resultat,
        erreur=erreur,
        historique=historique
    )


@app.route("/api/ai/<path:ip_address_value>")
def obtenir_analyse_ia(ip_address_value):
    """Retourne le statut de l'analyse Gemini."""

    resultat = analyses_ia.get(ip_address_value)

    if not resultat:
        return jsonify({
            "status": "not_found",
            "analysis": "Analyse IA introuvable."
        })

    return jsonify(resultat)


if __name__ == "__main__":
    app.run(debug=True)
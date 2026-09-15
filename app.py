from flask import Flask, render_template, request
from ipaddress import ip_address
from datetime import datetime

from ip_api import analyser_ip
from risk import calculer_risque
from database import enregistrer_recherche, obtenir_historique


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    resultat = None
    erreur = None

    if request.method == "POST":
        ip_saisie = request.form.get("ip", "").strip()

        # Vérification de l'adresse IP
        try:
            ip_address(ip_saisie)
        except ValueError:
            erreur = "❌ L'adresse IP saisie n'est pas valide."
            historique = obtenir_historique().data
            return render_template(
                "index.html",
                resultat=resultat,
                erreur=erreur,
                historique=historique
            )

        # Interrogation de l'API
        resultat_api = analyser_ip(ip_saisie)

        if not resultat_api.get("success"):
            erreur = resultat_api.get(
                "error",
                "Impossible d'analyser cette adresse IP."
            )

            historique = obtenir_historique().data

            return render_template(
                "index.html",
                resultat=resultat,
                erreur=erreur,
                historique=historique
            )

        # Calcul du risque
        score, statut = calculer_risque(resultat_api)

        resultat_api["risk_score"] = score
        resultat_api["risk_status"] = statut
        resultat_api["analysis_date"] = datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S"
        )

        # Enregistrement dans Supabase
        try:
            enregistrer_recherche(resultat_api)
        except Exception as e:
            print(f"Erreur Supabase : {e}")
            erreur = (
                "⚠️ L'analyse a fonctionné, "
                "mais l'enregistrement dans Supabase a échoué."
            )

        resultat = resultat_api

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


if __name__ == "__main__":
    app.run(debug=True)
def calculer_risque(ip_data):
    """
    Utilise le score de confiance AbuseIPDB
    comme niveau de risque entre 0 et 100.
    """

    score = int(ip_data.get("abuse_score", 0) or 0)

    if score >= 80:
        statut = "CRITIQUE"
    elif score >= 60:
        statut = "RISQUÉ"
    elif score >= 30:
        statut = "MOYEN"
    else:
        statut = "FAIBLE"

    return score, statut
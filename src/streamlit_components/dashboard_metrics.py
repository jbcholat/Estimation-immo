#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Component: Dashboard métriques estimation
US2 - Voir estimation + score fiabilité
"""

import streamlit as st
from typing import Dict, Optional


def render_dashboard_metrics(estimation_result: Dict) -> None:
    """
    Affiche le dashboard d'estimation avec métriques et score fiabilité.

    Args:
        estimation_result: Dict retourné par EstimationAlgorithm.estimate()
    """

    if not estimation_result or not estimation_result.get('success'):
        st.error("❌ Estimation invalide ou échouée")
        if estimation_result.get('erreur'):
            st.info(f"Détail: {estimation_result['erreur']}")
        return

    # Extraction données
    estimation = estimation_result.get('estimation', {})
    fiabilite = estimation_result.get('fiabilite', {})
    bien = estimation_result.get('bien', {})
    nb_comparables = estimation_result.get('nb_comparables_utilises', 0)

    prix_estime = estimation.get('prix_estime_eur')
    prix_min = estimation.get('prix_min_eur')
    prix_max = estimation.get('prix_max_eur')
    prix_au_m2 = estimation.get('prix_au_m2_eur')

    score_global = fiabilite.get('score_global', 0)
    evaluation = fiabilite.get('evaluation', 'Inconnue')

    # === SECTION 1 : ESTIMATION ===
    st.markdown("## 💰 Estimation")

    # Colonnes principales
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="💵 Prix estimé",
            value=f"{prix_estime:,.0f}€" if prix_estime else "N/A",
            help="Estimation basée sur comparables"
        )

    with col2:
        st.metric(
            label="📊 Prix au m²",
            value=f"{prix_au_m2:,.0f}€/m²" if prix_au_m2 else "N/A",
            help="Prix par m² habitable"
        )

    with col3:
        st.metric(
            label="🎯 Nb comparables",
            value=nb_comparables,
            help="Nombre de comparables utilisés pour l'estimation"
        )

    # Intervalle de confiance
    st.markdown("### Intervalle de confiance")
    col1, col2 = st.columns(2)

    with col1:
        st.info(f"🔻 **Prix minimum**: {prix_min:,.0f}€ (25e percentile)")

    with col2:
        st.info(f"🔺 **Prix maximum**: {prix_max:,.0f}€ (75e percentile)")

    st.markdown("---")

    # === SECTION 2 : FIABILITÉ ===
    st.markdown("## 🔒 Score de fiabilité")

    # Score global avec progress bar
    col1, col2 = st.columns([2, 1])

    with col1:
        # Progress bar
        st.progress(min(score_global / 100, 1.0))

    with col2:
        # Score textuel
        st.markdown(f"### {score_global}/100")

    # Évaluation
    if evaluation == "Excellente":
        color = "🟢"
    elif evaluation == "Bonne":
        color = "🟡"
    elif evaluation == "Moyenne":
        color = "🟠"
    else:
        color = "🔴"

    st.markdown(f"**Évaluation**: {color} {evaluation}")

    # Breakdown 4 composantes
    st.markdown("### Détail des composantes")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        vol_score = fiabilite.get('volume', 0)
        st.metric(
            label="📈 Volume",
            value=f"{vol_score}/30",
            help="Nombre comparables (30=10+, 25=5-9, 15=3-4, 5=1-2)"
        )

    with col2:
        sim_score = fiabilite.get('similarite', 0)
        st.metric(
            label="🎯 Similarité",
            value=f"{sim_score}/30",
            help="Score moyen comparables (30=≥80%, 25=≥75%, 15=≥70%)"
        )

    with col3:
        disp_score = fiabilite.get('dispersion', 0)
        st.metric(
            label="📊 Dispersion",
            value=f"{disp_score}/25",
            help="Variance prix (25=<15%, 20=<25%, 10=<40%)"
        )

    with col4:
        anc_score = fiabilite.get('anciennete', 0)
        st.metric(
            label="⏰ Ancienneté",
            value=f"{anc_score}/15",
            help="Fraîcheur données (15=<12m, 12=<24m, 8=<36m)"
        )

    st.markdown("---")

    # === SECTION 3 : BIEN ESTIMÉ ===
    st.markdown("## 🏠 Bien estimé")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(f"**Type**: {bien.get('type', 'N/A')}")

    with col2:
        st.info(f"**Surface**: {bien.get('surface_m2', 'N/A'):.1f}m²")

    with col3:
        st.info(f"**Coordonnées**: {bien.get('latitude', 0):.4f}°, {bien.get('longitude', 0):.4f}°")

    st.markdown("---")

    # === SECTION 4 : INTERPRÉTATION ===
    st.markdown("## 📖 Interprétation")

    if score_global >= 80:
        interp = (
            "✅ **Estimation très fiable**\n\n"
            "Vous pouvez faire confiance à cette estimation. "
            "L'algorithme a trouvé nombreux comparables similaires et récents."
        )
    elif score_global >= 65:
        interp = (
            "✅ **Estimation fiable**\n\n"
            "L'estimation est basée sur des comparables pertinents. "
            "À valider auprès de votre équipe d'experts."
        )
    elif score_global >= 50:
        interp = (
            "⚠️ **Estimation à valider**\n\n"
            "L'algorithme a trouvé des comparables mais avec certaines limitations. "
            "Recommandé de faire une analyse manuelle complémentaire."
        )
    else:
        interp = (
            "❌ **Estimation peu fiable**\n\n"
            "Données insuffisantes ou peu pertinentes. "
            "Procédez à une évaluation manuelle complète."
        )

    st.markdown(interp)

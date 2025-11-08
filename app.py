#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Estimateur Immobilier MVP - Streamlit Application
Phase 4 - Interface principale avec architecture hybride (Tabs)

Stack: Supabase + Google Maps + Streamlit + Folium + ReportLab
Zone: Chablais/Annemasse, Haute-Savoie (74)
"""

import streamlit as st
import pandas as pd
import logging
from datetime import datetime

from src.utils.config import Config
from src.supabase_data_retriever import SupabaseDataRetriever
from src.estimation_algorithm import EstimationAlgorithm
from src.streamlit_components.form_input import render_form_input, get_well_params
from src.streamlit_components.dashboard_metrics import render_dashboard_metrics
from src.streamlit_components.comparables_table import render_comparables_table
from src.streamlit_components.map_viewer import render_map_viewer
from src.streamlit_components.pdf_export import render_pdf_export

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===================================
# CONFIGURATION STREAMLIT
# ===================================

st.set_page_config(
    page_title="Estimation Immobilière 74",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
        border-bottom: 3px solid #1f77b4;
    }
    .info-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# ===================================
# CACHE & CONNEXIONS
# ===================================

@st.cache_resource(show_spinner=False)
def init_supabase_retriever():
    """Initialiser connexion Supabase (cache)"""
    logger.info("[INFO] Initialisation Supabase...")
    try:
        retriever = SupabaseDataRetriever()
        if retriever.test_connection():
            logger.info("[OK] Connexion Supabase OK")
            return retriever
        else:
            logger.error("[ERROR] Connexion Supabase echouee")
            # Return retriever anyway - it will work when called
            return retriever
    except Exception as e:
        logger.error(f"[ERROR] Exception Supabase: {e}")
        return None


@st.cache_resource
def init_estimation_algorithm():
    """Initialiser algorithme estimation"""
    logger.info("[INFO] Initialisation EstimationAlgorithm...")
    return EstimationAlgorithm()


# ===================================
# SESSION STATE INITIALIZATION
# ===================================

if 'geocoded_address' not in st.session_state:
    st.session_state['geocoded_address'] = None
if 'coordinates' not in st.session_state:
    st.session_state['coordinates'] = None
if 'bien_params' not in st.session_state:
    st.session_state['bien_params'] = None
if 'comparables_df' not in st.session_state:
    st.session_state['comparables_df'] = None
if 'estimation_result' not in st.session_state:
    st.session_state['estimation_result'] = None
if 'comparables_filtered' not in st.session_state:
    st.session_state['comparables_filtered'] = None

# ===================================
# TITRE PRINCIPAL
# ===================================

st.markdown(
    '<h1 class="main-header">🏠 Estimation Immobilière Chablais/Annemasse</h1>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="info-box">
<b>ℹ️ MVP Phase 4</b> - Estimez le prix d'un bien immobilier en Haute-Savoie (74)
basé sur transactions similaires (DVF+) et algorithme de scoring multi-critères.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ===================================
# SIDEBAR - FORMULAIRE + PARAMÈTRES
# ===================================

with st.sidebar:
    st.markdown("### ⚙️ Paramètres de recherche")

    # Paramètres globaux
    rayon_km = st.slider(
        "Rayon de recherche (km)",
        min_value=3,
        max_value=20,
        value=10,
        step=1,
        help="Distance maximale pour chercher comparables"
    )

    anciennete_max_ans = st.slider(
        "Ancienneté max transactions (ans)",
        min_value=1,
        max_value=10,
        value=3,
        step=1,
        help="Transactions max de X ans"
    )

    surface_tolerance_pct = st.slider(
        "Tolérance surface (%)",
        min_value=10,
        max_value=50,
        value=20,
        step=5,
        help="±X% de la surface saisie"
    )

    st.markdown("---")

    # Formulaire saisie bien
    well_params = render_form_input(sidebar=True)

    if well_params:
        # Stocker dans session_state si pas déjà
        if st.session_state['bien_params'] is None:
            st.session_state['bien_params'] = well_params

# ===================================
# MAIN CONTENT - CONTRÔLE FLUX
# ===================================

# Vérifier si bien saisie dans session_state
if st.session_state['bien_params'] is None:
    # Pas d'estimation = afficher message accueil
    st.markdown("""
    ## 👋 Bienvenue !

    **Commencer:**
    1. Remplissez le formulaire dans la **barre latérale** (adresse, type, surface)
    2. Cliquez sur **"🚀 Estimer"**
    3. Explorez les **3 onglets** : Estimation → Comparables → Carte

    **Zone couverte:** Chablais + Annemasse, Haute-Savoie (codes postaux 740xx, 742xx, 743xx)

    **Données:** 56,000+ transactions DVF+ (2014-2025)
    """)

else:
    # Bien saisie = effectuer estimation
    bien_params = st.session_state['bien_params']

    # Contrôle d'initialisation des services
    try:
        retriever = init_supabase_retriever()
        estimator = init_estimation_algorithm()

        if retriever is None or estimator is None:
            st.error("[ERROR] Erreur initialisation services. Verifiez configuration.")
            st.stop()

    except Exception as e:
        st.error(f"[ERROR] Erreur initialisation: {e}")
        logger.error(f"Init error: {e}")
        st.stop()

    # Récupérer comparables depuis Supabase
    if st.session_state['comparables_df'] is None:
        with st.spinner("Recherche comparables en cours..."):
            try:
                comparables_df = retriever.get_comparables(
                    latitude=bien_params['latitude'],
                    longitude=bien_params['longitude'],
                    type_bien=bien_params['type_bien'],
                    surface_min=bien_params['surface'] * (1 - surface_tolerance_pct / 100),
                    surface_max=bien_params['surface'] * (1 + surface_tolerance_pct / 100),
                    rayon_km=rayon_km,
                    annees=anciennete_max_ans,
                    limit=50
                )

                st.session_state['comparables_df'] = comparables_df

                if len(comparables_df) > 0:
                    st.success(f"[OK] {len(comparables_df)} comparable(s) trouve(s)")
                else:
                    st.warning("[WARNING] Aucun comparable trouve avec ces criteres")

            except Exception as e:
                st.error(f"[ERROR] Erreur recherche comparables: {e}")
                logger.error(f"Comparables error: {e}")
                st.stop()

    comparables_df = st.session_state['comparables_df']

    # Effectuer estimation
    if st.session_state['estimation_result'] is None and len(comparables_df) > 0:
        with st.spinner("Calcul estimation en cours..."):
            try:
                # Convertir DF en list de dicts pour estimateur
                comparables_list = comparables_df.to_dict('records')

                # Effectuer estimation
                estimation_result = estimator.estimate(
                    target_latitude=bien_params['latitude'],
                    target_longitude=bien_params['longitude'],
                    target_surface=bien_params['surface'],
                    target_type=bien_params['type_bien'],
                    comparables=comparables_list
                )

                st.session_state['estimation_result'] = estimation_result

                # Ajouter les scores au DataFrame des comparables
                if estimation_result.get('success') and estimation_result.get('comparables_with_scores'):
                    comparables_with_scores = pd.DataFrame(estimation_result['comparables_with_scores'])
                    st.session_state['comparables_df'] = comparables_with_scores
                    comparables_df = comparables_with_scores

                if estimation_result.get('success'):
                    st.success("[OK] Estimation calculee")
                else:
                    st.error(f"[ERROR] Erreur estimation: {estimation_result.get('erreur')}")

            except Exception as e:
                st.error(f"[ERROR] Erreur calcul estimation: {e}")
                logger.error(f"Estimation error: {e}")
                st.stop()

    estimation_result = st.session_state['estimation_result']

    # ===================================
    # AFFICHAGE TABS (3 onglets)
    # ===================================

    if estimation_result and estimation_result.get('success'):
        tab1, tab2, tab3 = st.tabs(["📊 Estimation", "📋 Comparables", "🗺️ Carte"])

        # === TAB 1 : ESTIMATION ===
        with tab1:
            render_dashboard_metrics(estimation_result)

            st.markdown("---")

            render_pdf_export(
                estimation_result,
                comparables_df,
                bien_address=bien_params.get('address')
            )

        # === TAB 2 : COMPARABLES ===
        with tab2:
            def recalculate_estimation(latitude, longitude, surface, type_bien, comparables, filtered=False):
                """Callback pour recalcul estimation avec comparables filtrés"""
                estimator = init_estimation_algorithm()
                new_estimation = estimator.estimate(
                    target_latitude=latitude,
                    target_longitude=longitude,
                    target_surface=surface,
                    target_type=type_bien,
                    comparables=comparables
                )
                st.session_state['estimation_result'] = new_estimation
                st.session_state['comparables_filtered'] = comparables

            render_comparables_table(
                comparables_df,
                recalculate_estimation,
                bien_params
            )

        # === TAB 3 : CARTE ===
        with tab3:
            render_map_viewer(
                bien_coords=(bien_params['latitude'], bien_params['longitude']),
                comparables_df=comparables_df,
                rayon_km=rayon_km,
                bien_address=bien_params.get('address')
            )

    else:
        st.error("[ERROR] Impossible d'effectuer l'estimation. Verifiez donnees et comparables.")

# ===================================
# FOOTER
# ===================================

st.markdown("---")
st.markdown("""
<center>
<small>
🏠 <b>Estimateur Immobilier MVP</b> - Chablais/Annemasse (74)<br>
Phase 4 | Supabase + Google Maps + Streamlit | DVF+ 56,000 transactions
</small>
</center>
""", unsafe_allow_html=True)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Component: Tableau comparables avec filtres
US3 - Filtrer comparables manuellement
"""

import streamlit as st
import pandas as pd
from typing import Optional


def render_comparables_table(
    comparables_df: pd.DataFrame,
    estimation_callback: callable,
    bien_params: dict
) -> None:
    """
    Affiche tableau interactif des comparables avec filtres et recalcul.

    Args:
        comparables_df: DataFrame avec colonnes: idmutation, datemut, valeurfonc, sbati, distance_km, score
        estimation_callback: Fonction callback pour recalcul estimation avec comparables filtrés
        bien_params: Dict paramètres bien (pour recalcul)
    """

    if comparables_df is None or len(comparables_df) == 0:
        st.warning("⚠️ Aucun comparable disponible")
        return

    st.markdown("## 📋 Comparables")

    # === SECTION 1 : FILTRES ===
    with st.expander("🔍 Filtres avancés", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            score_min = st.slider(
                "Score minimum",
                min_value=0,
                max_value=100,
                value=40,
                step=5,
                help="Filtrer comparables par score de similarité"
            )

        with col2:
            distance_max = st.slider(
                "Distance maximum (km)",
                min_value=1,
                max_value=20,
                value=10,
                step=1,
                help="Distance maximale depuis le bien"
            )

        with col3:
            prix_min_filter = st.number_input(
                "Prix minimum (€)",
                min_value=0,
                value=0,
                step=10000,
                help="Filtrer par prix minimum"
            )

        col1, col2 = st.columns(2)

        with col1:
            prix_max_filter = st.number_input(
                "Prix maximum (€)",
                min_value=0,
                value=1000000,
                step=10000,
                help="Filtrer par prix maximum"
            )

        with col2:
            anciennete_max = st.number_input(
                "Ancienneté max (mois)",
                min_value=1,
                value=36,
                step=6,
                help="Transactions de moins de X mois"
            )

    # === SECTION 2 : APPLICATION FILTRES ===
    df_filtered = comparables_df.copy()

    # Appliquer filtres
    if 'score' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['score'] >= score_min]

    if 'distance_km' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['distance_km'] <= distance_max]

    if 'valeurfonc' in df_filtered.columns:
        df_filtered = df_filtered[
            (df_filtered['valeurfonc'] >= prix_min_filter) &
            (df_filtered['valeurfonc'] <= prix_max_filter)
        ]

    st.markdown(f"**✅ {len(df_filtered)} / {len(comparables_df)} comparables sélectionnés**")

    # === SECTION 3 : AFFICHAGE TABLEAU ===
    # Préparer colonnes pour affichage (9 colonnes selon Issue #2)
    display_cols = []
    if 'adresse' in df_filtered.columns:
        display_cols.append('adresse')
    if 'libtypbien' in df_filtered.columns:
        display_cols.append('libtypbien')
    if 'datemut' in df_filtered.columns:
        display_cols.append('datemut')
    if 'valeurfonc' in df_filtered.columns:
        display_cols.append('valeurfonc')
    if 'sbati' in df_filtered.columns:
        display_cols.append('sbati')
    if 'prix_m2' in df_filtered.columns:
        display_cols.append('prix_m2')
    if 'nblocmut' in df_filtered.columns:
        display_cols.append('nblocmut')
    if 'score' in df_filtered.columns:
        display_cols.append('score')
    if 'distance_km' in df_filtered.columns:
        display_cols.append('distance_km')

    df_display = df_filtered[display_cols].copy() if display_cols else df_filtered

    # Formatter colonnes
    col_config = {}
    if 'adresse' in df_display.columns:
        col_config['adresse'] = st.column_config.TextColumn("Adresse", width="large")
    if 'libtypbien' in df_display.columns:
        col_config['libtypbien'] = st.column_config.TextColumn("Type", width="medium")
    if 'datemut' in df_display.columns:
        col_config['datemut'] = st.column_config.TextColumn("Date vente", width="small")
    if 'valeurfonc' in df_display.columns:
        col_config['valeurfonc'] = st.column_config.NumberColumn(
            "Prix vente (€)",
            format="%,.0f",
            width="medium"
        )
    if 'sbati' in df_display.columns:
        col_config['sbati'] = st.column_config.NumberColumn(
            "Surface (m²)",
            format="%.0f",
            width="small"
        )
    if 'prix_m2' in df_display.columns:
        col_config['prix_m2'] = st.column_config.NumberColumn(
            "Prix/m² (€)",
            format="%.0f",
            width="small"
        )
    if 'nblocmut' in df_display.columns:
        col_config['nblocmut'] = st.column_config.NumberColumn(
            "Nb pièces",
            format="%.0f",
            width="small"
        )
    if 'score' in df_display.columns:
        col_config['score'] = st.column_config.NumberColumn(
            "Pertinence",
            format="%.0f",
            width="small"
        )
    if 'distance_km' in df_display.columns:
        col_config['distance_km'] = st.column_config.NumberColumn(
            "Distance (km)",
            format="%.1f",
            width="small"
        )

    # Afficher dataframe interactif
    st.dataframe(
        df_display,
        use_container_width=True,
        column_config=col_config,
        height=300
    )

    st.markdown("---")

    # === SECTION 4 : STATISTIQUES ===
    st.markdown("### 📊 Statistiques comparables sélectionnés")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if 'valeurfonc' in df_filtered.columns:
            prix_median = df_filtered['valeurfonc'].median()
            st.metric("Prix médian", f"{prix_median:,.0f}€")

    with col2:
        if 'sbati' in df_filtered.columns:
            surface_moy = df_filtered['sbati'].mean()
            st.metric("Surface moy", f"{surface_moy:.0f}m²")

    with col3:
        if 'distance_km' in df_filtered.columns:
            distance_moy = df_filtered['distance_km'].mean()
            st.metric("Distance moy", f"{distance_moy:.1f}km")

    with col4:
        if 'score' in df_filtered.columns:
            score_moy = df_filtered['score'].mean()
            st.metric("Score moy", f"{score_moy:.0f}")

    st.markdown("---")

    # === SECTION 5 : RECALCUL ===
    st.markdown("### 🔄 Recalculer estimation")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.info(
            "💡 **Utiliser comparables filtrés**\n\n"
            "Appuyez sur le bouton pour recalculer l'estimation "
            "avec uniquement les comparables sélectionnés."
        )

    with col2:
        if st.button("🚀 Recalculer", use_container_width=True):
            if len(df_filtered) > 0:
                # Convertir filtrés en list de dicts pour estimation_callback
                comparables_list = df_filtered.to_dict('records')

                # Appeler callback
                estimation_callback(
                    latitude=bien_params['latitude'],
                    longitude=bien_params['longitude'],
                    surface=bien_params['surface'],
                    type_bien=bien_params['type_bien'],
                    comparables=comparables_list,
                    filtered=True
                )
                st.rerun()
            else:
                st.error("❌ Sélectionnez au moins 1 comparable")

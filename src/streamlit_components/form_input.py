#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Component: Formulaire d'entrée bien + géocodage
US1 - Saisir adresse → obtenir coordonnées GPS
"""

import streamlit as st
from typing import Optional, Dict, Tuple

from src.utils.geocoding import geocode_address


def render_form_input(sidebar: bool = True) -> Optional[Dict]:
    """
    Affiche le formulaire de saisie bien avec géocodage.

    Args:
        sidebar: Si True, affiche dans la sidebar; sinon dans le main

    Returns:
        Dict avec clés: address, type_bien, surface, pieces, latitude, longitude
        Ou None si formulaire non rempli
    """

    # Conteneur (sidebar ou main)
    if sidebar:
        container = st.sidebar
    else:
        container = st

    with container:
        st.markdown("### 🏠 Saisir le bien à estimer")

        # Adresse
        address = st.text_input(
            "Adresse complète",
            placeholder="Ex: 15 Rue de la Paix, Thonon-les-Bains, 74200",
            help="Entrez l'adresse complète pour meilleure précision"
        )

        # Type de bien
        type_bien = st.selectbox(
            "Type de bien",
            options=["Appartement", "Maison", "Studio", "Duplex"],
            help="Sélectionnez le type de bien"
        )

        # Surface
        surface = st.number_input(
            "Surface habitable (m²)",
            min_value=10.0,
            max_value=500.0,
            value=100.0,
            step=5.0,
            help="Surface habitable en m²"
        )

        # Nombre de pièces (optionnel)
        pieces = st.number_input(
            "Nombre de pièces principales",
            min_value=1,
            max_value=10,
            value=3,
            step=1,
            help="Nombre de pièces principales (optionnel)"
        )

        st.markdown("---")

        # Géocodage (déclenché si adresse non vide)
        geocoded_result = None

        if address and len(address) > 10:
            # Afficher spinner
            with st.spinner("🔍 Géocodage en cours..."):
                suggestions = geocode_address(address)

            if suggestions:
                if len(suggestions) == 1:
                    # Suggestion unique
                    suggestion = suggestions[0]
                    st.success(
                        f"✅ Trouvé: {suggestion['formatted_address']}"
                    )
                    geocoded_result = {
                        "formatted_address": suggestion['formatted_address'],
                        "latitude": suggestion['latitude'],
                        "longitude": suggestion['longitude'],
                    }
                else:
                    # Plusieurs suggestions → selectbox
                    st.info(f"⚠️ {len(suggestions)} suggestion(s) trouvée(s)")

                    formatted_addresses = [
                        s['formatted_address'] for s in suggestions
                    ]

                    selected_idx = st.selectbox(
                        "Sélectionnez l'adresse correcte:",
                        options=range(len(formatted_addresses)),
                        format_func=lambda i: formatted_addresses[i],
                        key="address_selector"
                    )

                    selected = suggestions[selected_idx]
                    geocoded_result = {
                        "formatted_address": selected['formatted_address'],
                        "latitude": selected['latitude'],
                        "longitude": selected['longitude'],
                    }
            else:
                st.error(
                    f"❌ Adresse non trouvée: {address}\n"
                    "Vérifiez l'orthographe ou soyez plus précis"
                )

        st.markdown("---")

        # Bouton Estimer (visible si adresse géocodée)
        col1, col2 = st.columns([1, 1])

        with col1:
            estimate_clicked = st.button(
                "🚀 Estimer",
                use_container_width=True,
                disabled=(geocoded_result is None)
            )

        with col2:
            reset_clicked = st.button(
                "🔄 Réinitialiser",
                use_container_width=True
            )

        # Actions
        if reset_clicked:
            if 'geocoded_address' in st.session_state:
                del st.session_state['geocoded_address']
            if 'coordinates' in st.session_state:
                del st.session_state['coordinates']
            if 'bien_params' in st.session_state:
                del st.session_state['bien_params']
            if 'estimation_result' in st.session_state:
                del st.session_state['estimation_result']
            st.rerun()

        if estimate_clicked and geocoded_result:
            # Stocker dans session_state
            st.session_state['geocoded_address'] = geocoded_result['formatted_address']
            st.session_state['coordinates'] = (
                geocoded_result['latitude'],
                geocoded_result['longitude']
            )
            st.session_state['bien_params'] = {
                'address': address,
                'type_bien': type_bien,
                'surface': surface,
                'pieces': pieces,
                'latitude': geocoded_result['latitude'],
                'longitude': geocoded_result['longitude'],
            }

            return {
                "address": address,
                "type_bien": type_bien,
                "surface": surface,
                "pieces": pieces,
                "latitude": geocoded_result['latitude'],
                "longitude": geocoded_result['longitude'],
            }

        return None


def get_well_params() -> Optional[Dict]:
    """Retourne les paramètres du bien depuis session_state"""
    if 'bien_params' in st.session_state:
        return st.session_state['bien_params']
    return None

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from src.data_processing import load_and_prepare_data
from src.geocoding import geocode_address
from src.comparable_finder import find_comparables
from src.estimation_engine import estimate_property

# Configuration de la page
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
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .stAlert {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Chargement des données (avec cache Streamlit)
@st.cache_data(show_spinner=False)
def load_data():
    return load_and_prepare_data()

# Titre principal
st.markdown('<h1 class="main-header">🏠 Estimation Immobilière Haute-Savoie (74)</h1>', 
            unsafe_allow_html=True)

# Chargement initial
with st.spinner("⏳ Chargement des données DV3F..."):
    try:
        df = load_data()
        st.success(f"✅ Base de données chargée : {len(df):,} transactions disponibles")
        
        # Affichage période couverte
        date_min = df['datemut'].min()
        date_max = df['datemut'].max()
        st.info(f"📅 Données disponibles du {date_min.strftime('%d/%m/%Y')} au {date_max.strftime('%d/%m/%Y')}")
        
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données : {str(e)}")
        st.stop()

st.markdown("---")

# Sidebar - Paramètres
with st.sidebar:
    st.markdown("### ⚙️ Paramètres de recherche")
    
    max_radius = st.slider(
        "Rayon de recherche max (km)",
        min_value=3,
        max_value=20,
        value=10,
        step=1,
        help="Plus le rayon est grand, plus vous aurez de comparables, mais moins ils seront précis géographiquement"
    )
    
    max_age_months = st.slider(
        "Ancienneté max des transactions (mois)",
        min_value=6,
        max_value=36,
        value=24,
        step=6,
        help="Transactions plus récentes = prix plus actuels"
    )
    
    surface_tolerance = st.slider(
        "Tolérance sur la surface (%)",
        min_value=10,
        max_value=50,
        value=25,
        step=5,
        help="±25% signifie qu'un bien de 100m² cherchera des comparables entre 75 et 125m²"
    )
    
    st.markdown("---")
    st.markdown("### 📊 Statistiques générales")
    st.metric("Transactions totales", f"{len(df):,}")
    st.metric("Prix médian", f"{df['valeurfonc'].median():,.0f} €")
    st.metric("Prix/m² médian", f"{df['prix_m2'].median():,.0f} €/m²")

# Formulaire principal
st.markdown("## 📝 Caractéristiques du bien à estimer")

# Ligne 1 : Adresse
col_addr, col_btn = st.columns([3, 1])

with col_addr:
    address = st.text_input(
        "🔍 Adresse complète",
        placeholder="Ex: 12 Avenue des Alpes, 74200 Thonon-les-Bains",
        help="Soyez le plus précis possible : numéro, rue, code postal, ville"
    )

with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)  # Espaceur
    geocode_btn = st.button("📍 Géocoder", type="secondary", use_container_width=True)

# Géocodage si demandé
if geocode_btn:
    if not address:
        st.warning("⚠️ Veuillez entrer une adresse")
    else:
        with st.spinner("🔍 Géocodage en cours..."):
            coords = geocode_address(address)
            
        if coords:
            st.session_state.coords = coords
            st.session_state.address = address
            st.success(f"✅ Adresse localisée : {coords['display_name']}")
        else:
            st.error("❌ Adresse non trouvée. Essayez avec plus de détails (code postal, ville)")

# Ligne 2 : Type et caractéristiques
col1, col2, col3 = st.columns(3)

with col1:
    property_type = st.selectbox(
        "Type de bien",
        ["Appartement", "Maison"],
        help="Type de bien que vous souhaitez estimer"
    )

with col2:
    if property_type == "Appartement":
        nb_pieces = st.selectbox(
            "Nombre de pièces",
            ["T1", "T2", "T3", "T4", "T5+"],
            index=2,  # T3 par défaut
            help="Nombre de pièces principales (chambres + séjour)"
        )
    else:
        nb_pieces = None
        taille_maison = st.selectbox(
            "Taille de la maison",
            ["Petite (<90m²)", "Moyenne (90-130m²)", "Grande (>130m²)"],
            index=1
        )

with col3:
    anciennete = st.selectbox(
        "Ancienneté",
        ["ancien", "recent", "neuf", "tous"],
        index=0,
        help="Ancien = +5 ans, Récent = 1-5 ans, Neuf = <1 an"
    )

# Ligne 3 : Surfaces
col1, col2 = st.columns(2)

with col1:
    surface = st.number_input(
        "Surface habitable (m²)",
        min_value=10,
        max_value=500,
        value=70,
        step=5,
        help="Surface habitable du bien (hors dépendances)"
    )

with col2:
    if property_type == "Maison":
        terrain = st.number_input(
            "Surface terrain (m²)",
            min_value=0,
            max_value=5000,
            value=500,
            step=50,
            help="Surface du terrain (facultatif)"
        )

# Bouton principal d'estimation
st.markdown("<br>", unsafe_allow_html=True)

if st.button("🎯 LANCER L'ESTIMATION", type="primary", use_container_width=True):
    
    # Vérifications
    if 'coords' not in st.session_state:
        st.error("⚠️ Veuillez d'abord géocoder l'adresse en cliquant sur le bouton 📍")
        st.stop()
    
    # Recherche des comparables
    with st.spinner("🔍 Recherche des biens comparables..."):
        try:
            comparables = find_comparables(
                df=df,
                target_lat=st.session_state.coords['lat'],
                target_lon=st.session_state.coords['lon'],
                property_type=property_type,
                surface=surface,
                nb_pieces=nb_pieces,
                anciennete=anciennete,
                max_radius_km=max_radius,
                max_age_months=max_age_months,
                surface_tolerance=surface_tolerance/100
            )
        except Exception as e:
            st.error(f"❌ Erreur lors de la recherche : {str(e)}")
            st.stop()
    
    # Vérification du nombre de comparables
    nb_comp = len(comparables)
    
    if nb_comp == 0:
        st.error("❌ Aucun bien comparable trouvé avec ces critères.")
        st.info("💡 Suggestions : augmentez le rayon de recherche, la tolérance sur la surface, ou l'ancienneté des transactions")
        st.stop()
    
    elif nb_comp < 5:
        st.warning(f"⚠️ Seulement {nb_comp} comparables trouvés. L'estimation sera peu fiable.")
    
    # Calcul de l'estimation
    with st.spinner("💰 Calcul de l'estimation..."):
        estimation = estimate_property(comparables, surface)
    
    if not estimation:
        st.error("❌ Impossible de calculer l'estimation")
        st.stop()
    
    # AFFICHAGE DES RÉSULTATS
    st.markdown("---")
    st.markdown("## 💰 Résultat de l'estimation")
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Prix estimé (médiane)",
            f"{estimation['median_price']:,} €".replace(',', ' '),
            help="Estimation basée sur la médiane des comparables"
        )
    
    with col2:
        st.metric(
            "Fourchette basse (Q1)",
            f"{estimation['q1_price']:,} €".replace(',', ' '),
            delta=f"{((estimation['q1_price']/estimation['median_price']-1)*100):.1f}%"
        )
    
    with col3:
        st.metric(
            "Fourchette haute (Q3)",
            f"{estimation['q3_price']:,} €".replace(',', ' '),
            delta=f"+{((estimation['q3_price']/estimation['median_price']-1)*100):.1f}%"
        )
    
    with col4:
        st.metric(
            "Prix/m² médian",
            f"{estimation['price_per_sqm']:,} €/m²".replace(',', ' '),
            help="Prix au mètre carré médian des comparables"
        )
    
    # Carte de confiance
    confidence = estimation['confidence']
    if confidence >= 80:
        conf_color = "🟢"
        conf_text = "Excellente"
    elif confidence >= 60:
        conf_color = "🟡"
        conf_text = "Bonne"
    elif confidence >= 40:
        conf_color = "🟠"
        conf_text = "Moyenne"
    else:
        conf_color = "🔴"
        conf_text = "Faible"
    
    st.markdown(f"""
        <div class="metric-card">
            <h3>{conf_color} Indice de confiance : {confidence}% ({conf_text})</h3>
            <p>📊 Basé sur <strong>{estimation['nb_comparables']}</strong> biens comparables</p>
            <p>📍 Distance moyenne : <strong>{estimation['distance_moyenne']:.1f} km</strong></p>
            <p>📏 Surface médiane des comparables : <strong>{estimation['surface_median_comparables']} m²</strong></p>
        </div>
    """, unsafe_allow_html=True)
    
    # Graphique de distribution des prix
    st.markdown("---")
    st.markdown("### 📊 Analyse des comparables")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogramme des prix
        fig_hist = go.Figure()
        
        fig_hist.add_trace(go.Histogram(
            x=comparables['valeurfonc'],
            nbinsx=20,
            name='Distribution des prix',
            marker_color='#1f77b4'
        ))
        
        # Ligne verticale pour l'estimation
        fig_hist.add_vline(
            x=estimation['median_price'],
            line_dash="dash",
            line_color="red",
            annotation_text="Estimation",
            annotation_position="top"
        )
        
        fig_hist.update_layout(
            title="Distribution des prix des comparables",
            xaxis_title="Prix (€)",
            yaxis_title="Nombre de biens",
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # Scatter plot : Prix vs Distance
        fig_scatter = go.Figure()
        
        fig_scatter.add_trace(go.Scatter(
            x=comparables['distance_km'],
            y=comparables['valeurfonc'],
            mode='markers',
            marker=dict(
                size=10,
                color=comparables['score_total'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Score")
            ),
            text=comparables['datemut'].dt.strftime('%d/%m/%Y'),
            hovertemplate='<b>Distance:</b> %{x:.1f} km<br>' +
                          '<b>Prix:</b> %{y:,.0f} €<br>' +
                          '<b>Date:</b> %{text}<br>' +
                          '<extra></extra>'
        ))
        
        fig_scatter.update_layout(
            title="Prix en fonction de la distance",
            xaxis_title="Distance (km)",
            yaxis_title="Prix (€)",
            height=400
        )
        
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Graphique supplémentaire : Prix/m² vs Surface
    fig_prix_m2 = go.Figure()
    
    fig_prix_m2.add_trace(go.Scatter(
        x=comparables['sbati'],
        y=comparables['prix_m2'],
        mode='markers',
        marker=dict(
            size=8,
            color=comparables['distance_km'],
            colorscale='RdYlGn_r',
            showscale=True,
            colorbar=dict(title="Distance (km)")
        ),
        text=comparables['valeurfonc'],
        hovertemplate='<b>Surface:</b> %{x} m²<br>' +
                      '<b>Prix/m²:</b> %{y:,.0f} €<br>' +
                      '<b>Prix total:</b> %{text:,.0f} €<br>' +
                      '<extra></extra>'
    ))
    
    # Votre bien
    fig_prix_m2.add_trace(go.Scatter(
        x=[surface],
        y=[estimation['price_per_sqm']],
        mode='markers',
        marker=dict(size=15, color='red', symbol='star'),
        name='Votre bien',
        hovertemplate='<b>Votre bien</b><br>' +
                      f'Surface: {surface} m²<br>' +
                      f'Prix/m² estimé: {estimation["price_per_sqm"]:,} €<br>' +
                      '<extra></extra>'
    ))
    
    fig_prix_m2.update_layout(
        title="Prix au m² en fonction de la surface",
        xaxis_title="Surface (m²)",
        yaxis_title="Prix/m² (€)",
        showlegend=True,
        height=400
    )
    
    st.plotly_chart(fig_prix_m2, use_container_width=True)
    
    # Tableau détaillé des comparables
    st.markdown("---")
    st.markdown("### 📋 Liste détaillée des comparables")
    
    # Préparation du dataframe d'affichage
    display_df = comparables.head(20).copy()
    
    # Sélection et renommage des colonnes
    display_columns = {
        'datemut': 'Date',
        'distance_km': 'Distance (km)',
        'sbati': 'Surface (m²)',
        'valeurfonc': 'Prix (€)',
        'prix_m2': 'Prix/m² (€)',
        'type_detail': 'Type',
        'score_total': 'Score'
    }
    
    display_df = display_df[list(display_columns.keys())].copy()
    display_df.columns = list(display_columns.values())
    
    # Formatage
    display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%d/%m/%Y')
    display_df['Distance (km)'] = display_df['Distance (km)'].round(2)
    display_df['Surface (m²)'] = display_df['Surface (m²)'].astype(int)
    display_df['Prix (€)'] = display_df['Prix (€)'].apply(lambda x: f"{int(x):,}".replace(',', ' '))
    display_df['Prix/m² (€)'] = display_df['Prix/m² (€)'].apply(lambda x: f"{int(x):,}".replace(',', ' '))
    display_df['Score'] = display_df['Score'].round(1)
    
    # Affichage avec style
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400
    )
    
    # Informations complémentaires
    st.markdown("---")
    st.markdown("### ℹ️ Informations complémentaires")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📐 Méthodologie d'estimation :**
        - Recherche de biens similaires (type, surface, ancienneté)
        - Filtrage par proximité géographique
        - Calcul du prix médian au m²
        - Ajustement selon la surface du bien
        - Pondération par score de pertinence
        """)
    
    with col2:
        st.markdown(f"""
        **📊 Statistiques des comparables :**
        - Prix minimum : {estimation['prix_min']:,} €
        - Prix maximum : {estimation['prix_max']:,} €
        - Prix/m² Q1 : {estimation['price_per_sqm_q1']:,} €
        - Prix/m² Q3 : {estimation['price_per_sqm_q3']:,} €
        """.replace(',', ' '))
    
    # Bouton d'export (préparation pour future fonctionnalité)
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("📄 Exporter en PDF", disabled=True):
            st.info("Fonctionnalité à venir")
    
    with col2:
        if st.button("📊 Exporter en Excel", disabled=True):
            st.info("Fonctionnalité à venir")
    
    # Sauvegarde de l'estimation dans la session
    st.session_state.last_estimation = {
        'date': datetime.now(),
        'address': st.session_state.address,
        'type': property_type,
        'surface': surface,
        'estimation': estimation,
        'nb_comparables': len(comparables)
    }

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem 0;'>
        <p>🏠 <strong>Estimation Immobilière Haute-Savoie</strong></p>
        <p>Données source : DV3F (Cerema) • Dernière mise à jour : {}</p>
        <p style='font-size: 0.8rem;'>⚠️ Cette estimation est indicative et ne remplace pas une expertise professionnelle</p>
    </div>
""".format(datetime.now().strftime('%d/%m/%Y')), unsafe_allow_html=True)
            

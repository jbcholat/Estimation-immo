import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.data_processing import load_and_prepare_data
from src.geocoding import geocode_address

# Configuration
st.set_page_config(
    page_title="Estimation Immobilière 74",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Estimation Immobilière Haute-Savoie (74)")

# Chargement des données
@st.cache_data
def load_data():
    return load_and_prepare_data()

# Fonction de recherche de comparables adaptée (sans coordonnées GPS)
def find_comparables_by_commune(df, commune_target, property_type, surface, nb_pieces=None, 
                                max_age_months=24, surface_tolerance=0.25):
    """
    Trouve les biens comparables dans la même commune et communes voisines
    """
    print(f"\n🔍 Recherche de comparables...")
    print(f" Commune cible : {commune_target}")
    print(f" Type : {property_type}")
    print(f" Surface : {surface} m²")
    
    df_search = df.copy()
    
    # 1. Filtre par commune (exacte d'abord, puis communes proches)
    commune_exacte = df_search[df_search['commune'].str.contains(commune_target, case=False, na=False)]
    
    if len(commune_exacte) < 5:
        # Si pas assez de comparables dans la commune exacte, élargir aux codes INSEE proches
        code_dept = commune_target[:2] if len(commune_target) >= 5 else "74"
        communes_dept = df_search[df_search['commune'].str.startswith(code_dept, na=False)]
        df_search = communes_dept
        print(f" ✓ Élargi au département : {len(df_search)} biens")
    else:
        df_search = commune_exacte
        print(f" ✓ Commune exacte : {len(df_search)} biens")
    
    # 2. Filtre date
    cutoff_date = datetime.now() - timedelta(days=30*max_age_months)
    df_search = df_search[df_search['datemut'] >= cutoff_date]
    print(f" ✓ {len(df_search)} biens < {max_age_months} mois")
    
    # 3. Filtre type de bien
    if property_type == 'Appartement':
        df_search = df_search[df_search['type_bien_simple'] == 'Appartement']
        # Filtre nombre de pièces si spécifié
        if nb_pieces and nb_pieces != 'Tous':
            pieces_num = nb_pieces.replace('T', '').replace('+', '')
            if pieces_num.isdigit():
                if nb_pieces.endswith('+'):
                    df_search = df_search[df_search['nblocapt'] >= int(pieces_num)]
                else:
                    df_search = df_search[df_search['nblocapt'] == int(pieces_num)]
        print(f" ✓ {len(df_search)} appartements")
    else:  # Maison
        df_search = df_search[df_search['type_bien_simple'] == 'Maison']
        print(f" ✓ {len(df_search)} maisons")
    
    # 4. Filtre surface
    surface_min = surface * (1 - surface_tolerance)
    surface_max = surface * (1 + surface_tolerance)
    df_search = df_search[
        (df_search['sbati'] >= surface_min) & 
        (df_search['sbati'] <= surface_max)
    ]
    print(f" ✓ {len(df_search)} biens avec surface {surface_min:.0f}-{surface_max:.0f} m²")
    
    if len(df_search) == 0:
        print(f"\n❌ Aucun comparable trouvé avec ces critères")
        return df_search
    
    # 5. Calcul du score de pertinence (sans distance GPS)
    df_search['score_date'] = 100 * (
        1 - (datetime.now() - df_search['datemut']).dt.days / (max_age_months * 30)
    )
    df_search['score_surface'] = 100 * (
        1 - abs(df_search['sbati'] - surface) / surface
    )
    
    # Score commune (priorité à la commune exacte)
    df_search['score_commune'] = df_search['commune'].apply(
        lambda x: 100 if commune_target.lower() in str(x).lower() else 70
    )
    
    df_search['score_total'] = (
        df_search['score_commune'] * 0.4 +
        df_search['score_date'] * 0.3 +
        df_search['score_surface'] * 0.3
    )
    
    # Tri par score
    df_search = df_search.sort_values('score_total', ascending=False)
    
    print(f"\n✅ {len(df_search)} comparables trouvés")
    print(f" Prix médian : {df_search['valeurfonc'].median():,.0f} €")
    
    return df_search

# Fonction d'estimation simplifiée
def estimate_property_simple(comparables, target_surface):
    """
    Calcule l'estimation sans coordonnées GPS
    """
    if len(comparables) == 0:
        return None
    
    # Statistiques sur les prix au m²
    prix_m2_median = comparables['prix_m2'].median()
    prix_m2_q1 = comparables['prix_m2'].quantile(0.25)
    prix_m2_q3 = comparables['prix_m2'].quantile(0.75)
    
    # Estimation par prix au m² médian
    estimation_prix_m2 = target_surface * prix_m2_median
    
    # Ajustement par effet de taille
    surface_median_comparables = comparables['sbati'].median()
    ratio_surface = target_surface / surface_median_comparables
    
    if ratio_surface > 1:
        ajustement = 1 - (ratio_surface - 1) * 0.05
    else:
        ajustement = 1 + (1 - ratio_surface) * 0.05
    
    ajustement = max(0.85, min(1.15, ajustement))
    estimation_ajustee = estimation_prix_m2 * ajustement
    
    # Calcul de la confiance
    nb_comparables = len(comparables)
    conf_nombre = min(100, nb_comparables * 5)
    cv = comparables['prix_m2'].std() / comparables['prix_m2'].mean()
    conf_dispersion = max(0, 100 - cv * 100)
    confidence = (conf_nombre * 0.7 + conf_dispersion * 0.3)
    
    return {
        'median_price': int(estimation_ajustee),
        'q1_price': int(target_surface * prix_m2_q1),
        'q3_price': int(target_surface * prix_m2_q3),
        'price_per_sqm': int(prix_m2_median),
        'nb_comparables': nb_comparables,
        'confidence': int(confidence),
        'surface_median_comparables': int(surface_median_comparables),
    }

# Interface principale
with st.spinner("Chargement des données..."):
    df = load_data()

st.success(f"✅ {len(df):,} transactions chargées")

# Section d'estimation
st.header("🎯 Estimation de votre bien")

col1, col2 = st.columns(2)

with col1:
    adresse = st.text_input("Adresse du bien", placeholder="Ex: Route du Bois de Ville, Armoy")
    type_bien = st.selectbox("Type de bien", ['Appartement', 'Maison'])
    surface = st.number_input("Surface (m²)", min_value=10, max_value=1000, value=100)

with col2:
    if type_bien == 'Appartement':
        nb_pieces = st.selectbox("Nombre de pièces", ['Tous', 'T1', 'T2', 'T3', 'T4', 'T5+'])
    else:
        nb_pieces = None
    
    anciennete_mois = st.slider("Transactions des derniers (mois)", 6, 36, 24)
    tolerance_surface = st.slider("Tolérance surface (%)", 10, 50, 25) / 100

if st.button("🔍 Estimer le bien", type="primary"):
    if adresse:
        # Extraction de la commune depuis l'adresse
        commune_guess = adresse.split(',')[-1].strip() if ',' in adresse else adresse.split()[-1]
        
        with st.spinner("Recherche des comparables..."):
            # Recherche des comparables
            comparables = find_comparables_by_commune(
                df, commune_guess, type_bien, surface, nb_pieces,
                anciennete_mois, tolerance_surface
            )
            
            if len(comparables) > 0:
                # Calcul de l'estimation
                estimation = estimate_property_simple(comparables, surface)
                
                if estimation:
                    # Affichage de l'estimation
                    st.success("🎉 Estimation réalisée avec succès !")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Prix estimé", f"{estimation['median_price']:,} €")
                    with col2:
                        st.metric("Prix/m²", f"{estimation['price_per_sqm']:,} €/m²")
                    with col3:
                        st.metric("Confiance", f"{estimation['confidence']}%")
                    
                    # Fourchette de prix
                    st.subheader("🎯 Fourchette d'estimation")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Prix bas (Q1)", f"{estimation['q1_price']:,} €")
                    with col2:
                        st.metric("Prix médian", f"{estimation['median_price']:,} €")
                    with col3:
                        st.metric("Prix haut (Q3)", f"{estimation['q3_price']:,} €")
                    
                    # Détails des comparables
                    st.subheader("🏘️ Biens comparables")
                    st.write(f"**{len(comparables)}** transactions similaires trouvées")
                    
                    # Préparation des données pour affichage
                    comparables_display = comparables.head(10).copy()
                    comparables_display['adresse_approx'] = comparables_display['commune']
                    comparables_display['date_vente'] = comparables_display['datemut'].dt.strftime('%d/%m/%Y')
                    comparables_display['prix_format'] = comparables_display['valeurfonc'].apply(lambda x: f"{x:,.0f} €")
                    comparables_display['surface_format'] = comparables_display['sbati'].apply(lambda x: f"{x:.0f} m²")
                    comparables_display['prix_m2_format'] = comparables_display['prix_m2'].apply(lambda x: f"{x:.0f} €/m²")
                    
                    # Calcul de la pertinence
                    def calculate_relevance(row):
                        score = row['score_total']
                        if score >= 90:
                            return "Excellente"
                        elif score >= 75:
                            return "Très bonne"
                        elif score >= 60:
                            return "Bonne"
                        else:
                            return "Correcte"
                    
                    comparables_display['pertinence'] = comparables_display.apply(calculate_relevance, axis=1)
                    
                    # Affichage du tableau
                    for idx, comp in comparables_display.iterrows():
                        with st.expander(f"📍 {comp['adresse_approx']} - {comp['prix_format']} - {comp['pertinence']}"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.write(f"**Date :** {comp['date_vente']}")
                                st.write(f"**Prix :** {comp['prix_format']}")
                            with col2:
                                st.write(f"**Surface :** {comp['surface_format']}")
                                st.write(f"**Prix/m² :** {comp['prix_m2_format']}")
                            with col3:
                                surface_diff = ((comp['sbati'] - surface) / surface) * 100
                                st.write(f"**Type :** {comp['type_bien_simple']}")
                                st.write(f"**Pertinence :** {comp['pertinence']}")
                                if abs(surface_diff) <= 15:
                                    st.write(f"**Surface :** Similaire ({surface_diff:+.0f}%)")
                                else:
                                    st.write(f"**Surface :** {surface_diff:+.0f}%")
                    
                    # Graphique des prix
                    fig = px.scatter(
                        comparables_display,
                        x='sbati',
                        y='prix_m2',
                        size='valeurfonc',
                        color='pertinence',
                        title="Prix/m² vs Surface des comparables",
                        labels={'sbati': 'Surface (m²)', 'prix_m2': 'Prix/m²'}
                    )
                    
                    # Ligne pour le bien à estimer
                    fig.add_hline(
                        y=estimation['price_per_sqm'],
                        line_dash="dash",
                        annotation_text=f"Prix/m² estimé: {estimation['price_per_sqm']:,} €"
                    )
                    fig.add_vline(
                        x=surface,
                        line_dash="dash",
                        annotation_text=f"Surface: {surface} m²"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                else:
                    st.error("Impossible de calculer l'estimation")
            else:
                st.warning("Aucun bien comparable trouvé. Essayez d'élargir les critères de recherche.")
    else:
        st.warning("Veuillez saisir une adresse pour l'estimation.")

# Statistiques générales
st.header("📊 Marché immobilier Haute-Savoie")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Transactions", f"{len(df):,}")
with col2:
    st.metric("Prix/m² médian", f"{df['prix_m2'].median():.0f} €")
with col3:
    st.metric("Communes", df['commune'].nunique())
with col4:
    st.metric("Types de biens", df['type_bien_simple'].nunique())
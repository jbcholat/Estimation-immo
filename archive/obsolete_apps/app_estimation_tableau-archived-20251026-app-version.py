import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.data_processing import load_and_prepare_data

# Configuration
st.set_page_config(
    page_title="Estimation Immobilière 74",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Estimation Immobilière Haute-Savoie (74)")

# Dictionnaire de correspondance codes INSEE -> noms de villes
CODE_INSEE_TO_VILLE = {
    '74010': 'Annecy',
    '74012': 'Annemasse', 
    '74281': 'Thonon-les-Bains',
    '74256': 'Saint-Gervais-les-Bains',
    '74056': 'Chamonix-Mont-Blanc',
    '74081': 'Cluses',
    '74236': 'Rumilly',
    '74225': 'Reignier-Esery',
    '74191': 'Passy',
    '74173': 'Morzine'
}

# Chargement des données
@st.cache_data
def load_data():
    return load_and_prepare_data()

# Fonction de recherche de comparables adaptée aux codes INSEE
def find_comparables_by_code_insee(df, ville_recherchee, property_type, surface, nb_pieces=None, 
                                  max_age_months=24, surface_tolerance=0.25):
    """
    Trouve les biens comparables par code INSEE ou nom de ville
    """
    print(f"\n🔍 Recherche de comparables...")
    print(f" Ville recherchée : {ville_recherchee}")
    print(f" Type : {property_type}")
    print(f" Surface : {surface} m²")
    
    df_search = df.copy()
    
    # 1. Recherche du code INSEE correspondant à la ville
    code_insee_target = None
    
    # Recherche directe par nom de ville
    for code, ville in CODE_INSEE_TO_VILLE.items():
        if ville_recherchee.lower() in ville.lower() or ville.lower() in ville_recherchee.lower():
            code_insee_target = f"['{code}']"
            print(f" ✓ Trouvé code INSEE : {code} pour {ville}")
            break
    
    # Si pas trouvé, chercher par correspondance partielle
    if not code_insee_target:
        for ville in CODE_INSEE_TO_VILLE.values():
            if ville_recherchee.lower() in ville.lower():
                # Récupérer le code correspondant
                for code, v in CODE_INSEE_TO_VILLE.items():
                    if v == ville:
                        code_insee_target = f"['{code}']"
                        print(f" ✓ Trouvé par correspondance partielle : {code} pour {ville}")
                        break
                break
    
    # Si toujours pas trouvé, essayer avec le code INSEE le plus fréquent
    if not code_insee_target:
        print(f" ⚠️ Ville '{ville_recherchee}' non trouvée, utilisation d'Annecy par défaut")
        code_insee_target = "['74010']"
    
    # Filtre par commune
    df_search = df_search[df_search['commune'] == code_insee_target]
    print(f" ✓ {len(df_search)} biens dans la commune {code_insee_target}")
    
    # Si pas assez de biens, élargir aux communes voisines
    if len(df_search) < 10:
        print(f" ⚠️ Pas assez de biens, élargissement aux communes principales")
        codes_principaux = ["['74010']", "['74012']", "['74281']", "['74256']", "['74056']"]
        df_search = df[df['commune'].isin(codes_principaux)]
        print(f" ✓ Élargi aux principales communes : {len(df_search)} biens")
    
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
                # Approximation du nombre de pièces via surface (pas de colonne spécifique)
                if nb_pieces == 'T1':
                    df_search = df_search[df_search['sbati'] <= 35]
                elif nb_pieces == 'T2':
                    df_search = df_search[(df_search['sbati'] > 35) & (df_search['sbati'] <= 55)]
                elif nb_pieces == 'T3':
                    df_search = df_search[(df_search['sbati'] > 55) & (df_search['sbati'] <= 80)]
                elif nb_pieces == 'T4':
                    df_search = df_search[(df_search['sbati'] > 80) & (df_search['sbati'] <= 110)]
                elif nb_pieces == 'T5+':
                    df_search = df_search[df_search['sbati'] > 110]
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
    
    # 5. Calcul du score de pertinence
    df_search['score_date'] = 100 * (
        1 - (datetime.now() - df_search['datemut']).dt.days / (max_age_months * 30)
    )
    df_search['score_surface'] = 100 * (
        1 - abs(df_search['sbati'] - surface) / surface
    )
    
    # Score commune (priorité à la commune exacte)
    df_search['score_commune'] = df_search['commune'].apply(
        lambda x: 100 if x == code_insee_target else 70
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

# Suggestion de villes
st.info("💡 **Villes principales disponibles :** Annecy, Annemasse, Thonon-les-Bains, Saint-Gervais-les-Bains, Chamonix-Mont-Blanc, Cluses, Rumilly, Passy, Morzine")

col1, col2 = st.columns(2)

with col1:
    ville = st.text_input("Ville", placeholder="Ex: Annecy, Thonon, Chamonix...")
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
    if ville:
        with st.spinner("Recherche des comparables..."):
            # Recherche des comparables
            comparables = find_comparables_by_code_insee(
                df, ville, type_bien, surface, nb_pieces,
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
                    
                    # Préparation des données pour le tableau
                    comparables_display = comparables.head(20).copy()
                    
                    # Conversion des codes INSEE en noms de villes
                    def code_to_ville(code_insee):
                        code_clean = code_insee.replace("['", "").replace("']", "")
                        return CODE_INSEE_TO_VILLE.get(code_clean, f"Code {code_clean}")
                    
                    comparables_display['Commune'] = comparables_display['commune'].apply(code_to_ville)
                    comparables_display['Date'] = comparables_display['datemut'].dt.strftime('%d/%m/%Y')
                    comparables_display['Prix'] = comparables_display['valeurfonc'].apply(lambda x: f"{x:,.0f} €")
                    comparables_display['Surface'] = comparables_display['sbati'].apply(lambda x: f"{x:.0f} m²")
                    comparables_display['Prix/m²'] = comparables_display['prix_m2'].apply(lambda x: f"{x:.0f} €/m²")
                    comparables_display['Type'] = comparables_display['type_bien_simple']
                    
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
                    
                    comparables_display['Pertinence'] = comparables_display.apply(calculate_relevance, axis=1)
                    
                    # Calcul de la différence de surface
                    def calculate_surface_diff(row):
                        diff = ((row['sbati'] - surface) / surface) * 100
                        if abs(diff) <= 5:
                            return "Identique"
                        elif abs(diff) <= 15:
                            return f"Similaire ({diff:+.0f}%)"
                        else:
                            return f"{diff:+.0f}%"
                    
                    comparables_display['Surface vs cible'] = comparables_display.apply(calculate_surface_diff, axis=1)
                    
                    # État standard pour tous (pas de données d'état dans DV3F)
                    comparables_display['État'] = 'Standard'
                    
                    # Sélection des colonnes pour le tableau
                    tableau_comparables = comparables_display[[
                        'Commune', 'Date', 'Prix', 'Surface', 'Prix/m²', 
                        'Type', 'Surface vs cible', 'Pertinence', 'État'
                    ]].reset_index(drop=True)
                    
                    # Affichage du tableau avec style
                    st.dataframe(
                        tableau_comparables,
                        use_container_width=True,
                        hide_index=True,
                    )
                    
                    # Option pour afficher plus de détails
                    if st.checkbox("Afficher les détails techniques"):
                        details_techniques = comparables_display[[
                            'Commune', 'Date', 'idmutation', 'refdoc', 'valeurfonc', 
                            'sbati', 'prix_m2', 'score_total'
                        ]].head(10)
                        st.subheader("🔧 Détails techniques (10 premiers)")
                        st.dataframe(details_techniques, use_container_width=True)
                    
                    # Graphique des prix
                    st.subheader("📊 Analyse graphique des comparables")
                    
                    fig = px.scatter(
                        comparables_display,
                        x='sbati',
                        y='prix_m2',
                        size='valeurfonc',
                        color='Pertinence',
                        hover_data=['Commune', 'Date', 'Prix'],
                        title="Prix/m² vs Surface des comparables",
                        labels={'sbati': 'Surface (m²)', 'prix_m2': 'Prix/m²'},
                        color_discrete_map={
                            'Excellente': '#1f77b4',
                            'Très bonne': '#ff7f0e', 
                            'Bonne': '#2ca02c',
                            'Correcte': '#d62728'
                        }
                    )
                    
                    # Ligne pour le bien à estimer
                    fig.add_hline(
                        y=estimation['price_per_sqm'],
                        line_dash="dash",
                        line_color="red",
                        annotation_text=f"Prix/m² estimé: {estimation['price_per_sqm']:,} €/m²"
                    )
                    fig.add_vline(
                        x=surface,
                        line_dash="dash",
                        line_color="red",
                        annotation_text=f"Surface cible: {surface} m²"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Statistiques des comparables
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Prix moyen", f"{comparables['valeurfonc'].mean():,.0f} €")
                    with col2:
                        st.metric("Prix médian", f"{comparables['valeurfonc'].median():,.0f} €")
                    with col3:
                        st.metric("Surface moyenne", f"{comparables['sbati'].mean():.0f} m²")
                    with col4:
                        st.metric("Écart-type prix/m²", f"{comparables['prix_m2'].std():.0f} €/m²")
                    
                else:
                    st.error("Impossible de calculer l'estimation")
            else:
                st.warning(f"Aucun bien comparable trouvé pour '{ville}'. Essayez avec une des villes principales : Annecy, Annemasse, Thonon-les-Bains...")
    else:
        st.warning("Veuillez saisir une ville pour l'estimation.")

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

# Top des communes
st.subheader("🏘️ Top des communes par nombre de transactions")
top_communes_df = df['commune'].value_counts().head(10).reset_index()
top_communes_df['ville_nom'] = top_communes_df['commune'].apply(
    lambda x: CODE_INSEE_TO_VILLE.get(x.replace("['", "").replace("']", ""), f"Code {x}")
)
top_communes_df.columns = ['Code INSEE', 'Nb transactions', 'Ville']
top_communes_df = top_communes_df[['Ville', 'Code INSEE', 'Nb transactions']]

st.dataframe(top_communes_df, use_container_width=True)
import pandas as pd
import numpy as np
from pathlib import Path

def load_and_prepare_data(file_path='data/raw/mutation_74.csv'):
    """
    Charge et nettoie les données DV3F
    Returns:
        pd.DataFrame: Données nettoyées
    """
    print(f"📂 Chargement des données : {file_path}")
    
    # Chargement avec le séparateur POINT-VIRGULE
    df = pd.read_csv(file_path, sep=';', encoding='utf-8', low_memory=False)
    
    print(f" ✓ {len(df):,} transactions chargées")
    print(f" ✓ Colonnes détectées : {len(df.columns)}")
    
    # NETTOYAGE ADAPTÉ AUX COLONNES DISPONIBLES
    print(" 🧹 Nettoyage des données...")
    
    conditions = []
    
    # 1. Prix renseigné (essentiel pour l'estimation)
    if 'valeurfonc' in df.columns:
        conditions.append(df['valeurfonc'] > 0)
        print("   ✓ Filtre : Prix > 0")
    
    # 2. Une seule commune (pour éviter les biens multi-communes)
    if 'nbcomm' in df.columns:
        conditions.append(df['nbcomm'] == 1)
        print("   ✓ Filtre : Une seule commune")
    
    # 3. Filtre sur nature de mutation (ventes uniquement)
    if 'libnatmut' in df.columns:
        # Garder seulement les ventes (exclure donations, etc.)
        ventes_keywords = ['Vente', 'VENTE', 'vente']
        mask_vente = df['libnatmut'].str.contains('|'.join(ventes_keywords), na=False)
        conditions.append(mask_vente)
        print("   ✓ Filtre : Ventes uniquement")
    
    # 4. Années récentes (données plus pertinentes)
    if 'anneemut' in df.columns:
        conditions.append(df['anneemut'] >= 2020)  # Depuis 2020
        print("   ✓ Filtre : Depuis 2020")
    
    # 5. Surfaces cohérentes pour l'immobilier
    if 'sbati' in df.columns:
        conditions.append((df['sbati'] > 10) & (df['sbati'] < 1000))  # Entre 10 et 1000 m²
        print("   ✓ Filtre : Surface 10-1000 m²")
    
    # Application des filtres
    if conditions:
        mask = conditions[0]
        for condition in conditions[1:]:
            mask = mask & condition
        df_clean = df[mask].copy()
    else:
        print("   ⚠️ Aucun filtre applicable")
        df_clean = df.copy()
    
    print(f" ✓ {len(df_clean):,} transactions après nettoyage")
    
    # CONVERSIONS ET ENRICHISSEMENTS
    print(" 🔄 Conversion des types...")
    
    # Conversion des dates
    if 'datemut' in df_clean.columns:
        df_clean['datemut'] = pd.to_datetime(df_clean['datemut'], errors='coerce')
        print("   ✓ Dates converties")
    
    # Conversion des colonnes numériques
    numeric_cols = ['valeurfonc', 'sbati', 'sbatapt', 'sbatmai', 'nbcomm', 'anneemut']
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    # Calcul du prix au m² si surface disponible
    if 'valeurfonc' in df_clean.columns and 'sbati' in df_clean.columns:
        df_clean['prix_m2'] = df_clean['valeurfonc'] / df_clean['sbati']
        # Filtre prix/m² cohérents (entre 500€ et 15000€/m²)
        mask_prix_coherent = (df_clean['prix_m2'] >= 500) & (df_clean['prix_m2'] <= 15000)
        df_clean = df_clean[mask_prix_coherent].copy()
        print(f"   ✓ Prix/m² calculé, {len(df_clean):,} transactions cohérentes")
    
    # Nettoyage des noms de communes
    if 'l_codinsee' in df_clean.columns:
        df_clean['commune'] = df_clean['l_codinsee'].str.split('|').str[0]  # Première commune
        print("   ✓ Codes INSEE nettoyés")
    
    # Création d'une colonne type de bien simplifiée
    if 'libtypbien' in df_clean.columns:
        def simplify_type(type_bien):
            if pd.isna(type_bien):
                return 'Inconnu'
            type_bien = str(type_bien).lower()
            if 'appartement' in type_bien or 'apt' in type_bien:
                return 'Appartement'
            elif 'maison' in type_bien:
                return 'Maison'
            elif 'local' in type_bien:
                return 'Local commercial'
            else:
                return 'Autre'
        
        df_clean['type_bien_simple'] = df_clean['libtypbien'].apply(simplify_type)
        print("   ✓ Types de bien simplifiés")
    
    # Statistiques finales
    print(f"\n📊 RÉSUMÉ DES DONNÉES NETTOYÉES :")
    print(f"   • {len(df_clean):,} transactions utilisables")
    if 'anneemut' in df_clean.columns:
        print(f"   • Années : {df_clean['anneemut'].min():.0f} - {df_clean['anneemut'].max():.0f}")
    if 'prix_m2' in df_clean.columns:
        print(f"   • Prix/m² médian : {df_clean['prix_m2'].median():.0f} €/m²")
    if 'type_bien_simple' in df_clean.columns:
        print(f"   • Types : {df_clean['type_bien_simple'].value_counts().to_dict()}")
    
    return df_clean
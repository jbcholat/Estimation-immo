import pandas as pd
from datetime import datetime, timedelta
from src.data_processing import load_and_prepare_data

# Chargement des données
print("📂 Chargement des données...")
df = load_and_prepare_data()
print(f"✅ {len(df)} transactions chargées\n")

# Diagnostic des communes
print("🏘️ ANALYSE DES COMMUNES :")
print(f"Nombre de communes uniques : {df['commune'].nunique()}")
print("\nTop 10 des communes (par nb transactions) :")
top_communes = df['commune'].value_counts().head(10)
print(top_communes)

print("\nÉchantillon des noms de communes :")
sample_communes = df['commune'].unique()[:20]
for i, commune in enumerate(sample_communes):
    print(f"{i+1:2d}. '{commune}'")

# Test de recherche manuelle
print("\n" + "="*60)
print("🔍 TEST DE RECHERCHE MANUELLE")

# Test avec Thonon (ta recherche)
test_ville = "Thonon"
print(f"\nRecherche pour : '{test_ville}'")

# 1. Recherche exacte
exacte = df[df['commune'] == test_ville]
print(f"Correspondance exacte : {len(exacte)} biens")

# 2. Recherche avec contains (case sensitive)
contains_case = df[df['commune'].str.contains(test_ville, na=False)]
print(f"Contient '{test_ville}' (case sensitive) : {len(contains_case)} biens")

# 3. Recherche avec contains (case insensitive)
contains_nocase = df[df['commune'].str.contains(test_ville, case=False, na=False)]
print(f"Contient '{test_ville}' (case insensitive) : {len(contains_nocase)} biens")

# 4. Recherche partielle
partial = df[df['commune'].str.lower().str.contains(test_ville.lower(), na=False)]
print(f"Recherche partielle : {len(partial)} biens")

if len(partial) > 0:
    print("Communes trouvées :")
    communes_trouvees = partial['commune'].unique()[:10]
    for commune in communes_trouvees:
        print(f"  - '{commune}'")

# Test avec les communes les plus fréquentes
print(f"\n" + "="*60)
print("🎯 TEST AVEC COMMUNES FRÉQUENTES")

for commune_test in top_communes.head(3).index:
    print(f"\n--- Test avec '{commune_test}' ---")
    
    # Filtres étape par étape
    df_test = df.copy()
    print(f"Dataset complet : {len(df_test)} biens")
    
    # Filtre commune
    df_test = df_test[df_test['commune'] == commune_test]
    print(f"Après filtre commune : {len(df_test)} biens")
    
    # Filtre date (24 mois)
    cutoff_date = datetime.now() - timedelta(days=30*24)
    df_test = df_test[df_test['datemut'] >= cutoff_date]
    print(f"Après filtre date (24 mois) : {len(df_test)} biens")
    
    # Filtre type (maison)
    df_test = df_test[df_test['type_bien_simple'] == 'Maison']
    print(f"Après filtre type (Maison) : {len(df_test)} biens")
    
    # Filtre surface (100m² ± 25%)
    surface_test = 100
    tolerance = 0.25
    surface_min = surface_test * (1 - tolerance)
    surface_max = surface_test * (1 + tolerance)
    df_test = df_test[(df_test['sbati'] >= surface_min) & (df_test['sbati'] <= surface_max)]
    print(f"Après filtre surface (75-125 m²) : {len(df_test)} biens")
    
    if len(df_test) > 0:
        print(f"✅ SUCCESS! {len(df_test)} comparables trouvés pour {commune_test}")
        print("Prix médian :", f"{df_test['valeurfonc'].median():,.0f} €")
        break
    else:
        print(f"❌ Aucun comparable pour {commune_test}")

# Statistiques générales sur les critères
print(f"\n" + "="*60)
print("📊 STATISTIQUES GÉNÉRALES")

print(f"\nTypes de biens :")
print(df['type_bien_simple'].value_counts())

print(f"\nDistribution des surfaces :")
print(f"Min : {df['sbati'].min():.0f} m²")
print(f"Q1 : {df['sbati'].quantile(0.25):.0f} m²")
print(f"Médiane : {df['sbati'].median():.0f} m²")
print(f"Q3 : {df['sbati'].quantile(0.75):.0f} m²")
print(f"Max : {df['sbati'].max():.0f} m²")

print(f"\nDistribution des années :")
print(df['anneemut'].value_counts().sort_index())
from src.data_processing import load_and_prepare_data

try:
    df = load_and_prepare_data()
    print(f"✅ SUCCESS! {len(df)} transactions chargées et nettoyées")
    print(f"✅ Colonnes disponibles: {list(df.columns)}")
    if 'prix_m2' in df.columns:
        print(f"✅ Prix/m² médian: {df['prix_m2'].median():.0f} €/m²")
except Exception as e:
    print(f"❌ ERREUR: {e}")

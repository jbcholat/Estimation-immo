import pandas as pd
import os
print("Contenu du dossier :", os.listdir('data/raw'))
print("=" * 50)
print("🔍 TEST DE CHARGEMENT DES DONNÉES")
print("=" * 50)

# Vérifie que le fichier existe
chemin = 'data/raw/mutation_74.csv'
print(f"\n1️⃣ Vérification du fichier : {chemin}")

if os.path.exists(chemin):
    print(f"   ✅ Fichier trouvé")
    taille = os.path.getsize(chemin) / (1024 * 1024)  # en Mo
    print(f"   📦 Taille : {taille:.2f} Mo")
else:
    print(f"   ❌ Fichier INTROUVABLE !")
    print(f"   📂 Vérifiez le chemin")
    exit()

# Essaie de charger
print(f"\n2️⃣ Chargement du CSV...")
try:
    df = pd.read_csv(chemin, 
                     sep='|', 
                     encoding='utf-8',
                     low_memory=False,
                     nrows=100)  # Charge seulement 100 lignes pour test
    
    print(f"   ✅ CSV chargé avec succès !")
    print(f"   📊 Nombre de lignes (échantillon) : {len(df)}")
    print(f"   📋 Nombre de colonnes : {len(df.columns)}")
    print(f"\n3️⃣ Premières colonnes :")
    print(f"   {list(df.columns[:10])}")
    
except Exception as e:
    print(f"   ❌ ERREUR lors du chargement : {e}")

print("\n" + "=" * 50)
input("Appuie sur Entrée pour fermer...")
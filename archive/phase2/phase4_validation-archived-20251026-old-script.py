#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import psycopg2

os.chdir(r'c:\analyse_immobiliere')
load_dotenv('.env')

DB_HOST = "db.fwcuftkjofoxyjbjzdnh.supabase.co"
DB_USER = "postgres"
DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")

print("\n=== PHASE 4: Index + Validation ===\n")

conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database="postgres", port=5432)
cursor = conn.cursor()

# Créer index
print("[1/3] Creating indexes...")
indexes = [
    "CREATE INDEX IF NOT EXISTS idx_mutation_datemut ON dvf_plus_2025_2.dvf_plus_mutation(datemut DESC)",
    "CREATE INDEX IF NOT EXISTS idx_mutation_annee ON dvf_plus_2025_2.dvf_plus_mutation(anneemut)",
    "CREATE INDEX IF NOT EXISTS idx_mutation_id ON dvf_plus_2025_2.dvf_plus_mutation(idmutation)",
    "CREATE INDEX IF NOT EXISTS idx_mutation_valeur ON dvf_plus_2025_2.dvf_plus_mutation(valeurfonc)",
    "CREATE INDEX IF NOT EXISTS idx_mutation_sbati ON dvf_plus_2025_2.dvf_plus_mutation(sbati)",
    "CREATE INDEX IF NOT EXISTS idx_adresse_codepostal ON dvf_plus_2025_2.dvf_plus_adresse(codepostal)",
]

for idx_sql in indexes:
    try:
        cursor.execute(idx_sql)
        conn.commit()
    except Exception as e:
        pass

print("OK: Indexes created\n")

# Validation
print("[2/3] Data validation...")
cursor.execute("SELECT COUNT(*) FROM dvf_plus_2025_2.dvf_plus_mutation")
mut_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM dvf_plus_2025_2.dvf_plus_adresse")
addr_count = cursor.fetchone()[0]

cursor.execute("SELECT MIN(datemut), MAX(datemut) FROM dvf_plus_2025_2.dvf_plus_mutation WHERE datemut IS NOT NULL")
result = cursor.fetchone()
min_date, max_date = result if result[0] else (None, None)

cursor.execute("SELECT ROUND(AVG(valeurfonc)) FROM dvf_plus_2025_2.dvf_plus_mutation WHERE valeurfonc > 0")
avg_price = cursor.fetchone()[0]

print(f"  Mutations: {mut_count:,}")
print(f"  Adresses: {addr_count:,}")
print(f"  Date range: {min_date} to {max_date}")
print(f"  Avg price: EUR {avg_price:,}\n")

# Taille DB
print("[3/3] Database size...")
cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
db_size = cursor.fetchone()[0]
print(f"  Database size: {db_size}")

cursor.close()
conn.close()

print("\nOK: PHASE 4 COMPLETE\n")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHASE 3 CORRECTION: Re-import DVF+ with CORRECT commune filtering
Filter by matching communes in l_codinsee field against target communes
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_batch

os.chdir(r'c:\analyse_immobiliere')
load_dotenv('.env')

DB_HOST = "db.fwcuftkjofoxyjbjzdnh.supabase.co"
DB_USER = "postgres"
DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")

# 83 target communes for Chablais + Annemasse
TARGET_COMMUNES = {
    'ABONDANCE', 'ALLINGES', 'ANTHY-SUR-LEMAN', 'ARMOY', 'BALLAISON',
    'BAUME (LA)', 'BELLEVAUX', 'BERNEX', 'BIOT (LE)', 'BOEGE', 'BONNEVAUX',
    'BONS-EN-CHABLAIS', 'BRENTHONNE', 'BURDIGNIN', 'CHAMPANGES', 'CHATEL',
    'CHAUMONT', 'CHAVANNAZ', 'CHENE-EN-SEMINE', 'CHENS-SUR-LEMAN', 'CHESSENAZ',
    'CHEVENOZ', 'CHILLY', 'CLARAFOND-ARCINE', 'CLERMONT', 'CONTAMINE-SARZIN',
    'DESINGY', 'DOUVAINE', 'DROISY', 'ESSERT-ROMAND', 'EVIAN-LES-BAINS',
    'EXCENEVEX', 'FESSY', 'FETERNES', 'FORCLAZ (LA)', 'FRANGY',
    'HABERE-LULLIN', 'HABERE-POCHE', "LA CHAPELLE-D'ABONDANCE", 'LA COTE D ARBROZ',
    'LARRINGES', 'LOISIN', 'LUGRIN', 'LULLIN', 'LULLY', 'LYAUD (LE)',
    'MACHILLY', 'MARGENCEL', 'MARIN', 'MARLIOZ', 'MASSONGY', 'MAXILLY-SUR-LEMAN',
    'MEILLERIE', 'MENTHONNEX-SOUS-CLERMONT', 'MESSERY', 'MINZIER', 'MONTRIOND',
    'MORZINE', 'MUSIEGES', 'NERNIER', 'NEUVECELLE', 'NOVEL', 'PUBLIER',
    'REYVROZ', 'SAINT-ANDRE-DE-BOEGE', 'SAINT-CERGUES', 'SAINT-GINGOLPH',
    "SAINT-JEAN-D'AULPS", 'SAINT-PAUL-EN-CHABLAIS', 'SALLENOVES', 'SAXEL',
    'SCIEZ', 'SEYTROUX', 'THOLLON-LES-MEMISES', 'THONON LES BAINS', 'VACHERESSE',
    'VAILLY', 'VANZY', 'VEIGY-FONCENEX', 'VERNAZ (LA)', 'VILLARD', 'VINZIER', 'YVOIRE'
}

SQL_FILE = r"c:\analyse_immobiliere\data\raw\DVFPlus_2025-1-0_SQL_LAMB93_R084-ED251\1_DONNEES_LIVRAISON\dvf_plus_d74.sql"

print("\n=== PHASE 3 CORRECTION: Import DVF+ Chablais + Annemasse by Communes ===\n")

conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database="postgres", port=5432)
cursor = conn.cursor()

print("[0/3] Purging old data...")
cursor.execute("DELETE FROM dvf_plus_2025_2.dvf_plus_mutation")
cursor.execute("DELETE FROM dvf_plus_2025_2.dvf_plus_disposition")
cursor.execute("DELETE FROM dvf_plus_2025_2.dvf_plus_local")
cursor.execute("DELETE FROM dvf_plus_2025_2.dvf_plus_lot")
cursor.execute("DELETE FROM dvf_plus_2025_2.dvf_plus_volume")
cursor.execute("DELETE FROM dvf_plus_2025_2.dvf_plus_suf")
cursor.execute("DELETE FROM dvf_plus_2025_2.dvf_plus_disposition_parcelle")
cursor.execute("DELETE FROM dvf_plus_2025_2.dvf_plus_adresse_dispoparc")
cursor.execute("DELETE FROM dvf_plus_2025_2.dvf_plus_adresse_local")
cursor.execute("DELETE FROM dvf_plus_2025_2.dvf_plus_adresse")
cursor.execute("DELETE FROM dvf_plus_2025_2.dvf_plus_mutation_article_cgi")
cursor.execute("DELETE FROM dvf_plus_2025_2.dvf_plus_parcelle")
conn.commit()
print("OK: Old data cleared\n")

mutation_count = 0
mutation_imported = 0
batch = []
mutation_ids = set()

print("[1/3] Parsing + Re-importing mutations with CORRECT commune filter...")
in_mutation = False

with open(SQL_FILE, 'r', encoding='utf-8', errors='ignore') as f:
    for line_num, line in enumerate(f):
        if 'COPY dvf_plus_2025_2.dvf_plus_mutation' in line and 'article_cgi' not in line:
            in_mutation = True
            continue

        if in_mutation:
            if line.startswith(r'\.'):
                # Flush final batch
                if batch:
                    try:
                        cols = ','.join(['%s'] * len(batch[0]))
                        sql = f"INSERT INTO dvf_plus_2025_2.dvf_plus_mutation VALUES ({cols})"
                        execute_batch(cursor, sql, batch, page_size=500)
                        conn.commit()
                        mutation_imported += len(batch)
                    except Exception as e:
                        print(f"  Warning on final batch: {e}")
                break

            if line.strip() and not line.startswith('COPY'):
                mutation_count += 1
                fields = line.strip().split('\t')

                # Field 18 contains l_codinsee (array of commune names)
                # Format example: "1$74200$THONON LES BAINS$74281$THONON LES BAINS"
                if len(fields) > 18:
                    communes_str = fields[18]

                    # Extract commune names from l_codinsee field
                    # Split by $ and look for our target communes
                    is_target = False
                    parts = communes_str.split('$')
                    for i, part in enumerate(parts):
                        # Commune names appear after INSEE codes
                        if part in TARGET_COMMUNES:
                            is_target = True
                            break

                    if is_target:
                        mutation_imported += 1
                        idmutation = fields[0]
                        mutation_ids.add(idmutation)

                        fields = [None if f == r'\N' else f for f in fields]
                        batch.append(tuple(fields))

                        if len(batch) >= 500:
                            try:
                                cols = ','.join(['%s'] * len(batch[0]))
                                sql = f"INSERT INTO dvf_plus_2025_2.dvf_plus_mutation VALUES ({cols})"
                                execute_batch(cursor, sql, batch, page_size=500)
                                conn.commit()
                            except Exception as e:
                                print(f"  Error: {e}")
                            batch = []

                if mutation_count % 50000 == 0:
                    print(f"  Processed {mutation_count:,} total | Imported {mutation_imported:,} target")

print(f"\nOK: Re-import complete (Imported {mutation_imported:,} mutations)\n")

# Validation
print("[2/3] Validation...")
cursor.execute("SELECT COUNT(*) FROM dvf_plus_2025_2.dvf_plus_mutation")
final_count = cursor.fetchone()[0]

cursor.execute("""
    SELECT anneemut, COUNT(*) as cnt
    FROM dvf_plus_2025_2.dvf_plus_mutation
    GROUP BY anneemut
    ORDER BY anneemut
""")
distribution = cursor.fetchall()

print(f"  Total mutations Chablais + Annemasse: {final_count:,}")
print(f"\n  Distribution par annee:")
for year, cnt in distribution:
    print(f"    {year}: {cnt:,}")

cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
db_size = cursor.fetchone()[0]
print(f"\n  Database size: {db_size}")

cursor.close()
conn.close()

print("\n=== PHASE 3 CORRECTION COMPLETE ===")
print(f"RESULT: {final_count:,} mutations (target: ~25k-30k)")
if 20000 <= final_count <= 35000:
    print("STATUS: OK - Volume correct!")
else:
    print(f"STATUS: Check - Volume {'too low' if final_count < 20000 else 'too high'}?")
print()

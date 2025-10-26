#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORRECTION Phase 3: Re-import DVF+ avec filtrage CORRECT par codes postaux
Inclut Chablais + Annemasse (15 codes postaux, 83 communes)
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

# 15 codes postaux Chablais + Annemasse
CODES_POSTAUX_CORRECTS = {
    # Chablais
    '74110', '74140', '74200', '74270', '74360',
    '74390', '74420', '74430', '74470', '74500', '74890',
    # Annemasse (NOUVEAU)
    '74100', '74240', '74380', '74350'
}

SQL_FILE = r"c:\analyse_immobiliere\data\raw\DVFPlus_2025-1-0_SQL_LAMB93_R084-ED251\1_DONNEES_LIVRAISON\dvf_plus_d74.sql"

print("\n=== CORRECTION: Re-import DVF+ Chablais + Annemasse ===\n")

conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database="postgres", port=5432)
cursor = conn.cursor()

print("[0/3] Purging old data...")
cursor.execute("DELETE FROM dvf_plus_2025_2.dvf_plus_mutation")
conn.commit()
print("OK: Old mutations cleared\n")

mutation_count = 0
mutation_imported = 0
batch = []

print("[1/3] Parsing + Re-importing mutations with CORRECT postal code filter...")
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

                # Vérifier TOUTES les communes (l_codinsee est un array: "1$74281$THONON...")
                # Chercher si UNE commune correspond à nos codes postaux
                # NOTE: l_codinsee[18] contient format: "CODE_INSEE$74200$COMMUNE" etc

                if len(fields) > 18:
                    communes_str = fields[18]
                    is_target = False

                    # Vérifier si au moins un code postal cible est dans la chaîne
                    for cp in CODES_POSTAUX_CORRECTS:
                        if cp in communes_str:
                            is_target = True
                            break

                    if is_target:
                        mutation_imported += 1
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

print(f"\nOK: Re-import complete\n")

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
print(f"\n  Distribution par année:")
for year, cnt in distribution:
    print(f"    {year}: {cnt:,}")

cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
db_size = cursor.fetchone()[0]
print(f"\n  Database size: {db_size}")

cursor.close()
conn.close()

print("\n=== CORRECTION COMPLETE ===")
print(f"RESULT: {final_count:,} mutations (expected ~25k-30k)")
if 20000 <= final_count <= 35000:
    print("STATUS: OK - Volume correct!")
else:
    print("STATUS: Check - Volume still off?")
print()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHASE 3 CORRECTION: Re-import DVF+ with CORRECT INSEE code filtering
Filter mutations by matching INSEE codes in l_codinsee field
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

# INSEE codes for Chablais + Annemasse (from existing data)
TARGET_INSEE_CODES = {
    '74005', '74014', '74020', '74026', '74032', '74042', '74056', '74063',
    '74070', '74075', '74078', '74100', '74106', '74107', '74110', '74119',
    '74122', '74126', '74131', '74136', '74139', '74140', '74154', '74155',
    '74161', '74163', '74172', '74200', '74206', '74209', '74210', '74212',
    '74218', '74236', '74240', '74254', '74269', '74270', '74281', '74284',
    '74287', '74302'
}

SQL_FILE = r"c:\analyse_immobiliere\data\raw\DVFPlus_2025-1-0_SQL_LAMB93_R084-ED251\1_DONNEES_LIVRAISON\dvf_plus_d74.sql"

print("\n=== PHASE 3 CORRECTION: Import DVF+ by INSEE Code Filtering ===\n")

conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database="postgres", port=5432)
cursor = conn.cursor()

print(f"[0/3] Target INSEE codes: {sorted(TARGET_INSEE_CODES)}\n")

mutation_count = 0
mutation_imported = 0
batch = []
mutation_ids = set()

print("[1/3] Parsing + Re-importing mutations with INSEE code filter...")
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

                # Field 18 contains l_codinsee array: {74056}, {74276}, etc
                if len(fields) > 18:
                    l_codinsee_raw = fields[18]  # e.g., "{74056}"

                    # Extract INSEE code from {XXXXX} format
                    # Remove braces and check if any INSEE code matches
                    is_target = False

                    # Parse {INSEE1},{INSEE2},... format (actually it's {INSEE})
                    import re
                    insee_codes = re.findall(r'\{?(\d{5})\}?', l_codinsee_raw)

                    for insee in insee_codes:
                        if insee in TARGET_INSEE_CODES:
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

print(f"  Total mutations: {final_count:,}")
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

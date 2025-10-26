#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PHASE 3 : Import DVF+ Chablais"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_batch

load_dotenv()

DB_HOST = "db.fwcuftkjofoxyjbjzdnh.supabase.co"
DB_USER = "postgres"
DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")
DB_NAME = "postgres"
DB_PORT = 5432

CODES_CHABLAIS = {
    '74110', '74140', '74200', '74270', '74360',
    '74390', '74420', '74430', '74470', '74500', '74890'
}

SQL_FILE = r"c:\analyse_immobiliere\data\raw\DVFPlus_2025-1-0_SQL_LAMB93_R084-ED251\1_DONNEES_LIVRAISON\dvf_plus_d74.sql"

print("\n=== PHASE 3: Import DVF+ Chablais ===\n")

conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, port=DB_PORT)
cursor = conn.cursor()
print("OK: Connecte a Supabase\n")

mutation_ids = set()
mutation_count = 0
mutation_chablais = 0
total_adresses = 0
adresses_chablais = 0

# Etape 1: Parser mutations
print("[1/2] Parsing mutations Chablais...")
in_mutation = False
batch = []

with open(SQL_FILE, 'r', encoding='utf-8', errors='ignore') as f:
    for line_num, line in enumerate(f):
        if 'COPY dvf_plus_2025_2.dvf_plus_mutation' in line and 'article_cgi' not in line:
            in_mutation = True
            continue

        if in_mutation:
            if line.startswith(r'\.'):
                if batch:
                    try:
                        cols = ','.join(['%s'] * len(batch[0]))
                        sql = f"INSERT INTO dvf_plus_2025_2.dvf_plus_mutation VALUES ({cols})"
                        execute_batch(cursor, sql, batch, page_size=500)
                        conn.commit()
                    except Exception as e:
                        pass
                break

            if line.strip() and not line.startswith('COPY'):
                mutation_count += 1
                fields = line.strip().split('\t')

                if len(fields) > 18:
                    communes_str = fields[18]
                    is_chablais = any(code in communes_str for code in CODES_CHABLAIS)

                    if is_chablais:
                        mutation_chablais += 1
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
                                pass
                            batch = []

                if mutation_count % 50000 == 0:
                    print(f"  {mutation_count:,} mutations traitees ({mutation_chablais:,} Chablais)")

print(f"OK: {mutation_chablais:,} mutations Chablais identifiees\n")

# Etape 2: Parser adresses
print("[2/2] Parsing adresses Chablais...")
in_adresse = False
batch = []

with open(SQL_FILE, 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        if 'COPY dvf_plus_2025_2.dvf_plus_adresse' in line and 'dispoparc' not in line and '_local' not in line:
            in_adresse = True
            continue

        if in_adresse:
            if line.startswith(r'\.'):
                if batch:
                    try:
                        cols = ','.join(['%s'] * len(batch[0]))
                        sql = f"INSERT INTO dvf_plus_2025_2.dvf_plus_adresse VALUES ({cols})"
                        execute_batch(cursor, sql, batch, page_size=1000)
                        conn.commit()
                    except Exception as e:
                        pass
                break

            if line.strip() and not line.startswith('COPY'):
                total_adresses += 1
                fields = line.strip().split('\t')

                if len(fields) >= 7:
                    codepostal = fields[6]
                    if codepostal in CODES_CHABLAIS:
                        adresses_chablais += 1
                        fields = [None if f == r'\N' else f for f in fields]
                        batch.append(tuple(fields))

                        if len(batch) >= 1000:
                            try:
                                cols = ','.join(['%s'] * len(batch[0]))
                                sql = f"INSERT INTO dvf_plus_2025_2.dvf_plus_adresse VALUES ({cols})"
                                execute_batch(cursor, sql, batch, page_size=1000)
                                conn.commit()
                            except Exception as e:
                                pass
                            batch = []

print(f"OK: {adresses_chablais:,} adresses Chablais importees\n")

# Validation
print("=== RESULTATS ===")
print(f"Mutations total dept 74: {mutation_count:,}")
print(f"Mutations Chablais: {mutation_chablais:,} ({100*mutation_chablais/max(1,mutation_count):.1f}%)")
print(f"Adresses Chablais: {adresses_chablais:,}/{total_adresses:,}")

cursor.execute("SELECT COUNT(*) FROM dvf_plus_2025_2.dvf_plus_mutation")
db_count = cursor.fetchone()[0]
print(f"\nVERIFICATION DB: {db_count:,} mutations en base")

cursor.close()
conn.close()
print("\nOK: PHASE 3 COMPLETE\n")

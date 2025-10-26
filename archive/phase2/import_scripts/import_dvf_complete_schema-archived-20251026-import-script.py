#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Importer le schéma DVF+ complet depuis dvf_initial.sql
Utilise psycopg2 pour parsing SQL robuste
"""

import os
import sys
import io
import re
from dotenv import load_dotenv
import psycopg2

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

print("=" * 70)
print("IMPORT SCHEMA DVF+ COMPLET")
print("=" * 70)

db_password = os.getenv("SUPABASE_DB_PASSWORD")
schema_file = r"c:\analyse_immobiliere\data\raw\DVFPlus_2025-1-0_SQL_LAMB93_R084-ED251\1_DONNEES_LIVRAISON\dvf_initial.sql"

try:
    # Connexion
    conn = psycopg2.connect(
        host="db.fwcuftkjofoxyjbjzdnh.supabase.co",
        database="postgres",
        user="postgres",
        password=db_password,
        port=5432
    )

    cursor = conn.cursor()

    print(f"\n📂 Lecture {schema_file}...")

    # Lire le fichier
    with open(schema_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    print(f"   ✅ Fichier chargé ({len(sql_content)} caractères)")

    # Parser les statements SQL
    # Diviser par ; mais ignorer les ; dans les strings
    statements = []
    current = ""
    in_string = False
    escape_next = False

    for i, char in enumerate(sql_content):
        if escape_next:
            current += char
            escape_next = False
            continue

        if char == '\\' and in_string:
            current += char
            escape_next = True
            continue

        if char == "'" and not escape_next:
            in_string = not in_string
            current += char
            continue

        if char == ';' and not in_string:
            stmt = current.strip()
            if stmt and not stmt.startswith('--'):
                statements.append(stmt)
            current = ""
            continue

        current += char

    if current.strip():
        stmt = current.strip()
        if stmt and not stmt.startswith('--'):
            statements.append(stmt)

    print(f"\n💾 Exécution {len(statements)} statements...")

    success_count = 0
    error_count = 0

    for i, stmt in enumerate(statements):
        try:
            cursor.execute(stmt)
            success_count += 1

            if (i + 1) % 50 == 0:
                conn.commit()
                print(f"   ✓ {i + 1}/{len(statements)} statements exécutés...")

        except psycopg2.Error as e:
            error_count += 1
            if error_count <= 5:
                # Afficher seulement les 5 premières erreurs
                if "already exists" not in str(e) and "duplicate" not in str(e):
                    print(f"   ⚠️  Statement {i + 1}: {str(e)[:80]}")

    conn.commit()

    print(f"\n✅ Import complété:")
    print(f"   - {success_count} statements exécutés avec succès")
    print(f"   - {error_count} erreurs (dont 'already exists')")

    # Vérifier création tables
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_schema LIKE 'dvf%'
    """)
    table_count = cursor.fetchone()[0]
    print(f"   - {table_count} tables créées dans schémas dvf*")

    # Vérifier fonctions
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.routines
        WHERE routine_schema = 'dvf'
    """)
    func_count = cursor.fetchone()[0]
    print(f"   - {func_count} fonctions PostGIS créées")

    # Lister tables principales
    cursor.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'dvf' AND table_name IN (
            'mutation', 'local', 'adresse', 'disposition', 'parcelle'
        )
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    print(f"\n📊 Tables principales DVF créées:")
    for table_name, in tables:
        print(f"   ✅ dvf.{table_name}")

    cursor.close()
    conn.close()

    print("\n" + "=" * 70)
    print("✅ SCHEMA DVF+ COMPLETE IMPORTE")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ ERREUR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

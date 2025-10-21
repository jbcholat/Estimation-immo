#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Importer DVF+ en nettoyant les commentaires pg_dump
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
print("IMPORT SCHEMA DVF+ COMPLET (NETTOYAGE)")
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

    with open(schema_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"   ✅ {len(lines)} lignes chargées")

    # Nettoyer: enlever commentaires pg_dump
    print("\n🧹 Nettoyage commentaires pg_dump...")

    cleaned_lines = []
    skip_until_sql = False

    for line in lines:
        stripped = line.strip()

        # Ignorer commentaires pg_dump (TOC, Type, Schema, Owner, etc.)
        if stripped.startswith('--') and ('TOC entry' in line or 'Type:' in line or
                                           'Schema:' in line or 'Owner:' in line or
                                           'Name:' in line):
            continue

        # Ignorer SET statements simples
        if stripped.startswith('SET ') and not 'search_path' in line.lower():
            continue

        # Garder autres commentaires SQL standards (pas pg_dump)
        if stripped.startswith('--') and 'TOC' not in line:
            cleaned_lines.append(line)
            continue

        # Garder tout le reste
        if stripped:
            cleaned_lines.append(line)

    sql_content = ''.join(cleaned_lines)

    # Diviser par statement
    statements = []
    current = ""
    in_string = False

    for char in sql_content:
        if char == "'" and (not current or current[-1] != '\\'):
            in_string = not in_string

        if char == ';' and not in_string:
            stmt = current.strip()
            if stmt and not stmt.startswith('--'):
                statements.append(stmt)
            current = ""
        else:
            current += char

    print(f"💾 Exécution {len(statements)} statements...")

    success_count = 0
    error_count = 0
    errors = []

    for i, stmt in enumerate(statements):
        try:
            cursor.execute(stmt)
            success_count += 1

            if (i + 1) % 100 == 0:
                conn.commit()
                print(f"   ✓ {i + 1}/{len(statements)}...")

        except psycopg2.Error as e:
            error_count += 1
            error_msg = str(e)
            if error_count <= 10 and "already exists" not in error_msg and "duplicate" not in error_msg:
                errors.append(f"  {i + 1}: {error_msg[:80]}")

    conn.commit()

    print(f"\n✅ Import complété:")
    print(f"   - {success_count} statements OK")
    print(f"   - {error_count} erreurs")

    if errors:
        print(f"\n   Premières erreurs:")
        for err in errors[:5]:
            print(f"   {err}")

    # Vérifier tables
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_schema LIKE 'dvf%'
    """)
    table_count = cursor.fetchone()[0]

    print(f"\n   📊 Tables créées: {table_count}")

    # Lister tables DVF principales
    if table_count > 0:
        cursor.execute("""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema LIKE 'dvf%'
            ORDER BY table_schema, table_name
            LIMIT 20
        """)
        print(f"\n   Tables présentes:")
        for schema, table in cursor.fetchall():
            print(f"      - {schema}.{table}")

    cursor.close()
    conn.close()

    print("\n" + "=" * 70)
    print("✅ IMPORT TERMINE")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ ERREUR: {str(e)}")
    sys.exit(1)

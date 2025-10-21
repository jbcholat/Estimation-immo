#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supprimer tables incomplètes avant import DVF+ complet
"""

import os
import sys
import io
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

print("=" * 70)
print("SUPPRESSION DONNEES ACTUELLES (INCOMPLES)")
print("=" * 70)

db_password = os.getenv("SUPABASE_DB_PASSWORD")
db_url = f"postgresql+psycopg2://postgres:{db_password}@db.fwcuftkjofoxyjbjzdnh.supabase.co:5432/postgres"

engine = create_engine(db_url, echo=False)

try:
    with engine.connect() as conn:
        # Supprimer les vues d'abord (dépendances)
        print("\n1. Suppression des vues...")
        views_to_drop = ['v_mutations_chablais', 'v_mutations_hautesavoie', 'v_mutations_recentes']
        for view in views_to_drop:
            try:
                conn.execute(text(f"DROP VIEW IF EXISTS dvf.{view}"))
                conn.commit()
                print(f"   ✅ Vue {view} supprimée")
            except Exception as e:
                print(f"   ⚠️  Erreur suppression {view}: {str(e)[:60]}")

        # Supprimer les tables
        print("\n2. Suppression des tables...")
        tables_to_drop = ['dvf.mutations', 'dvf.mutation_74']
        for table in tables_to_drop:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                conn.commit()
                print(f"   ✅ Table {table} supprimée")
            except Exception as e:
                print(f"   ⚠️  Erreur suppression {table}: {str(e)[:60]}")

        # Vérifier schéma subsiste
        print("\n3. Vérification...")
        result = conn.execute(text("""
            SELECT schema_name FROM information_schema.schemata
            WHERE schema_name = 'dvf'
        """))
        if result.fetchone():
            print("   ✅ Schéma dvf préservé")
        else:
            print("   ⚠️  Schéma dvf manquant - sera créé lors du prochain import")

    print("\n" + "=" * 70)
    print("✅ DONNEES SUPPRIMEES")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ ERREUR: {str(e)}")
    sys.exit(1)

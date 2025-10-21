#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Importer le schéma DVF+ dans Supabase
Phase 2 - Setup Database
"""

import os
import sys
import io
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

def import_schema():
    """Importe le schéma DVF+ depuis dvf_initial.sql"""

    print("=" * 70)
    print("IMPORT SCHEMA DVF+ VERS SUPABASE")
    print("=" * 70)

    db_password = os.getenv("SUPABASE_DB_PASSWORD")
    db_url = f"postgresql+psycopg2://postgres:{db_password}@db.fwcuftkjofoxyjbjzdnh.supabase.co:5432/postgres"

    schema_file = r"c:\analyse_immobiliere\data\raw\DVFPlus_2025-1-0_SQL_LAMB93_R084-ED251\1_DONNEES_LIVRAISON\dvf_initial.sql"

    print(f"\n📂 Lecture fichier schema: {schema_file}")

    try:
        # Lire le fichier SQL
        with open(schema_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print(f"   ✅ Fichier chargé ({len(sql_content)} caractères)")

        # Créer engine et importer
        engine = create_engine(db_url, echo=False)

        print("\n💾 Import du schéma en cours...")
        print("   (Cette opération peut prendre quelques minutes)")

        with engine.connect() as conn:
            # Exécuter le script SQL
            # Diviser par ";" pour exécuter statement par statement
            statements = sql_content.split(';')
            count = 0

            for stmt in statements:
                stmt = stmt.strip()
                if stmt and not stmt.startswith('--'):
                    try:
                        conn.execute(text(stmt))
                        count += 1
                        if count % 50 == 0:
                            print(f"   ✓ {count} statements exécutés...")
                    except Exception as e:
                        # Ignorer les erreurs de schémas/tables qui existent déjà
                        if "already exists" not in str(e) and "duplicate" not in str(e):
                            print(f"   ⚠️  Statement échoué: {str(e)[:100]}")

            conn.commit()

        print(f"\n✅ Import complété: {count} statements exécutés")

        # Vérifier les schémas créés
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT schema_name
                FROM information_schema.schemata
                WHERE schema_name LIKE 'dvf%'
                ORDER BY schema_name
            """))
            schemas = result.fetchall()
            if schemas:
                print(f"\n📊 Schémas créés ({len(schemas)}):")
                for schema_name, in schemas:
                    print(f"   - {schema_name}")

        print("\n" + "=" * 70)
        print("✅ SCHEMA DVF+ IMPORTÉ AVEC SUCCÈS")
        print("=" * 70)
        return True

    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        return False

if __name__ == "__main__":
    success = import_schema()
    sys.exit(0 if success else 1)

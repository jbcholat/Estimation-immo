#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Créer vues et index PostGIS
"""

import os
import sys
import io
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

def create_views_and_indexes():
    """Crée les vues et index nécessaires"""

    print("=" * 70)
    print("CREATION VUES ET INDEX POSTGIS")
    print("=" * 70)

    db_password = os.getenv("SUPABASE_DB_PASSWORD")
    db_url = f"postgresql+psycopg2://postgres:{db_password}@db.fwcuftkjofoxyjbjzdnh.supabase.co:5432/postgres"

    engine = create_engine(db_url, echo=False)

    try:
        with engine.connect() as conn:
            # 1. Créer index sur colonnes critiques
            print("\n1️⃣ Création des index...")

            indexes = [
                ("idx_mutations_datemut", "CREATE INDEX IF NOT EXISTS idx_mutations_datemut ON dvf.mutations (datemut DESC)"),
                ("idx_mutations_valeurfonc", "CREATE INDEX IF NOT EXISTS idx_mutations_valeurfonc ON dvf.mutations (valeurfonc)"),
                ("idx_mutations_sbati", "CREATE INDEX IF NOT EXISTS idx_mutations_sbati ON dvf.mutations (sbati)"),
                ("idx_mutations_coddep", "CREATE INDEX IF NOT EXISTS idx_mutations_coddep ON dvf.mutations (coddep)"),
                ("idx_mutations_libnatmut", "CREATE INDEX IF NOT EXISTS idx_mutations_libnatmut ON dvf.mutations (libnatmut)")
            ]

            for name, sql in indexes:
                try:
                    conn.execute(text(sql))
                    conn.commit()
                    print(f"   ✅ {name} créé")
                except Exception as e:
                    print(f"   ⚠️  {name}: {str(e)[:60]}")

            # 2. Créer vues pratiques
            print("\n2️⃣ Création des vues...")

            views = [
                ("v_mutations_hautesavoie", """
                    CREATE OR REPLACE VIEW dvf.v_mutations_hautesavoie AS
                    SELECT
                        idmutation,
                        datemut,
                        valeurfonc,
                        sbati,
                        nblocmut,
                        coddep,
                        libnatmut
                    FROM dvf.mutations
                    WHERE coddep = '74'
                      AND valeurfonc > 0
                      AND sbati > 0
                    ORDER BY datemut DESC
                """),
                ("v_mutations_chablais", """
                    CREATE OR REPLACE VIEW dvf.v_mutations_chablais AS
                    SELECT *
                    FROM dvf.v_mutations_hautesavoie
                    WHERE coddep IN ('74')
                    ORDER BY datemut DESC
                """),
                ("v_mutations_recentes", """
                    CREATE OR REPLACE VIEW dvf.v_mutations_recentes AS
                    SELECT *
                    FROM dvf.mutations
                    WHERE datemut >= CURRENT_DATE - INTERVAL '3 years'
                      AND valeurfonc > 50000
                      AND sbati > 0
                    ORDER BY datemut DESC
                """)
            ]

            for name, sql in views:
                try:
                    conn.execute(text(sql))
                    conn.commit()
                    print(f"   ✅ Vue {name} créée")
                except Exception as e:
                    print(f"   ⚠️  Vue {name}: {str(e)[:60]}")

            # 3. Vérifier les résultats
            print("\n3️⃣ Vérification des index...")
            result = conn.execute(text("""
                SELECT indexname FROM pg_indexes
                WHERE schemaname = 'dvf'
                ORDER BY indexname
            """))
            indexes_list = result.fetchall()
            print(f"   ✅ {len(indexes_list)} index dans schéma dvf:")
            for index_name, in indexes_list:
                print(f"      - {index_name}")

            print("\n4️⃣ Vérification des vues...")
            result = conn.execute(text("""
                SELECT viewname FROM pg_views
                WHERE schemaname = 'dvf'
                ORDER BY viewname
            """))
            views_list = result.fetchall()
            print(f"   ✅ {len(views_list)} vues dans schéma dvf:")
            for view_name, in views_list:
                print(f"      - {view_name}")

            # Compter les données par vue
            print("\n5️⃣ Données dans les vues...")
            for view_name in ['v_mutations_hautesavoie', 'v_mutations_chablais', 'v_mutations_recentes']:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM dvf.{view_name}"))
                    count = result.scalar()
                    print(f"   - {view_name}: {count} mutations")
                except:
                    pass

        print("\n" + "=" * 70)
        print("✅ VUES ET INDEX CREES AVEC SUCCES")
        print("=" * 70)
        return True

    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_views_and_indexes()
    sys.exit(0 if success else 1)

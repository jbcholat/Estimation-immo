#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import final DVF+ avec parsing robuste
"""

import os
import sys
import io
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine, text

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

def final_import():
    """Import final avec pandas"""

    print("=" * 70)
    print("IMPORT DVF+ FINAL AVEC PARSING ROBUSTE")
    print("=" * 70)

    db_password = os.getenv("SUPABASE_DB_PASSWORD")
    db_url = f"postgresql+psycopg2://postgres:{db_password}@db.fwcuftkjofoxyjbjzdnh.supabase.co:5432/postgres"
    csv_file = r"c:\analyse_immobiliere\data\raw\mutation_74.csv"

    engine = create_engine(db_url, echo=False)

    try:
        # Créer table
        with engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS dvf"))
            table_sql = """
            CREATE TABLE IF NOT EXISTS dvf.mutations (
                idmutation BIGINT PRIMARY KEY,
                datemut VARCHAR(20),
                valeurfonc FLOAT,
                nblocmut INTEGER,
                sbati FLOAT,
                coddep VARCHAR(3),
                libnatmut VARCHAR(200)
            )
            """
            conn.execute(text(table_sql))
            conn.commit()
            print("✅ Table créée")

        print(f"\n📥 Lecture {csv_file}...")

        # Lire CSV avec pandas
        df = pd.read_csv(csv_file, sep=';', dtype={
            'idmutation': 'Int64',
            'datemut': 'str',
            'valeurfonc': 'float',
            'nblocmut': 'Int64',
            'sbati': 'float',
            'coddep': 'str',
            'libnatmut': 'str'
        })

        print(f"   ✅ {len(df)} lignes chargées")

        # Sélectionner et nettoyer les colonnes
        df_clean = pd.DataFrame({
            'idmutation': df['idmutation'],
            'datemut': df['datemut'],
            'valeurfonc': df['valeurfonc'],
            'nblocmut': df['nblocmut'],
            'sbati': df['sbati'],
            'coddep': df['coddep'].astype(str).str[:3],
            'libnatmut': df['libnatmut'].astype(str).str[:200]
        })

        # Nettoyer les valeurs NA
        df_clean = df_clean.fillna({'datemut': '2020-01-01', 'valeurfonc': 0, 'sbati': 0})

        print(f"\n💾 Insertion dans Supabase...")

        # Insérer par chunks
        chunk_size = 5000
        total_inserted = 0

        with engine.connect() as conn:
            for i, chunk in enumerate(df_clean.to_dict('records')):
                try:
                    insert_sql = text("""
                        INSERT INTO dvf.mutations
                        (idmutation, datemut, valeurfonc, nblocmut, sbati, coddep, libnatmut)
                        VALUES (:idmutation, :datemut, :valeurfonc, :nblocmut, :sbati, :coddep, :libnatmut)
                        ON CONFLICT (idmutation) DO NOTHING
                    """)
                    conn.execute(insert_sql, chunk)
                    total_inserted += 1

                    if (i + 1) % chunk_size == 0:
                        conn.commit()
                        print(f"   ✓ {i + 1} lignes insérées...")

                except Exception as e:
                    if i < 5:
                        print(f"   ⚠️  Ligne {i}: {str(e)[:60]}")

            conn.commit()

        # Vérifier
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM dvf.mutations"))
            count = result.scalar()

        print(f"\n✅ Import complété: {count} mutations dans Supabase")

        print("\n" + "=" * 70)
        print("✅ DONNEES DVF+ IMPORTEES")
        print("=" * 70)
        return True

    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = final_import()
    sys.exit(0 if success else 1)

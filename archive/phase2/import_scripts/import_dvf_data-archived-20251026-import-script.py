#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Importer les données DVF+ (mutation_74.csv) vers Supabase
Phase 2 - Setup Database
"""

import os
import sys
import io
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, Table, Column, String, Integer, Float, Date, MetaData
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

def create_dvf_tables(engine):
    """Crée les tables DVF simplifiées"""

    print("Création des tables DVF...")

    with engine.connect() as conn:
        # Créer schéma dvf
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS dvf"))
        conn.commit()

        # Table simplifiée pour mutations
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS dvf.mutation_74 (
            idmutation BIGINT PRIMARY KEY,
            datemut DATE,
            valeurfonc FLOAT,
            nblocmut INTEGER,
            sbati FLOAT,
            coddep VARCHAR(3),
            libnatmut VARCHAR(100),
            nbcomm INTEGER,
            nbapt2pp INTEGER,
            nbmai2pp INTEGER
        )
        """
        conn.execute(text(create_table_sql))
        conn.commit()
        print("   ✅ Table dvf.mutation_74 créée")

def import_mutation_csv(engine):
    """Importe mutation_74.csv vers Supabase"""

    print("\n" + "=" * 70)
    print("IMPORT DONNEES DVF+ (mutation_74.csv) VERS SUPABASE")
    print("=" * 70)

    csv_file = r"c:\analyse_immobiliere\data\raw\mutation_74.csv"

    db_password = os.getenv("SUPABASE_DB_PASSWORD")
    db_url = f"postgresql+psycopg2://postgres:{db_password}@db.fwcuftkjofoxyjbjzdnh.supabase.co:5432/postgres"

    engine = create_engine(db_url, echo=False)

    try:
        # Créer les tables
        create_dvf_tables(engine)

        print(f"\n📂 Lecture fichier CSV: {csv_file}")

        # Lire le CSV en chunks
        chunks = pd.read_csv(csv_file, sep=';', chunksize=5000)

        print("   Lecture du fichier en cours...")
        total_rows = 0
        chunk_count = 0

        for chunk in chunks:
            chunk_count += 1

            # Sélectionner les colonnes pertinentes
            cols_to_use = ['idmutation', 'datemut', 'valeurfonc', 'nblocmut', 'sbati',
                           'coddep', 'libnatmut', 'nbcomm', 'nbapt2pp', 'nbmai2pp']

            # Vérifier que les colonnes existent
            cols_present = [c for c in cols_to_use if c in chunk.columns]
            chunk = chunk[cols_present]

            # Convertir les types
            chunk['datemut'] = pd.to_datetime(chunk['datemut'], format='%d/%m/%Y', errors='coerce')
            chunk['valeurfonc'] = pd.to_numeric(chunk['valeurfonc'], errors='coerce')
            chunk['sbati'] = pd.to_numeric(chunk['sbati'], errors='coerce')

            # Insérer dans la base de données
            with engine.connect() as conn:
                for _, row in chunk.iterrows():
                    insert_stmt = text("""
                        INSERT INTO dvf.mutation_74
                        (idmutation, datemut, valeurfonc, nblocmut, sbati, coddep, libnatmut, nbcomm, nbapt2pp, nbmai2pp)
                        VALUES (:idmutation, :datemut, :valeurfonc, :nblocmut, :sbati, :coddep, :libnatmut, :nbcomm, :nbapt2pp, :nbmai2pp)
                        ON CONFLICT (idmutation) DO NOTHING
                    """)
                    try:
                        conn.execute(insert_stmt, {
                            'idmutation': row.get('idmutation'),
                            'datemut': row.get('datemut'),
                            'valeurfonc': row.get('valeurfonc'),
                            'nblocmut': row.get('nblocmut'),
                            'sbati': row.get('sbati'),
                            'coddep': str(row.get('coddep', '74'))[:3],
                            'libnatmut': str(row.get('libnatmut', ''))[:100],
                            'nbcomm': row.get('nbcomm'),
                            'nbapt2pp': row.get('nbapt2pp'),
                            'nbmai2pp': row.get('nbmai2pp')
                        })
                    except Exception as e:
                        print(f"   ⚠️  Erreur insertion ligne: {e}")

                conn.commit()

            total_rows += len(chunk)
            if chunk_count % 5 == 0:
                print(f"   ✓ {total_rows} lignes insérées...")

        # Vérifier les données
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM dvf.mutation_74"))
            count = result.scalar()

        print(f"\n✅ Import complété: {count} mutations importées")

        print("\n" + "=" * 70)
        print("✅ DONNEES DVF+ IMPORTEES AVEC SUCCÈS")
        print("=" * 70)
        return True

    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = import_mutation_csv(None)
    sys.exit(0 if success else 1)

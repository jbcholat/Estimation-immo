#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import rapide des données DVF+ using COPY (beaucoup plus rapide)
"""

import os
import sys
import io
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

def quick_import():
    """Import rapide via COPY PostgreSQL"""

    print("=" * 70)
    print("IMPORT RAPIDE DVF+ VIA COPY")
    print("=" * 70)

    db_password = os.getenv("SUPABASE_DB_PASSWORD")
    db_url = f"postgresql+psycopg2://postgres:{db_password}@db.fwcuftkjofoxyjbjzdnh.supabase.co:5432/postgres"

    csv_file = r"c:\analyse_immobiliere\data\raw\mutation_74.csv"

    engine = create_engine(db_url, echo=False)

    try:
        with engine.connect() as conn:
            # 1. Créer schéma et table si n'existe pas
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS dvf"))

            table_sql = """
            CREATE TABLE IF NOT EXISTS dvf.mutations (
                idmutation BIGINT PRIMARY KEY,
                datemut DATE,
                valeurfonc FLOAT,
                sbati FLOAT,
                nblocmut INTEGER,
                nbapt2pp INTEGER,
                nbmai2pp INTEGER,
                coddep VARCHAR(3),
                libnatmut VARCHAR(200)
            )
            """
            conn.execute(text(table_sql))
            conn.commit()
            print("✅ Table créée")

            # 2. Import données simplifiées
            print(f"\n📥 Import {csv_file}...")

            # Utiliser psycopg2 directement pour COPY
            from psycopg2 import connect

            db_conn = connect(
                host="db.fwcuftkjofoxyjbjzdnh.supabase.co",
                database="postgres",
                user="postgres",
                password=db_password,
                port=5432
            )

            cursor = db_conn.cursor()

            # Lecture du CSV et insertion des donnees valides
            with open(csv_file, 'r', encoding='utf-8') as f:
                # Sauter header
                header = f.readline()

                # Insérer les données
                count = 0
                skip = 0

                for line_num, line in enumerate(f, 1):
                    try:
                        fields = line.rstrip('\n').split(';')

                        idmutation = int(fields[0])
                        datemut = fields[6] if fields[6] and fields[6] != "NaT" else None
                        valeurfonc = float(fields[12]) if fields[12] else None
                        nblocmut = int(fields[13]) if fields[13] else 0
                        nbcomm = int(fields[15]) if fields[15] else 0
                        nbcodes = fields[16] if fields[16] else "[]"
                        nbparmut = int(fields[19]) if fields[19] else 0
                        nbsuf = int(fields[21]) if fields[21] else 0
                        sterr = float(fields[22]) if fields[22] else 0
                        nbvolmut = int(fields[23]) if fields[23] else 0
                        sbati = float(fields[44]) if fields[44] else 0
                        nbapt2pp = int(fields[33]) if fields[33] else 0
                        nbmai2pp = int(fields[29]) if fields[29] else 0
                        libnatmut = fields[10][:200] if fields[10] else ""
                        coddep = fields[9][:3] if fields[9] else "74"

                        if datemut:
                            datemut_formatted = datemut  # Assuming correct format
                        else:
                            datemut_formatted = None

                        cursor.execute("""
                            INSERT INTO dvf.mutations
                            (idmutation, datemut, valeurfonc, sbati, nblocmut, nbapt2pp, nbmai2pp, coddep, libnatmut)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (idmutation) DO NOTHING
                        """, (idmutation, datemut_formatted, valeurfonc, sbati, nblocmut, nbapt2pp, nbmai2pp, coddep, libnatmut))

                        count += 1
                        if count % 10000 == 0:
                            db_conn.commit()
                            print(f"   ✓ {count} lignes insérées...")

                    except Exception as e:
                        skip += 1
                        if skip < 10:
                            print(f"   ⚠️  Ligne {line_num} échouée: {str(e)[:80]}")

                db_conn.commit()

            cursor.close()
            db_conn.close()

            print(f"\n✅ Import complété:")
            print(f"   - {count} lignes insérées")
            print(f"   - {skip} lignes échouées")

            # Vérifier
            with engine.connect() as check_conn:
                result = check_conn.execute(text("SELECT COUNT(*) FROM dvf.mutations"))
                total = result.scalar()
                print(f"   - Total dans DB: {total}")

        print("\n" + "=" * 70)
        print("✅ IMPORT RAPIDE COMPLÉTÉ")
        print("=" * 70)
        return True

    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = quick_import()
    sys.exit(0 if success else 1)

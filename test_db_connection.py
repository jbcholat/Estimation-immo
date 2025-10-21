#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test connexion PostgreSQL Supabase + PostGIS
Phase 2 - Setup Database
"""

import os
import sys
import io
from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy import create_engine, text

# Forcer UTF-8 sur Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Charger variables d'environnement
load_dotenv()

def test_connection():
    """Test la connexion à la base de données PostgreSQL Supabase"""

    print("=" * 60)
    print("TEST CONNEXION POSTGRESQL SUPABASE + POSTGIS")
    print("=" * 60)

    # Récupérer credentials
    url = os.getenv("SUPABASE_URL")
    db_password = os.getenv("SUPABASE_DB_PASSWORD")

    if not db_password:
        print("❌ ERREUR: SUPABASE_DB_PASSWORD non trouvé dans .env")
        return False

    # Construire connection string
    db_url = f"postgresql+psycopg2://postgres:{db_password}@db.fwcuftkjofoxyjbjzdnh.supabase.co:5432/postgres"

    print(f"\n🔗 Tentative connexion: db.fwcuftkjofoxyjbjzdnh.supabase.co:5432")

    try:
        # Créer engine SQLAlchemy
        engine = create_engine(db_url, echo=False)

        # Test connexion
        with engine.connect() as conn:
            # Test 1: Vérifier connexion simple
            result = conn.execute(text("SELECT 1"))
            print("✅ Connexion PostgreSQL réussie")

            # Test 2: Vérifier PostGIS
            try:
                postgis_result = conn.execute(text("SELECT postgis_version()"))
                postgis_version = postgis_result.scalar()
                print(f"✅ PostGIS activé: {postgis_version}")
            except Exception as e:
                print(f"⚠️  PostGIS non activé: {str(e)}")
                print("   → À activer via Supabase Dashboard (Settings → Extensions → PostGIS)")

            # Test 3: Lister les extensions disponibles
            try:
                ext_result = conn.execute(text("""
                    SELECT extname, extversion
                    FROM pg_extension
                    ORDER BY extname
                """))
                extensions = ext_result.fetchall()
                print(f"\n📦 Extensions disponibles ({len(extensions)}):")
                for ext_name, ext_version in extensions:
                    print(f"   - {ext_name} ({ext_version})")
            except Exception as e:
                print(f"⚠️  Erreur lecture extensions: {e}")

            # Test 4: Lister les tables
            try:
                tables_result = conn.execute(text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """))
                tables = tables_result.fetchall()
                if tables:
                    print(f"\n📋 Tables existantes ({len(tables)}):")
                    for table_name, in tables:
                        print(f"   - {table_name}")
                else:
                    print("\n📋 Aucune table dans le schéma public")
            except Exception as e:
                print(f"⚠️  Erreur lecture tables: {e}")

        print("\n" + "=" * 60)
        print("✅ TEST RÉUSSI - Base de données opérationnelle")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ ERREUR CONNEXION: {str(e)}")
        print("\n" + "=" * 60)
        print("Diagnostique:")
        print("- Vérifier SUPABASE_DB_PASSWORD dans .env")
        print("- Vérifier connexion réseau vers db.fwcuftkjofoxyjbjzdnh.supabase.co")
        print("- Vérifier que le projet Supabase est actif")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

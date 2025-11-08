#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Activer PostGIS sur Supabase
Phase 2 - Setup Database
"""

import os
import sys
import io
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Forcer UTF-8 sur Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

def activate_postgis():
    """Active l'extension PostGIS sur la base de données"""

    print("=" * 70)
    print("ACTIVATION POSTGIS - SUPABASE")
    print("=" * 70)

    db_password = os.getenv("SUPABASE_DB_PASSWORD")
    db_url = f"postgresql+psycopg2://postgres:{db_password}@db.fwcuftkjofoxyjbjzdnh.supabase.co:5432/postgres"

    try:
        engine = create_engine(db_url, echo=False)

        with engine.connect() as conn:
            # Créer une nouvelle transaction pour éviter les erreurs
            conn.rollback()

            print("\n1. Activation extension PostGIS...")
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
            conn.commit()
            print("   ✅ Extension PostGIS créée")

            print("\n2. Activation PostGIS Topology...")
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis_topology"))
            conn.commit()
            print("   ✅ Extension PostGIS Topology créée")

            print("\n3. Vérification PostGIS...")
            result = conn.execute(text("SELECT postgis_version()"))
            version = result.scalar()
            print(f"   ✅ PostGIS actif: {version}")

            print("\n" + "=" * 70)
            print("✅ POSTGIS ACTIVÉ AVEC SUCCÈS")
            print("=" * 70)
            return True

    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        print("\nAlternative: Activer via Supabase Dashboard")
        print("1. Aller à: https://app.supabase.com/project/fwcuftkjofoxyjbjzdnh/database/extensions")
        print("2. Chercher 'postgis'")
        print("3. Cliquer 'Enable'")
        return False

if __name__ == "__main__":
    success = activate_postgis()
    sys.exit(0 if success else 1)

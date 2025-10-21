"""Test connexion Supabase et verification PostGIS"""
# -*- coding: utf-8 -*-
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Fix encoding pour Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout.reconfigure(encoding='utf-8')

# Charger variables d'environnement
load_dotenv()

# Configuration connexion
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Extraire projet ID de l'URL
project_id = SUPABASE_URL.replace('https://', '').replace('.supabase.co', '')

# Créer connection string PostgreSQL (direct connection port 5432)
db_url = f"postgresql+psycopg2://postgres:{SUPABASE_KEY}@db.{project_id}.supabase.co:5432/postgres"

print("=" * 60)
print("TEST CONNEXION SUPABASE - ESTIMATEUR IMMOBILIER MVP")
print("=" * 60)
print()
print(f"URL Supabase: {SUPABASE_URL}")
print(f"Project ID: {project_id}")
print(f"Database Host: db.{project_id}.supabase.co:5432")
print()

try:
    # Créer engine SQLAlchemy
    engine = create_engine(db_url, echo=False)

    print("✅ Engine SQLAlchemy créé avec succès")
    print()

    # Test connexion simple
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 as test"))
        test_value = result.fetchone()[0]
        print(f"✅ Connexion Supabase OK (test query returned: {test_value})")
        print()

        # Vérifier version PostgreSQL
        result = conn.execute(text("SELECT version()"))
        pg_version = result.fetchone()[0]
        print(f"PostgreSQL version:")
        print(f"  {pg_version[:80]}...")
        print()

        # Vérifier PostGIS activé
        try:
            result = conn.execute(text("SELECT postgis_version()"))
            postgis_version = result.fetchone()[0]
            print(f"✅ PostGIS activé - Version: {postgis_version}")
            print()
        except Exception as e:
            print(f"⚠️  PostGIS NON activé - Erreur: {str(e)}")
            print("   ACTION REQUISE: Activer extension PostGIS")
            print()

        # Lister tables existantes
        result = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        tables = [row[0] for row in result.fetchall()]

        if tables:
            print(f"📊 Tables existantes dans schema 'public' ({len(tables)}):")
            for table in tables:
                print(f"   - {table}")
        else:
            print("⚠️  Aucune table trouvée dans schema 'public'")
            print("   ACTION REQUISE: Importer données DVF+")
        print()

        # Vérifier extensions
        result = conn.execute(text("""
            SELECT extname, extversion
            FROM pg_extension
            ORDER BY extname
        """))
        extensions = result.fetchall()

        print(f"🔌 Extensions PostgreSQL activées ({len(extensions)}):")
        for ext_name, ext_version in extensions:
            marker = "✅" if ext_name in ['postgis', 'postgis_topology'] else "  "
            print(f"   {marker} {ext_name} (v{ext_version})")
        print()

    print("=" * 60)
    print("RÉSUMÉ TEST")
    print("=" * 60)
    print("✅ Connexion Supabase fonctionnelle")
    print("✅ PostgreSQL accessible")
    if 'postgis_version' in locals():
        print("✅ PostGIS activé et opérationnel")
    else:
        print("⚠️  PostGIS à activer")

    if tables:
        print(f"✅ {len(tables)} table(s) détectée(s)")
    else:
        print("⚠️  Données DVF+ à importer")
    print()

except Exception as e:
    print(f"❌ ERREUR DE CONNEXION:")
    print(f"   {str(e)}")
    print()
    print("Suggestions de résolution:")
    print("1. Vérifier SUPABASE_KEY dans .env")
    print("2. Vérifier accès réseau (firewall)")
    print("3. Vérifier projet Supabase actif")
    print()

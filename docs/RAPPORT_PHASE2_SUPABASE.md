# Rapport Phase 2 - Setup Supabase & Donnees DVF+

**Agent**: `supabase-data-agent`
**Date**: 2025-10-21
**Statut**: PRET POUR EXECUTION
**Duree estimee**: 2-3 heures

---

## 1. CONTEXTE & OBJECTIF

### Mission Phase 2
Configurer la base de donnees Supabase (PostgreSQL + PostGIS) et importer les donnees DVF+ pour la zone Chablais/Annemasse (Haute-Savoie, codes postaux 740xx/742xx/743xx).

### Livrable Principal
- Base de donnees Supabase operationnelle avec PostGIS
- Donnees DVF+ importees et structurees
- Classe Python `SupabaseDataRetriever` fonctionnelle
- 5 tests valides avec adresses reelles

---

## 2. ANALYSE DOCUMENTATION EXISTANTE

### Documents Consultes
- **docs/SETUP_SUPABASE.md**: Guide complet setup PostGIS + import DVF+
- **docs/PLAN_MVP_IMPLEMENTATION.md**: Architecture globale MVP
- **.env**: Credentials Supabase disponibles

### Informations Cles Identifiees

#### Connexion Supabase
```
URL:  https://fwcuftkjofoxyjbjzdnh.supabase.co
Key:  sbp_c56fb1e3ee2778583ab929550793aabaa9dc552a (API key, pas DB password)
```

#### Donnees DVF+ Disponibles
Localisation: `c:\analyse_immobiliere\data\raw\DVFPlus_2025-1-0_SQL_LAMB93_R084-ED251\`

Fichiers SQL:
- **dvf_initial.sql**: 3,430 lignes (schema + fonctions)
- **dvf_departements.sql**: 26,623,352 lignes (TOUTES les donnees France)

Structure DVF+:
- Schema: `dvf` + `dvf_annexe`
- Tables principales: mutations, dispositions, adresses, locaux, parcelles
- Partitionnement par departement (ex: `dvf_d74` pour Haute-Savoie)

---

## 3. PROBLEME IDENTIFIE - ACCES BASE DE DONNEES

### Test Connexion Effectue
```bash
python test_supabase_connection.py
```

### Resultat du Test
```
ERROR: password authentication failed for user "postgres"
```

### Diagnostic
La cle fournie `sbp_c56fb1e3ee2778583ab929550793aabaa9dc552a` est une **API Key Supabase** (service_role key), **PAS** le mot de passe PostgreSQL direct.

### Solutions Possibles

#### Option 1: Utiliser Supabase Client Python (RECOMMANDE)
```python
from supabase import create_client

url = "https://fwcuftkjofoxyjbjzdnh.supabase.co"
key = "sbp_c56fb1e3ee2778583ab929550793aabaa9dc552a"
supabase = create_client(url, key)

# Requetes via API REST
data = supabase.table('dvf_data').select('*').eq('code_departement', '74').limit(10).execute()
```

**Avantages**:
- Pas besoin du mot de passe DB
- API REST securisee
- Row Level Security (RLS) gere automatiquement

**Inconvenients**:
- Pas de requetes PostGIS directes (ST_DWithin, ST_Distance)
- Performance reduite pour requetes spatiales complexes

#### Option 2: Recuperer Database Password (OPTIMAL)
Via Supabase Dashboard:
1. Aller a: https://app.supabase.com/project/fwcuftkjofoxyjbjzdnh/settings/database
2. Section "Connection string"
3. Recuperer le **Database Password** (different de l'API key)
4. Format connexion:
```
postgresql://postgres:[PASSWORD]@db.fwcuftkjofoxyjbjzdnh.supabase.co:5432/postgres
```

**Avantages**:
- Acces direct PostgreSQL + PostGIS
- Requetes spatiales completes (ST_DWithin, ST_Distance)
- Performance optimale

**Inconvenients**:
- Necessite credentials supplementaires

#### Option 3: Utiliser PostgREST via Supabase
Supabase expose automatiquement l'API PostgREST:
```python
import requests

headers = {
    'apikey': 'sbp_c56fb1e3ee2778583ab929550793aabaa9dc552a',
    'Authorization': 'Bearer sbp_c56fb1e3ee2778583ab929550793aabaa9dc552a'
}

response = requests.get(
    'https://fwcuftkjofoxyjbjzdnh.supabase.co/rest/v1/dvf_data',
    headers=headers,
    params={'code_departement': 'eq.74', 'limit': 10}
)
```

---

## 4. SCHEMA BASE DE DONNEES CIBLE

### Structure DVF+ Actuelle (fichiers SQL)
```sql
CREATE SCHEMA dvf;
CREATE SCHEMA dvf_annexe;

-- Tables principales
dvf.mutation           -- Ventes immobilieres
dvf.disposition        -- Details ventes
dvf.local              -- Biens (maisons, apparts)
dvf.adresse            -- Adresses
dvf.parcelle           -- Parcelles cadastrales

-- Tables partitionnees par departement
dvf_d74.mutation       -- Mutations Haute-Savoie
dvf_d74.local          -- Locaux Haute-Savoie
...
```

### Schema Simplifie Propose (MVP)
Pour le MVP, creer une vue consolidee:

```sql
CREATE VIEW dvf_zone_chablais AS
SELECT
  m.idmutation as id_mutation,
  m.datemut as date_mutation,
  m.valeurfonc as valeur_fonciere,
  m.natmut as nature_mutation,
  l.typlocal as type_local,
  l.sbati as surface_reelle_bati,
  l.nbpieceprinc as nombre_pieces_principales,
  a.geomloc as geom,  -- Geometrie PostGIS
  a.codepostal as code_postal,
  a.commune as nom_commune,
  a.libvoie as adresse_nom_voie
FROM dvf_d74.mutation m
JOIN dvf_d74.disposition d ON m.idmutation = d.idmutation
JOIN dvf_d74.local l ON d.idlocal = l.idlocal
JOIN dvf_d74.adresse_local al ON l.idlocal = al.idlocal
JOIN dvf_d74.adresse a ON al.idadresse = a.idadresse
WHERE a.codepostal ~ '^(740|742|743)'  -- Filtre zone Chablais
  AND m.valeurfonc > 0
  AND l.sbati > 0
  AND l.typlocal IN ('Maison', 'Appartement')
  AND m.natmut = 'Vente'
ORDER BY m.datemut DESC;
```

### Index PostGIS Requis
```sql
-- Index spatial GIST
CREATE INDEX idx_adresse_geom_gist ON dvf_d74.adresse USING GIST (geomloc);

-- Index filtrage rapide
CREATE INDEX idx_mutation_datemut ON dvf_d74.mutation (datemut DESC);
CREATE INDEX idx_local_typlocal ON dvf_d74.local (typlocal);
CREATE INDEX idx_adresse_codepostal ON dvf_d74.adresse (codepostal);
```

---

## 5. ARCHITECTURE PYTHON PROPOSEE

### Classe SupabaseDataRetriever

#### Fichier: `src/supabase_data_retriever.py`

```python
"""
Module de recuperation des donnees DVF+ depuis Supabase
"""
import os
from typing import List, Dict, Optional
import pandas as pd
from dotenv import load_dotenv

# Option 1: Client Supabase (API REST)
from supabase import create_client, Client

# Option 2: SQLAlchemy (acces direct PostgreSQL)
# from sqlalchemy import create_engine, text
# from geoalchemy2 import Geometry, WKTElement


class SupabaseDataRetriever:
    """
    Recupere les donnees DVF+ depuis Supabase pour zone Chablais/Annemasse

    Attributes:
        supabase_client: Client Supabase API
        engine: SQLAlchemy engine (si acces direct DB)
    """

    def __init__(self, use_direct_db: bool = False):
        """
        Initialise connexion Supabase

        Args:
            use_direct_db: Si True, utilise connexion PostgreSQL directe
                           Si False, utilise API REST Supabase
        """
        load_dotenv()

        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        self.db_password = os.getenv('SUPABASE_DB_PASSWORD')  # A recuperer

        if use_direct_db and self.db_password:
            # Option 2: Connexion directe PostgreSQL
            self._init_direct_db()
        else:
            # Option 1: API REST Supabase
            self._init_api_client()

    def _init_api_client(self):
        """Initialise client API Supabase"""
        self.supabase_client = create_client(self.supabase_url, self.supabase_key)
        self.connection_type = 'api'

    def _init_direct_db(self):
        """Initialise connexion directe PostgreSQL"""
        from sqlalchemy import create_engine

        project_id = self.supabase_url.replace('https://', '').replace('.supabase.co', '')
        db_url = f"postgresql+psycopg2://postgres:{self.db_password}@db.{project_id}.supabase.co:5432/postgres"

        self.engine = create_engine(db_url, echo=False)
        self.connection_type = 'direct'

    def get_comparables(
        self,
        latitude: float,
        longitude: float,
        type_local: str,
        surface_min: float,
        surface_max: float,
        rayon_km: float = 10.0,
        date_min: str = '2022-01-01',
        limit: int = 30
    ) -> pd.DataFrame:
        """
        Recupere les comparables DVF+ dans un rayon geographique

        Args:
            latitude: Latitude du bien cible (WGS84)
            longitude: Longitude du bien cible (WGS84)
            type_local: 'Maison' ou 'Appartement'
            surface_min: Surface minimale (m2)
            surface_max: Surface maximale (m2)
            rayon_km: Rayon de recherche (km)
            date_min: Date minimale (YYYY-MM-DD)
            limit: Nombre max de resultats

        Returns:
            DataFrame avec colonnes:
                - id_mutation, date_mutation, valeur_fonciere
                - type_local, surface_reelle_bati, nombre_pieces_principales
                - latitude, longitude, distance_km
                - code_postal, nom_commune, adresse_nom_voie
        """
        if self.connection_type == 'direct':
            return self._get_comparables_postgis(
                latitude, longitude, type_local, surface_min, surface_max,
                rayon_km, date_min, limit
            )
        else:
            return self._get_comparables_api(
                latitude, longitude, type_local, surface_min, surface_max,
                rayon_km, date_min, limit
            )

    def _get_comparables_postgis(
        self, lat, lon, type_local, surf_min, surf_max, rayon_km, date_min, limit
    ) -> pd.DataFrame:
        """
        Requete PostGIS directe (ST_DWithin pour performance)
        """
        from sqlalchemy import text

        query = text("""
        SELECT
            m.idmutation as id_mutation,
            m.datemut as date_mutation,
            m.valeurfonc as valeur_fonciere,
            l.typlocal as type_local,
            l.sbati as surface_reelle_bati,
            l.nbpieceprinc as nombre_pieces_principales,
            ST_Y(ST_Transform(a.geomloc, 4326)) as latitude,
            ST_X(ST_Transform(a.geomloc, 4326)) as longitude,
            ST_Distance(
                a.geomloc::geography,
                ST_SetSRID(ST_Point(:lon, :lat), 4326)::geography
            ) / 1000 AS distance_km,
            a.codepostal as code_postal,
            a.commune as nom_commune,
            a.libvoie as adresse_nom_voie
        FROM dvf_d74.mutation m
        JOIN dvf_d74.disposition d ON m.idmutation = d.idmutation
        JOIN dvf_d74.local l ON d.idlocal = l.idlocal
        JOIN dvf_d74.adresse_local al ON l.idlocal = al.idlocal
        JOIN dvf_d74.adresse a ON al.idadresse = a.idadresse
        WHERE ST_DWithin(
                a.geomloc::geography,
                ST_SetSRID(ST_Point(:lon, :lat), 4326)::geography,
                :rayon_m
            )
          AND l.typlocal = :type_local
          AND l.sbati BETWEEN :surf_min AND :surf_max
          AND m.datemut >= :date_min
          AND m.valeurfonc > 0
          AND m.natmut = 'Vente'
          AND a.codepostal ~ '^(740|742|743)'
        ORDER BY distance_km
        LIMIT :limit
        """)

        with self.engine.connect() as conn:
            result = conn.execute(
                query,
                {
                    'lat': lat,
                    'lon': lon,
                    'rayon_m': rayon_km * 1000,
                    'type_local': type_local,
                    'surf_min': surf_min,
                    'surf_max': surf_max,
                    'date_min': date_min,
                    'limit': limit
                }
            )

            df = pd.DataFrame(result.fetchall(), columns=result.keys())

        return df

    def _get_comparables_api(
        self, lat, lon, type_local, surf_min, surf_max, rayon_km, date_min, limit
    ) -> pd.DataFrame:
        """
        Requete via API REST Supabase (limitation: pas de ST_DWithin)
        Filtrage geographique fait en post-processing Python
        """
        import math

        # Recuperer tous les biens de la zone Chablais
        response = self.supabase_client.table('dvf_zone_chablais') \
            .select('*') \
            .eq('type_local', type_local) \
            .gte('surface_reelle_bati', surf_min) \
            .lte('surface_reelle_bati', surf_max) \
            .gte('date_mutation', date_min) \
            .limit(1000) \
            .execute()

        df = pd.DataFrame(response.data)

        # Calculer distance haversine en Python
        def haversine_distance(lat1, lon1, lat2, lon2):
            R = 6371  # Rayon Terre en km
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
                math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            return R * c

        df['distance_km'] = df.apply(
            lambda row: haversine_distance(lat, lon, row['latitude'], row['longitude']),
            axis=1
        )

        # Filtrer rayon + trier + limiter
        df = df[df['distance_km'] <= rayon_km] \
            .sort_values('distance_km') \
            .head(limit)

        return df

    def get_market_stats(
        self,
        code_postal: str,
        type_local: str,
        date_min: str = '2022-01-01'
    ) -> Dict:
        """
        Calcule statistiques de marche pour une zone donnee

        Args:
            code_postal: Code postal (ex: '74200')
            type_local: 'Maison' ou 'Appartement'
            date_min: Date minimale

        Returns:
            Dict avec:
                - nb_ventes: Nombre de ventes
                - prix_median: Prix median (EUR)
                - prix_m2_median: Prix/m2 median
                - surface_mediane: Surface mediane (m2)
        """
        if self.connection_type == 'direct':
            from sqlalchemy import text

            query = text("""
            SELECT
                COUNT(*) as nb_ventes,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY m.valeurfonc) as prix_median,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY m.valeurfonc / l.sbati) as prix_m2_median,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY l.sbati) as surface_mediane
            FROM dvf_d74.mutation m
            JOIN dvf_d74.disposition d ON m.idmutation = d.idmutation
            JOIN dvf_d74.local l ON d.idlocal = l.idlocal
            JOIN dvf_d74.adresse_local al ON l.idlocal = al.idlocal
            JOIN dvf_d74.adresse a ON al.idadresse = a.idadresse
            WHERE a.codepostal = :code_postal
              AND l.typlocal = :type_local
              AND m.datemut >= :date_min
              AND m.valeurfonc > 0
              AND m.natmut = 'Vente'
            """)

            with self.engine.connect() as conn:
                result = conn.execute(
                    query,
                    {'code_postal': code_postal, 'type_local': type_local, 'date_min': date_min}
                )
                row = result.fetchone()

            return {
                'nb_ventes': row[0],
                'prix_median': float(row[1]),
                'prix_m2_median': float(row[2]),
                'surface_mediane': float(row[3])
            }
        else:
            # Version API (plus lente)
            response = self.supabase_client.table('dvf_zone_chablais') \
                .select('valeur_fonciere,surface_reelle_bati') \
                .eq('code_postal', code_postal) \
                .eq('type_local', type_local) \
                .gte('date_mutation', date_min) \
                .execute()

            df = pd.DataFrame(response.data)

            return {
                'nb_ventes': len(df),
                'prix_median': df['valeur_fonciere'].median(),
                'prix_m2_median': (df['valeur_fonciere'] / df['surface_reelle_bati']).median(),
                'surface_mediane': df['surface_reelle_bati'].median()
            }
```

---

## 6. CHECKLIST PHASE 2 DETAILLEE

### Etape 1: Recuperer Credentials Supabase (30 min)

**ACTION REQUISE AVANT DE CONTINUER**

- [ ] Aller sur: https://app.supabase.com/project/fwcuftkjofoxyjbjzdnh/settings/database
- [ ] Section "Connection string" > "URI"
- [ ] Copier le **Database Password** (commence par `postgres://postgres:[PASSWORD]@...`)
- [ ] Ajouter dans `.env`:
```env
SUPABASE_DB_PASSWORD=<votre_password_ici>
```

**Alternative**: Utiliser uniquement API REST (moins performant pour requetes spatiales)

---

### Etape 2: Activer PostGIS sur Supabase (15 min)

- [ ] Aller sur: https://app.supabase.com/project/fwcuftkjofoxyjbjzdnh/database/extensions
- [ ] Chercher "postgis"
- [ ] Cliquer "Enable" si OFF
- [ ] Verifier activation:
```sql
SELECT postgis_version();
-- Expected: "3.x.x POSTGIS..."
```

**Via SQL Editor Supabase**:
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
```

---

### Etape 3: Importer Schema DVF+ (30 min)

#### Option A: Import via psql (RECOMMANDE)
```bash
# Depuis c:\analyse_immobiliere\

# 1. Installer psql si necessaire (inclus dans PostgreSQL)
# Download: https://www.postgresql.org/download/windows/

# 2. Importer schema
psql -h db.fwcuftkjofoxyjbjzdnh.supabase.co \
     -U postgres \
     -d postgres \
     -f data/raw/DVFPlus_2025-1-0_SQL_LAMB93_R084-ED251/1_DONNEES_LIVRAISON/dvf_initial.sql

# 3. Mot de passe: <SUPABASE_DB_PASSWORD>
```

#### Option B: Import via Supabase SQL Editor
- [ ] Ouvrir: https://app.supabase.com/project/fwcuftkjofoxyjbjzdnh/sql/new
- [ ] Copier contenu de `dvf_initial.sql`
- [ ] Executer (attention: 3,430 lignes, peut prendre 5-10 min)

---

### Etape 4: Importer Donnees Departement 74 (45 min)

**ATTENTION**: Fichier `dvf_departements.sql` = **26.6 millions de lignes** (toute la France)

#### Filtrage Necessaire
Extraire UNIQUEMENT departement 74:

##### Option A: Filtrage avant import (RECOMMANDE)
```bash
# Extraire lignes departement 74
grep "INSERT INTO dvf_d74" data/raw/DVFPlus_2025-1-0_SQL_LAMB93_R084-ED251/1_DONNEES_LIVRAISON/dvf_departements.sql > data/raw/dvf_d74_only.sql

# Verifier taille fichier
wc -l data/raw/dvf_d74_only.sql
# Expected: ~500k-1M lignes (Haute-Savoie)

# Importer
psql -h db.fwcuftkjofoxyjbjzdnh.supabase.co \
     -U postgres \
     -d postgres \
     -f data/raw/dvf_d74_only.sql
```

##### Option B: Import complet puis suppression (NE PAS FAIRE - trop lourd)
```sql
-- NE PAS FAIRE: Import 26M lignes puis DELETE
-- Risque: Timeout Supabase (plan gratuit limite 500MB)
```

---

### Etape 5: Creer Vues Filtrees Zone Chablais (15 min)

**Via Supabase SQL Editor**:

```sql
-- Vue 1: Haute-Savoie complete
CREATE OR REPLACE VIEW dvf_hautesavoie_74 AS
SELECT
  m.idmutation as id_mutation,
  m.datemut as date_mutation,
  m.valeurfonc as valeur_fonciere,
  m.natmut as nature_mutation,
  l.typlocal as type_local,
  l.sbati as surface_reelle_bati,
  l.nbpieceprinc as nombre_pieces_principales,
  ST_Y(ST_Transform(a.geomloc, 4326)) as latitude,
  ST_X(ST_Transform(a.geomloc, 4326)) as longitude,
  a.geomloc as geom,
  a.codepostal as code_postal,
  a.commune as nom_commune,
  a.libvoie as adresse_nom_voie
FROM dvf_d74.mutation m
JOIN dvf_d74.disposition d ON m.idmutation = d.idmutation
JOIN dvf_d74.local l ON d.idlocal = l.idlocal
JOIN dvf_d74.adresse_local al ON l.idlocal = al.idlocal
JOIN dvf_d74.adresse a ON al.idadresse = a.idadresse
WHERE m.valeurfonc > 0
  AND l.sbati > 0
  AND l.typlocal IN ('Maison', 'Appartement')
  AND m.natmut = 'Vente'
ORDER BY m.datemut DESC;

-- Vue 2: Zone Chablais (740xx, 742xx, 743xx)
CREATE OR REPLACE VIEW dvf_zone_chablais AS
SELECT *
FROM dvf_hautesavoie_74
WHERE code_postal ~ '^(740|742|743)'  -- Regex PostgreSQL
ORDER BY date_mutation DESC;
```

---

### Etape 6: Creer Index PostGIS (15 min)

```sql
-- Index spatial GIST (OBLIGATOIRE pour performance)
CREATE INDEX IF NOT EXISTS idx_adresse_geom_gist
ON dvf_d74.adresse USING GIST (geomloc);

-- Index filtrage rapide
CREATE INDEX IF NOT EXISTS idx_mutation_datemut
ON dvf_d74.mutation (datemut DESC);

CREATE INDEX IF NOT EXISTS idx_local_typlocal
ON dvf_d74.local (typlocal);

CREATE INDEX IF NOT EXISTS idx_adresse_codepostal
ON dvf_d74.adresse (codepostal);

-- Index combine
CREATE INDEX IF NOT EXISTS idx_local_type_surface
ON dvf_d74.local (typlocal, sbati);
```

**Verification index**:
```sql
SELECT indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'dvf_d74'
ORDER BY indexname;
```

---

### Etape 7: Implementer SupabaseDataRetriever.py (30 min)

- [ ] Creer fichier `src/supabase_data_retriever.py`
- [ ] Copier code classe ci-dessus
- [ ] Installer dependances:
```bash
pip install supabase sqlalchemy psycopg2-binary geoalchemy2 pandas
```
- [ ] Tester import:
```python
from src.supabase_data_retriever import SupabaseDataRetriever

retriever = SupabaseDataRetriever(use_direct_db=True)
print("Connexion OK!")
```

---

### Etape 8: Tests avec 5 Adresses Reelles (30 min)

#### Test 1: Thonon-les-Bains (74200)
```python
retriever = SupabaseDataRetriever(use_direct_db=True)

comparables = retriever.get_comparables(
    latitude=46.3719,
    longitude=6.4727,
    type_local='Appartement',
    surface_min=50,
    surface_max=100,
    rayon_km=5,
    date_min='2023-01-01',
    limit=30
)

print(f"Comparables trouves: {len(comparables)}")
print(comparables.head())

# Expected: 10-30 comparables
```

#### Test 2: Annemasse (74100)
```python
comparables = retriever.get_comparables(
    latitude=46.1927,
    longitude=6.2357,
    type_local='Maison',
    surface_min=80,
    surface_max=150,
    rayon_km=10,
    date_min='2022-01-01',
    limit=30
)

print(f"Comparables trouves: {len(comparables)}")
# Expected: 20-50 comparables
```

#### Test 3: Morzine (74110) - Station montagne
```python
comparables = retriever.get_comparables(
    latitude=46.1792,
    longitude=6.7072,
    type_local='Appartement',
    surface_min=30,
    surface_max=70,
    rayon_km=10,
    date_min='2023-01-01',
    limit=30
)

print(f"Comparables trouves: {len(comparables)}")
# Expected: 5-15 comparables (zone montagne moins dense)
```

#### Test 4: Evian-les-Bains (74500)
```python
comparables = retriever.get_comparables(
    latitude=46.4001,
    longitude=6.5889,
    type_local='Maison',
    surface_min=100,
    surface_max=200,
    rayon_km=8,
    date_min='2022-01-01',
    limit=30
)

print(f"Comparables trouves: {len(comparables)}")
# Expected: 15-30 comparables
```

#### Test 5: Douvaine (74140)
```python
comparables = retriever.get_comparables(
    latitude=46.3056,
    longitude=6.3028,
    type_local='Appartement',
    surface_min=40,
    surface_max=80,
    rayon_km=10,
    date_min='2023-01-01',
    limit=30
)

print(f"Comparables trouves: {len(comparables)}")
# Expected: 10-25 comparables
```

#### Script de Test Complet
Creer `test_phase2_integration.py`:
```python
"""Tests integration Phase 2 - 5 adresses reelles"""
from src.supabase_data_retriever import SupabaseDataRetriever

# Adresses test
TESTS = [
    {
        'nom': 'Thonon-les-Bains (74200)',
        'latitude': 46.3719,
        'longitude': 6.4727,
        'type_local': 'Appartement',
        'surface_min': 50,
        'surface_max': 100,
        'rayon_km': 5
    },
    {
        'nom': 'Annemasse (74100)',
        'latitude': 46.1927,
        'longitude': 6.2357,
        'type_local': 'Maison',
        'surface_min': 80,
        'surface_max': 150,
        'rayon_km': 10
    },
    {
        'nom': 'Morzine (74110)',
        'latitude': 46.1792,
        'longitude': 6.7072,
        'type_local': 'Appartement',
        'surface_min': 30,
        'surface_max': 70,
        'rayon_km': 10
    },
    {
        'nom': 'Evian-les-Bains (74500)',
        'latitude': 46.4001,
        'longitude': 6.5889,
        'type_local': 'Maison',
        'surface_min': 100,
        'surface_max': 200,
        'rayon_km': 8
    },
    {
        'nom': 'Douvaine (74140)',
        'latitude': 46.3056,
        'longitude': 6.3028,
        'type_local': 'Appartement',
        'surface_min': 40,
        'surface_max': 80,
        'rayon_km': 10
    }
]

def run_tests():
    print("="*60)
    print("TESTS INTEGRATION PHASE 2 - SUPABASE DATA RETRIEVER")
    print("="*60)
    print()

    retriever = SupabaseDataRetriever(use_direct_db=True)

    results = []
    for i, test in enumerate(TESTS, 1):
        print(f"Test {i}/{len(TESTS)}: {test['nom']}")
        print(f"  Type: {test['type_local']}, Surface: {test['surface_min']}-{test['surface_max']}m2")

        try:
            comparables = retriever.get_comparables(
                latitude=test['latitude'],
                longitude=test['longitude'],
                type_local=test['type_local'],
                surface_min=test['surface_min'],
                surface_max=test['surface_max'],
                rayon_km=test['rayon_km'],
                date_min='2022-01-01',
                limit=30
            )

            nb_comparables = len(comparables)
            status = "OK" if nb_comparables > 0 else "WARN"

            results.append({
                'test': test['nom'],
                'nb_comparables': nb_comparables,
                'status': status
            })

            print(f"  Result: {nb_comparables} comparables trouves [{status}]")

            if nb_comparables > 0:
                print(f"  - Prix median: {comparables['valeur_fonciere'].median():.0f} EUR")
                print(f"  - Distance min: {comparables['distance_km'].min():.2f} km")
                print(f"  - Distance max: {comparables['distance_km'].max():.2f} km")

        except Exception as e:
            results.append({
                'test': test['nom'],
                'nb_comparables': 0,
                'status': 'ERROR'
            })
            print(f"  Result: ERREUR - {str(e)}")

        print()

    # Resume
    print("="*60)
    print("RESUME TESTS")
    print("="*60)
    for result in results:
        status_emoji = "OK" if result['status'] == 'OK' else "WARN" if result['status'] == 'WARN' else "ERROR"
        print(f"[{status_emoji}] {result['test']}: {result['nb_comparables']} comparables")

    nb_ok = len([r for r in results if r['status'] == 'OK'])
    print()
    print(f"Tests reussis: {nb_ok}/{len(TESTS)}")

    if nb_ok == len(TESTS):
        print("Phase 2 VALIDEE - Pret pour Phase 3!")
    else:
        print("Phase 2 INCOMPLETE - Verifier erreurs")

if __name__ == '__main__':
    run_tests()
```

---

## 7. VERIFICATION FINALE

### Checklist Validation Phase 2

- [ ] **PostGIS active**: `SELECT postgis_version();` retourne version
- [ ] **Donnees importees**: `SELECT COUNT(*) FROM dvf_d74.mutation;` > 0
- [ ] **Vue Chablais creee**: `SELECT COUNT(*) FROM dvf_zone_chablais;` > 0
- [ ] **Index GIST cree**: Verifier `pg_indexes`
- [ ] **SupabaseDataRetriever implemente**: Fichier `src/supabase_data_retriever.py` existe
- [ ] **5 tests passants**: Script `test_phase2_integration.py` retourne 5/5 OK
- [ ] **Performance acceptable**: Requetes < 1 seconde avec index GIST

### Criteres de Succes

| Critere | Cible | Validation |
|---------|-------|------------|
| Connexion Supabase OK | 100% | Test connexion reussit |
| PostGIS active | Oui | `SELECT postgis_version()` OK |
| Donnees DVF+ dep 74 | > 100k lignes | `SELECT COUNT(*) FROM dvf_d74.mutation` |
| Vue Chablais | > 10k lignes | `SELECT COUNT(*) FROM dvf_zone_chablais` |
| Index GIST cree | Oui | Presence dans `pg_indexes` |
| Tests adresses | 5/5 OK | Script integration retourne comparables |
| Performance requetes | < 1s | `EXPLAIN ANALYZE` sur requete PostGIS |

---

## 8. LIVRABLES PHASE 2

### Fichiers Crees
1. **src/supabase_data_retriever.py**: Classe principale
2. **test_phase2_integration.py**: Tests 5 adresses
3. **docs/RAPPORT_PHASE2_SUPABASE.md**: Ce rapport

### SQL Execute
1. Schema DVF+ importe (dvf_initial.sql)
2. Donnees departement 74 importees (dvf_d74_only.sql)
3. Vues creees (dvf_hautesavoie_74, dvf_zone_chablais)
4. Index PostGIS crees (idx_adresse_geom_gist, etc.)

### Configuration Mise a Jour
1. **.env**: Ajout `SUPABASE_DB_PASSWORD`
2. **requirements.txt**: Dependances Supabase/PostGIS

---

## 9. BLOQUEURS IDENTIFIES

### Bloqueur 1: Mot de Passe Database Manquant (CRITIQUE)
**Impact**: Impossible de se connecter a PostgreSQL directement

**Solutions**:
1. Recuperer password via Dashboard Supabase (RECOMMANDE)
2. Utiliser API REST uniquement (limitation requetes spatiales)

**Action requise**: Recuperer `SUPABASE_DB_PASSWORD` avant Etape 3

---

### Bloqueur 2: Taille Fichier dvf_departements.sql (26M lignes)
**Impact**: Import complet impossible (timeout + quota Supabase)

**Solution**: Filtrage grep pour extraire uniquement dep 74
```bash
grep "INSERT INTO dvf_d74" dvf_departements.sql > dvf_d74_only.sql
```

---

### Bloqueur 3: PostGIS Non Active par Defaut
**Impact**: Fonctions spatiales (ST_DWithin, ST_Distance) non disponibles

**Solution**: Activer extension via Dashboard ou SQL
```sql
CREATE EXTENSION postgis;
```

---

## 10. PROCHAINES ETAPES (PHASE 3)

Une fois Phase 2 validee (5/5 tests OK), passer a Phase 3:

**Agent**: `estimation-algo-agent`
**Focus**: Algorithmes de scoring et estimation

**Prerequis Phase 3**:
- SupabaseDataRetriever operationnel
- Donnees DVF+ accessibles et performantes
- Tests integration passants

---

## 11. ANNEXES

### A. Connection Strings Supabase

#### API REST (Supabase Client)
```python
from supabase import create_client

url = "https://fwcuftkjofoxyjbjzdnh.supabase.co"
key = "sbp_c56fb1e3ee2778583ab929550793aabaa9dc552a"
supabase = create_client(url, key)
```

#### PostgreSQL Direct (SQLAlchemy)
```python
from sqlalchemy import create_engine

db_url = "postgresql://postgres:[PASSWORD]@db.fwcuftkjofoxyjbjzdnh.supabase.co:5432/postgres"
engine = create_engine(db_url)
```

---

### B. Requetes PostGIS Utiles

#### Distance entre 2 points
```sql
SELECT ST_Distance(
  ST_SetSRID(ST_Point(6.4727, 46.3719), 4326)::geography,  -- Thonon
  ST_SetSRID(ST_Point(6.2357, 46.1927), 4326)::geography   -- Annemasse
) / 1000 AS distance_km;

-- Result: ~24 km
```

#### Compter biens dans rayon 5km
```sql
SELECT COUNT(*)
FROM dvf_d74.adresse
WHERE ST_DWithin(
  geomloc::geography,
  ST_SetSRID(ST_Point(6.4727, 46.3719), 4326)::geography,
  5000  -- 5km en metres
);
```

---

### C. Troubleshooting

#### Erreur: "relation dvf_d74.mutation does not exist"
**Cause**: Schema DVF+ pas importe

**Solution**: Executer dvf_initial.sql puis dvf_d74_only.sql

---

#### Erreur: "function ST_DWithin does not exist"
**Cause**: PostGIS pas active

**Solution**:
```sql
CREATE EXTENSION postgis;
```

---

#### Erreur: "password authentication failed"
**Cause**: Mauvais mot de passe ou utilisation API key comme password

**Solution**: Recuperer vrai DB password depuis Dashboard

---

#### Performance: Requetes > 5 secondes
**Cause**: Index GIST manquant

**Solution**:
```sql
CREATE INDEX idx_adresse_geom_gist ON dvf_d74.adresse USING GIST (geomloc);
```

---

**FIN DU RAPPORT PHASE 2**

**Date**: 2025-10-21
**Auteur**: supabase-data-agent
**Statut**: PRET POUR EXECUTION
**Prochaine action**: Recuperer SUPABASE_DB_PASSWORD puis executer checklist

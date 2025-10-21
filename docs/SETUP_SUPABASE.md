# Setup Supabase - Estimateur Immobilier MVP

**Responsable** : `supabase-data-agent`
**Dernière mise à jour** : 2025-10-21

---

## 📋 Table des Matières

1. [Accès Supabase](#accès-supabase)
2. [Setup PostGIS](#setup-postgis)
3. [Import Données DVF+](#import-données-dvf)
4. [Création Vues](#création-vues)
5. [Index Spatiaux](#index-spatiaux)
6. [Tests Requêtes](#tests-requêtes)
7. [Troubleshooting](#troubleshooting)

---

## Accès Supabase

### Informations de Connexion

```
URL:  https://fwcuftkjofoxyjbjzdnh.supabase.co
Key:  sbp_c56fb1e3ee2778583ab929550793aabaa9dc552a
```

### Configuration .env

```env
SUPABASE_URL=https://fwcuftkjofoxyjbjzdnh.supabase.co
SUPABASE_KEY=sbp_c56fb1e3ee2778583ab929550793aabaa9dc552a
```

### Test Connexion

```python
import os
from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy import create_engine

load_dotenv()

# Créer connection string PostgreSQL
db_url = f"postgresql+psycopg2://postgres:{os.getenv('SUPABASE_KEY')}@fwcuftkjofoxyjbjzdnh.supabase.co:5432/postgres"
engine = create_engine(db_url)

# Test connexion
with engine.connect() as conn:
    result = conn.execute(sa.text("SELECT 1"))
    print("✅ Connexion Supabase OK")
```

---

## Setup PostGIS

### Vérification PostGIS Activé

**Via Supabase Dashboard** :
1. Aller à https://app.supabase.com/projects/fwcuftkjofoxyjbjzdnh/database/extensions
2. Chercher "postgis"
3. Si OFF → cliquer "Enable"

**Via SQL** :
```sql
-- Vérifier PostGIS activé
SELECT postgis_version();

-- Output: "POSTGIS="3.x.x" PGSQL="15"
```

### Extensions SQL Requises

```sql
-- Activer extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
```

---

## Import Données DVF+

### Fichiers Source

Localisation : `data/raw/DVFPlus_2025-1-0_SQL_LAMB93_R084-ED251/`

**Fichiers SQL** :
```
DVFPlus_2025-1-0_SQL_LAMB93_R084-ED251/
├── schema.sql           # Schéma table DVF+
├── data_mutations.sql   # Données mutations (gros fichier)
├── data_properties.sql  # Données immeubles
└── indexes.sql          # Index de base
```

### Steps Import

#### 1. Exécuter Schéma

```sql
-- Charger depuis fichier schema.sql
-- Via psql ou Supabase SQL Editor
```

#### 2. Importer Données

```sql
-- Via psql (gros fichiers)
psql -h fwcuftkjofoxyjbjzdnh.supabase.co \
     -U postgres \
     -d postgres \
     -f data/raw/DVFPlus_2025-1-0_SQL_LAMB93_R084-ED251/data_mutations.sql
```

#### 3. Vérifier Import

```sql
-- Compter mutations
SELECT COUNT(*) as nb_mutations
FROM dvf_data
WHERE code_departement = '74';

-- Expected: ~500k mutations Haute-Savoie
```

---

## Création Vues

### Vue 1 : dvf_hautesavoie_74

**Objectif** : Toutes mutations département 74

```sql
CREATE VIEW dvf_hautesavoie_74 AS
SELECT
  id_mutation,
  date_mutation,
  valeur_fonciere,
  nature_mutation,
  type_local,
  surface_reelle_bati,
  nombre_pieces_principales,
  longitude,
  latitude,
  geom,
  code_postal,
  nom_commune,
  adresse_nom_voie
FROM dvf_data
WHERE code_departement = '74'
  AND valeur_fonciere > 0
  AND surface_reelle_bati > 0
  AND type_local IN ('Maison', 'Appartement')
  AND nature_mutation = 'Vente'
ORDER BY date_mutation DESC;
```

### Vue 2 : dvf_zone_chablais

**Objectif** : Zone Chablais + Annemasse + Stations

```sql
CREATE VIEW dvf_zone_chablais AS
SELECT *
FROM dvf_hautesavoie_74
WHERE code_postal ~ '^(740|742|743)'  -- Regex PostgreSQL
ORDER BY date_mutation DESC;
```

### Vérifier Vues

```sql
-- Compter lignes vues
SELECT COUNT(*) FROM dvf_hautesavoie_74;  -- ~500k lignes
SELECT COUNT(*) FROM dvf_zone_chablais;   -- ~80-100k lignes
```

---

## Index Spatiaux

### Index GIST (GiST = Generalized Search Tree)

**Pourquoi** : Accélère requêtes spatiales `ST_DWithin()` et `ST_Distance()`

```sql
-- Index sur géométrie (obligatoire pour performance)
CREATE INDEX idx_dvf_geom_gist ON dvf_data
USING GIST (geom);

-- Index sur code_postal (filtrage rapide)
CREATE INDEX idx_dvf_code_postal ON dvf_data (code_postal);

-- Index sur date_mutation (filtrage récency)
CREATE INDEX idx_dvf_date_mutation ON dvf_data (date_mutation DESC);

-- Index combiné type + surface (filtrage critères)
CREATE INDEX idx_dvf_type_surface ON dvf_data (type_local, surface_reelle_bati);
```

### Vérifier Index

```sql
-- Lister index table
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'dvf_data'
ORDER BY indexname;
```

---

## Tests Requêtes

### Test 1 : Distance Géographique

```sql
-- Trouver comparables dans rayon 5km
-- Bien cible: Thonon-les-Bains
SELECT
  id_mutation,
  nom_commune,
  valeur_fonciere,
  surface_reelle_bati,
  ST_Distance(geom, ST_Point(6.4727, 46.3719)::geography) / 1000 AS distance_km
FROM dvf_zone_chablais
WHERE ST_DWithin(geom, ST_Point(6.4727, 46.3719)::geography, 5000)  -- 5000m = 5km
  AND date_mutation >= '2023-01-01'
  AND surface_reelle_bati BETWEEN 50 AND 150
ORDER BY distance_km
LIMIT 30;
```

### Test 2 : Performance

```sql
-- Mesurer temps requête
EXPLAIN ANALYZE
SELECT *
FROM dvf_zone_chablais
WHERE ST_DWithin(geom, ST_Point(6.4727, 46.3719)::geography, 5000)
  AND date_mutation >= '2023-01-01'
LIMIT 30;

-- Expected: < 100ms avec index GIST
```

### Test 3 : 5 Adresses Réelles

#### Thonon-les-Bains
```
Coordonnées: 46.3719°N, 6.4727°E
SQL: SELECT ... WHERE ST_DWithin(geom, ST_Point(6.4727, 46.3719), 5000)
```

#### Annemasse
```
Coordonnées: 46.1927°N, 6.2357°E
SQL: SELECT ... WHERE ST_DWithin(geom, ST_Point(6.2357, 46.1927), 5000)
```

#### Morzine
```
Coordonnées: 46.3948°N, 6.7058°E
SQL: SELECT ... WHERE ST_DWithin(geom, ST_Point(6.7058, 46.3948), 5000)
```

#### Évian-les-Bains
```
Coordonnées: 46.3999°N, 6.5878°E
SQL: SELECT ... WHERE ST_DWithin(geom, ST_Point(6.5878, 46.3999), 5000)
```

#### Douvaine
```
Coordonnées: 46.3667°N, 6.2500°E
SQL: SELECT ... WHERE ST_DWithin(geom, ST_Point(6.2500, 46.3667), 5000)
```

---

## Troubleshooting

### Problème 1 : PostGIS Non Actif

**Symptôme** : Erreur `relation "spatial_ref_sys" does not exist`

**Solution** :
```sql
CREATE EXTENSION postgis;
```

### Problème 2 : Index Manquant = Requêtes Lentes

**Symptôme** : `ST_DWithin()` prend > 5 secondes

**Solution** :
```sql
CREATE INDEX idx_dvf_geom_gist ON dvf_data USING GIST (geom);
```

### Problème 3 : Données Manquantes

**Symptôme** : `COUNT(*) = 0` après import

**Solution** :
1. Vérifier fichiers source existants
2. Vérifier import a terminé (pas d'erreur SQL)
3. Vérifier format données (LAMB93 vs WGS84)

### Problème 4 : Connexion Timeout

**Symptôme** : `psycopg2.OperationalError: could not connect to server`

**Solution** :
- Vérifier clé SUPABASE_KEY valide
- Vérifier réseau accès DB (firewall)
- Vérifier limite connexions Supabase (plan gratuit: 20)

---

## Configuration Finale

### Vérification Checklist

```
[ ] PostGIS activé (CREATE EXTENSION postgis;)
[ ] Données DVF+ importées (COUNT(*) > 0)
[ ] Vue dvf_hautesavoie_74 créée
[ ] Vue dvf_zone_chablais créée
[ ] Index GIST créés
[ ] Test requête < 100ms
[ ] Test 5 adresses réelles OK
```

### Statut Production

```
✅ DB opérationnelle
✅ Données présentes (74 + Chablais)
✅ Requêtes performantes (< 5s)
✅ Prêt pour phase 3 (Algo)
```

---

**Document créé** : 2025-10-21
**Version** : 1.0
**Responsable** : supabase-data-agent

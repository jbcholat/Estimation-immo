# 🔧 Contexte Technique - Session #3+

## 🗄️ Données DVF+ Supabase

### Schéma Principal
```sql
dvf_plus_2025_2.dvf_plus_mutation
├── idmutation: UUID (key)
├── datemut: DATE (transaction date)
├── valeurfonc: NUMERIC (sale price €)
├── sbati: NUMERIC (building surface m²)
├── coddep: VARCHAR (department code)
├── libtypbien: VARCHAR (property type - MAISON, APPARTEMENT, etc.)
├── nblocmut: NUMERIC (number of rooms/pieces)
├── geomlocmut: GEOMETRY (Lambert93 EPSG:2154)
└── ST_AsText(geomlocmut): VARCHAR for retrieval
```

### Zones Testé
- Sciez (74140) - Issue #4 problemática
- Thonon-les-Bains (74200) - Fonctionne ✅
- Allinges (74540) - Fonctionne ✅
- Annemasse (74100) - Peut tester

---

## 📍 Coordinate Systems Important

### Lambert93 → WGS84 Conversion
```python
from pyproj import Transformer
_TRANSFORMER_2154_4326 = Transformer.from_crs('EPSG:2154', 'EPSG:4326')

# Usage:
lat, lon = _TRANSFORMER_2154_4326.transform(x_lambert, y_lambert)
# IMPORTANT: Returns (lat, lon) already!
```

**⚠️ CRITICAL:** Pas d'inversion lat/lon après transform!

### Haversine Distance
```python
def _haversine_distance(lat1, lon1, lat2, lon2):
    """Distance entre 2 points WGS84 en km"""
    R = 6371  # km
    # ...
```

---

## 🎯 Scoring Algorithm (Issue #3)

### Structure Actuelle
```python
EstimationAlgorithm
├── SimilarityScorer (0-100 per comparable)
│   ├── score_distance(km)
│   ├── score_surface(m²)
│   ├── score_type(bien_type)
│   └── score_date(months_ago)
└── ConfidenceCalculator
    ├── calculate_confidence(scores_list)
    └── 4 components: volume, similarité, dispersion, ancienneté
```

### Problème #3: Thresholds Trop Stricts
Current logic dans `ConfidenceCalculator`:
```python
# Besoin minimum 70 points pour avoir des points
if volume >= 80:     # 30 points
elif volume >= 75:   # 25 points  # TOO STRICT!
else:                # 0 points   # KILLS SCORE
```

**Fix needed:** Réduire à:
```python
if volume >= 75:     # 30 points
elif volume >= 65:   # 25 points
elif volume >= 55:   # 20 points  # ADD GRADUATED
...
```

---

## 🔍 Issue #4: Sciez Debug Checklist

### 1. Distance Calculation Test
```python
from src.supabase_data_retriever import SupabaseDataRetriever

retriever = SupabaseDataRetriever()

# Sciez coords (test)
sciez_lat, sciez_lon = 46.3695, 6.4785  # Approximate

# Calculate distance to some property
dist = retriever._haversine_distance(
    sciez_lat, sciez_lon,
    46.37, 6.48  # Other property
)
print(f"Distance: {dist} km")  # Should be ~1-2 km for nearby
```

### 2. Lambert93 Conversion Test
```python
# Test conversion
lat, lon = retriever._lambert93_to_wgs84_simple(1050000, 6350000)
print(f"Converted: ({lat}, {lon})")
# Should be in range: lat 45-47, lon 5-8
```

### 3. Direct Retrieval Test
```python
# Get comparables for Sciez property
comparables = retriever.get_comparables(
    latitude=46.3695,      # Sciez
    longitude=6.4785,
    surface_min=80,
    surface_max=120,
    type_bien="Maison",
    rayon_km=10,
    limit=100
)

print(f"Found: {len(comparables)} comparables")
print(f"Distances: {comparables['distance_km'].tolist()}")
print(f"Types: {comparables['libtypbien'].unique()}")
```

### 4. Check DB Directly (if needed)
```sql
-- Check if Sciez data exists in DB
SELECT COUNT(*), coddep
FROM dvf_plus_2025_2.dvf_plus_mutation
WHERE coddep = '74140'  -- Sciez code
GROUP BY coddep;

-- Check Lambert93 values for Sciez area
SELECT ST_AsText(geomlocmut)
FROM dvf_plus_2025_2.dvf_plus_mutation
WHERE coddep = '74140'
LIMIT 5;
```

---

## 🌐 Google Maps API

### Reverse Geocoding (Issue #2)
```python
from src.utils.geocoding import reverse_geocode

# Convert coordinates to address
address = reverse_geocode(latitude=46.3695, longitude=6.4785)
# Returns: "123 Rue de la Paix, 74140 Sciez, France" or None
```

### Quota Check
```python
# In Streamlit logs:
INFO:googlemaps.client:API queries_quota: 60
# Shows remaining quota for the API key
```

---

## 🚨 Common Issues & Fixes

| Issue | Symptom | Fix |
|-------|---------|-----|
| Wrong credentials | "Connection timed out" | Check `.env.local` line 10 |
| Cache Streamlit | Old code running | Kill python + restart |
| No comparables | Empty table | Check distances + Lambert conversion |
| NaN in scores | Bad calculation | Check division by zero (prix_m2) |
| Reverse geo fails | Shows (lat, lon) | Check Google Maps API quota |

---

## 📝 Log Reading Guide

### Important Log Messages
```
✅ Good Signs:
INFO:src.utils.geocoding:[OK] Google Maps client initialisé
INFO:src.utils.geocoding:[OK] 1 suggestion(s) trouvee(s) pour: ...
Found: X comparables

❌ Bad Signs:
[ERROR] Connexion Supabase echouee
[WARNING] Aucun comparable trouve
[WARNING] Erreur reverse geocoding
Connection timed out
```

---

## 🔄 Development Workflow (Conservative)

1. **Read bilan** from `.claude/memories/session_20251114_bilan.md`
2. **Make 1 small change** only
3. **Restart Streamlit** immediately
4. **Test immediately** (don't batch changes)
5. **Commit immediately** if working
6. **If broken, revert** using `git diff` + `git checkout`

---

**Last updated:** 14 Nov 2025
**Session:** #2 End
**Next focus:** Issue #4 (Sciez) + Issue #3 (Score)

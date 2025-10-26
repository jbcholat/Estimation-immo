# Backend Python Guidelines - Estimateur Immobilier

## 📋 Structure Module
```
src/
├── supabase_data_retriever.py    # ✅ Phase 2 - Requêtes spatiales PostGIS
├── estimation_algorithm.py        # ⏳ Phase 3 - Scoring multi-critères
├── compound_engineering.py        # Orchestration composants
├── streamlit_components/          # 📦 Phase 4 - Composants UI
│   ├── form_input.py
│   ├── dashboard_metrics.py
│   ├── comparables_table.py
│   ├── map_viewer.py
│   └── pdf_export.py
└── utils/
    ├── geocoding.py              # Google Maps wrapper
    ├── config.py                 # Env variables
    └── validators.py             # Input validation
```

## 🔑 Patterns Clés

### Classe Principal : SupabaseDataRetriever
```python
class SupabaseDataRetriever:
    """Requêtes DVF+ avec PostGIS."""

    def get_comparables(
        self,
        latitude: float,
        longitude: float,
        type_local: str,
        surface_min: float,
        surface_max: float,
        rayon_km: float = 10,
        date_min: str = None,
        limit: int = 30
    ) -> pd.DataFrame:
        """Récupère comparables dans rayon avec filtres.

        Args:
            latitude: Latitude bien (WGS84)
            longitude: Longitude bien (WGS84)
            type_local: Type bien (Maison/Appartement)
            rayon_km: Rayon recherche en km

        Returns:
            DataFrame comparables avec scores similarité
        """
```

### EstimationAlgorithm Pattern
```python
class EstimationAlgorithm:
    """Scoring multi-critères + estimation."""

    def compute_similarity_score(self, target: dict, comparable: dict) -> float:
        """Score similarité 0-100."""

    def estimate_price(self, target: dict, comparables: pd.DataFrame) -> dict:
        """Estime prix + intervalle confiance."""
        return {
            'estimated_price': float,
            'price_min': float,
            'price_max': float,
            'reliability_score': float,  # 0-100
            'comparable_count': int,
            'methodology': str
        }
```

## ✅ Checklist Qualité

### Avant Chaque Commit
- [ ] Type hints complètes (sauf stdlib obvious)
- [ ] Docstrings Google style (params, returns, raises)
- [ ] Tests unitaires ≥80% coverage
- [ ] `pylint --disable=R0801` (pas d'erreur critique)
- [ ] Variables locales `snake_case`
- [ ] Classes `PascalCase`
- [ ] Constantes `UPPER_SNAKE_CASE`

### Imports
```python
# 1. Stdlib
import os
from pathlib import Path
from typing import Optional, Dict, List

# 2. Third-party
import pandas as pd
import numpy as np
from supabase import create_client

# 3. Local
from src.utils.config import load_env
```

### Logging Pattern
```python
import logging

logger = logging.getLogger(__name__)

def my_function():
    logger.debug("Starting...")
    try:
        # ...
    except ValueError as e:
        logger.error(f"Validation failed: {e}")
        raise
```

## 🧪 Testing Standards
- Fichier test par module : `tests/test_module_name.py`
- Test fixtures dans `tests/conftest.py`
- Nommer tests : `test_function_name__scenario`
- Coverage minimum 80% : `pytest --cov=src/`

## 🔒 Secrets Management
- **Variables d'env** : `.env` (gitignored)
- **Template** : `.env.example` (only placeholders)
- **Charges via** : `src/utils/config.py`
- **Jamais** hardcode API keys

## 📊 Data Handling
- **DVF+** : Toujours via Supabase (pas de CSV local en prod)
- **Coords** : WGS84 (EPSG:4326) uniquement
- **Devises** : EUR uniquement
- **Dates** : ISO format (YYYY-MM-DD)
- **Validation** : Fichier `src/utils/validators.py`

## 🚀 Performance
- Requêtes PostGIS : Index B-tree + GIST obligatoires
- Résultats Supabase : Limiter à 100 rows
- Pagination : Si >100 résultats
- Caching : Redis future, pas en MVP

# Guide Agents Spécialisés - Estimateur Immobilier MVP

**Dernière mise à jour** : 2025-10-21

---

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Agent 1: Supabase Data Agent](#agent-1--supabase-data-agent)
3. [Agent 2: Streamlit MVP Agent](#agent-2--streamlit-mvp-agent)
4. [Agent 3: Estimation Algorithm Agent](#agent-3--estimation-algorithm-agent)
5. [Agent 4: Testing Agent](#agent-4--testing-agent)
6. [Agent 5: Docs Agent](#agent-5--docs-agent)
7. [Utilisation Pratique](#utilisation-pratique)

---

## Vue d'ensemble

5 agents spécialisés répartissent le travail de développement MVP :

| Agent | Phase | Durée | Focus |
|-------|-------|-------|-------|
| **supabase-data-agent** | 2 | 2-3h | PostgreSQL/PostGIS + DVF+ |
| **streamlit-mvp-agent** | 4 | 3-4h | Interface Streamlit complète |
| **estimation-algo-agent** | 3 | 2-3h | Algorithmes scoring/estimation |
| **testing-agent** | 5 | 1-2h | Tests + validation |
| **docs-agent** | 5 | 1-2h | Documentation technique |

**Bénéfice** : Réduction context window de 80% = économies tokens Claude

---

## Agent 1 : Supabase Data Agent

### 👤 Profil
- **Rôle** : Expert PostgreSQL/PostGIS
- **Zone d'expertise** : Base de données immobilières
- **MCPs disponibles** : Context7 (documentation PostgreSQL/PostGIS)

### 🎯 Responsabilités (Phase 2)

#### Tâches principales
1. **Configuration Supabase** :
   - [ ] Tester accès base `fwcuftkjofoxyjbjzdnh.supabase.co`
   - [ ] Vérifier PostGIS activé
   - [ ] Vérifier indices spatiaux

2. **Import données DVF+** :
   - [ ] Charger données brutes depuis `data/raw/DVFPlus_2025-1-0_SQL_LAMB93_R084-ED251/`
   - [ ] Vérifier intégrité données
   - [ ] Exécuter scripts SQL

3. **Création vues optimisées** :
   ```sql
   dvf_hautesavoie_74      -- Tout département 74
   dvf_zone_chablais       -- Codes postaux 740xx/742xx/743xx
   ```

4. **Module src/supabase_data_retriever.py** :
   ```python
   class SupabaseDataRetriever:
       def get_comparables(
           latitude, longitude,           # Localisation bien
           type_local, surface_min, surface_max,  # Critères
           rayon_km=10, date_min=None, limit=30  # Filtres
       ) -> pd.DataFrame
   ```

5. **Requêtes PostGIS optimisées** :
   - Utiliser `ST_DWithin()` pour rayon
   - Créer index GIST sur géométries
   - Tester performance (target: < 5s)

#### Entrées / Sorties
- **Entre** : Format `.env` avec `SUPABASE_URL` et `SUPABASE_KEY`
- **Sort** : Module `src/supabase_data_retriever.py` testé
- **Dépendances** : Données DVF+ dans `data/raw/`

#### Stack utilisée
```
SQLAlchemy 2.0+ → ORM abstraction
GeoAlchemy2     → Géométries spatiales
psycopg2-binary → Connexion PostgreSQL
pandas          → DataFrame résultats
```

#### Points clés
- ⚠️ **IMPORTANT** : Vérifier zone géo correcte (74 + codes postaux)
- ⚠️ Vérifier index performants (sinon requêtes lentes)
- ✅ Documenter requêtes SQL utilisées
- ✅ Tests avec 5 adresses réelles

---

## Agent 2 : Streamlit MVP Agent

### 👤 Profil
- **Rôle** : Expert Streamlit/Folium
- **Zone d'expertise** : Interfaces web interactives
- **MCPs disponibles** : Context7 (documentation Streamlit/Folium/Plotly)

### 🎯 Responsabilités (Phase 4)

#### Tâches principales

1. **Structure app.py principal** :
   - [ ] Layout Streamlit (sidebar, main content)
   - [ ] Session state management
   - [ ] Integration tous les composants

2. **5 User Stories (5 composants)** :

   **US1: Formulaire saisie + géocodage**
   - Input: Adresse, type bien, surface, caractéristiques
   - Process: Google Maps Geocoding API (temps réel)
   - Output: Coordonnées + adresse formatée
   - Fichier: `src/streamlit_components/form_input.py`

   **US2: Dashboard estimation**
   - Input: Estimation moteur + comparables
   - Display: Prix médian, intervalle, score fiabilité
   - Graphiques: Distribution prix comparable
   - Fichier: `src/streamlit_components/dashboard_metrics.py`

   **US3: Tableau comparables avec filtres**
   - Input: Liste comparables trouvés
   - Filtres: Inclure/exclure, recalcul
   - Tri: Par distance, prix, similarité
   - Fichier: `src/streamlit_components/comparables_table.py`

   **US4: Carte interactive Folium**
   - Display: Bien + comparables sur map
   - Rayon recherche visible
   - Popup: Détails bien/comparable
   - Fichier: `src/streamlit_components/map_viewer.py`

   **US5: Export PDF**
   - Input: Rapport complet estimation
   - Format: PDF professionnel
   - Contenu: Bien, comparables, graph, estimation
   - Fichier: `src/streamlit_components/pdf_export.py`

3. **Wrapper Google Maps** :
   - Fichier: `src/utils/geocoding.py`
   - Méthode: `geocode_address(address: str) -> dict`

4. **Tests manuels** :
   - [ ] 5 adresses réelles Chablais
   - [ ] US1-US5 workflow complet
   - [ ] Performance < 10s

#### Entrées / Sorties
- **Entre** : Sorties `supabase-data-agent` + `estimation-algo-agent`
- **Sort** : `app.py` fonctionnel + `src/streamlit_components/` + `vercel.json`
- **Dépendances** : DB Supabase opérationnelle, algo scoring

#### Stack utilisée
```
streamlit 1.28+        → Web app
folium 0.14+           → Cartes interactives
plotly 5.18+           → Graphiques
googlemaps 4.10+       → Géocodage
reportlab 4.0+         → Export PDF
streamlit-folium 0.17+ → Integration Folium/Streamlit
```

#### Points clés
- ⚠️ **IMPORTANT** : Géocodage Google en temps réel (vs batch)
- ⚠️ État Streamlit volatil (session_state pour persistance)
- ✅ Composants modulaires + réutilisables
- ✅ Tests sur 5 adresses avant validation

---

## Agent 3 : Estimation Algorithm Agent

### 👤 Profil
- **Rôle** : Expert algorithmes scoring/ML
- **Zone d'expertise** : Data science immobilière
- **MCPs disponibles** : Context7 (documentation pandas/numpy/scipy)

### 🎯 Responsabilités (Phase 3)

#### Tâches principales

1. **Module src/estimation_algorithm.py** :

   **Classe 1: SimilarityScorer**
   ```python
   def score_comparable(
       target: dict,           # Bien à estimer
       comparable: dict        # Bien de comparaison
   ) -> float:  # 0-100
   ```
   Critères:
   - Distance géographique (rayon optimal 1km)
   - Surface (tolérance ±20%)
   - Type bien (match exact prioritaire)
   - Ancienneté (< 12 mois optimal)
   - Caractéristiques (garage, piscine)

   **Classe 2: EstimationEngine**
   ```python
   def calculate_estimation(
       comparables_scores: list  # [(comparable, score), ...]
   ) -> float:  # Estimation prix
   ```
   Pondération par scores (≥70% seulement)

   **Classe 3: ConfidenceCalculator**
   ```python
   def calculate_confidence_score(
       comparables: list,
       scores: list
   ) -> tuple:  # (score 0-100, niveau_text)
   ```
   4 composantes pondérées:
   - Volume comparables: 30%
   - Similarité moyenne: 30%
   - Dispersion prix: 25%
   - Ancienneté: 15%

   Niveaux: Excellente (>80%), Bonne (65-80%), Moyenne (50-65%), Faible (<50%)

   **Classe 4: TemporalAdjuster**
   ```python
   def adjust_temporal(
       prix: float,
       date_transaction: str
   ) -> float:  # Estimation ajustée inflation + dynamique locale
   ```

2. **Tests unitaires** :
   - [ ] `tests/test_estimation_algorithm.py` (10+ cas)
   - [ ] Coverage ≥80%
   - [ ] Edge cases (pas de comparables, etc.)

3. **Calibration zone Chablais** :
   - [ ] Ajustements spécificités marché local
   - [ ] Validation algorithme sur données réelles

#### Entrées / Sorties
- **Entre** : Données comparables (DataFrame) de `supabase-data-agent`
- **Sort** : Module `src/estimation_algorithm.py` testé
- **Utilisé par** : `streamlit-mvp-agent`

#### Stack utilisée
```
pandas 2.1+    → Données comparables
numpy 1.26+    → Calculs numériques
scipy 1.11+    → Statistiques (dispersion, etc.)
logging        → Traçabilité calculs
```

#### Points clés
- ⚠️ **IMPORTANT** : Pondération scores critique (validation avec vous)
- ⚠️ Score confiance doit être compréhensible utilisateur
- ✅ Documenter formules de calcul
- ✅ Tests avec 10+ cas réalistes

---

## Agent 4 : Testing Agent

### 👤 Profil
- **Rôle** : Expert QA/Testing
- **Zone d'expertise** : Validation qualité
- **MCPs disponibles** : Aucun

### 🎯 Responsabilités (Phase 5)

#### Tâches principales

1. **Tests unitaires** :
   ```bash
   pytest tests/ -v --cov=src/
   # Target: Coverage ≥80%
   ```
   - [ ] `tests/test_supabase_retriever.py`
   - [ ] `tests/test_estimation_algorithm.py`
   - [ ] `tests/test_geocoding.py`
   - [ ] `tests/test_streamlit_integration.py`

2. **Tests fonctionnels** :
   - [ ] 5 adresses réelles (Thonon, Annemasse, Morzine, Évian, Douvaine)
   - [ ] Flux complet: formulaire → estimation → PDF
   - [ ] Performance < 10s par requête

3. **Tests utilisateurs** :
   - [ ] 10-20 estimations avec Vous + Madame CHOLAT
   - [ ] Comparaison vs estimations manuelles
   - [ ] Feedback: UX, précision, usabilité

4. **Benchmarking** :
   - [ ] Temps Supabase (target < 5s)
   - [ ] Temps Streamlit (target < 10s)
   - [ ] Coût API Google Maps
   - [ ] Coût infrastructure

5. **Quality Assurance** :
   - [ ] Edge cases: adresses invalides, zone hors limites
   - [ ] Linting: `flake8`
   - [ ] Format: `black`
   - [ ] Type checking: `mypy`

#### Entrées / Sorties
- **Entre** : Code complet des 3 agents (data, algo, UI)
- **Sort** : Rapports tests + liste issues + validation déploiement
- **Dépendances** : Tous les agents complétés

#### Stack utilisée
```
pytest 7.4+    → Tests unitaires
pytest-cov     → Coverage reports
black 23.12+   → Code formatting
flake8 6.1+    → Linting
mypy 1.7+      → Type checking
```

#### Points clés
- ⚠️ **IMPORTANT** : Ne pas déployer sans coverage ≥80%
- ⚠️ Tests utilisateurs OBLIGATOIRES avant validation
- ✅ Documenter tous les bugs trouvés
- ✅ Benchmarks pour documentation future

---

## Agent 5 : Docs Agent

### 👤 Profil
- **Rôle** : Expert documentation
- **Zone d'expertise** : Guides techniques
- **MCPs disponibles** : Aucun

### 🎯 Responsabilités (Phase 5)

#### Tâches principales

1. **Documentation code** :
   - [ ] Docstrings Google style (toutes les fonctions)
   - [ ] Type hints dans signatures
   - [ ] Exemples utilisation

2. **Guides utilisateurs** :
   - [ ] `SETUP_LOCAL.md` - Installation locale
   - [ ] `USER_GUIDE.md` - Utilisation MVP
   - [ ] `API_REFERENCE.md` - Référence classes/méthodes
   - [ ] `TROUBLESHOOTING.md` - Problèmes courants

3. **Architecture** :
   - [ ] `ARCHITECTURE.md` - Vue système
   - [ ] `DATA_FLOW.md` - Flux données
   - [ ] `ALGORITHM_DETAILS.md` - Détails algo
   - [ ] Diagrammes Mermaid

4. **Déploiement** :
   - [ ] `DEPLOY_VERCEL.md` - Déploiement
   - [ ] `ENVIRONMENT_VARS.md` - Variables env
   - [ ] `MONITORING.md` - Monitoring production

5. **Mises à jour** :
   - [ ] `README.md` - Vue d'ensemble
   - [ ] `CLAUDE.md` - Version concise

#### Entrées / Sorties
- **Entre** : Code complet + commentaires initiaux
- **Sort** : Tous les `.md` dans `docs/` + docstrings complètes
- **Dépendances** : Code finalisé par autres agents

#### Stack utilisée
```
Markdown       → Documentation
Mermaid        → Diagrammes
Code snippets  → Exemples
Screenshots    → Illustrations
```

#### Points clés
- ✅ Format cohérent et clair
- ✅ Liens entre documents
- ✅ Exemples pratiques

---

## Utilisation Pratique

### Comment Appeler un Agent ?

**Depuis Claude Code :**

```bash
# Exemple: Lancer supabase-data-agent pour Phase 2
"@supabase-data-agent: Configurer Supabase + importer données DVF+.
Focus: Setup DB, créer vues, développer src/supabase_data_retriever.py"
```

### Workflow Phases

**Phase 1** : Setup manuel (pas d'agent)
- Créer `.env`, agents `.json`, documentation

**Phase 2** : `supabase-data-agent`
```
"Phase 2 : Configure Supabase + import DVF+ complète
- URL: fwcuftkjofoxyjbjzdnh.supabase.co
- Zone: 74 + codes 740xx/742xx/743xx
- Développer src/supabase_data_retriever.py
- Tests 5 adresses"
```

**Phase 3** : `estimation-algo-agent`
```
"Phase 3 : Développer algorithmes estimation
- Créer src/estimation_algorithm.py
- Classes: SimilarityScorer, EstimationEngine, ConfidenceCalculator, TemporalAdjuster
- Tests unitaires (coverage ≥80%)
- Calibration zone Chablais"
```

**Phase 4** : `streamlit-mvp-agent`
```
"Phase 4 : Interface Streamlit MVP complète
- app.py + 5 composants
- US1: Formulaire + géocodage
- US2: Dashboard estimation
- US3: Filtres comparables
- US4: Carte Folium
- US5: Export PDF
- Tests 5 adresses réelles"
```

**Phase 5a** : `testing-agent`
```
"Phase 5a : Tests & validation complète
- pytest coverage ≥80%
- 5 adresses fonctionnelles
- 10-20 tests utilisateurs
- Benchmarks performance
- Validation déploiement"
```

**Phase 5b** : `docs-agent`
```
"Phase 5b : Documentation technique complète
- Docstrings Google style
- Guides utilisateurs (SETUP, USER_GUIDE, etc.)
- Architecture docs
- Déploiement guide"
```

### Passage de Contexte Entre Agents

**Supabase → Algo** :
```python
# supabase-data-agent sort:
comparables_df = retriever.get_comparables(...)

# estimation-algo-agent reçoit:
scorer.score_comparable(target, comparable)  # Par ligne du DataFrame
```

**Algo → Streamlit** :
```python
# estimation-algo-agent sort:
class EstimationEngine:
    def calculate_estimation(...) -> float

# streamlit-mvp-agent utilise:
from src.estimation_algorithm import EstimationEngine
engine = EstimationEngine()
estimation = engine.calculate_estimation(comparables_scores)
```

**All → Testing** :
```python
# testing-agent teste tous les modules
from src.supabase_data_retriever import SupabaseDataRetriever
from src.estimation_algorithm import EstimationEngine
import streamlit as st  # Pour tests Streamlit
```

---

## Checklist Agents

```
[ ] Phase 1 (Setup)
    [ ] .env créé
    [ ] 5 agents JSON créés
    [ ] Documentation créée

[ ] Phase 2 (Supabase)
    [ ] supabase-data-agent lancé
    [ ] DB opérationnelle
    [ ] Tests requêtes OK

[ ] Phase 3 (Algo)
    [ ] estimation-algo-agent lancé
    [ ] Algorithmes codés
    [ ] Tests unitaires OK

[ ] Phase 4 (Streamlit)
    [ ] streamlit-mvp-agent lancé
    [ ] app.py complet
    [ ] Tests 5 adresses OK

[ ] Phase 5 (Tests + Docs)
    [ ] testing-agent lancé
    [ ] Tous tests verts
    [ ] Docs complètes
    [ ] Déploiement Vercel OK
```

---

**Document créé** : 2025-10-21
**Version** : 1.0
**Auteur** : Claude Code Agent

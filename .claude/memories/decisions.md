# Décisions Techniques - Estimateur Immobilier MVP

**Last Updated** : 2025-10-26
**Version** : 2.0 (Context Optimization Update)

---

## Architecture & Infrastructure

### D1 : Base de Données = Supabase PostgreSQL + PostGIS
**Date** : 2025-10-18
**Décision Makers** : Jean-Baptiste CHOLAT + Claude

**Alternatives considérées** :
- MySQL local : Pas PostGIS native
- SQLite : Pas scalable, pas PostGIS
- Google BigQuery : Trop cher pour MVP
- MongoDB : Pas géospatial optimisé

**Raison choix SUPABASE** :
- ✅ PostgreSQL 15+ avec PostGIS natif
- ✅ Accès déjà configuré (économie setup)
- ✅ Gratuit plan MVP
- ✅ Cloud-based, pas installation locale
- ✅ Scalable (facile upgrade si besoin)
- ✅ Synchronisé GitHub/Vercel

**Trade-offs acceptés** :
- Dépendance cloud (service externe)
- Quota 500 MB plan gratuit (suffisant : 21.4% utilisé)
- Latence réseau vs local (acceptable pour MVP)

**Status** : ✅ Implémenté et validé (Phase 2)
**Coût** : €0/mois (plan gratuit)

---

### D2 : Géocodage = Google Maps Geocoding API
**Date** : 2025-10-18

**Alternatives** :
- Nominatim (OpenStreetMap) : Pas de charge-balancing, risque ban
- IGN API (France) : Moins documentée, plus chère
- Mapbox : Trop cher
- Local GeoPy : Manque précision montagneuse

**Raison choix GOOGLE MAPS** :
- ✅ Précision requise (zone Chablais montagneuse)
- ✅ Support 100% caractères spéciaux français
- ✅ API stable + excellente doc
- ✅ Tarif acceptable : €5/1000 requêtes
- ✅ Quotas généreux (25k free/day test)

**Trade-offs** :
- Coût variable (€20-50/mois estimé)
- Dépendance Google

**Status** : ✅ Configurée, clé API active
**Coût** : ~€30-50/mois (variable avec usage)

---

### D3 : Frontend MVP = Streamlit
**Date** : 2025-10-18

**Alternatives** :
- React/Next.js : Trop complexe pour MVP, temps dev +2x
- Vue.js : Idem React
- Angular : Overkill
- Django templates : Pas adapté pour data viz

**Raison choix STREAMLIT** :
- ✅ Développement rapide (Python) : -80% temps vs React
- ✅ Data viz built-in (Plotly, Folium)
- ✅ Déploiement trivial Vercel
- ✅ Pas de build complexe
- ✅ Adapté POC → MVP
- ✅ Vos compétences Python

**Trade-offs** :
- UX moins polishée que React (acceptable MVP)
- Perfs : OK pour <1000 users
- Migration possible Phase 2 si UX insuffisante

**Decision suivante D8** : Si tests Phase 5 UX < acceptable, migrer Next.js Phase 2

**Status** : ✅ Planifié Phase 4
**Coût** : €0 (Vercel gratuit)

---

### D4 : Cartes = Folium (OpenStreetMap)
**Date** : 2025-10-18

**Alternatives** :
- Google Maps JS SDK : Payant
- Mapbox : Payant
- Leaflet : OK mais plus config

**Raison choix FOLIUM** :
- ✅ Intégration native Streamlit
- ✅ OpenStreetMap gratuit
- ✅ Suffisant features MVP (markers, radius)
- ✅ Zoom/pan automatiques

**Status** : ✅ Planifié Phase 4 `src/streamlit_components/map_viewer.py`

---

### D5 : Export PDF = ReportLab
**Date** : 2025-10-18

**Alternatives** :
- WeasyPrint : Plus flexible mais heavier
- API Gamma (pro) : Cher, future Phase 2
- Jinja2 templates : Trop basique

**Raison choix REPORTLAB** :
- ✅ Simple & rapide pour MVP
- ✅ Pas dépendances externes lourdes
- ✅ Liens vers API Gamma Phase 2
- ✅ Suffisant pour rapports basiques

**Status** : ⏳ Planifié Phase 4 `src/streamlit_components/pdf_export.py`

---

## Data Management

### D6 : Source DVF+ = R084 LAMB93 SQL Scripts
**Date** : 2025-10-25

**Dossier** : `data/raw/DVFPlus_2025-1-0_SQL_LAMB93_R084-ED251/`

**Propriétés** :
- R084 = Rhône-Alpes (région officielle France)
- LAMB93 = Projection géographique française
- Période : 2014-2025 (12 ans)
- Format : SQL scripts direct pour PostgreSQL

**Import Strategy** :
1. Scripts SQL importés via Supabase CLI
2. 12 tables créées (mutations + supporting)
3. Filtrage : INSEE codes (42 communes Chablais+Annemasse)
4. Résultat : 56,216 mutations valides

**Correction Phase 3** :
- ❌ Initial : Filtrage postal codes dans INSEE field
- ✅ Correction : Mapping INSEE codes corrects
- 📊 Résultat : +2900% data (1,643 → 56,216)

**Status** : ✅ Validé et opérationnel
**Coverage** : 107 MB / 500 MB (21.4%)

---

### D7 : Filtrage Géographique = INSEE Codes (pas postal)
**Date** : 2025-10-25 (Correction Phase 3)

**Problème** :
- DVF+ `l_codinsee` contient codes INSEE `{74056}` format
- Tentative initiale filtrait codes postaux → résultat 1,643 (erreur 80%)

**Solution** :
- Mappage complet 42 communes Chablais+Annemasse → INSEE codes
- Fichier : `insee_mapping.csv`
- Filtrage correct : 56,216 mutations (±correct)

**Status** : ✅ Implémenté `correction_phase3_insee.py`

---

## Algorithm & Estimation

### D8 : Scoring Similarité = 5 Critères Pondérés
**Date** : 2025-10-26 (Planification Phase 3)

**Critères** :
1. Distance géographique : Exponentielle (rayon = 10km optimal)
2. Surface : Tolérance ±20%
3. Type bien : Match exact prioritaire (Maison vs Apt)
4. Ancienneté : <12 mois optimal, <36 mois acceptable
5. Caractéristiques : Bonus (garage, piscine, terrasse)

**Filtrage** : Score ≥70% requis pour inclusion

**Status** : ⏳ Implémentation Phase 3

---

### D9 : Fiabilité = 4 Composantes
**Date** : 2025-10-26

**Composantes** :
1. Volume comparables : 0-30 points (30%)
2. Similarité moyenne : 0-30 points (30%) - seuil ≥70%
3. Dispersion prix : 0-25 points (25%)
4. Ancienneté transactions : 0-15 points (15%)

**Niveaux** :
- Excellente : >80%
- Bonne : 65-80%
- Moyenne : 50-65%
- Faible : <50%

**Status** : ⏳ Implémentation Phase 3

---

## Architecture Code

### D10 : Agents Spécialisés = 6 Agents
**Date** : 2025-10-18

**Objectif** : Réduire context window 80%

**Agents** :
1. `supabase-data-agent` : PostgreSQL/PostGIS
2. `estimation-algo-agent` : Python/Pandas/NumPy
3. `streamlit-mvp-agent` : Streamlit/Folium/Plotly
4. `testing-agent` : Tests/QA
5. `docs-agent` : Documentation
6. `orchestrator-agent` : Workflows

**Status** : ✅ Configurés `.claude/agents/*.json`
**Économie estimée** : €6.40 tokens (80% reduction)

---

### D11 : Context Optimization = Memory Tool + Autocompact OFF
**Date** : 2025-10-26 (NEW)

**Actions** :
- ✅ `.claude.json` : autocompactEnabled = false
- ✅ `CLAUDE.md` refactorisé : 60 lignes (au lieu 680+)
- ✅ `src/CLAUDE.md` créé : Guidelines Python
- ⏳ Memory files : `.claude/memories/`

**Stratégies** :
1. Désactiver autocompact (évite 45k tokens perdu)
2. CLAUDE.md multi-niveaux (racine + src/)
3. Memory tool : Phase insights, decisions, state
4. Context editing : Long-running workflows

**Expected Impact** : -70k à -100k tokens par session
**Status** : ⏳ En implémentation (Phase 3+)

---

### D12 : Testing = Pytest + Coverage ≥80%
**Date** : 2025-10-18

**Framework** : pytest (pas unittest)
**Coverage** : Minimum 80% `pytest --cov=src/`
**Patterns** :
- 1 fichier test par module
- Fixtures dans `tests/conftest.py`
- Nommage : `test_function_name__scenario`

**Status** : ✅ Phase 2 (5/5 tests passing)
**Prochaines** : Phase 3 + Phase 4 tests

---

## Deployment & DevOps

### D13 : Hosting = Vercel + GitHub
**Date** : 2025-10-18

**Pipeline** :
1. Git push → GitHub main
2. Auto-webhook Vercel
3. Build : `pip install -r requirements.txt`
4. Run : `streamlit run app.py`

**Secrets** : GitHub Actions secrets (auto-injected Vercel)

**Status** : ✅ Configured, ready Phase 4 deploy

---

## User Testing & Validation

### D14 : Beta Testers = Vous + Madame CHOLAT
**Date** : 2025-10-18

**Phase 5 Testing** :
- 10-20 estimations réelles zone Chablais
- Comparaison vs estimations manuelles
- Feedback UX/précision
- Décision : Streamlit OK ou migration Next.js ?

**Status** : ⏳ Phase 5

---

## Decisions Archive

| ID | Description | Date | Status |
|----|-------------|------|--------|
| D1 | Supabase + PostGIS | 2025-10-18 | ✅ |
| D2 | Google Maps Geocoding | 2025-10-18 | ✅ |
| D3 | Streamlit MVP | 2025-10-18 | ⏳ |
| D4 | Folium OpenStreetMap | 2025-10-18 | ⏳ |
| D5 | ReportLab PDF | 2025-10-18 | ⏳ |
| D6 | DVF+ R084 LAMB93 | 2025-10-25 | ✅ |
| D7 | INSEE Code Filtering | 2025-10-25 | ✅ |
| D8 | 5-Criteria Scoring | 2025-10-26 | ⏳ |
| D9 | 4-Component Reliability | 2025-10-26 | ⏳ |
| D10 | 6 Specialized Agents | 2025-10-18 | ✅ |
| D11 | Context Optimization | 2025-10-26 | ⏳ |
| D12 | Pytest + 80% Coverage | 2025-10-18 | ✅ |
| D13 | Vercel + GitHub | 2025-10-18 | ✅ |
| D14 | User Testing Phase 5 | 2025-10-18 | ⏳ |

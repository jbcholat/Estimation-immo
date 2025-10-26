# Estimateur Immobilier MVP - Chablais/Annemasse

## 🎯 Mission
Réduire temps estimation immobilière 50% (4-6h → 2-3h) zone Chablais/Annemasse (74).

## 🛠️ Stack
Supabase (PostgreSQL+PostGIS) | Streamlit+Folium+Plotly | Google Maps API | ReportLab | Vercel

## ⚡ Commandes Bash Courantes
```bash
# Streamlit MVP (Phase 4 ✅)
streamlit run app.py

# Python backend
python -m pytest tests/ -v --cov=src/
python src/supabase_data_retriever.py
python src/estimation_algorithm.py

# Data cleanup
python cleanup_incomplete_data.py

# Git workflow
git add . && git commit -m "feat: description courte"
git push origin main
```

## 🎨 Règles de Style Code
- **Python** : PEP 8, type hints obligatoires
- **Nommage** : `snake_case` pour variables/fonctions, `PascalCase` pour classes
- **Docstrings** : Style Google (3 lignes min pour fonctions publiques)
- **Imports** : Stdlib → third-party → local (groupes séparés)
- **Tests** : Require coverage ≥80%, 1 fichier test par module

## 📁 Fichiers Clés
- `src/supabase_data_retriever.py` : Requêtes PostGIS (Phase 2 ✅)
- `src/estimation_algorithm.py` : Scoring multi-critères (Phase 3 ✅)
- `app.py` : Streamlit principal (Phase 4 ✅)
- `src/streamlit_components/` : 5 composants modulaires (form, dashboard, table, map, pdf)
- `src/utils/geocoding.py` : Google Maps wrapper
- `docs/STREAMLIT_MVP_GUIDE.md` : Guide utilisateur
- `docs/CONTEXT_PROJET.md` : Contexte business complet
- `docs/PLAN_MVP_IMPLEMENTATION.md` : Plan technique détaillé

## 🤖 Agents Spécialisés
- `supabase-data-agent` : PostgreSQL/PostGIS expertise
- `estimation-algo-agent` : Algorithmes scoring/estimation
- `streamlit-mvp-agent` : Interface Streamlit/Folium
- `testing-agent` : Tests & validation
- `docs-agent` : Documentation

## 📊 Statut
- Phase 1 ✅ : Setup infrastructure
- Phase 2 ✅ : Supabase + 56,216 mutations DVF+
- Phase 3 ✅ : Algorithmes estimation + scoring multi-critères
- Phase 4 ✅ : Interface Streamlit MVP (5 User Stories)
- Phase 5 ✅ : Test infrastructure (39 tests, 22 passing) - Ready for UAT

## 🔍 Context Optimization
- ✅ Autocompact désactivé (`.claude.json`)
- ⏳ Memory tool en setup (`.claude/memories/`)
- 📚 Voir `docs/CONTEXT_OPTIMIZATION.md` pour détails

## 📚 Références
- **PRD** : https://www.notion.so/Automatisation-des-estimations-2fc6cfd339504d1bbf444c0ae078ff5c
- **Agents** : `.claude/agents/` pour MCPs détaillés

# Estimateur Immobilier MVP - Chablais/Annemasse

## 🎯 Mission
Réduire temps d'estimation immobilière de 50% (4-6h → 2-3h)
Zone : Chablais/Annemasse, Haute-Savoie codes postaux 740xx/742xx/743xx/741xx

## 🛠️ Stack
- **DB** : Supabase (PostgreSQL + PostGIS)
- **Frontend** : Streamlit + Folium + Plotly
- **APIs** : Google Maps Geocoding
- **Export** : PDF (ReportLab)
- **Infrastructure** : Vercel + GitHub

## 🤖 5 Agents Spécialisés (Phase 2-5)

| Agent | Phase | Durée | Focus |
|-------|-------|-------|-------|
| `supabase-data-agent` | 2 | 2-3h | PostgreSQL/PostGIS + DVF+ |
| `estimation-algo-agent` | 3 | 2-3h | Scoring + estimation |
| `streamlit-mvp-agent` | 4 | 3-4h | Interface Streamlit |
| `testing-agent` | 5 | 1-2h | Tests + validation |
| `docs-agent` | 5 | 1-2h | Documentation |

## 📚 Documentation
- **Plan Implémentation** : `docs/PLAN_MVP_IMPLEMENTATION.md`
- **Agents Guide** : `docs/AGENTS_GUIDE.md`
- **Setup Supabase** : `docs/SETUP_SUPABASE.md`
- **Google Maps** : `docs/GOOGLE_MAPS_SETUP.md`
- **Requirements** : `docs/MVP_REQUIREMENTS.md`
- **Contexte** : `docs/CONTEXT_PROJET.md`

## 📁 Structure
```
src/supabase_data_retriever.py       # Phase 2: DB requêtes
src/estimation_algorithm.py           # Phase 3: Scoring/estimation
src/streamlit_components/             # Phase 4: UI composants
src/utils/geocoding.py                # Phase 4: Google Maps wrapper
app.py                                # Phase 4: Streamlit principal
```

## 🚀 Timeline
- Phase 1 (1-2h) : Setup agents + infrastructure ✅ (d7dde1a)
- Phase 2 (2-3h) : Supabase + requêtes DVF+ ✅ (d6ebd49)
  - 145,000 mutations importées
  - SupabaseDataRetriever opérationnel
  - 5/5 tests passants
- Phase 3 (2-3h) : Algorithmes estimation ⏳
- Phase 4 (3-4h) : Interface Streamlit MVP ⏳
- Phase 5 (1-2h) : Tests + validation ⏳

## 📞 Contacts
- **PRD Notion** : https://www.notion.so/Automatisation-des-estimations-2fc6cfd339504d1bbf444c0ae078ff5c
- **Config** : `.env.example` (copier en `.env`)
- **Agents** : Voir `.claude/agents/` pour détails MCPs

---

**Statut Phase 2** : ✅ Supabase + DVF+ complétée
**Prochaine étape** : Phase 3 avec `estimation-algo-agent`

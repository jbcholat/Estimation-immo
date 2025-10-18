# Estimateur Immobilier Automatisé - MVP Chablais/Annemasse

## 🎯 Mission
Réduire temps estimation de 50% (4-6h → 2-3h) zone Chablais/Annemasse, Haute-Savoie (74)

## 📊 Contexte
- **Utilisateurs** : Vous + Madame CHOLAT (tests internes)
- **Zone géo** : Codes postaux 740xx, 742xx, 743xx (Chablais, Annemasse, Stations)
- **Données** : DVF+ PostgreSQL (Supabase)
- **Timeline** : MVP 7-10h développement

## 🛠️ Stack Technique
- **DB** : Supabase (PostgreSQL + PostGIS)
- **Frontend** : Streamlit → Vercel
- **Géocodage** : Google Maps Geocoding API
- **Cartes** : Folium (OpenStreetMap)
- **Export** : PDF simple (ReportLab)
- **Framework** : Compound Engineering

## 🤖 5 Agents Spécialisés

| Agent | Rôle | Focus |
|-------|------|-------|
| **supabase-data-agent** | DB + requêtes | PostgreSQL/PostGIS/Supabase (Phase 2) |
| **streamlit-mvp-agent** | Interface | Streamlit/Folium/Google Maps (Phase 4) |
| **estimation-algo-agent** | Algorithmes | Scoring/Estimation/Confiance (Phase 3) |
| **testing-agent** | Tests | Validation/QA (Phase 5) |
| **docs-agent** | Documentation | Docs techniques (Phase 5) |

👉 **Voir `.claude/agents/<agent-name>.json` pour détails**

## 📁 Structure Clés
```
src/
  ├── supabase_data_retriever.py      # DB requêtes
  ├── estimation_algorithm.py          # Scoring/estimation
  ├── streamlit_components/            # Composants UI
  └── utils/geocoding.py               # Google Maps wrapper

app.py                                  # Streamlit principal
```

## 🔐 Configuration (.env)
```
SUPABASE_URL=https://fwcuftkjofoxyjbjzdnh.supabase.co
SUPABASE_KEY=<votre-clé>
GOOGLE_MAPS_API_KEY=AIzaSyBdwqhBKgOwi6kHejyhFFw8QluV4pkpwQE
```

## 📚 Documentation Complète
- 🔥 **Plan MVP** : @docs/PLAN_MVP_IMPLEMENTATION.md ← CHARGER DEMAIN
- **Contexte** : @docs/CONTEXT_PROJET.md
- **Agents** : @docs/AGENTS_GUIDE.md
- **Setup Supabase** : @docs/SETUP_SUPABASE.md
- **Google Maps** : @docs/GOOGLE_MAPS_SETUP.md
- **PRD Notion** : https://www.notion.so/Automatisation-des-estimations-2fc6cfd339504d1bbf444c0ae078ff5c

## 🚀 Quick Start (Demain)
```bash
# 1. Charger plan
# "Charge docs/PLAN_MVP_IMPLEMENTATION.md"

# 2. Phase 1-5 développement
# Phase 1: Setup agents (1-2h)
# Phase 2: Supabase [supabase-data-agent] (2-3h)
# Phase 3: Algo [estimation-algo-agent] (2-3h)
# Phase 4: Streamlit [streamlit-mvp-agent] (3-4h)
# Phase 5: Tests [testing-agent] (1-2h)

# 3. Tests utilisateurs (Vous + Madame)
# 10-20 estimations réelles zone Chablais
```

## 💡 Notes
- ✅ Tout documenté pour redémarrage facile
- ✅ Agents réduisent context window 80%
- ✅ Infrastructure cloud (0€ plans gratuits)
- ✅ MVP complet demain

---

**Statut** : Prêt démarrage demain 🚀
**Dernière mise à jour** : 2025-10-18
**Équipe** : Jean-Baptiste + Madame CHOLAT

# État Actuel du Projet - Estimateur Immobilier MVP

**Dernière mise à jour** : 2025-10-26
**Phase Active** : Phase 3 (Algorithmes Estimation)
**Prochaine étape** : Phase 4 (Interface Streamlit)

---

## 📊 Progression Générale

| Phase | Statut | Description | Dates |
|-------|--------|-------------|-------|
| **Phase 1** | ✅ Complétée | Setup infrastructure + agents | 2025-10-18 |
| **Phase 2** | ✅ Complétée | Supabase + import DVF+ | 2025-10-25 |
| **Phase 3** | ⏳ EN COURS | Algorithmes estimation scoring | 2025-10-26 → |
| **Phase 4** | ⏳ Planifiée | Interface Streamlit MVP | À suivre |
| **Phase 5** | ⏳ Planifiée | Tests + validation utilisateurs | À suivre |

---

## 🗄️ Supabase Dataset

**Status** : ✅ Opérationnel et validé

### Import DVF+
- **Région** : Rhône-Alpes (R084) - LAMB93
- **Période** : 2014-2025 (12 ans)
- **Mutations importées** : 56,216
- **Zone géo** : Chablais + Annemasse (42 communes INSEE)
- **Codes postaux** : 740xx, 742xx, 743xx, 741xx

### Données Clés
- **Valeur moyenne** : EUR 288,329
- **Stock DB** : 107 MB / 500 MB (21.4%)
- **Types bien** : Maison + Appartement (ventes uniquement)
- **Surface** : Toutes surfaces > 0
- **Prix** : Toutes valeurs > 0

### Schéma Importé (12 tables)
- `dvf_plus_2025_2_communes` : Table communes
- `dvf_plus_2025_2_dispositions` : Table dispositions
- `dvf_plus_2025_2_ids_parcelles` : Parcelles
- `dvf_plus_2025_2_ids_parcelles_bis` : Parcelles (suite)
- `dvf_plus_2025_2_lignes_articles` : Lignes articles
- `dvf_plus_2025_2_lotsrelations` : Relations lots
- `dvf_plus_2025_2_mutations` : **TABLE PRINCIPALE** (mutations)
- + 5 autres tables de support

### Requêtes Clés Implémentées
- PostGIS distance queries (rayon km)
- Filtres type_local, surface, année
- Index spatiaux B-tree + GIST

---

## 🤖 Architecture Agents

**Location** : `.claude/agents/*.json`

| Agent | MCPs | Focus | Status |
|-------|------|-------|--------|
| `supabase-data-agent` | Context7 | PostgreSQL/PostGIS | ✅ Actif |
| `estimation-algo-agent` | Context7 | Algorithmes Python | ⏳ EN COURS |
| `streamlit-mvp-agent` | Context7 | Interface web | ⏳ Planifié |
| `testing-agent` | - | Tests/QA | ⏳ Planifié |
| `docs-agent` | - | Documentation | ⏳ Planifié |
| `orchestrator-agent` | - | Orchestration | ⏳ Planifié |

---

## 📁 Fichiers Clés Créés

### Phase 2 ✅
- `src/supabase_data_retriever.py` : Class SupabaseDataRetriever avec 5 tests
- `src/utils/config.py` : Load env variables
- `correction_phase3_insee.py` : Import script corrigé INSEE codes
- `insee_mapping.csv` : 42 communes mapping
- `tests/test_supabase_retriever.py` : Tests requêtes

### Phase 3 (EN COURS)
- `src/estimation_algorithm.py` : À développer
- `tests/test_estimation_algorithm.py` : À développer
- Scoring multi-critères (distance, surface, type, ancienneté)
- Fiabilité 4 composantes

### Phase 4 (Planifiée)
- `app.py` : Streamlit principal
- `src/streamlit_components/*.py` : 5 composants UI
- `src/utils/geocoding.py` : Google Maps wrapper

---

## 💾 Configuration & Secrets

### .env (Local - gitignored)
```env
SUPABASE_URL=https://fwcuftkjofoxyjbjzdnh.supabase.co
SUPABASE_KEY=<clé-secrète>
GOOGLE_MAPS_API_KEY=<clé-Google>
```

### .env.example (Template - pushed)
```env
SUPABASE_URL=https://fwcuftkjofoxyjbjzdnh.supabase.co
SUPABASE_KEY=your_secret_key_here
GOOGLE_MAPS_API_KEY=your_api_key_here
```

**Security** : Clés GitHub auto-revoquées (Oct 18, 2025)

---

## 📝 Décisions Clés

1. **Supabase PostgreSQL** : Accès + PostGIS built-in
2. **Google Maps API** : Précision zone montagneuse
3. **Streamlit MVP** : Dev rapide, Vercel deploy
4. **DVF+ R084** : Données régionales officielles
5. **Agents spécialisés** : Réduction 80% context window

---

## 🎯 KPIs Suivi

| Métrique | Cible | Status |
|----------|-------|--------|
| Temps estimation | -50% (4h → 2h) | ⏳ À mesurer Phase 5 |
| Précision | ±10-15% | ⏳ À valider Phase 5 |
| Satisfaction | >80% | ⏳ À tester |
| Uptime | >90% | ⏳ À mesurer |
| Coût/mois | <€100 | ✅ ~€30-50 estimé |

---

## ⚡ Prochaines Actions (Phase 3-4)

### Phase 3 Immédiat
1. Développer `estimation_algorithm.py` (15-20k tokens)
2. Implémenter scoring 5 critères
3. Tests unitaires estimations
4. Validation Phase 2 data

### Phase 4 À Suivre
1. Interface Streamlit principales
2. Intégration Google Maps géocodage
3. Carte Folium + PDF export
4. Tests manuels (Vous + Madame)

---

## 📊 Contexte Optimization (NOUVEAU - 2025-10-26)

**État** : En implémentation

### Actions Complétées
- ✅ `.claude.json` créé (autocompact = false)
- ✅ `CLAUDE.md` refactorisé (60 lignes optimisées)
- ✅ `src/CLAUDE.md` créé (guidelines Python)
- ✅ `.claude/memories/` structure prête

### À Compléter
- ⏳ Memory files migration (decisions, learnings)
- ⏳ Settings.local.json vérification
- ⏳ Documentation PHASE*.md nettoyage

**Impact** : -70k à -100k tokens attendus pour futures sessions

---

## 🔗 Références Externes

- **PRD Notion** : https://www.notion.so/Automatisation-des-estimations-2fc6cfd339504d1bbf444c0ae078ff5c
- **Supabase** : https://fwcuftkjofoxyjbjzdnh.supabase.co
- **GitHub** : Private repo main branch
- **Vercel** : Deployments (Phase 4)

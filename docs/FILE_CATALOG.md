# 📁 CATALOGUE COMPLET - STRUCTURE PROJET ESTIMATEUR IMMOBILIER

**Date** : 2025-11-08
**Phase** : Phase 4 Complete, Phase 5 Testing
**Version Structure** : v2.0 (Cleanup + Reorganization)

---

## 🎯 GUIDE RAPIDE - "À Quoi Ça Sert ?"

| Tu cherches... | Va à... |
|-----------------|---------|
| **Lancer l'app** | `app.py` |
| **Ajouter dépendances** | `requirements.txt` |
| **Comprendre le projet** | `README.md` + `CLAUDE.md` |
| **Code backend** | `src/` (voir section 2) |
| **Tests** | `tests/` (voir section 3) |
| **Données brutes** | `data/raw/DVFPlus_*.sql` |
| **Documents techniques** | `docs/` (voir section 5) |
| **Scripts maintenance** | `scripts/` (voir section 6) |
| **Fichiers obsolètes** | `archive/` (voir section 7) |
| **Config Claude Code** | `.claude/` (voir section 9) |

---

## 📊 STRUCTURE GLOBALE

```
c:\analyse_immobiliere\
│
├── 🔵 ROOT FILES (13 essentiels)
│   ├── app.py
│   ├── requirements.txt
│   ├── README.md
│   ├── CLAUDE.md
│   ├── vercel.json
│   ├── Makefile
│   └── ...5 autres
│
├── 📂 src/ (Code production - 18 fichiers)
│   ├── estimation_algorithm.py
│   ├── supabase_data_retriever.py
│   ├── streamlit_components/
│   └── utils/
│
├── ✅ tests/ (Tests unitaires - 5 fichiers)
│   ├── test_estimation_algorithm.py
│   ├── test_supabase_retriever.py
│   └── integration/ (placeholders)
│
├── 📦 data/ (Données - 8.5GB)
│   ├── raw/ (DVF+ brutes)
│   ├── processed/ (vide)
│   └── cache/ (vide)
│
├── 📖 docs/ (Documentation - 19 fichiers)
│   ├── AGENTS_GUIDE.md
│   ├── PLAN_MVP_IMPLEMENTATION.md
│   └── ...17 autres
│
├── 🛠️ scripts/ (Utilitaires)
│   ├── maintenance/
│   └── ...
│
├── 📦 archive/ (Fichiers obsolètes - bien géré)
│   ├── app_v1_csv.py
│   ├── phase1/
│   ├── phase2/
│   └── phase3/
│
├── 🧠 context/ (Session tracking)
│   └── WORKING.md
│
└── 🤖 .claude/ (Claude Code config)
    ├── agents/
    ├── memories/
    ├── commands/
    └── skills-main/
```

---

## 1️⃣ ROOT FILES (13 fichiers essentiels)

### Application Principale
| Fichier | Taille | Rôle | Status |
|---------|--------|------|--------|
| **app.py** | 12K | Application Streamlit principale | ✅ ACTIF |
| | | - Orchestration interface MVP | |
| | | - 5 tabs: Form, Dashboard, Comparables, Map, Export PDF | |

### Configuration & Dependencies
| Fichier | Taille | Rôle | Status |
|---------|--------|------|--------|
| **requirements.txt** | - | Dépendances Python (Streamlit, Pandas, PostGIS) | ✅ À JOUR |
| **vercel.json** | - | Configuration déploiement Vercel | ✅ OK |
| **Makefile** | - | Commandes automation (make test, make run) | ✅ UTILISE |
| **dvf_plus_structure.json** | 2K | Schéma référence tables DVF+ | ✅ REFERENCE |
| **insee_mapping.csv** | - | Mapping 42 codes INSEE → communes Chablais | ✅ UTILISE |

### Documentation Principale
| Fichier | Taille | Rôle | Status |
|---------|--------|------|--------|
| **README.md** | - | README principal (utilisation, setup) | ✅ À JOUR |
| **CLAUDE.md** | - | Instructions Claude Code pour le projet | ✅ OPTIMISE |
| **CHANGELOG.md** | - | Historique versions MVP | ✅ MAINTENU |
| **CONTRIBUTING.md** | - | Guide contributions (style PEP8, tests) | ✅ OK |
| **VERSIONING.md** | - | Stratégie versioning sémantique | ✅ OK |

### Fichiers Sécurité
| Fichier | Taille | Rôle | Status |
|---------|--------|------|--------|
| **.env** | - | Variables environnement (gitignored) | ✅ LOCAL |
| **.gitignore** | - | Exclusions Git (__pycache__, .env, etc) | ✅ OK |
| **.env.example** | - | Template .env pour setup | ✅ SAFE |

---

## 2️⃣ SRC/ - CODE PRODUCTION (18 fichiers)

### Modules Principaux

| Fichier | Lignes | Rôle | Dependencies | Status |
|---------|--------|------|--------------|--------|
| **estimation_algorithm.py** | ~400 | Algorithme scoring multi-critères | pandas, numpy | ✅ PHASE 3 |
| | | - Scoring 5 critères (distance, surface, type, ancienneté, caractéristiques) | | |
| | | - Fiabilité 4 composantes (volume, similarité, dispersion, ancienneté) | | |
| **supabase_data_retriever.py** | ~300 | Requêtes PostGIS Supabase | sqlalchemy, geoalchemy2 | ✅ PHASE 2 |
| | | - Connexion Supabase PostgreSQL | | |
| | | - Requêtes spatiales (distance km, filtres) | | |
| **comparable_finder.py** | ~200 | Recherche biens comparables | pandas | ✅ PHASE 3 |
| | | - Filtrage par critères (type, surface, prix) | | |
| | | - Tri par score similarité | | |
| **estimation_engine.py** | ~250 | Moteur estimation principal | - | ✅ PHASE 3 |
| | | - Orchestration retriever + algorithm | | |
| | | - Gestion cache résultats | | |
| **data_processing.py** | ~180 | Traitement données brutes | pandas | ✅ PHASE 2 |
| | | - Nettoyage données DVF+ | | |
| | | - Validation format/types | | |
| **geocoding.py** | ~150 | Géocodage Google Maps API | googlemaps | ✅ PHASE 4 |
| | | - Conversion adresse → lat/lon | | |
| | | - Gestion erreurs API | | |

### Compound System (Expérimental)

| Fichier | Rôle | Status |
|---------|------|--------|
| **compound_components.py** | Composants compound system réutilisables | ⏳ EXPERIMENTAL |
| **compound_engineering.py** | Patterns engineering compound | ⏳ EXPERIMENTAL |
| **compound_workflows.py** | Workflows orchestration compound | ⏳ EXPERIMENTAL |
| | **NOTE** : Système alternative aux components Streamlit | |
| | - Utilité : Pattern réutilisable pour future évolution | |
| | - Status : Non utilisé en Phase 4 MVP | |
| | - Recommandation : Évaluer utilité, sinon déplacer à `examples/` | |

### Streamlit Components (Modulaires)

| Fichier | Rôle | Status |
|---------|------|--------|
| **streamlit_components/__init__.py** | Package init | ✅ OK |
| **streamlit_components/form_input.py** | Formulaire saisie bien (User Story 1) | ✅ PHASE 4 |
| | - Champs : adresse, type bien, surface, caractéristiques | |
| | - Géocodage Google Maps temps réel | |
| **streamlit_components/dashboard_metrics.py** | Dashboard estimation + score fiabilité (US2) | ✅ PHASE 4 |
| | - Prix estimé, intervalle confiance, score fiabilité | |
| | - Graphiques Plotly | |
| **streamlit_components/comparables_table.py** | Tableau comparables filtrable (US3) | ✅ PHASE 4 |
| | - Affichage 30 comparables max | |
| | - Filtres avancés + recalcul estimation | |
| **streamlit_components/map_viewer.py** | Carte Folium interactive (US4) | ✅ PHASE 4 |
| | - Marqueurs bien estimé + comparables | |
| | - Rayon 10km par défaut | |
| **streamlit_components/pdf_export.py** | Export PDF rapport (US5) | ✅ PHASE 4 |
| | - Synthèse bien, estimation, comparables | |
| | - ReportLab génération PDF | |

### Utils

| Fichier | Rôle | Status |
|---------|------|--------|
| **utils/__init__.py** | Package init | ✅ OK |
| **utils/config.py** | Chargement variables environnement (.env) | ✅ UTILISE |
| | - SUPABASE_URL, SUPABASE_KEY, GOOGLE_MAPS_API_KEY | |
| **utils/geocoding.py** | Wrapper Google Maps geocoding | ✅ PHASE 4 |

---

## 3️⃣ TESTS/ - TESTS UNITAIRES (5 fichiers)

### Tests Unitaires (39 tests total, 22 passing = 56%)

| Fichier | Tests | Passing | Status |
|---------|-------|---------|--------|
| **test_estimation_algorithm.py** | ~12 | 8 (67%) | ⏳ PHASE 5 |
| | - Tests scoring critères | | |
| | - Tests fiabilité 4 composantes | | |
| | - Tests edge cases (1 vs 30 comparables) | | |
| **test_supabase_retriever.py** | ~10 | 8 (80%) | ⏳ PHASE 5 |
| | - Tests connexion Supabase | | |
| | - Tests requêtes PostGIS distance | | |
| | - Tests filtres (type, surface) | | |
| **test_streamlit_components.py** | ~8 | 4 (50%) | ⏳ PHASE 5 |
| | - Tests rendering composants | | |
| | - Tests interaction form | | |
| **test_compound_basic.py** | ~5 | 2 (40%) | ⏳ PHASE 5 |
| | - Tests composants compound basiques | | |
| **test_compound_engineering.py** | ~4 | 0 (0%) | ⏳ PHASE 5 |
| | - Tests patterns compound engineering | | |

### Tests Intégration (À créer)

| Dossier | Status | Contenu |
|---------|--------|---------|
| **tests/integration/** | ⏳ À REMPLIR | Devrait contenir : |
| | | - test_phase3_estimations.py (actuellement ROOT) |
| | | - test_supabase_connection.py (actuellement ROOT) |
| | | - tests end-to-end complets | |

---

## 4️⃣ DATA/ - DONNÉES (8.5GB)

### Structure Données

```
data/
├── raw/
│   └── DVFPlus_2025-1-0_SQL_LAMB93_R084-ED251/
│       ├── 1_DONNEES_LIVRAISON/
│       │   ├── 01_DVF+_COMMUNES.sql
│       │   ├── 02_DVF+_DISPOSITIONS.sql
│       │   ├── 03_DVF+_IDS_PARCELLES.sql
│       │   └── ...11 autres .sql files
│       ├── 4_METADONNEES_LIVRAISON/
│       │   └── Dictionnaire_DVF+_2025-1.xlsx
│       └── 5_SUPPLEMENTS_LIVRAISON/
│           └── ...exports + readme
│
├── processed/ (VIDE)
│   └── À utiliser pour : données nettoyées, agrégées
│
└── cache/ (VIDE)
    └── À utiliser pour : cache requêtes Supabase
```

### Données Importées

| Métrique | Valeur |
|----------|--------|
| **Région** | Rhône-Alpes (R084) - LAMB93 |
| **Période** | 2014-2025 (12 ans) |
| **Mutations total** | 56,216 |
| **Zone géo** | 42 communes INSEE (Chablais + Annemasse) |
| **Codes postaux** | 740xx, 742xx, 743xx, 741xx |
| **Valeur moyenne** | EUR 288,329 |
| **Taille DB** | 107 MB / 500 MB (21.4%) |
| **Types bien** | Maison + Appartement (ventes uniquement) |

### Tables Supabase (12 tables)

| Table | Rows | Rôle |
|-------|------|------|
| **dvf_plus_2025_2_mutations** | 56,216 | **TABLE PRINCIPALE** - mutations immobilières |
| dvf_plus_2025_2_communes | 96 | Référence communes |
| dvf_plus_2025_2_dispositions | 195,423 | Dispositions immobilières |
| dvf_plus_2025_2_ids_parcelles | 236,159 | Identifiants parcelles |
| dvf_plus_2025_2_ids_parcelles_bis | 44,982 | Parcelles (suite) |
| dvf_plus_2025_2_lignes_articles | 67,234 | Lignes articles |
| dvf_plus_2025_2_lotsrelations | 8,456 | Relations lots |
| + 5 autres tables | - | Support/référence |

---

## 5️⃣ DOCS/ - DOCUMENTATION (19 fichiers .md + assets)

### Documentation Technique

| Fichier | Taille | Rôle | Status |
|---------|--------|------|--------|
| **PLAN_MVP_IMPLEMENTATION.md** | 22K | Plan technique détaillé (Phases 1-5) | ✅ REFERENCE |
| **CONTEXT_PROJET.md** | 11K | Contexte business projet | ✅ OK |
| **CONTEXT_OPTIMIZATION.md** | 10K | Optimisation contexte Claude | ✅ NOUVEAU |
| **MVP_REQUIREMENTS.md** | 13K | Requirements techniques MVP | ✅ OK |

### Guides Utilisateurs

| Fichier | Taille | Rôle | Status |
|---------|--------|------|--------|
| **STREAMLIT_MVP_GUIDE.md** | 12K | Guide utilisateur MVP (5 user stories) | ✅ PHASE 4 |
| **GOOGLE_MAPS_SETUP.md** | 12K | Setup Google Maps Geocoding API | ✅ OK |
| **SETUP_SUPABASE.md** | 7.6K | Setup Supabase PostgreSQL | ✅ OK |

### Guides Techniques

| Fichier | Taille | Rôle | Status |
|---------|--------|------|--------|
| **AGENTS_GUIDE.md** | 15K | Guide utilisation agents spécialisés | ✅ REFERENCE |
| **FILE_MANAGEMENT.md** | 14K | Guide gestion fichiers + archivage | ✅ OK |
| **GIT_WORKFLOW.md** | 7.4K | Workflow Git (branching, commits, PR) | ✅ OK |
| **PRECOMMIT_SETUP.md** | 7.3K | Setup pre-commit hooks | ✅ OK |
| **COMPOUND_ENGINEERING.md** | 15K | Doc compound system (expérimental) | ⏳ REFERENCE |

### Rapports Phases

| Fichier | Taille | Rôle | Status |
|---------|--------|------|--------|
| **RAPPORT_PHASE2_SUPABASE.md** | 32K | Rapport complet Phase 2 (import DVF+) | ✅ ARCHIVE |
| **PHASE3_CORRECTION_REPORT.md** | 6.4K | Rapport correction INSEE codes Phase 3 | ✅ PHASE 3 |
| **PHASE5_VALIDATION_REPORT.md** | 14K | Rapport validation Phase 5 (tests) | ✅ PHASE 5 |

### Sécurité & Maintenance

| Fichier | Taille | Rôle | Status |
|---------|--------|------|--------|
| **SECURITY_API_KEYS.md** | 13K | Gestion sécurité API keys | ✅ CRITICAL |
| **SECURITY_SETUP_COMPLETE.md** | 7.1K | Setup sécurité complet | ✅ OK |
| **IMPORT_DVF_RAPPORT.md** | 5.5K | Rapport import DVF+ process | ✅ ARCHIVE |
| **TERMINAL_SETUP.md** | 12K | Setup terminal + environnement | ✅ REFERENCE |

### Assets

| Fichier | Taille | Rôle | Status |
|---------|--------|------|--------|
| **modele_dv3f.png** | 1.2MB | Schéma modèle DVF+ visuel | ✅ REFERENCE |

---

## 6️⃣ SCRIPTS/ - UTILITAIRES (À ORGANISER)

### Maintenance Scripts

| Fichier | Rôle | Status |
|---------|------|--------|
| **scripts/maintenance/file_organizer.py** | Archivage automatique fichiers obsolètes | ✅ OK |
| **activate_postgis.py** (MOVE TO `scripts/maintenance/`) | Activation extension PostGIS | ⏳ MOVE |
| **cleanup_incomplete_data.py** (MOVE TO `scripts/maintenance/`) | Nettoyage données incomplètes Supabase | ⏳ MOVE |

### Validation Scripts

| Fichier | Rôle | Status |
|---------|------|--------|
| **debug_scoring.py** (MOVE TO `scripts/validation/`) | Debug algorithme scoring | ⏳ MOVE |
| **debug_recherche.py** (MOVE TO `scripts/validation/`) | Debug recherche comparables | ⏳ MOVE |

### À Archiver (Phase 2-3 Obsolète)

| Fichier | Rôle | Status |
|---------|------|--------|
| **correction_phase3_insee.py** | Correction codes INSEE (Phase 3 only) | ⏳ ARCHIVE |
| **test_phase2_integration.py** | Tests integration Phase 2 (obsolète) | ⏳ ARCHIVE |
| **validate_phase3_with_real_data.py** | Validation Phase 3 (obsolète) | ⏳ ARCHIVE |
| **test_supabase_connection.py** | Test connexion (move to tests/integration/) | ⏳ MOVE |
| **test_phase3_estimations.py** | Tests estimation (move to tests/integration/) | ⏳ MOVE |

---

## 7️⃣ ARCHIVE/ - FICHIERS OBSOLÈTES (Bien géré ✅)

### Structure Archive

```
archive/
├── app_v1_csv.py (16.8K)              # Ancienne version app (CSV local)
├── ARCHIVAL_LOG.json (9.8K)           # LOG COMPLET des archives (excellent!)
├── REORGANIZATION_SUMMARY_20251026.md # Summary cleanup précédent
│
├── obsolete_apps/ (4 scripts)
│   ├── old_version_*.py               # Versions expérimentales
│
├── phase1/ (3 fichiers)
│   └── tests_obsoletes/
│
├── phase2/ (import scripts + old)
│   ├── import_scripts/ (9 fichiers .py)
│   │   ├── dvf_import_*.py
│   │   └── final_import.py
│
├── phase3/ (validation scripts)
│   └── validation_scripts/ (2 fichiers)
│       ├── validate_real_data.py
│       └── correction_insee.py
│
└── phase_docs/ (5 fichiers .md)
    ├── PHASE*.md (docs anciennes)
    └── old_reports/
```

### ARCHIVAL_LOG.json (Excellent !)

Fichier qui trace **TOUT** ce qui est archivé :
- Date archivage
- Raison archivage
- Chemin original → archivé
- Métadonnées (taille, type, phase)

**STATUS** : ✅ **EXCELLENTE PRATIQUE** - Continuer ainsi !

---

## 8️⃣ CONTEXT/ - SESSION TRACKING

| Fichier | Rôle | Status |
|---------|------|--------|
| **context/WORKING.md** | Tracking état session Phase 5 (bugs, fixes, notes) | ✅ MISE À JOUR |

**Usage** : Noter session actuelle (bugs trouvés, fixes appliqués, contexte session)

---

## 9️⃣ .CLAUDE/ - CLAUDE CODE CONFIGURATION

### Agents (7 agents spécialisés ✅)

```
.claude/agents/
├── file-manager-agent.json       # Gestion fichiers, archivage, cleanup
├── orchestrator-agent.json       # Orchestration Sonnet/Haiku/Grok
├── supabase-data-agent.json      # PostgreSQL/PostGIS expertise
├── estimation-algo-agent.json    # Algorithmes scoring/estimation
├── streamlit-mvp-agent.json      # Interface Streamlit/Folium
├── testing-agent.json            # Tests & validation
└── docs-agent.json               # Documentation
```

### Memory (Persistance Cross-Session)

```
.claude/memories/
├── project_state.md              # État actuel, phase, données
├── decisions.md                  # D1-D14 décisions tech
├── phase_learnings.md            # Lessons Phase 2-3, risks, mitigations
├── file_management_rules.md      # Règles gestion fichiers
└── QUICK_START.md               # Guide redémarrage
```

### Commands (Slash Commands)

```
.claude/commands/
└── smart-handoff.md             # Sauvegarde contexte entre sessions
```

### Skills (Marketplace Plugins)

```
.claude/skills-main/
├── artifact-builder/
├── canvas-design/
├── document-skills/
├── mcp-builder/
└── ...10 autres skills
```

---

## 🧹 FICHIERS À NETTOYER (URGENT)

### À SUPPRIMER IMMÉDIATEMENT

| Fichier | Raison | Espace |
|---------|--------|--------|
| **src/estimation_algorithm.py.tmp.\*** (6 fichiers) | Fichiers temporaires éditeur | 60KB |
| **nul** | Fichier vide accidentel | - |
| **streamlit.log** | Log obsolète Phase 4 | 273B |
| **FILE_STRUCTURE_REPORT.txt** | Ancien rapport (remplacé) | 2KB |

### À DÉPLACER

| De | Vers | Type |
|----|------|------|
| `activate_postgis.py` | `scripts/maintenance/` | Move |
| `cleanup_incomplete_data.py` | `scripts/maintenance/` | Move |
| `debug_scoring.py` | `scripts/validation/` | Move |
| `debug_recherche.py` | `scripts/validation/` | Move |

### À ARCHIVER

| Fichier | Vers | Raison |
|---------|------|--------|
| `correction_phase3_insee.py` | `archive/phase3/` | Obsolète Phase 3 |
| `test_phase2_integration.py` | `archive/phase2/` | Obsolète Phase 2 |
| `validate_phase3_with_real_data.py` | `archive/phase3/` | Obsolète Phase 3 |

---

## 📊 MÉTRIQUES FINALES

### Avant Cleanup
- **Fichiers ROOT** : 30 (trop !)
- **Fichiers temp** : 6
- **Dossiers vides** : 3
- **Scripts mal placés** : 9
- **Structure cohérence** : 70%

### Après Cleanup (Objectif)
- **Fichiers ROOT** : 13 (idéal)
- **Fichiers temp** : 0
- **Dossiers vides** : 0
- **Scripts mal placés** : 0
- **Structure cohérence** : 95%

---

## ✅ CHECKLIST UTILISATION

### Pour DÉVÉLOPPEURS

- [ ] Lire `README.md` (setup + commandes)
- [ ] Lire `CLAUDE.md` (contexte projet)
- [ ] Consulter `src/CLAUDE.md` (guidelines Python)
- [ ] Lancer tests : `make test`
- [ ] Lancer app : `make run` ou `streamlit run app.py`

### Pour DOCUMENTATION

- [ ] Lire `PLAN_MVP_IMPLEMENTATION.md` (architecture)
- [ ] Consulter `AGENTS_GUIDE.md` (utilisation agents)
- [ ] Voir `FILE_MANAGEMENT.md` (organiser fichiers)
- [ ] Vérifier `SECURITY_API_KEYS.md` (secrets)

### Pour MAINTENANCE

- [ ] Archiver fichiers obsolètes avec `ARCHIVAL_LOG.json`
- [ ] Garder ROOT FILES propre (<15 fichiers)
- [ ] Mettre à jour `project_state.md` (memory)
- [ ] Vérifier `.gitignore` à chaque ajout

---

## 🎯 POINTS CLÉS

| Point | Recommandation |
|-------|-----------------|
| **ROOT FILES** | Garder ≤13 fichiers essentiels |
| **SCRIPTS** | Organiser en sous-dossiers (maintenance/, validation/) |
| **ARCHIVE** | Utiliser ARCHIVAL_LOG.json pour tracer |
| **DOCUMENTATION** | 19 fichiers excellent - continuer |
| **COMPOUND** | Évaluer utilité, sinon déplacer à examples/ |
| **TESTS** | 39 tests existants, 22 passing - Phase 5 en cours |
| **DATA** | 56,216 mutations en Supabase - ✅ OK |
| **MEMORY** | Utiliser .claude/memories pour persistance |

---

## 📞 CONTACT RAPIDE

- **Questions structure?** → Voir `FILE_MANAGEMENT.md`
- **Questions code?** → Voir `src/CLAUDE.md`
- **Questions agents?** → Voir `.claude/agents/` + `AGENTS_GUIDE.md`
- **Questions données?** → Voir `SETUP_SUPABASE.md`
- **Questions déploiement?** → Voir `vercel.json` + Déployer via Vercel dashboard

---

**Généré** : 2025-11-08
**Par** : file-manager-agent + docs-agent
**Prochaine révision** : End of Phase 5 (après UAT)

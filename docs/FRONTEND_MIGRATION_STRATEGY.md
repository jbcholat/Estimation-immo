# 🚀 PHASE 4 - Guide pour Demain (Interface Streamlit MVP)

**Date de préparation** : 2025-10-22
**À lancer** : 2025-10-23 (nouvelle conversation)
**Durée estimée** : 3-4h

---

## ✅ RECAP - Ce qui est TERMINE

### Phase 1-3 Complétées ✅

```
✅ Phase 1 (d7dde1a) : Setup agents + infrastructure
✅ Phase 2 (d6ebd49) : Supabase + DVF+ import (145k mutations)
✅ Phase 3 (20f773c) : EstimationAlgorithm (33/33 tests passants)

Phase 4 : Interface Streamlit MVP ⏳ (À faire)
Phase 5 : Tests + validation ⏳
```

### EstimationAlgorithm Opérationnel ✅

```
Classe EstimationAlgorithm complète avec:
- SimilarityScorer: Scoring 0-100 multi-critères
- EstimationEngine: Estimation pondérée
- ConfidenceCalculator: Fiabilité 4 composantes
- TemporalAdjuster: Inflation + marché Chablais

Code: src/estimation_algorithm.py
Tests: 33/33 passants (test_phase3_estimations.py)
Validation: 3/3 biens Chablais estimés avec succès
```

---

## 🎯 PHASE 4 - OBJECTIF

Créer **interface Streamlit MVP** pour estimation immobilière :

```
USER FLOW:
1. User entre adresse (ex: "10 Rue Victor Hugo, Thonon-les-Bains")
2. Clic "Estimer"
3. Système:
   - Géocode adresse (Google Maps)
   - Récupère comparables (Supabase)
   - Estime prix (EstimationAlgorithm)
   - Affiche résultats
4. User peut exporter PDF
```

**Livrables** :
- `app.py` : Streamlit principal
- Formulaire saisie bien (adresse, type, surface, caractéristiques)
- Affichage résultats (estimation, fourchette, fiabilité, graphiques)
- Carte Folium (localisation + comparables)
- Export PDF (ReportLab)

---

## 📁 FICHIERS UTILES POUR PHASE 4

| Fichier | Contenu | Usage |
|---------|---------|-------|
| `src/estimation_algorithm.py` | EstimationAlgorithm | Importer + utiliser .estimate() |
| `src/supabase_data_retriever.py` | SupabaseDataRetriever | get_comparables() |
| `PHASE3_RECAP_COMPLET.md` | Détails EstimationAlgorithm | Specs scoring/fiabilité |
| `docs/MVP_REQUIREMENTS.md` | US1-US5 (user stories) | Specs interface |
| `docs/GOOGLE_MAPS_SETUP.md` | Config Google Maps | Geocoding |
| `.env` | Credentials | GOOGLE_MAPS_API_KEY, Supabase |

---

## 🛠️ STACK PHASE 4

```
Frontend:
├── Streamlit 1.28+ (web app)
├── Folium 0.14+ (cartes interactives)
├── Plotly 5.18+ (graphiques)
└── ReportLab 4.0+ (export PDF)

Backend:
├── src/estimation_algorithm.py (estimation)
├── src/supabase_data_retriever.py (données)
└── Google Maps Geocoding API (adresse → coords)
```

---

## 📋 TÂCHES PHASE 4 (3-4h)

### Tâche 1 : Layout Streamlit (30 min)
```python
# app.py structure:
├── st.title("Estimateur Immobilier - Chablais/Annemasse")
├── SECTION 1: Formulaire saisie
│   ├── Adresse (text input)
│   ├── Type bien (selectbox)
│   ├── Surface (number input)
│   ├── Pièces (number input)
│   └── Caractéristiques (checkboxes)
│
├── SECTION 2: Résultats
│   ├── Estimation (metrique)
│   ├── Fourchette (metrique)
│   ├── Fiabilité (gauge/progress)
│   ├── Graphique comparables (Plotly)
│   └── Carte (Folium)
│
└── SECTION 3: Export
    └── Bouton PDF
```

### Tâche 2 : Intégration Geocoding (30 min)
```python
# Utiliser Google Maps API
from utils.geocoding import geocode_address

latitude, longitude = geocode_address("10 Rue Victor Hugo, 74200")
```

**Fichier** : `src/utils/geocoding.py` (à créer)
- Fonction `geocode_address(address_string) → (lat, lon)`
- Gestion erreurs (adresse non trouvée, quota API)

### Tâche 3 : Intégration Estimation (45 min)
```python
# Workflow:
from src.estimation_algorithm import EstimationAlgorithm
from src.supabase_data_retriever import SupabaseDataRetriever

algo = EstimationAlgorithm()
retriever = SupabaseDataRetriever()

# 1. Récupérer comparables
comparables = retriever.get_comparables(
    latitude, longitude,
    type_bien,
    surface_min, surface_max,
    rayon_km=10
)

# 2. Estimer
result = algo.estimate(
    latitude, longitude, surface, type_bien,
    comparables.to_dict('records')
)

# 3. Afficher
st.metric("Prix estimé", f"{result['estimation']['prix_estime_eur']:,} EUR")
```

### Tâche 4 : Visualisations (60 min)
1. **Carte Folium** :
   - Marker bien cible (rouge)
   - Markers comparables (bleu)
   - Distance annotations

2. **Graphiques Plotly** :
   - Box plot prix comparables
   - Scatter plot surface vs prix
   - Bar chart scores composantes fiabilité

### Tâche 5 : Export PDF (30 min)
```python
# Utiliser ReportLab pour générer PDF avec:
├── Résumé bien (adresse, surface, type)
├── Estimation (prix, fourchette, prix/m²)
├── Fiabilité (score, composantes)
├── Graphiques principaux
└── Liste comparables (tableau)
```

### Tâche 6 : Tests Streamlit (30 min)
```python
# test_phase4_streamlit.py:
├── Test geocoding Google Maps
├── Test estimation flow complet
├── Test affichage résultats
└── Test export PDF
```

---

## 🤖 ORCHESTRATION MULTI-MODELES

```
Tâche 1 (Layout) : Haiku (TOI)
  → Structurer app.py, widgets Streamlit

Tâche 2 (Geocoding) : Haiku
  → Wrapper Google Maps simple

Tâche 3 (Estimation) : Haiku
  → Intégration EstimationAlgorithm

Tâche 4 (Visualisations) : Grok Code Fast 1
  → Générer graphiques Folium/Plotly (économie ~50%)
  → Boilerplate Folium/Plotly

Tâche 5 (PDF Export) : Grok Code Fast 1
  → Générer template ReportLab (boilerplate)

Tâche 6 (Tests) : Grok Code Fast 1
  → Générer 15+ tests Streamlit/PDF (économie ~60%)
```

---

## 📊 TIMELINE PHASE 4

| Activité | Durée | Modèle | Notes |
|----------|-------|--------|-------|
| Tâche 1: Layout Streamlit | 30 min | Haiku | Structure de base |
| Tâche 2: Geocoding Google Maps | 30 min | Haiku | Wrapper simple |
| Tâche 3: Intégration Estimation | 45 min | Haiku | Flow complet |
| Tâche 4: Visualisations Folium/Plotly | 60 min | Grok | Boilerplate graphiques |
| Tâche 5: Export PDF ReportLab | 30 min | Grok | Template PDF |
| Tâche 6: Tests Streamlit | 30 min | Grok | 15+ tests |
| **TOTAL** | **3h45** | | |

---

## 🔐 CREDENTIALS NECESSAIRES

```
.env
├── SUPABASE_URL=https://fwcuftkjofoxyjbjzdnh.supabase.co
├── SUPABASE_KEY=sbp_c56fb1e3ee2778583ab929550793aabaa9dc552a
├── SUPABASE_DB_PASSWORD=tetrarchic-gazumping-lares-mercaptide
└── GOOGLE_MAPS_API_KEY=AIzaSyBdwqhBKgOwi6kHejyhFFw8QluV4pkpwQE
```

Tous présents dans `.env` (Phase 2)

---

## 📋 CHECKLIST AVANT PHASE 4

**À vérifier demain matin** :

- [ ] EstimationAlgorithm testé ✅ (Phase 3 complétée)
- [ ] SupabaseDataRetriever opérationnel ✅ (Phase 2)
- [ ] Google Maps API active ✅ (docs/GOOGLE_MAPS_SETUP.md)
- [ ] `.env` credentials valides ✅
- [ ] Streamlit installé (`pip install streamlit`)
- [ ] Folium installé (`pip install folium`)
- [ ] Plotly installé (`pip install plotly`)
- [ ] ReportLab installé (`pip install reportlab`)

---

## 🎯 COMMANDE PHASE 4

Copie/colle dans **nouvelle conversation** (après avoir vérifié checklist) :

```
Phase 4: Interface Streamlit MVP pour estimations immobilières

PRE-REQUIS FAITS :
✅ EstimationAlgorithm complet et testé (33/33 tests)
✅ SupabaseDataRetriever operationnel
✅ Google Maps API configurée
✅ Credentials .env valides
✅ Streamlit/Folium/Plotly/ReportLab installes

PHASE 4 - OBJECTIF :
Creer interface Streamlit MVP pour estimation immobiliere Chablais/Annemasse

TÂCHES :
1. Créer app.py avec layout Streamlit
2. Formulaire saisie (adresse, type, surface, pièces, caractéristiques)
3. Géocodage Google Maps
4. Intégration EstimationAlgorithm
5. Affichage résultats (estimation, fourchette, fiabilité)
6. Visualisations (Folium carte + Plotly graphiques)
7. Export PDF (ReportLab)
8. Tests Streamlit (15+ tests)

ORCHESTRATION :
- Haiku pour app.py, geocoding, estimation (logique métier)
- Grok pour visualisations Folium/Plotly/PDF (boilerplate)
- Grok pour tests Streamlit (économie coût ~60%)

LIVRABLES ATTENDUS :
- app.py (interface Streamlit principale)
- src/utils/geocoding.py (wrapper Google Maps)
- src/streamlit_components/ (composants réutilisables)
- test_phase4_streamlit.py (15+ tests)
- PHASE4_RECAP_COMPLET.md (documentation complète)
- 5/5 tests passants sur flow estimation complet

DURÉE : 3-4 heures
```

---

## 📞 CONTACTS & RESSOURCES

- **PRD Notion** : https://www.notion.so/Automatisation-des-estimations-2fc6cfd339504d1bbf444c0ae078ff5c
- **Streamlit Docs** : https://docs.streamlit.io/
- **Folium Docs** : https://python-visualization.github.io/folium/
- **Plotly Docs** : https://plotly.com/python/
- **ReportLab Docs** : https://www.reportlab.com/docs/

---

## 🎯 FIN DU GUIDE

**Document créé** : 2025-10-22
**À utiliser** : 2025-10-23 (demain, nouvelle conversation)
**Context** : Nouvelle conversation = 100% context frais
**Statut** : Phase 3 100% terminée et committée ✅

### Pour demain :
1. Lis ce guide START_PHASE4_DEMAIN.md
2. Vérifie checklist (Streamlit/Folium/Plotly/ReportLab installés)
3. Lance Phase 4 avec la commande fournie
4. Profite de l'orchestration Haiku/Grok pour optimiser coût/vitesse ! 💚

---

**Statut Projet** : 🟡 **EN BONNE VOIE** - 60% complet (Phase 4 démarrage demain)
- Phase 1-3: ✅ COMPLETE
- Phase 4: ⏳ A FAIRE (Streamlit MVP)
- Phase 5: ⏳ A FAIRE (Tests/validation)

**Prochaine étape** : Interface utilisateur Streamlit avec intégration EstimationAlgorithm

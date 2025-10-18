# Contexte Projet - Estimateur Immobilier Automatisé

**Créé** : 2025-10-18
**Dernière mise à jour** : 2025-10-18

---

## 📖 Historique du Projet

### Génèse (Octobre 2025)

**Problème initial** : Estimations immobilières manuelles prennent 4-6 heures par dossier dans région Chablais/Annemasse

**Solution proposée** : Automatisation ML + IA pour réduire temps de 50% (4-6h → 2-3h)

### Pivot Stratégique (18 octobre 2025)

**Avant** :
- POC Streamlit simple avec données CSV
- Focus : Proof of concept
- Stack : CSV local + Pandas + Streamlit basic

**Après (AUJOURD'HUI)** :
- MVP production-ready avec infrastructure cloud
- Focus : Outil utilisable immédiatement par équipe
- Stack : Supabase + Google Maps + Streamlit + Vercel

---

## 🎯 Objectifs Business

### Objectif Principal

**Réduire temps de production des estimations immobilières de 50%**
- Actuel : 4-6 heures par dossier
- Cible : 2-3 heures par dossier

### Objectifs Secondaires

1. **Qualité** : Maintenir ou améliorer précision des estimations
2. **Traçabilité** : Documenter comparables utilisés et leur pertinence
3. **Scalabilité** : Traiter plus de dossiers sans ressources supplémentaires additionnelles
4. **Facilité** : Interface simple pour agents immobiliers (utilisateurs non-tech)

### Métriques de Succès (KPIs)

| KPI | Cible | Mesure |
|-----|-------|--------|
| **Temps estimation** | -50% | Chronomètre avant/après |
| **Précision** | ±10-15% | Comparaison vs estimations manuelles |
| **Acceptation utilisateurs** | >80% satisfaction | Feedback Vous + Madame CHOLAT |
| **Fiabilité** | >90% uptime | Monitoring Vercel |
| **Cost-effectiveness** | <€100/mois | Infrastructure cloud |

---

## 📍 Zone Géographique

### Région Principale : Haute-Savoie Département 74

**Zone Chablais** :
- Thonon-les-Bains (chef-lieu Chablais)
- Évian-les-Bains
- Douvaine
- Sciez
- Autres communes chablaisiens

**Zone Annemasse** :
- Annemasse
- Gaillard
- Vétraz-Monthoux
- Ambilly
- Autres communes Annemassiens

**Stations Montagne** :
- Morzine
- Avoriaz
- Samoëns
- Vallée de Chamonix (proche)

**Filtrage** : Codes postaux 740xx, 742xx, 743xx

### Spécificités du Marché

- **Hétérogénéité** : Lac, montagne, campagne, périphérie Suisse proche
- **Volume limité** : Moins de transactions que grandes villes
- **Dynamique particulière** : Marché immobilier spécifique (résidences secondaires, tourisme)
- **Expertise requise** : Connaissances terrain essentielles pour validation finale

---

## 👥 Utilisateurs

### Utilisateurs Primaires

**Vous + Madame CHOLAT** (équipe interne)

**Usage** :
- Tests internes MVP (10-20 estimations réelles)
- Validation algorithmes
- Feedback UX/précision
- Collecte cas d'usage

### Utilisateurs Futurs (Phase 2)

**Clients** (potentiellement)
- Agents immobiliers zone Chablais/Annemasse
- Mise à disposition via site web
- Modèle : À déterminer (freemium, premium, API, etc.)

---

## 🛠️ Décisions Techniques Prises

### 1. Base de Données : Supabase (PostgreSQL + PostGIS)

**Alternative considérée** : MySQL, SQLite local, Google BigQuery

**Raison choix** :
- ✅ Accès déjà configuré (économie setup)
- ✅ PostgreSQL + PostGIS : requêtes spatiales natives
- ✅ Cloud-based : pas installation locale
- ✅ Scalable : facile augmenter capacité
- ✅ Gratuit plan MVP
- ✅ Synchronisé Vercel + GitHub

### 2. Géocodage : Google Maps Geocoding API

**Alternative considérée** : Nominatim (OpenStreetMap), IGN API

**Raison choix** :
- ✅ Précision requise zone montagneuse
- ✅ Support caractères spéciaux (français)
- ✅ Pas de problème coût ($5/1000 requêtes)
- ✅ API stable et documentée

**API Key** : `AIzaSyBdwqhBKgOwi6kHejyhFFw8QluV4pkpwQE`

### 3. Frontend : Streamlit MVP

**Alternative considérée** : React/Next.js, Vue.js, Angular

**Raison choix MVP** :
- ✅ Développement rapide (Python)
- ✅ Déploiement simple Vercel
- ✅ Pas de build complexe
- ✅ Adapté pour POC/MVP

**Futur** : Si UX insuffisante après tests, migration vers Next.js possible

### 4. Cartes : Folium (gratuit)

**Alternative** : Google Maps JS API (payant), Mapbox

**Raison** :
- ✅ Intégration native Streamlit
- ✅ OpenStreetMap (gratuit)
- ✅ Suffisant pour MVP

### 5. Export PDF : ReportLab

**Alternative** : WeasyPrint, API Gamma

**Raison** :
- ✅ Simple et rapide pour MVP
- ✅ Pas de dépendances externes
- ✅ Lien vers API Gamma à l'avenir

**Future** : API Gamma pour mise en page professionnelle (Phase 2)

### 6. Framework Architecture : Compound Engineering

**Raison conservé** :
- ✅ Architecture modulaire établie
- ✅ Composants réutilisables
- ✅ Orchestration propre
- ✅ Extensible pour ajouter nouveaux composants

---

## 🤖 Agents Spécialisés (5 Agents)

**Objectif** : Réduire context window de 80% vs chargement tous les MCPs

### Agent 1 : supabase-data-agent
- MCPs : Context7
- Focus : PostgreSQL/PostGIS/Supabase
- Exclus : Notion, Playwright, Perplexity

### Agent 2 : streamlit-mvp-agent
- MCPs : Context7
- Focus : Streamlit/Folium/Plotly/Google Maps
- Exclus : Notion, Playwright, Grok

### Agent 3 : estimation-algo-agent
- MCPs : Context7
- Focus : Pandas/NumPy/Algorithmes
- Exclus : Web, API externes

### Agent 4 : testing-agent
- MCPs : Aucun
- Focus : Tests/QA
- Exclus : Tous

### Agent 5 : docs-agent
- MCPs : Aucun
- Focus : Documentation
- Exclus : Tous

---

## 📊 Stack Technique Final

```
FRONTEND :
  - Streamlit (MVP web app)
  - Folium (cartes OpenStreetMap)
  - Plotly (graphiques)
  - ReportLab (export PDF)

BACKEND :
  - Python 3.10+
  - SQLAlchemy (ORM)
  - GeoAlchemy2 (geo queries)
  - googlemaps (géocodage)

DATABASE :
  - Supabase (PostgreSQL 15+)
  - PostGIS (requêtes spatiales)
  - Index B-tree/GIST

INFRASTRUCTURE :
  - Supabase (DB cloud)
  - Vercel (frontend hosting)
  - GitHub (source control)
  - Google Maps API (géocodage)

ORCHESTRATION :
  - Compound Engineering (framework custom)
  - Components modulaires
  - Workflows chainés
```

---

## 💾 Données

### Source Principale : DVF+

- **Fichiers** : data/raw/DVFPlus_2025-1-0_SQL_LAMB93_R084-ED251/
- **Région** : Rhône-Alpes (R084)
- **Projection** : LAMB93 (système français)
- **Période** : 2019-2025 (6 ans)
- **Format** : SQL scripts

### Filtrage Appliqué

1. **Département** : 74 (Haute-Savoie)
2. **Codes postaux** : 740xx, 742xx, 743xx
3. **Type transaction** : Ventes uniquement
4. **Type bien** : Maisons + Appartements
5. **Valeur** : > 0 (données valides)
6. **Surface** : > 0 (données cohérentes)

### Schéma Clés Utilisées

```
id_mutation              - Identifiant transaction
date_mutation           - Date transaction
valeur_fonciere         - Prix de vente
type_local              - Type bien (Maison, Apt)
surface_reelle_bati     - Surface habitée
nombre_pieces_principales - Nb pièces
longitude, latitude     - Coordonnées géographiques
code_postal, nom_commune - Localisation
```

---

## 🚀 Timeline & Jalons

### Phase 0 : Préparation Documentation ✅
- **Durée** : 1-2h
- **Statut** : Complété (18 oct 23:45)
- **Livrables** : Plans, agents, configuration

### Phase 1 : Setup Infrastructure ⏳
- **Durée** : 1-2h
- **Date** : 19 oct (demain)
- **Livrables** : Agents, CLAUDE.md, docs

### Phase 2 : Setup Supabase ⏳
- **Durée** : 2-3h
- **Date** : 19 oct (demain)
- **Agent** : supabase-data-agent
- **Livrables** : DB opérationnel, requêtes testées

### Phase 3 : Estimation Algorithm ⏳
- **Durée** : 2-3h
- **Date** : 19 oct (demain)
- **Agent** : estimation-algo-agent
- **Livrables** : Algorithmes, tests unitaires

### Phase 4 : Interface Streamlit ⏳
- **Durée** : 3-4h
- **Date** : 19 oct (demain)
- **Agent** : streamlit-mvp-agent
- **Livrables** : MVP complet, 5 User Stories

### Phase 5 : Tests & Validation ⏳
- **Durée** : 1-2h
- **Date** : 19 oct (demain)
- **Agent** : testing-agent
- **Livrables** : MVP validé, tests utilisateurs

**Total estimé** : 7-10 heures développement (concentrées demain)

---

## 💰 Budget & Coûts

### Infrastructure

| Service | Plan | Coût |
|---------|------|------|
| Supabase | Gratuit | €0 |
| Vercel | Gratuit | €0 |
| GitHub | Gratuit | €0 |
| Google Maps | Pay-as-you-go | ~€20-50/mois |
| **TOTAL** | | **~€20-50/mois** |

### Développement (Tokens Claude)

- **Sans agents** : 2,000 requêtes × €0.004 = €8.00
- **Avec agents** : 2,000 requêtes × €0.0008 = €1.60
- **Économie** : €6.40 (80%)

### ROI Estimé

**Investissement** : ~€1.60 dev + €30 infra = €31.60

**Bénéfice** :
- Temps économisé : 2-3h par estimation × ~50 estimations/mois = 100-150h/mois
- Valeur temps : À définir selon tarif horaire expert

---

## 🔄 Processus de Validation

### Tests Unitaires
- Supabase requêtes (5 adresses)
- Algorithmes scoring (10 cas)
- Géocodage Google (edge cases)

### Tests Intégration
- Workflow complet (formulaire → estimation → PDF)
- Performance requêtes Supabase
- API Google Maps (quotas, erreurs)

### Tests Utilisateurs
- Vous + Madame CHOLAT
- 10-20 estimations réelles Chablais/Annemasse
- Comparaison vs estimations manuelles
- Feedback UX/précision

### Critères Acceptation

- ✅ Estimations ±10-15% de valeur réelle
- ✅ Score fiabilité cohérent
- ✅ Interface utilisable (< 1 min par estimation)
- ✅ Export PDF fonctionnel
- ✅ Performance acceptable (< 10s réponse)

---

## 📚 Documentation de Référence

### À Consulter

- **PRD Notion** : https://www.notion.so/Automatisation-des-estimations-2fc6cfd339504d1bbf444c0ae078ff5c
- **Plan MVP** : @docs/PLAN_MVP_IMPLEMENTATION.md ← VOUS ÊTES ICI
- **Agents Guide** : @docs/AGENTS_GUIDE.md
- **Setup Supabase** : @docs/SETUP_SUPABASE.md
- **Google Maps** : @docs/GOOGLE_MAPS_SETUP.md
- **MVP Requirements** : @docs/MVP_REQUIREMENTS.md
- **Git Workflow** : @docs/GIT_WORKFLOW.md
- **Compound Engineering** : @docs/COMPOUND_ENGINEERING.md

---

## 🎯 Next Steps

**Demain matin :**

1. Charger ce contexte + PLAN_MVP_IMPLEMENTATION.md
2. Lancer Phase 1 : Setup agents + infrastructure
3. Phases 2-5 : Développement MVP intensif
4. Tests utilisateurs : Vous + Madame CHOLAT

**Résultat attendu** : MVP Streamlit opérationnel + déploié Vercel

---

**Document créé** : 2025-10-18 23:50
**Dernière révision** : 2025-10-18 23:50
**Auteur** : Claude Code Agent

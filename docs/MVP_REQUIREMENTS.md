# MVP Requirements - Estimateur Immobilier Chablais/Annemasse

**Dernière mise à jour** : 2025-10-21
**Responsables** : Tous agents

---

## 📋 Vue d'Ensemble

**Projet** : MVP Estimateur Immobilier automatisé
**Zone** : Chablais/Annemasse, Haute-Savoie (74)
**Utilisateurs** : Vous + Madame CHOLAT (tests internes)
**Objectif** : Réduire temps estimation de 50% (4-6h → 2-3h)
**Timeline** : 7-10h développement (Phases 1-5)

---

## 🎯 Objectifs Quantifiés

| Métrique | Cible | Mesure |
|----------|-------|--------|
| **Temps estimation** | -50% | 4-6h → 2-3h |
| **Précision** | ±10-15% | vs estimations manuelles |
| **Fiabilité score** | >90% uptime | Monitoring Vercel |
| **Couverture zone** | 100% | Codes postaux 740xx/742xx/743xx |
| **Performance** | <10s/requête | Dashboard dashboard Streamlit |
| **Acceptation utilisateurs** | >80% | Feedback Vous + Madame |
| **Cost** | <€100/mois | Infrastructure cloud |

---

## 📊 Spécifications Techniques

### Zone Géographique

**Codes postaux inclus** :
- `740xx` : Stations montagne (Morzine, Avoriaz, Samoëns, Chamonix...)
- `742xx` : Chablais (Thonon-les-Bains, Évian-les-Bains, Douvaine, Sciez...)
- `743xx` : Annemasse (Annemasse, Gaillard, Vétraz-Monthoux, Ambilly...)

**Filtrage SQL** :
```sql
WHERE code_departement = '74'
  AND code_postal ~ '^(740|742|743)'
```

### Données Utilisées

**Source** : DVF+ (Données De Valeur Foncière plus)
- Immeubles vendus depuis 2019
- Types : Maisons, Appartements
- Transactions : Ventes uniquement
- Qualité : Données officielles gouvernement français

### Stack Technologique

```
├── Backend
│   ├── PostgreSQL 15+ (Supabase)
│   ├── PostGIS (requêtes spatiales)
│   ├── Python 3.10+ (local execution)
│   └── SQLAlchemy/GeoAlchemy2 (ORM)
│
├── Frontend
│   ├── Streamlit 1.28+ (web app)
│   ├── Folium 0.14+ (cartes)
│   ├── Plotly 5.18+ (graphiques)
│   └── ReportLab 4.0+ (export PDF)
│
├── APIs Externes
│   ├── Google Maps Geocoding (adresse → coords)
│   └── Supabase API (HTTP wrapper optionnel)
│
└── Infrastructure
    ├── Supabase (cloud DB)
    ├── Vercel (hosting Streamlit)
    └── GitHub (source control)
```

---

## 📋 Spécifications Fonctionnelles

### US1 : Formulaire Saisie Bien + Géocodage

**Description** : Utilisateur saisit bien à estimer, système retrouve coordonnées

**Données Entrée** :
- Adresse (texte libre)
- Type bien (dropdown: Maison, Appartement, Terrain, Autre)
- Surface (m², numérique)
- Nombre pièces (numérique)
- Caractéristiques (checkboxes: Garage, Piscine, Terrasse)

**Processus** :
1. User entre adresse (ex: "10 Rue Victor Hugo, Thonon-les-Bains")
2. Clic sur "Estimer"
3. Google Maps Geocoding convertit adresse → (lat, lng)
4. Système retrouve comparables dans rayon 5-10km

**Données Sortie** :
- Coordonnées (latitude, longitude)
- Adresse formatée confirmée
- Précision géocodage (ROOFTOP / APPROXIMATE)

**Critères Acceptation** :
- ✅ Géocodage temps réel (< 2s)
- ✅ Adresse non trouvée → message d'erreur clair
- ✅ Validation champs requis
- ✅ Support accents français

**Composant** : `src/streamlit_components/form_input.py`

---

### US2 : Dashboard Estimation

**Description** : Affichage résultat estimation + score de fiabilité

**Données Entrée** :
- Bien cible (de US1)
- Comparables trouvés (de DB)
- Scores similarité (de algo)

**Affichage** :
- **Prix estimation** : Nombre gros (ex: "€385,000")
- **Intervalle** : Plage prix (ex: "€350k - €420k")
- **Score fiabilité** : 0-100% + qualificatif
  - Excellente: > 80%
  - Bonne: 65-80%
  - Moyenne: 50-65%
  - Faible: < 50%
- **Graphique** : Distribution prix comparables (histogram)
- **Indicateurs** :
  - Nb comparables utilisés (ex: "12 comparables")
  - Distance moyenne (ex: "2.3km")
  - Similarité moyenne (ex: "78%")

**Critères Acceptation** :
- ✅ Estimation affichée
- ✅ Score fiabilité explicite
- ✅ Graphiques lisibles
- ✅ Responsive design (mobile + desktop)

**Composant** : `src/streamlit_components/dashboard_metrics.py`

---

### US3 : Filtres Comparables Manuels

**Description** : Utilisateur peut inclure/exclure comparables et recalculer

**Contrôles** :
- Table comparables (tri, filtres)
- Checkboxes Inclure/Exclure par comparable
- Bouton "Recalculer estimation"

**Actions** :
- Exclure comparable → recalcul score de fiabilité
- Inclure comparable → recalcul avec bien
- Afficher impact sur estimation (vs avant)

**Critères Acceptation** :
- ✅ Table lisible (colonnes: adresse, surface, prix, distance, score)
- ✅ Recalcul < 1s après click
- ✅ Indication changement prix

**Composant** : `src/streamlit_components/comparables_table.py`

---

### US4 : Carte Interactive Folium

**Description** : Visualiser bien + comparables sur carte

**Affichage** :
- Bien cible : marqueur rouge distinctive
- Comparables : marqueurs bleus
- Rayon recherche : cercle pointillé (5-10km)
- Popup : Détails chaque point (au hover)

**Interactions** :
- Zoom/Pan libre
- Tooltip distance (à chaque point)
- Basemap: OpenStreetMap

**Critères Acceptation** :
- ✅ Carte charge < 3s
- ✅ Marqueurs clairement distingués
- ✅ Popup informatif
- ✅ Responsive sur mobile

**Composant** : `src/streamlit_components/map_viewer.py`

---

### US5 : Export PDF

**Description** : Générer rapport PDF complet estimation

**Contenu PDF** :
- En-tête : Titre + date
- Section 1 : Bien estimé
  - Adresse, type, surface, caractéristiques
  - Coordonnées géographiques
- Section 2 : Estimation
  - Prix estimé + intervalle
  - Score fiabilité + explication
  - Graphique distribution prix
- Section 3 : Comparables
  - Table 10-15 comparables (adresse, prix, surface, distance, score)
  - Note méthodologie
- Pied de page : Logo, date export, disclaimer

**Format** :
- Page A4 (210×297mm)
- Marges 1cm
- Font: Arial 10pt
- Couleurs: Noir/Gris (B&W print-friendly)

**Critères Acceptation** :
- ✅ PDF généré < 5s
- ✅ Pas de corruption graphiques
- ✅ Lisible impression B&W
- ✅ Fichier < 5MB

**Composant** : `src/streamlit_components/pdf_export.py`

---

## 🔧 Spécifications Techniques Détaillées

### Supabase Data Retriever

**Classe** : `SupabaseDataRetriever` (Phase 2)

```python
class SupabaseDataRetriever:
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
        """
        Retour DataFrame comparables compatibles
        Colonnes: id, commune, adresse, type, surface, pieces, prix, date, lat, lng
        """
```

**Performance** : < 5s pour rayon 10km, zone Chablais

---

### Algorithme Estimation

**Classe** : `EstimationEngine` (Phase 3)

**Scoring multi-critères** (0-100) :
1. **Distance** : Exponentielle
   - 0km : 100
   - 1km : 90
   - 5km : 50
   - 10km : 20

2. **Surface** : Tolérance ±20%
   - Exact (±10%) : 100
   - ±20% : 80
   - > 20% : 0

3. **Type bien** : Match exact prioritaire
   - Exact (Maison=Maison) : 100
   - Différent : 0

4. **Ancienneté** : Récence prioritaire
   - < 12 mois : 100
   - < 36 mois : 80
   - > 36 mois : 50

5. **Caractéristiques** : Bonus/Malus
   - +10 si garage match
   - +10 si piscine match
   - +5 si terrasse match

**Filtrage** : Inclure comparables avec score ≥ 70%

**Estimation** : Moyenne pondérée par scores

**Score Fiabilité** (4 composantes) :
- Volume comparables (30%) : 0-30 pts
- Similarité moyenne (30%) : score_moyen / 100 × 30
- Dispersion prix (25%) : 1 - (std_dev / moyenne) × 25, min 0
- Ancienneté (15%) : si < 12 mois: 15, < 36: 10, > 36: 5

**Ajustement temporel** :
- Inflation annuelle ~2% zone Chablais
- Dynamique locale = spécificités marché Chablais (estivale, tourisme)

**Sortie** :
- `estimation: float` (prix estimé €)
- `intervalle: (float, float)` (min, max)
- `confiance: float` (0-100%)
- `niveau_confiance: str` ("Excellente" / "Bonne" / etc)
- `nb_comparables: int`
- `similarite_moyenne: float`

---

### Interface Streamlit

**Structure app.py** :

```
📱 STREAMLIT APP
├── Sidebar
│   ├── Menu navigation
│   └── Info projet
│
├── Main Content
│   ├── Page 1: Formulaire (US1)
│   ├── Page 2: Dashboard (US2)
│   ├── Page 3: Comparables (US3)
│   ├── Page 4: Carte (US4)
│   └── Page 5: Export (US5)
│
└── Footer
    ├── Version
    └── Contact
```

**Performance** :
- Page load: < 3s
- Réponse interaction: < 1s
- Export PDF: < 5s

---

## 🧪 Critères Tests & Validation

### Tests Unitaires

**Couverture minimale** : 80%

- `test_supabase_retriever.py` (10+ tests)
- `test_estimation_algorithm.py` (15+ tests)
- `test_geocoding.py` (8+ tests)
- `test_streamlit_integration.py` (5+ tests)

### Tests Fonctionnels

**5 Adresses réelles Chablais** :
1. Thonon-les-Bains (46.3719°N, 6.4727°E)
2. Annemasse (46.1927°N, 6.2357°E)
3. Morzine (46.3948°N, 6.7058°E)
4. Évian-les-Bains (46.3999°N, 6.5878°E)
5. Douvaine (46.3667°N, 6.2500°E)

**Workflow** :
- Saisir bien (adresse + caractéristiques)
- Valider géocodage
- Vérifier estimation affichée
- Tester filtres comparables
- Vérifier carte correcte
- Exporter PDF
- Vérifier PDF lisible

### Tests Utilisateurs

**10-20 estimations avec Vous + Madame CHOLAT** :
- Comparer estimation système vs manuelle
- Mesurer différence (precision ±10-15%)
- Collecter feedback UX
- Collecter feedback confiance (score fiabilité vs avis expert)

### Benchmarks Performance

| Métrique | Target | Mesure |
|----------|--------|--------|
| Géocodage Google Maps | < 2s | Time.perf_counter() |
| Requête Supabase comparables | < 5s | SQL EXPLAIN ANALYZE |
| Calcul estimation algo | < 1s | Pandas groupby |
| Rendu page Streamlit | < 3s | Page load time |
| Export PDF | < 5s | ReportLab rendering |

---

## 📦 Livrables Phase par Phase

### Phase 1 (1-2h)
- ✅ 5 agents JSON créés
- ✅ `.env` configuré
- ✅ Documentation (AGENTS_GUIDE, SETUP_SUPABASE, etc.)
- ✅ Structure projet complète
- ✅ Commit "feat: setup agents et infrastructure"

### Phase 2 (2-3h)
- ✅ `src/supabase_data_retriever.py` complète
- ✅ DB opérationnelle (DVF+ importée)
- ✅ Vues créées (chablais zone)
- ✅ Index GIST performants
- ✅ Tests 5 adresses réelles
- ✅ Commit "feat: supabase data retriever + DB setup"

### Phase 3 (2-3h)
- ✅ `src/estimation_algorithm.py` complète
- ✅ Classes: SimilarityScorer, EstimationEngine, ConfidenceCalculator, TemporalAdjuster
- ✅ Tests unitaires 15+ cas
- ✅ Coverage ≥80%
- ✅ Commit "feat: estimation algorithms complete"

### Phase 4 (3-4h)
- ✅ `app.py` Streamlit complet
- ✅ 5 composants US1-US5 complets
- ✅ `src/utils/geocoding.py` wrapper Google Maps
- ✅ Tests manuels 5 adresses OK
- ✅ `vercel.json` configuré
- ✅ Commit "feat: streamlit mvp complete"

### Phase 5 (1-2h)
- ✅ Tous tests verts (pytest coverage ≥80%)
- ✅ 10-20 tests utilisateurs Vous + Madame
- ✅ Déploiement Vercel réussi
- ✅ URL publique accessible
- ✅ Documentation complète
- ✅ Commit "feat: tests validated + docs complete"

---

## 🎯 Décision Post-MVP

**Après Phase 5** :

Évaluer option :
1. **Streamlit + Vercel suffisant** → Déploiement production immédiat
2. **UX insatisfaisante** → Migration vers Next.js + API backend
3. **Performance insuffisante** → Optimisations requises

**Critères décision** :
- ✅ Feedback utilisateurs > 80% satisfaction
- ✅ Précision estimations ±10-15%
- ✅ Performance acceptable (< 10s par requête)
- ✅ Fiabilité > 90% uptime

---

**Document créé** : 2025-10-21
**Version** : 1.0
**Tous agents responsables**

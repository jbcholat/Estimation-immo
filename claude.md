# Analyse Immobilière - Documentation pour Claude

## 🏢 Contexte Projet
- **Projet**: Application d'estimation immobilière pour la Haute-Savoie (74)
- **Objectif**: Fournir des estimations immobilières fiables basées sur données DV3F et connaissances locales
- **Stack**: Python (Streamlit), Pandas, Plotly, Geolocalisation
- **Région Focus**: Haute-Savoie - communes comme Thonon-les-Bains, Evian, Annecy, etc.

## 🔧 Commandes Essentielles

```bash
# Lancer l'application
streamlit run app.py

# Développement
python -m pytest tests/

# Linter/Format
black src/
ruff check src/

# Installation dépendances
pip install -r requirements.txt
```

## 📁 Structure du Projet

```
analyse_immobiliere/
├── app.py                          # Streamlit main app
├── requirements.txt                # Dependencies
├── src/
│   ├── data_processing.py         # Chargement et préparation données DV3F
│   ├── geocoding.py               # Géocodage adresses
│   ├── comparable_finder.py       # Logique recherche biens comparables
│   ├── estimation_engine.py       # Moteur calcul estimation
│   └── utils/                     # Utilitaires (formatage, validation)
├── data/                          # Données DV3F (si local)
├── tests/                         # Suite de tests
├── docs/                          # Documentation
│   ├── architecture.md            # Architecture application
│   ├── specifications.md          # Spécifications fonctionnelles
│   ├── data-model.md             # Modèle de données
│   └── notion-export/            # Export Notion (User Stories, EPICs)
└── .claude/                       # Configuration Claude
```

## 💡 Conventions de Code

**Python :**
- Format: Black (line length: 100)
- Linter: Ruff
- Type hints obligatoires pour fonctions publiques
- Docstrings: Google style
- Exemple:
  ```python
  def estimate_property(comparables: pd.DataFrame, surface: float) -> dict:
      """Calculate property estimation based on comparables.

      Args:
          comparables: DataFrame with comparable properties
          surface: Target property surface in m²

      Returns:
          Dictionary with estimation metrics
      """
  ```

**Git :**
- Branches: `feature/xxx`, `fix/xxx`, `docs/xxx`
- Commits: Conventional commits (feat:, fix:, docs:, etc.)
- PR required pour main

## 🏗️ Architecture Patterns

**Data Flow :**
1. Utilisateur entre adresse → Géocodage
2. Recherche comparables (radius, surface, type, ancienneté)
3. Calcul scores de pertinence
4. Estimation prix (médiane, quartiles)
5. Affichage résultats + visualisations

**État Session Streamlit :**
- `st.session_state.coords` : Coordonnées géocodées
- `st.session_state.address` : Adresse saisie
- `st.session_state.last_estimation` : Dernière estimation calculée

**Données Clés :**
- Source: DV3F (Cerema) - transactions immobilières
- Colonnes principales: `datemut`, `valeurfonc`, `sbati`, `type_detail`, coordonnées
- Calculs: `prix_m2`, `distance_km`, `score_total`

## 📊 Workflows Principaux

### WF1: Estimation Immobilière
```
Input: Adresse, type bien, surface, ancienneté
↓ Géocodage
↓ Recherche comparables (rayon, tolerance surface)
↓ Scoring (proximité, ancienneté, type)
↓ Calcul médiane/quartiles
Output: Estimation + confiance + visualisations
```

### WF2: Paramétrage Recherche
```
Sidebar parameters:
- Rayon recherche max (3-20 km)
- Ancienneté max (6-36 mois)
- Tolérance surface (10-50%)
```

## 🧪 Tests Obligatoires

- Tests unitaires: `tests/unit/`
- Tests intégration: `tests/integration/`
- Données test: `tests/fixtures/`
- Coverage minimum: 80%

```bash
pytest tests/ -v --cov=src/
```

## 📝 À Compléter

Ces sections seront détaillées après exploration Notion :
- [ ] Specifications fonctionnelles détaillées (User Stories)
- [ ] EPICs et roadmap
- [ ] Modèle données précis
- [ ] Business rules Haute-Savoie
- [ ] Intégrations externes requises

**Action**: Exporter les pages Notion (User Stories, EPICs, Documents) en Markdown pour fusion dans `docs/`.

## 🔗 Références Documentation

- @docs/architecture.md (à créer)
- @docs/specifications.md (à créer)
- @docs/data-model.md (à créer)
- Notion Export: @docs/notion-export/ (en attente)

---

**Dernière mise à jour**: 2025-10-17
**Responsable**: Jean-Baptiste CHOLAT

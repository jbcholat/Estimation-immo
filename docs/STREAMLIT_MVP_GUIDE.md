# Guide Utilisateur - Estimateur Immobilier MVP

**Version:** Phase 4
**Date:** 2025-10-26
**Zone:** Chablais/Annemasse, Haute-Savoie (74)

---

## 📖 Table des matières

1. [Installation & Lancement](#installation--lancement)
2. [Guide Utilisateur (5 User Stories)](#guide-utilisateur-5-user-stories)
3. [Paramètres de Recherche](#paramètres-de-recherche)
4. [Interprétation des Résultats](#interprétation-des-résultats)
5. [FAQ & Troubleshooting](#faq--troubleshooting)

---

## Installation & Lancement

### Prérequis

- Python 3.10+
- Virtualenv ou venv
- Variables .env configurées (voir [Configuration](#configuration))

### Lancer l'application

```bash
# Activer virtualenv
source venv_immobilier/bin/activate  # Linux/Mac
# OU
.\venv_immobilier\Scripts\activate   # Windows

# Installer dépendances
pip install -r requirements.txt

# Lancer Streamlit
streamlit run app.py
```

**L'application ouvrira dans votre navigateur à:** `http://localhost:8501`

### Configuration

Créer `.env.local` (hors git) avec vos secrets :

```env
# Supabase
SUPABASE_URL=https://fwcuftkjofoxyjbjzdnh.supabase.co
SUPABASE_DB_PASSWORD=votre_password_ici
SUPABASE_KEY=votre_clé_ici

# Google Maps
GOOGLE_MAPS_API_KEY=votre_clé_ici

# Debug
DEBUG=False
LOG_LEVEL=INFO
```

**NE JAMAIS** commiter `.env.local` ou `.env` (voir [Sécurité des API Keys](#sécurité-des-api-keys))

---

## Guide Utilisateur (5 User Stories)

### US1 : Saisir adresse → Obtenir coordonnées GPS

**Location:** Barre latérale (sidebar) gauche

**Étapes:**

1. **Entrez l'adresse complète**
   - Exemple: `15 Rue de la Paix, Thonon-les-Bains, 74200`
   - Soyez aussi précis que possible pour meilleure géolocalisation

2. **Sélectionnez le type de bien**
   - Appartement
   - Maison
   - Studio
   - Duplex

3. **Entrez la surface (m²)**
   - Surface habitable en mètres carrés
   - Utilisé pour trouver comparables similaires

4. **Nombre de pièces** (optionnel)
   - Aide à affiner la recherche

5. **Cliquez "🚀 Estimer"**
   - Google Maps géocode l'adresse en temps réel
   - Si multiple suggestions → sélectionnez la bonne
   - Les coordonnées GPS s'affichent en vert ✅

**💡 Conseil:** Si adresse non trouvée, essayez sans le code postal ou avec une orthographe simplifiée

---

### US2 : Voir estimation + Score fiabilité

**Location:** Tab "📊 Estimation"

**Affichages:**

1. **💰 Prix estimé**
   - Estimation principale basée sur comparables
   - Moy pondérée avec scores de similarité

2. **📊 Prix au m²**
   - Calcul automatique : prix / surface
   - Utile pour comparaison marché

3. **🎯 Nb comparables**
   - Nombre utilisé pour l'estimation
   - Plus nombreux = estimation + fiable

4. **Intervalle de confiance**
   - 🔻 **25e percentile** (min)
   - 🔺 **75e percentile** (max)
   - Intervalle où se situerait le vrai prix (50% de probabilité)

5. **🔒 Score de fiabilité (0-100)**
   - Évaluation qualitative : Excellente / Bonne / Moyenne / Faible
   - Basé sur 4 composantes (voir détails ci-dessous)

6. **Détail 4 composantes (scores partiels)**

   | Composante | Max | Critères |
   |-----------|-----|----------|
   | **📈 Volume** | 30 | Nombre comparables (30=10+, 25=5-9, 15=3-4, 5=1-2) |
   | **🎯 Similarité** | 30 | Score moyen comparables (30=≥80%, 25=≥75%, 15=≥70%) |
   | **📊 Dispersion** | 25 | Variance prix (25=<15%, 20=<25%, 10=<40%) |
   | **⏰ Ancienneté** | 15 | Fraîcheur données (15=<12m, 12=<24m, 8=<36m) |

**💡 Interprétation:**
- **Score ≥80 (Excellente):** Faire confiance à l'estimation
- **Score 65-80 (Bonne):** Valider auprès équipe experts
- **Score 50-65 (Moyenne):** Analyse manuelle complémentaire recommandée
- **Score <50 (Faible):** Évaluation manuelle complète nécessaire

---

### US3 : Filtrer comparables manuellement

**Location:** Tab "📋 Comparables"

**Étapes:**

1. **Cliquez "🔍 Filtres avancés"** pour déplier options

2. **Ajustez les filtres:**
   - ⭐ **Score minimum** : Comparables avec score ≥ seuil
   - 📍 **Distance maximum (km)** : Exclure trop loin
   - 💵 **Prix min/max** : Fourchette de prix
   - ⏰ **Ancienneté max (mois)** : Données fraîches uniquement

3. **Visualisez tableau**
   - Colonnes: Prix | Surface | Distance | Score | Date
   - **✅ X / Y comparables sélectionnés** (avec filtres appliqués)

4. **Analysez statistiques**
   - Prix médian
   - Surface moyenne
   - Distance moyenne
   - Score moyen

5. **Recalcul estimation**
   - Cliquez "🚀 Recalculer"
   - L'estimation se met à jour avec comparables filtrés
   - Observe l'impact des filtres sur prix/fiabilité

**💡 Cas d'usage:**
- Exclure comparables trop vieux (ancienneté)
- Exclure comparables très différents (score min)
- Affiner recherche sur zone précise (distance)

---

### US4 : Visualiser bien + comparables sur carte

**Location:** Tab "🗺️ Carte"

**Affichages:**

1. **Carte interactive Folium**
   - Zoom par défaut: niveau 13 (zone locale)
   - Base cartographique: OpenStreetMap (gratuit)

2. **Marqueur bien cible**
   - 🔴 **Marqueur rouge** = propriété à estimer
   - Popup: Adresse saisie
   - Cliquez pour voir info

3. **Cercle bleu semi-transparent**
   - Rayon de recherche
   - Défaut: 10 km
   - Ajustable via sidebar "Rayon de recherche"

4. **Marqueurs comparables (verts)**
   - 🟩 **Vert foncé** = Score excellent (≥80)
   - 🟩 **Vert clair** = Score bon (70-80)
   - 🟨 **Orange** = Score moyen (60-70)
   - 🟥 **Rouge** = Score faible (<60)
   - Taille ∝ score (plus gros = meilleur score)
   - Cliquez popup pour voir: Prix | Surface | Date | Score

5. **Légende**
   - Rappel couleurs/symboles

6. **Statistiques spatiales**
   - Distance moyenne / minimale
   - Score moyen
   - Nb comparables

**💡 Utilisation:**
- Vérifier bien isolé ou en zone dense
- Identifier clusters de comparables
- Spot-checker distances/scores visuellement

---

### US5 : Export rapport PDF

**Location:** Tab "📊 Estimation", section "📄 Export PDF"

**Étapes:**

1. **Cliquez "📥 Télécharger rapport PDF"**

2. **PDF généré automatiquement**
   - 1 page simple
   - Contient:
     - En-tête: Adresse + Date
     - Section Estimation: Prix, intervalle, score
     - Section Bien: Type, surface, coordonnées
     - Section Fiabilité: Scores composantes
     - Top 5 comparables: Table récapitulatif

3. **Fichier sauvegardé**
   - Nom: `estimation_YYYYMMDD_HHMMSS.pdf`
   - Dossier: Downloads par défaut

4. **Utilisation**
   - Partager avec clients
   - Archive dossiers
   - Preuve documentée de l'estimation

**💡 Note:** PDF simple pour MVP. Version pro possible avec API Gamma (Phase 5)

---

## Paramètres de Recherche

Accessibles dans **sidebar**, ajustent requête Supabase:

| Paramètre | Plage | Défaut | Effet |
|-----------|-------|--------|-------|
| **Rayon recherche (km)** | 3-20 | 10 | Distance max pour chercher comparables |
| **Ancienneté max (ans)** | 1-10 | 3 | Transactions max de X ans |
| **Tolérance surface (%)** | 10-50 | 20 | ±X% de la surface saisie |

**Impactent:** Nb comparables trouvés, pertinence, ancienneté

---

## Interprétation des Résultats

### Scénarios courants

#### ✅ Excellente estimation (Score ≥80)
- ✅ 10+ comparables proches
- ✅ Scores moyen ≥80%
- ✅ Prix cohérents (faible dispersion)
- ✅ Données récentes (<12 mois)
- **Action:** Faire confiance à l'estimation

#### ✅ Bonne estimation (Score 65-80)
- ✅ 5-9 comparables
- ✅ Scores moyen 70-75%
- ✅ Dispersion prix modérée
- ✅ Données 12-24 mois
- **Action:** Valider auprès équipe

#### ⚠️ Estimation à valider (Score 50-65)
- ⚠️ 3-4 comparables
- ⚠️ Scores moyen <70%
- ⚠️ Dispersion prix importante
- ⚠️ Données >24 mois
- **Action:** Analyse complémentaire recommandée

#### ❌ Peu fiable (Score <50)
- ❌ <3 comparables trouvés
- ❌ Scores <70%
- ❌ Forte dispersion prix
- ❌ Données très anciennes
- **Action:** Évaluation manuelle obligatoire

### Questions / Interprétations

**"Pourquoi si peu de comparables ?"**
→ Paramètres de recherche trop restrictifs (rayon petit, tolérance surface petite). Augmentez les sliders.

**"Pourquoi prix très dispersés (0-1M€) ?"**
→ Comparables hétérogènes (maison/studio, bon état/mauvais état). Utilisez filtres Tab Comparables.

**"Estimateur dit 'Faible' mais certains comparables 'Excellents' ?"**
→ Normal ! Nb comparables insuffisant malgré bons scores individuels. Augmentez rayon recherche.

---

## FAQ & Troubleshooting

### Q: "❌ Adresse non trouvée"

**Solutions:**
1. Vérifiez orthographe (accents, majuscules)
2. Essayez sans code postal
3. Utilisez nom commune + canton
4. Exemples OK:
   - `Thonon-les-Bains` ✅
   - `Évian` ✅
   - `Annemasse, Haute-Savoie` ✅

### Q: "⚠️ Aucun comparable trouvé"

**Solutions:**
1. Augmentez "Rayon recherche" (→ 15-20 km)
2. Augmentez "Tolérance surface" (→ 30-50%)
3. Réduisez "Ancienneté max" si zone très nouvelle

### Q: "❌ Erreur connexion Supabase"

**Causes possibles:**
1. `.env.local` manquant ou mal configuré
   → Copier template `.env.example` → remplir clés
2. Clés Supabase expirées
   → Vérifier dans console Supabase
3. Réseau bloqué (firewall)
   → Vérifier connexion Internet

### Q: "🐢 App lente / lag"

**Causes possibles:**
1. Premiers chargements (Supabase init) = normal
2. Zoom arrière carte trop loin
   → Zoom avant sur zone
3. 50+ comparables affichés
   → Filtrer (score, distance)

### Q: "PDF ne télécharge pas"

**Solutions:**
1. Vérifiez pop-up blockers navigateur
2. Essayez autre navigateur
3. Vérifiez space disque local

### Q: "Comment exporter historique estimations ?"

**Phase MVP:** Pas de historique. Workaround:
- Télécharger PDF après chaque estimation
- Exporter tableau Comparables via Streamlit (bouton download)

→ Historique prévu Phase 5

---

## Support & Ressources

### Documentation Technique
- [PLAN_MVP_IMPLEMENTATION.md](PLAN_MVP_IMPLEMENTATION.md) - Plan complet
- [CONTEXT_PROJET.md](CONTEXT_PROJET.md) - Contexte business
- [PHASE3_CORRECTION_REPORT.md](PHASE3_CORRECTION_REPORT.md) - Correction import DVF+

### Données
- **Source:** DVF+ (Mutations immobilières)
- **Région:** Rhône-Alpes (R084)
- **Volume:** 56,000+ transactions
- **Zone:** Haute-Savoie (74) - Codes postaux 740xx, 742xx, 743xx
- **Période:** 2014-2025

### Infrastructure
- **DB:** Supabase (PostgreSQL + PostGIS)
- **Frontend:** Streamlit (Python)
- **Géocodage:** Google Maps API
- **Déploiement:** Vercel (futur)

### Contacts
- **Issues / Bugs:** Voir GitHub issues
- **Questions:** Consulter CLAUDE.md

---

## Notes Finales

- **MVP Scope:** Estimation basée algorithmes + pas ML (Phase 5?)
- **Accuracy:** ±10-15% de valeur réelle (validation testteurs)
- **Zone:** Chablais/Annemasse uniquement (adaptatif futur)
- **Updates:** DVF+ updated quarterly (données ~3 mois lag)

---

**Dernière mise à jour:** 2025-10-26
**Auteur:** Claude Code Agent
**Status:** Phase 4 MVP Complete ✅

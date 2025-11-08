# 🎨 Configuration Serveur MCP Figma

**Date de création** : 2025-11-07
**Projet** : Estimation IMO - Design Interface
**Objectif** : Connecter Figma à Claude Code pour design → code automatique

---

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Prérequis](#prérequis)
3. [Étape 1 : Obtenir le token Figma](#étape-1--obtenir-le-token-figma)
4. [Étape 2 : Installer le serveur MCP](#étape-2--installer-le-serveur-mcp)
5. [Étape 3 : Configurer Claude Desktop](#étape-3--configurer-claude-desktop)
6. [Étape 4 : Tester la connexion](#étape-4--tester-la-connexion)
7. [Utilisation](#utilisation)
8. [Cas d'usage pour Estimation IMO](#cas-dusage-pour-estimation-imo)
9. [Troubleshooting](#troubleshooting)

---

## Vue d'ensemble

### Qu'est-ce que le Figma MCP ?

Le **Figma MCP (Model Context Protocol) Server** est un serveur officiel développé par Figma qui permet à Claude Code d'accéder directement aux designs Figma pour :

- 📐 Analyser les layouts et composants
- 🎨 Extraire les design tokens (couleurs, typographies, espacements)
- 💻 Générer du code (React, HTML/CSS, Streamlit) à partir des designs
- 🔄 Maintenir la cohérence design ↔ code

### Avantages pour Estimation IMO

| Avantage | Bénéfice |
|----------|----------|
| **Design informé** | Code généré correspond exactement au design |
| **Gain de temps** | Pas de traduction manuelle design → code |
| **Cohérence** | Design tokens synchronisés automatiquement |
| **Itération rapide** | Modifier Figma → Régénérer code instantanément |
| **Documentation** | Design system toujours à jour |

---

## Prérequis

### ✅ Logiciels requis

- [x] **Node.js** 18.x ou supérieur
  - Vérifier : `node --version`
  - Installer : https://nodejs.org/

- [x] **npm** (installé avec Node.js)
  - Vérifier : `npm --version`

- [x] **Claude Desktop** (application installée)
  - Windows : `C:\Users\[USER]\AppData\Local\Programs\Claude\`

- [x] **Compte Figma** (gratuit ou payant)
  - Créer : https://www.figma.com/signup

### 📂 Emplacements des fichiers

| OS | Claude Config | npm global |
|----|---------------|------------|
| **Windows** | `%APPDATA%\Claude\claude_desktop_config.json` | `%APPDATA%\npm\node_modules\` |
| **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` | `/usr/local/lib/node_modules/` |
| **Linux** | `~/.config/Claude/claude_desktop_config.json` | `/usr/lib/node_modules/` |

---

## Étape 1 : Obtenir le token Figma

### 1.1 Se connecter à Figma

1. Allez sur https://www.figma.com/
2. Connectez-vous avec votre compte

### 1.2 Générer un Personal Access Token

1. **Cliquez sur votre profil** (icône en haut à gauche)
2. **Sélectionnez "Settings"**
3. **Allez dans l'onglet "Security"** (ou "Account Settings" → "Security")
4. **Descendez jusqu'à "Personal access tokens"**
5. **Cliquez sur "Create new token"** ou "Generate new token"

### 1.3 Configurer le token

**Nom du token** :
```
Claude MCP Server - Estimation IMO
```

**Scopes (permissions)** - Sélectionnez :
- ✅ `file_content:read` - Lecture du contenu des fichiers
- ✅ `file_variables:read` - Lecture des variables de design
- ✅ `file_dev_resources:read` - Lecture des ressources Dev Mode
- ✅ `files:read` - Lecture des métadonnées des fichiers

### 1.4 Copier et sauvegarder le token

⚠️ **IMPORTANT** :
- Le token s'affiche **UNE SEULE FOIS**
- Copiez-le immédiatement dans un endroit sûr
- Format : `figd_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX` (environ 40-50 caractères)

**Stockage sécurisé** :
```bash
# Ajoutez au fichier .env.local du projet
echo "FIGMA_ACCESS_TOKEN=figd_VOTRE_TOKEN_ICI" >> .env.local
```

---

## Étape 2 : Installer le serveur MCP

### Option A : Installation globale (Recommandée)

```bash
# Ouvrir PowerShell ou Terminal en tant qu'administrateur
npm install -g figma-mcp-server
```

**Avantages** :
- ✅ Accessible depuis n'importe où
- ✅ Une seule installation
- ✅ Facile à mettre à jour

**Vérifier l'installation** :
```bash
# Windows PowerShell
npm list -g figma-mcp-server

# Trouver le chemin d'installation
npm root -g
# Retourne par exemple : C:\Users\YourUser\AppData\Roaming\npm\node_modules
```

**Chemin complet du serveur** :
```
C:\Users\[VOTRE_USER]\AppData\Roaming\npm\node_modules\figma-mcp-server\dist\index.js
```

### Option B : Installation locale (Alternative)

```bash
# Dans le dossier du projet
cd ~/Estimation-immo
mkdir figma-mcp
cd figma-mcp
npm install figma-mcp-server
```

**Chemin complet** :
```
C:\Users\[VOTRE_USER]\Estimation-immo\figma-mcp\node_modules\figma-mcp-server\dist\index.js
```

---

## Étape 3 : Configurer Claude Desktop

### 3.1 Localiser le fichier de configuration

**Windows** :
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Accès rapide** :
1. Appuyez sur `Win + R`
2. Tapez : `%APPDATA%\Claude`
3. Ouvrez `claude_desktop_config.json` avec un éditeur de texte

### 3.2 Modifier la configuration

**Si le fichier est vide ou contient `{}`** :

```json
{
  "mcpServers": {
    "figma": {
      "command": "node",
      "args": [
        "C:/Users/VOTRE_USER/AppData/Roaming/npm/node_modules/figma-mcp-server/dist/index.js"
      ],
      "env": {
        "FIGMA_ACCESS_TOKEN": "figd_VOTRE_TOKEN_ICI"
      }
    }
  }
}
```

**Si le fichier contient déjà des serveurs MCP** :

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    },
    "figma": {
      "command": "node",
      "args": [
        "C:/Users/VOTRE_USER/AppData/Roaming/npm/node_modules/figma-mcp-server/dist/index.js"
      ],
      "env": {
        "FIGMA_ACCESS_TOKEN": "figd_VOTRE_TOKEN_ICI"
      }
    }
  }
}
```

### 3.3 Points critiques de configuration

⚠️ **ATTENTION - Erreurs fréquentes** :

1. **Chemins Windows** :
   - ✅ Utilisez `/` (slashes) : `C:/Users/...`
   - ✅ OU `\\` (double backslash) : `C:\\Users\\...`
   - ❌ PAS `\` (single backslash) : `C:\Users\...`

2. **Chemin absolu obligatoire** :
   - ✅ `C:/Users/.../figma-mcp-server/dist/index.js`
   - ❌ `~/AppData/.../figma-mcp-server/dist/index.js`
   - ❌ `figma-mcp-server` (sans chemin)

3. **Token Figma** :
   - ✅ Remplacez `VOTRE_TOKEN_ICI` par votre vrai token
   - Format : `figd_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`

### 3.4 Sauvegarder et redémarrer

1. **Sauvegardez** le fichier `claude_desktop_config.json`
2. **Fermez complètement** Claude Desktop (pas juste minimiser)
3. **Relancez** Claude Desktop

---

## Étape 4 : Tester la connexion

### 4.1 Vérifier dans Claude Code

1. Ouvrez une nouvelle conversation dans Claude Code
2. Le serveur Figma devrait apparaître dans les outils disponibles
3. Vous devriez voir des fonctions comme :
   - `figma_get_file`
   - `figma_get_file_nodes`
   - `figma_get_image`
   - `figma_get_comments`

### 4.2 Test simple

Créez un fichier de test dans Figma, puis dans Claude Code :

```
Peux-tu te connecter à Figma et récupérer les informations
du fichier avec l'ID : ABC123XYZ ?
```

**Où trouver l'ID du fichier Figma ?**

Dans l'URL de votre fichier Figma :
```
https://www.figma.com/file/ABC123XYZ/Mon-Design-Estimation-IMO
                           ^^^^^^^^^
                           Ceci est l'ID du fichier
```

### 4.3 Test complet

Prompt de test :

```
1. Accède à mon fichier Figma (ID: ABC123XYZ)
2. Liste tous les composants de la page "Home"
3. Extrais les couleurs utilisées
4. Génère le code Streamlit pour le composant "PropertyCard"
```

Si tout fonctionne, vous devriez recevoir :
- ✅ Liste des composants
- ✅ Palette de couleurs
- ✅ Code Streamlit généré

---

## Utilisation

### Commandes utiles avec Figma MCP

#### 1. Analyser un design

```
Analyse le fichier Figma (ID: ABC123) et donne-moi :
- La structure des pages
- Les composants principaux
- Les design tokens (couleurs, fonts, espacements)
```

#### 2. Générer du code

```
Génère le code Streamlit pour la page "PropertyEstimation"
du fichier Figma ABC123. Utilise les composants existants
dans src/streamlit_components/
```

#### 3. Extraire les design tokens

```
Extrait tous les design tokens (couleurs, typographie,
espacements) du fichier Figma ABC123 et crée un fichier
src/design_tokens.py
```

#### 4. Comparer design vs code

```
Compare le design Figma (ID: ABC123, page "Dashboard")
avec le code actuel dans app.py et identifie les différences
```

---

## Cas d'usage pour Estimation IMO

### 🎯 Workflow recommandé

#### Phase 1 : Design dans Figma

1. **Créer le fichier Figma** "Estimation IMO - MVP"
2. **Designer les pages** :
   - Page d'accueil
   - Formulaire de saisie
   - Dashboard d'estimation
   - Carte interactive
   - Rapport PDF

3. **Définir le design system** :
   - Couleurs : Primaire, secondaire, accents
   - Typographie : Titres, body, captions
   - Espacements : Grid 8px, marges, paddings
   - Composants : Buttons, Cards, Inputs, etc.

#### Phase 2 : Extraction avec Claude + Figma MCP

```
Voici le lien de mon design Estimation IMO :
https://www.figma.com/file/ABC123/Estimation-IMO-MVP

Tâches :
1. Analyse la structure complète
2. Extrais les design tokens dans src/design_tokens.py
3. Génère les composants Streamlit dans src/streamlit_components/
4. Crée app.py selon le design exact
5. Assure la cohérence avec le design system
```

#### Phase 3 : Itération design ↔ code

Lorsque vous modifiez le design dans Figma :

```
Le design Figma a été mis à jour (page "Dashboard").
Régénère le code correspondant dans src/streamlit_components/dashboard_metrics.py
```

### 📊 Composants à créer

| Composant Figma | Fichier Python | Description |
|-----------------|----------------|-------------|
| `FormInput` | `form_input.py` | Formulaire de saisie bien |
| `DashboardMetrics` | `dashboard_metrics.py` | Métriques d'estimation |
| `ComparablesTable` | `comparables_table.py` | Tableau des comparables |
| `MapViewer` | `map_viewer.py` | Carte interactive Folium |
| `PDFExport` | `pdf_export.py` | Export rapport PDF |
| `PropertyCard` | `property_card.py` | Carte affichage bien |

### 🎨 Design tokens à extraire

```python
# src/design_tokens.py (généré depuis Figma)

COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'danger': '#d62728',
    'background': '#f0f2f6',
    'text': '#262730',
}

TYPOGRAPHY = {
    'heading_1': {'size': '2.5rem', 'weight': 700},
    'heading_2': {'size': '2rem', 'weight': 600},
    'body': {'size': '1rem', 'weight': 400},
    'caption': {'size': '0.875rem', 'weight': 400},
}

SPACING = {
    'xs': '0.25rem',  # 4px
    'sm': '0.5rem',   # 8px
    'md': '1rem',     # 16px
    'lg': '1.5rem',   # 24px
    'xl': '2rem',     # 32px
}
```

---

## Troubleshooting

### Problème 1 : "Figma MCP not found"

**Symptômes** : Claude Code ne voit pas le serveur Figma

**Solutions** :
1. Vérifier que `figma-mcp-server` est installé :
   ```bash
   npm list -g figma-mcp-server
   ```
2. Vérifier le chemin dans `claude_desktop_config.json`
3. Redémarrer Claude Desktop complètement

### Problème 2 : "Invalid Figma token"

**Symptômes** : Erreur d'authentification Figma

**Solutions** :
1. Vérifier que le token est correct dans `claude_desktop_config.json`
2. Régénérer un nouveau token dans Figma Settings
3. Vérifier les scopes du token (file_content:read minimum)

### Problème 3 : "Cannot find file"

**Symptômes** : Fichier Figma non trouvé

**Solutions** :
1. Vérifier l'ID du fichier dans l'URL Figma
2. Vérifier que vous avez accès au fichier (propriétaire ou éditeur)
3. Le fichier doit être dans votre compte Figma

### Problème 4 : "Path not found" (Windows)

**Symptômes** : Erreur de chemin dans Claude Desktop

**Solutions** :
1. Remplacer `\` par `/` dans les chemins :
   ```json
   "C:/Users/Name/..." au lieu de "C:\Users\Name\..."
   ```
2. Utiliser le chemin absolu complet
3. Vérifier que le fichier `index.js` existe bien

### Problème 5 : Node.js version incompatible

**Symptômes** : Erreur au lancement du serveur

**Solutions** :
1. Vérifier la version Node.js :
   ```bash
   node --version
   # Doit être >= 18.x
   ```
2. Mettre à jour Node.js : https://nodejs.org/

---

## Ressources

### Documentation officielle

- **Figma MCP Server** : https://www.figma.com/blog/introducing-figmas-dev-mode-mcp-server/
- **Guide Figma** : https://help.figma.com/hc/en-us/articles/32132100833559
- **Model Context Protocol** : https://modelcontextprotocol.io/

### Communauté

- **GitHub Issues** : https://github.com/figma/figma-mcp-server/issues
- **Figma Forum** : https://forum.figma.com/
- **Claude Code Discord** : https://discord.gg/claude

### Tutoriels

- **Design to Code** : https://www.builder.io/blog/figma-mcp-server
- **Best Practices** : https://www.mcpevals.io/blog/best-mcp-servers-for-designers

---

## Checklist de configuration

```
[ ] Node.js 18+ installé
[ ] npm fonctionnel
[ ] Compte Figma créé
[ ] Token Figma personnel généré (figd_XXX...)
[ ] Token sauvegardé dans .env.local
[ ] figma-mcp-server installé (npm install -g)
[ ] Chemin d'installation trouvé (npm root -g)
[ ] claude_desktop_config.json modifié
[ ] Chemin absolu correct (avec /)
[ ] Token ajouté dans config
[ ] Claude Desktop redémarré
[ ] Connexion Figma testée
[ ] Fichier de test Figma créé
[ ] Extraction design tokens réussie
```

---

## Prochaines étapes

Une fois le Figma MCP configuré :

1. **Créer le fichier Figma** "Estimation IMO - MVP"
2. **Designer les 5 pages principales**
3. **Définir le design system complet**
4. **Extraire les design tokens** → `src/design_tokens.py`
5. **Générer les composants** → `src/streamlit_components/`
6. **Itérer** design ↔ code jusqu'à satisfaction

---

**Document créé** : 2025-11-07
**Auteur** : Claude Code Agent
**Version** : 1.0
**Statut** : ✅ Prêt pour configuration

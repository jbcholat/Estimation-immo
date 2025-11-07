# 🚀 Figma MCP - Quick Start

Configuration rapide du serveur MCP Figma en 5 minutes.

---

## ⚡ Installation Express

### 1️⃣ Obtenir le token Figma (2 min)

1. https://www.figma.com/ → Connexion
2. Profil (haut gauche) → **Settings**
3. Onglet **Security**
4. Section **Personal access tokens**
5. **Create new token** :
   - Nom : `Claude MCP - Estimation IMO`
   - Scopes : `file_content:read`, `file_variables:read`, `file_dev_resources:read`
6. **Copier le token** (format : `figd_XXXXX...`)

### 2️⃣ Installer le serveur (1 min)

```bash
# PowerShell (Administrateur)
npm install -g figma-mcp-server

# Trouver le chemin d'installation
npm root -g
```

**Résultat** : Vous obtenez un chemin comme :
```
C:\Users\VotreNom\AppData\Roaming\npm\node_modules
```

### 3️⃣ Configurer Claude Desktop (2 min)

**Fichier** : `%APPDATA%\Claude\claude_desktop_config.json`

**Ajouter** :
```json
{
  "mcpServers": {
    "figma": {
      "command": "node",
      "args": [
        "C:/Users/VOTRE_NOM/AppData/Roaming/npm/node_modules/figma-mcp-server/dist/index.js"
      ],
      "env": {
        "FIGMA_ACCESS_TOKEN": "figd_VOTRE_TOKEN_ICI"
      }
    }
  }
}
```

⚠️ **Remplacez** :
- `VOTRE_NOM` par votre nom d'utilisateur Windows
- `figd_VOTRE_TOKEN_ICI` par votre token Figma

⚠️ **Utilisez `/` (slashes)** et NON `\` (backslashes)

### 4️⃣ Redémarrer Claude Desktop

1. Fermez **complètement** Claude Desktop
2. Relancez l'application

### 5️⃣ Tester

Dans Claude Code :
```
Peux-tu te connecter à Figma et lister les outils disponibles ?
```

---

## 🎨 Utilisation pour Estimation IMO

### Créer votre design

1. Créez un fichier Figma : "Estimation IMO - MVP"
2. Designez vos pages (Accueil, Formulaire, Dashboard, etc.)
3. Copiez l'ID du fichier depuis l'URL :
   ```
   https://www.figma.com/file/ABC123XYZ/...
                               ^^^^^^^^^
                               Ceci est l'ID
   ```

### Générer le code

Dans Claude Code :
```
Analyse mon design Figma (ID: ABC123XYZ) et :
1. Extrais les design tokens (couleurs, fonts, espacements)
2. Génère les composants Streamlit dans src/streamlit_components/
3. Crée app.py selon le design exact
```

---

## 🆘 Problèmes courants

| Problème | Solution |
|----------|----------|
| "Figma MCP not found" | Vérifier le chemin dans config.json |
| "Invalid token" | Régénérer le token dans Figma |
| "Path not found" | Utiliser `/` au lieu de `\` dans les chemins |
| Node.js error | Vérifier version : `node --version` (doit être ≥18) |

---

## 📚 Documentation complète

Voir : `docs/FIGMA_MCP_SETUP.md`

---

**🎯 Vous êtes prêt à designer l'interface Estimation IMO avec Figma !**

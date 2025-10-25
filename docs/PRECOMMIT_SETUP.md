# 🛡️ Setup Pre-Commit Hooks - Protection Contre les Secrets

**Dernière mise à jour** : 2025-10-25
**Statut** : ✅ À installer immédiatement
**Importance** : 🔴 CRITIQUE

---

## 📋 Table des Matières

1. [Qu'est-ce que Pre-Commit?](#quest-ce-que-pre-commit)
2. [Installation Rapide (3 minutes)](#installation-rapide-3-minutes)
3. [Comment ça Marche?](#comment-ça-marche)
4. [Tests & Vérification](#tests--vérification)
5. [Commandes Utiles](#commandes-utiles)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Qu'est-ce que Pre-Commit?

### En Termes Simples

**Pre-commit = Garde de sécurité qui scanne tes commits AVANT qu'ils partent sur GitHub**

Workflow:
```
1. Tu tapes: git commit -m "..."
2. Pre-commit scanne les fichiers
3. ✅ Pas de secret détecté → commit accepté
4. ❌ Secret détecté → commit BLOQUÉ avec erreur
```

### Ce que Detect-Secrets Cherche

Pre-commit va détecter automatiquement:

| Pattern | Exemple | Détection |
|---------|---------|-----------|
| **xAI API Keys** | `xai-OFmpjg3Ic3fx...` | ✅ Bloqué |
| **Supabase Keys** | `sbp_c56fb1e3ee...` | ✅ Bloqué |
| **Google Maps Keys** | `AIzaSyBdwqhBKgOwi6k...` | ✅ Bloqué |
| **AWS Keys** | `AKIA2XYZABC...` | ✅ Bloqué |
| **Private Keys** | `-----BEGIN RSA PRIVATE KEY-----` | ✅ Bloqué |
| **Generic Passwords** | `password: "sup3rS3cr3t"` | ✅ Bloqué |

---

## ⚡ Installation Rapide (3 minutes)

### Étape 1️⃣: Installer Pre-Commit

```bash
pip install pre-commit
```

**Vérifier l'installation:**
```bash
pre-commit --version
# Doit afficher: pre-commit 3.x.x
```

### Étape 2️⃣: Initialiser Pre-Commit dans le Repo

Dans le terminal, à la racine du projet:

```bash
pre-commit install
```

**Résultat attendu:**
```
pre-commit installed at .git/hooks/pre-commit
```

### Étape 3️⃣: Vérifier l'Installation

```bash
ls -la .git/hooks/pre-commit
```

Doit exister. Voilà! C'est installé. 🎉

### (Optionnel) Étape 4️⃣: Scan Initial

Pour scanner tous les fichiers du repo:

```bash
pre-commit run --all-files
```

**Premier run peut prendre du temps** (télécharge les outils). Runs suivants = rapides.

---

## 🔧 Comment ça Marche?

### Configuration Fichiers

**2 fichiers contrôlent pre-commit:**

1. **`.pre-commit-config.yaml`** (comment j'ai créé)
   - Définit les hooks à exécuter
   - Détecte secrets, code quality, fichiers sensibles
   - Version contrôlée (dans GitHub)

2. **`.secrets.baseline`** (comment j'ai créé)
   - Liste les "faux positifs" à ignorer
   - Permet exceptions contrôlées
   - Version contrôlée (dans GitHub)

### Workflow Détaillé

**Quand tu fais:**
```bash
git add file1.py file2.md
git commit -m "Add feature"
```

**Voici ce qui se passe:**

```
1. Pre-commit charge la config
2. Exécute les hooks (detect-secrets, private-key, etc.)
3. Scanne tous les fichiers à committer
4. Cherche patterns dangereux
5. Si rien trouvé → commit continue ✅
6. Si secret trouvé → commit BLOQUÉ ❌
```

**Message d'erreur si secret détecté:**
```
ERROR: Detected secret in staged files

File: src/config.py
Match: "xai-OFmpjg3Ic3fx7HH1qln8XVtmMygVI8emgX5nhyaGOps0eLTEQ0ZAPk3dKRHMpQrKo9kWeiGAWOHRYMVg"

SOLUTION:
1. Remove the secret from the file
2. Use environment variables instead
3. Restart the commit
```

---

## 🧪 Tests & Vérification

### Test 1️⃣: Vérifier que Pre-Commit est Actif

```bash
# Cherche le hook
cat .git/hooks/pre-commit | head -5

# Doit afficher: #!/usr/bin/env bash
```

### Test 2️⃣: Tester avec un Faux Secret

**Crée un fichier test:**

```bash
echo "SECRET_KEY = xai-TEST123456789" > test_secret.txt
git add test_secret.txt
git commit -m "Test"
```

**Résultat attendu:**
```
ERROR: Detected secret in staged files
File: test_secret.txt
Match: "xai-TEST123456789"
```

✅ Pre-commit fonctionne!

**Nettoie:**
```bash
git reset HEAD test_secret.txt
rm test_secret.txt
```

### Test 3️⃣: Test avec un Fichier Normal

**Crée un fichier normal:**

```bash
echo "# Mon commentaire" > test_normal.py
git add test_normal.py
git commit -m "Add normal file"
```

**Résultat attendu:**
```
✓ No secrets detected
✓ Commit successful
```

✅ Les commits normaux passent!

**Nettoie:**
```bash
git reset HEAD test_normal.py
rm test_normal.py
```

---

## 📝 Commandes Utiles

### Scan Manuel (Avant de Committer)

```bash
# Scanner tous les fichiers
pre-commit run --all-files

# Scanner un fichier spécifique
pre-commit run --files src/config.py

# Scanner avec logs détaillés
pre-commit run --all-files -v
```

### Mettre à Jour les Hooks

Quand `.pre-commit-config.yaml` change:

```bash
pre-commit autoupdate
```

### Désactiver Pre-Commit (Temporaire)

**Si tu dois bypass temporairement:**

```bash
git commit --no-verify -m "Message"
```

⚠️ **Attention:** Utilisé seulement en cas d'urgence! Ne recommenceras pas!

### Réinitialiser Pre-Commit

```bash
pre-commit uninstall
pre-commit install
```

---

## 🔧 Troubleshooting

### ❌ Problème: "Command not found: pre-commit"

**Cause:** Pre-commit n'est pas installé

**Solution:**
```bash
pip install pre-commit
pre-commit --version
```

---

### ❌ Problème: "Hook staged file modification"

**Cause:** Un hook a modifié un fichier (ex: formatter)

**Solution:** C'est normal!
```bash
# Pre-commit a reformaté ton code
git add .  # Rajoute les modifs
git commit -m "Message"  # Recommence
```

---

### ❌ Problème: ".git/hooks/pre-commit permission denied"

**Cause:** Permissions incorrectes sur le hook

**Solution:**
```bash
chmod +x .git/hooks/pre-commit
pre-commit run --all-files
```

---

### ❌ Problème: Pre-Commit Est Trop Lent

**Cause:** Premiers runs sont lents (télécharge outils)

**Solution:**
- Premiers runs: 1-2 minutes (normal)
- Runs suivants: 5-10 secondes
- Très normal sur Windows

---

### ❌ Problème: "False Positive" - Secret Détecté à Tort

**Si un fichier normal est bloqué:**

1. Ajoute à `.secrets.baseline`:
   ```json
   {
     "results": {
       "file.py": [
         {
           "type": "Secret Keyword",
           "line_number": 42
         }
       ]
     }
   }
   ```

2. Reconfigure:
   ```bash
   pre-commit run --all-files
   ```

---

## 🎯 Checklist

- [ ] `pip install pre-commit` (installer)
- [ ] `pre-commit install` (configurer)
- [ ] `ls -la .git/hooks/pre-commit` (vérifier existence)
- [ ] Test avec secret factice (doit être bloqué)
- [ ] Test avec fichier normal (doit passer)
- [ ] `git commit` accepte commits normaux

---

## 📝 Résumé

**Installation = 3 commandes:**
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files  # Test
```

**Utilisation = Normale, pas de changement:**
```bash
git add .
git commit -m "..."  # Pre-commit scanne automatiquement
# ✅ Si pas de secret → commit
# ❌ Si secret → bloqué
```

**Résultat:**
- ✅ Aucun secret ne peut être accidentellement commité
- ✅ Protection locale AVANT GitHub
- ✅ Peace of mind pour repo public

---

**Document créé le 2025-10-25**
**Prochaine étape**: Installer et tester

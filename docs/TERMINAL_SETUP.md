# 🖥️ Configuration Terminal PowerShell - Guide Complet

**Dernière mise à jour** : 2025-10-25
**Statut** : ✅ À appliquer immédiatement pour débloquer le terminal

---

## 📋 Table des Matières

1. [Diagnostic du Problème](#diagnostic-du-problème)
2. [Solution Recommandée](#solution-recommandée)
3. [Instructions Pas-à-Pas](#instructions-pas-à-pas)
4. [Vérification du Succès](#vérification-du-succès)
5. [Solutions Alternatives](#solutions-alternatives)
6. [Troubleshooting](#troubleshooting)
7. [Références](#références)

---

## 🔴 Diagnostic du Problème

### L'Erreur que Tu Vois

```
Impossible de charger le fichier C:\analyse_immobiliere\venv_immobilier\Scripts\Activate.ps1,
car l'exécution de scripts est désactivée sur ce système.
```

### Qu'est-ce qui se passe?

**Windows PowerShell** a une politique de sécurité par défaut qui **bloque l'exécution de tous les scripts PowerShell**. Cette protection existe pour éviter l'exécution accidentelle de malware.

Quand tu ouvres un terminal dans VSCode:
1. VSCode tente d'exécuter le profil PowerShell
2. Ce profil active automatiquement ton environnement virtuel Python (`venv_immobilier`)
3. L'activation utilise le script `Activate.ps1` (un script PowerShell)
4. ❌ PowerShell refuse d'exécuter ce script → **Erreur**

### Impact sur le Développement

**Sans correction:**
- ❌ Terminal affiche une erreur à chaque ouverture
- ❌ L'environnement virtuel Python ne s'active pas automatiquement
- ❌ Risque d'utiliser le mauvais Python (celui du système au lieu du venv)
- ❌ Dépendances du projet non disponibles

---

## ✅ Solution Recommandée

### Pourquoi Autoriser les Scripts PowerShell?

**Politique `RemoteSigned` = Bon équilibre sécurité/praticité:**

| Élément | Statut | Détail |
|---------|--------|--------|
| **Scripts locaux** | ✅ Autorisés | Scripts que tu crées (comme `Activate.ps1`) |
| **Scripts distants** | ⚠️ Signés requis | Scripts téléchargés doivent être signés numériquement |
| **Protection malware** | ✅ Maintenue | Bloque les scripts non-signés d'Internet |
| **Pratique pour dev** | ✅ Oui | Activation venv automatique fonctionne |
| **Recommandé par Microsoft** | ✅ Oui | Politique standard pour développeurs |

### La Commande

Tu vas exécuter **UNE SEULE commande** pour autoriser les scripts PowerShell:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Explication des paramètres:**
- `RemoteSigned` : Scripts locaux OK, scripts distants doivent être signés
- `-Scope CurrentUser` : S'applique seulement à ton compte utilisateur (pas global système)

---

## 🚀 Instructions Pas-à-Pas

### Étape 1️⃣: Ouvrir PowerShell en Mode Administrateur

**Méthode A: Via Windows (Recommandée)**
1. Appuie sur `Windows Key` (touche avec le logo Windows)
2. Tape: `powershell`
3. Tu vois "Windows PowerShell" dans les résultats
4. **Clique droit** → **"Exécuter en tant qu'administrateur"**
5. Une boîte de dialogue blanche s'ouvre (PowerShell)

**Méthode B: Via le Menu Démarrer**
1. Clique sur **Menu Démarrer** (en bas à gauche)
2. Tape `powershell` dans la barre de recherche
3. Clique droit sur "Windows PowerShell"
4. Clique sur **"Exécuter en tant qu'administrateur"**

**Méthode C: Via VSCode (Plus Rapide)**
1. Dans VSCode, ouvre un terminal (`Ctrl + ```)
2. Clique sur le menu `Terminal` → `Run Task...` → Cherche une tâche admin
3. **OU** ouvre simplement le terminal et tape `pwsh -NoProfile` (exécute sans profil, donc pas d'erreur)

### Étape 2️⃣: Exécuter la Commande

**Dans la fenêtre PowerShell ouverte en admin, copie-colle cette commande exactement:**

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Puis appuie sur `Entrée`**

### Étape 3️⃣: Confirmer l'Opération

PowerShell va te demander:

```
Voulez-vous vraiment modifier la stratégie d'exécution ?
[O] Oui  [T] Tous  [N] Non  [?] Aide (la valeur par défaut est "N"):
```

**Tape `O` (pour "Oui") et appuie sur `Entrée`**

### Étape 4️⃣: Vérifier le Succès

Tape cette commande pour confirmer que la modification a été appliquée:

```powershell
Get-ExecutionPolicy -List
```

Tu devrais voir quelque chose comme:

```
        Scope ExecutionPolicy
        ----- ---------------
MachinePolicy       Undefined
   UserPolicy       Undefined
      Process       Undefined
  CurrentUser  RemoteSigned     ← Cette ligne doit afficher "RemoteSigned"
 LocalMachine     Restricted
```

✅ Si tu vois **`RemoteSigned`** pour `CurrentUser`, c'est bon!

### Étape 5️⃣: Redémarrer le Terminal VSCode

1. **Ferme tous les terminaux VSCode** ouverts
2. **Ferme VSCode complètement** (facultatif mais recommandé)
3. **Rouvre VSCode**
4. Ouvre un nouveau terminal (`Ctrl + ```)

---

## 🎯 Vérification du Succès

### ✅ Checklist - Tout Fonctionne!

Après redémarrage du terminal, vérifie ces points:

- [ ] **Pas d'erreur au démarrage du terminal**
  - L'erreur "Impossible de charger le fichier..." ne s'affiche plus

- [ ] **Indicateur du venv activé visible**
  - Tu vois `(venv_immobilier)` au début de ta ligne de commande
  - Exemple: `(venv_immobilier) PS C:\analyse_immobiliere>`

- [ ] **Python utilise le bon interpréteur**
  Exécute cette commande dans le terminal:
  ```powershell
  python --version
  ```
  Tu devrais voir: `Python 3.x.x` (la version de ton venv)

- [ ] **Pip trouve les dépendances du projet**
  ```powershell
  pip list | grep -i "supabase\|streamlit"
  ```
  Tu devrais voir les packages du projet

### 📊 Diagnostic Complet (Si tu veux plus de détails)

Exécute cette commande pour un diagnostic complet:

```powershell
"=== DIAGNOSTIC TERMINAL ===";
Write-Host "Politique ExecutionPolicy: " -NoNewLine; Get-ExecutionPolicy;
Write-Host "Python: " -NoNewLine; python --version;
Write-Host "Venv actif: " -NoNewLine; if($env:VIRTUAL_ENV) { "OUI - $env:VIRTUAL_ENV" } else { "NON" };
Write-Host "Pip version: " -NoNewLine; pip --version;
```

---

## 🔄 Solutions Alternatives

Si pour une raison quelconque tu préfères ne pas utiliser la Solution 1, voici tes alternatives:

### Solution 2️⃣: Désactiver l'Auto-Activation du venv

**Quand l'utiliser:**
- Tu veux contrôle total et activer manuellement le venv quand nécessaire
- Tu préfères éviter toute modification de politiques de sécurité Windows

**Comment faire:**
1. Dans VSCode, va dans `Fichier` → `Préférences` → `Paramètres`
2. Cherche: `python.terminal.autoActivateEnvironmentInNewTerminals`
3. **Décochez cette option**

**Inconvénients:**
- À chaque terminal, tu dois taper: `. .\venv_immobilier\Scripts\Activate.ps1`
- Risque d'oublier et utiliser le mauvais Python

### Solution 3️⃣: Utiliser Git Bash à la Place de PowerShell

**Quand l'utiliser:**
- Tu préfères Bash (interface Unix-like) à PowerShell
- Tu utilises déjà Git Bash sur ta machine

**Comment faire:**
1. Si tu n'as pas Git Bash, installe [Git for Windows](https://git-scm.com/download/win)
2. Dans VSCode, va dans `Fichier` → `Préférences` → `Paramètres`
3. Cherche: `terminal.integrated.defaultProfile.windows`
4. Change la valeur en: `Git Bash`
5. Redémarre VSCode

**Avantages:**
- Pas besoin de modifier les politiques Windows
- Activation venv fonctionne directement avec bash
- Interface plus familière si tu viens d'Unix/Linux

**Inconvénients:**
- Interface différente de PowerShell (commandes bash au lieu de powershell)
- Certains outils Windows intégrés moins bien supportés

### Tableau Comparatif des 3 Solutions

| Critère | Solution 1 (RemoteSigned) | Solution 2 (Pas d'auto-activation) | Solution 3 (Git Bash) |
|---------|---------------------------|------------------------------------|-----------------------|
| **Sécurité** | ✅ Bon | ✅ Excellent | ✅ Bon |
| **Facilité** | ✅ 1 commande | ⚠️ Manuel chaque fois | ✅ 1 fois, puis facile |
| **Venv auto** | ✅ Oui | ❌ Non | ✅ Oui |
| **Interface** | PowerShell | PowerShell | Bash |
| **Recommandation** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |

---

## 🔧 Troubleshooting

### ❌ Problème: "Accès refusé" en exécutant la commande

**Cause:** Tu n'as pas ouvert PowerShell en mode Administrateur

**Solution:**
- Ferme PowerShell
- Rouvre en mode Admin (voir Étape 1)
- Réexécute la commande

---

### ❌ Problème: Le venv ne s'active toujours pas

**Cause possible 1:** VSCode ne détecte pas le venv

**Solution:**
```powershell
# Cherche le venv
python -m venv --help
ls .\venv_immobilier\Scripts\
```

**Cause possible 2:** Le profil PowerShell n'existe pas ou est vide

**Solution:**
```powershell
# Vérifie le profil
cat $PROFILE
# Crée un profil basique
if (!(Test-Path -Path $PROFILE)) {
  New-Item -ItemType File -Path $PROFILE -Force
  Add-Content -Path $PROFILE -Value ". '$env:VIRTUAL_ENV\Scripts\Activate.ps1'"
}
```

---

### ❌ Problème: "Je veux revenir à Restricted"

**Si tu veux annuler la modification:**

```powershell
Set-ExecutionPolicy -ExecutionPolicy Restricted -Scope CurrentUser
```

(Puis confirme avec `O`)

---

### ❌ Problème: "Je vois toujours l'erreur même après les changements"

**Solution:**
1. Ferme complètement VSCode
2. Redémarre ton ordinateur (pour forcer rechargement des politiques)
3. Rouvre VSCode et teste

---

## 📚 Références

### Documentation Microsoft

- [ExecutionPolicy Documentation](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy)
- [PowerShell Security Best Practices](https://docs.microsoft.com/en-us/powershell/scripting/learn/shell/security-best-practices)

### Documentation Python

- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [VSCode Python Integration](https://code.visualstudio.com/docs/python/environments)

### Autres Ressources

- [VSCode Terminal Configuration](https://code.visualstudio.com/docs/editor/integrated-terminal)
- [Git Bash vs PowerShell](https://stackoverflow.com/questions/32597209/git-bash-vs-command-line)

---

## 📝 Notes de Sécurité

### Pourquoi RemoteSigned est sûr

**Scripts locaux** (comme `Activate.ps1`):
- ✅ Tu les contrôles complètement
- ✅ Pas de téléchargement d'Internet
- ✅ Safe pour exécution

**Scripts distants** (téléchargés):
- ⚠️ Doivent être **signés numériquement** par un éditeur de confiance
- ⚠️ PowerShell vérifie la signature avant d'exécuter
- ⚠️ Bloque malware non-signé

**Résultat:**
- ✅ Bonne sécurité
- ✅ Pas de friction pour le dev local
- ✅ Recommandé par Microsoft pour développeurs

---

## 🎯 Résumé

**Pour débloquer ton terminal:**

1. Ouvre PowerShell **en mode Admin**
2. Exécute: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
3. Confirme avec `O`
4. Redémarre VSCode
5. ✅ Terminal fonctionne!

**Questions?** Consulte la section [Troubleshooting](#troubleshooting) ci-dessus.

---

**Document créé le 2025-10-25**
**Prochaine révision**: Après application de la solution

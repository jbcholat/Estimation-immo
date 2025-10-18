# Guide Git Workflow - Analyse Immobilière

Guide rapide pour gérer les versions et collaborer sur le projet.

## Quick Start

### 1️⃣ Créer une nouvelle fonctionnalité

```bash
# Créer une branche depuis develop
git checkout develop
git pull origin develop
git checkout -b feature/mon-feature

# Développer et tester
# ... modifications ...

# Commit avec message structuré
git add .
git commit -m "feat(module): description courte

Description détaillée si nécessaire

Fixes #123"

# Pousser et créer une PR
git push origin feature/mon-feature
gh pr create --title "feat: titre PR" --body "Description détaillée"
```

### 2️⃣ Corriger un bug

```bash
# Branche fix
git checkout develop
git pull origin develop
git checkout -b fix/mon-bug

# Correction et test
git add .
git commit -m "fix(module): corriger comportement

Le bug était causé par...
Solution: ...

Closes #456"

git push origin fix/mon-bug
gh pr create --fill
```

### 3️⃣ Créer une hotfix (bug en production)

```bash
# Hotfix depuis main
git checkout main
git pull origin main
git checkout -b hotfix/mon-hotfix

# Correction immédiate
git add .
git commit -m "hotfix: description courte"

# Pousser vers main ET develop
git push origin hotfix/mon-hotfix
gh pr create --base main --title "hotfix: ..."
```

### 4️⃣ Préparer une release

```bash
# Créer branche de release
git checkout develop
git pull origin develop
git checkout -b release/1.1.0

# Mettre à jour CHANGELOG.md et version
# Tester en détail
# Corriger les éventuels bugs

# Merge vers main
git checkout main
git merge --no-ff release/1.1.0
git tag -a v1.1.0 -m "Release 1.1.0: Description"

# Merge vers develop
git checkout develop
git merge --no-ff release/1.1.0

# Pousser
git push origin main develop v1.1.0

# Créer release GitHub
gh release create v1.1.0 --generate-notes
```

## Commandes Courantes

### Statut et synchronisation

```bash
# Voir l'état local
git status

# Voir les différences
git diff                    # Changements non stagés
git diff --staged          # Changements stagés
git diff main..develop     # Différences entre branches

# Mettre à jour locale
git fetch origin            # Récupérer les changements distants
git pull origin develop     # Fetch + merge

# Historique
git log --oneline -10                    # 10 derniers commits
git log --oneline --graph --all         # Vue complète
git log --author="jbcholat" --oneline   # Commits d'un auteur
```

### Branches

```bash
# Lister les branches
git branch                      # Branches locales
git branch -r                   # Branches distantes
git branch -a                   # Toutes les branches

# Créer/supprimer
git branch mon-branch           # Créer localement
git checkout -b mon-branch      # Créer et basculer
git branch -d mon-branch        # Supprimer localement
git push origin --delete mon-branch   # Supprimer distante

# Basculer
git checkout develop            # Basculer vers develop
git checkout -                  # Basculer vers branche précédente
git switch main                 # Nouvelle syntaxe
```

### Tags et Releases

```bash
# Gérer les tags
git tag                         # Lister les tags
git tag -a v1.0.0 -m "Message" # Créer un tag annoté
git push origin v1.0.0          # Pousser un tag
git tag -d v1.0.0               # Supprimer localement
git push origin :v1.0.0         # Supprimer distant

# Releases GitHub CLI
gh release list                          # Lister les releases
gh release create v1.0.0 --generate-notes  # Créer avec notes auto
gh release create v1.0.0 --notes "Notes"   # Avec notes custom
gh release delete v1.0.0                # Supprimer
```

### Commits et historique

```bash
# Modifier le dernier commit
git commit --amend --no-edit     # Ajouter des changements
git commit --amend -m "Nouveau message"  # Changer le message

# Annuler
git revert <commit>              # Créer un commit inverse
git reset --soft HEAD~1          # Annuler dernier commit (garder changements)
git reset --hard HEAD~1          # Annuler dernier commit (perdre changements)

# Temporaire
git stash                        # Sauvegarder les changements
git stash list                   # Lister les stashs
git stash pop                    # Restaurer le dernier stash
git stash drop                   # Supprimer le dernier stash
```

### Fusionner et Rebase

```bash
# Merge (fusion non-destructive)
git merge feature/mon-feature    # Fusionner une branche

# Rebase (fusion linéaire)
git rebase develop               # Rembaser sur develop
git rebase -i HEAD~3             # Rebase interactif des 3 derniers commits

# Résoudre les conflits
git status                       # Voir les fichiers en conflit
# Éditer les fichiers
git add fichier-resolu
git commit -m "Résoudre conflit de merge"
```

## GitHub CLI - Gestion des PRs

```bash
# Lister les PRs
gh pr list                                    # Toutes les PRs
gh pr list --assignee jbcholat               # PRs assignées
gh pr list --state closed                    # PRs fermées
gh pr list --draft                           # Draft PRs

# Créer une PR
gh pr create                                 # Créer interactivement
gh pr create --title "Title" --body "Body"  # Avec options
gh pr create --fill                          # Auto-remplir

# Voir une PR
gh pr view 42                                # PR #42
gh pr view 42 --web                          # Ouvrir dans navigateur

# Vérifier une PR
gh pr checks 42                              # Voir les checks
gh pr review 42 -c -b "Commentaire"         # Commenter une PR
gh pr review 42 -a                           # Approuver

# Merger une PR
gh pr merge 42                               # Merger une PR
gh pr merge 42 --squash                      # Squash avant merge
gh pr merge 42 --rebase                      # Rebase avant merge
```

## Bonne pratique

### ✅ À FAIRE

- ✅ Commits petits et atomiques
- ✅ Messages descriptifs et significatifs
- ✅ Branch nommée explicitement
- ✅ Tests avant de pousser
- ✅ Sync régulière avec main/develop
- ✅ PR avec description complète
- ✅ Rebase avant merge si possible

### ❌ À ÉVITER

- ❌ Force push sur main/develop
- ❌ Commits `fix`, `wip`, `asdf`
- ❌ Merge commits superflu
- ❌ Branches longue durée
- ❌ PRs sans description
- ❌ Push de secrets dans git

## Troubleshooting

### Annuler un push accidentel

```bash
# Si pas encore mergé (main)
git revert <commit>
git push origin main

# Sinon, prendre contact!
```

### Récupérer un commit supprimé

```bash
git reflog                  # Voir tous les commits
git checkout <commit-hash>  # Retourner au commit
```

### Nettoyer les branches locales

```bash
git branch -d merged-branch              # Supprimer fusionnée
git fetch origin --prune                 # Nettoyer les refs
git branch -vv                           # Voir les branches mortes
```

---

**Plus d'infos :**
- [VERSIONING.md](../VERSIONING.md) - Stratégie de versioning
- [CHANGELOG.md](../CHANGELOG.md) - Historique des versions
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub CLI Documentation](https://cli.github.com/)

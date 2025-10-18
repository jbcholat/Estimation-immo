# Stratégie de Versioning - Analyse Immobilière

## Semantic Versioning (SemVer)

Ce projet suit [Semantic Versioning 2.0.0](https://semver.org/lang/fr/)

### Format: `MAJOR.MINOR.PATCH`

- **MAJOR**: Changements incompatibles avec les versions antérieures
- **MINOR**: Nouvelles fonctionnalités rétro-compatibles
- **PATCH**: Corrections de bugs rétro-compatibles

### Exemples
- `1.0.0` - Première version stable
- `1.1.0` - Nouvelles fonctionnalités ajoutées
- `1.1.1` - Correction de bugs
- `2.0.0` - Changement majeur

## Branching Strategy (Git Flow)

### Branches principales
- **main** : Production (versions stables)
- **develop** : Intégration (prochaine release)

### Branches de support
- **feature/xxx** : Nouvelles fonctionnalités
  - Exemple: `feature/estimation-algo`, `feature/geocoding-api`
  - Branchée depuis: `develop`
  - Fusionnée vers: `develop` (via PR)

- **fix/xxx** : Corrections de bugs
  - Exemple: `fix/validation-surface`, `fix/api-timeout`
  - Branchée depuis: `develop`
  - Fusionnée vers: `develop` (via PR)

- **hotfix/xxx** : Corrections urgentes en production
  - Exemple: `hotfix/api-crash`, `hotfix/data-validation`
  - Branchée depuis: `main`
  - Fusionnée vers: `main` ET `develop`

- **docs/xxx** : Documentation uniquement
  - Exemple: `docs/user-guide`, `docs/api-reference`

### Release Flow
1. Créer une branche `release/x.y.z` depuis `develop`
2. Corrections finales et tests
3. Fusionner vers `main` et créer un tag `vx.y.z`
4. Fusionner vers `develop`

## Commits

### Format Conventional Commits
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- **feat**: Nouvelle fonctionnalité
- **fix**: Correction de bug
- **docs**: Documentation
- **style**: Formatage (Black, Ruff)
- **refactor**: Refactorisation sans changement fonctionnel
- **test**: Tests unitaires/intégration
- **chore**: Maintenance (deps, config)
- **perf**: Amélioration de performance

### Exemples
```
feat(estimation): ajouter algo de scoring avancé

Implémentation du scoring multi-critères
- Distance pondérée
- Ancienneté surface
- Localisation

Fixes #42
```

```
fix(geocoding): corriger timeout API externe

Le timeout était trop court pour les adresses complexes.
Augmentation de 3s à 5s.

Closes #38
```

## Releases sur GitHub

Les releases sont créées automatiquement avec :
- Tag git: `vx.y.z`
- Release notes générées depuis commits
- Changelog mis à jour

### Commandes utiles
```bash
# Voir les tags
git tag -l

# Créer une release locale
git tag -a v1.0.0 -m "Release 1.0.0: First stable version"

# Pousser la release
git push origin v1.0.0

# Créer une GitHub release
gh release create v1.0.0 --generate-notes
```

## Changelog

Maintenu dans `CHANGELOG.md` en format [Keep a Changelog](https://keepachangelog.com/lang/fr/)

Sections:
- **Added** - Nouvelles fonctionnalités
- **Changed** - Changements existants
- **Fixed** - Corrections de bugs
- **Removed** - Fonctionnalités supprimées
- **Deprecated** - Fonctionnalités dépréciées

## Workflow PR

1. ✅ Créer branche feature/fix
2. ✅ Développer et tester localement
3. ✅ Push et créer PR
4. ✅ Code review (au moins 1 approbation)
5. ✅ Tests CI/CD passent
6. ✅ Merge vers develop

## Versioning des données

Les versions de données DV3F sont tracées dans:
- `data/VERSION.txt` - Version actuelle
- `data/CHANGELOG.md` - Historique des mises à jour

---

**Dernière mise à jour**: 2025-10-18

# Contribuer au projet Analyse Immobilière

Merci de vouloir contribuer ! Ce guide explique comment participer au projet.

## 📋 Table des matières

1. [Code de Conduite](#code-de-conduite)
2. [Avant de Commencer](#avant-de-commencer)
3. [Processus de Contribution](#processus-de-contribution)
4. [Standards de Code](#standards-de-code)
5. [Commits et PRs](#commits-et-prs)
6. [Aide et Support](#aide-et-support)

## Code de Conduite

- ✅ Soyez respectueux
- ✅ Soyez inclusif
- ✅ Soyez constructif
- ❌ Pas de harcèlement
- ❌ Pas de discrimination

## Avant de Commencer

### Prérequis

```bash
# Python 3.10+
python --version

# Git
git --version

# GitHub CLI
gh --version
```

### Installation de l'environnement

```bash
# 1. Cloner le repo
git clone https://github.com/jbcholat/Estimation-immo.git
cd Estimation-immo

# 2. Créer un environnement virtuel
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Pour le développement

# 4. Vérifier l'installation
pytest tests/

# 5. Lancer l'app
streamlit run app.py
```

### Configurer votre fork (optionnel mais recommandé)

```bash
# Forker sur GitHub (cliquer le bouton fork)

# Cloner votre fork
git clone https://github.com/VOTRE_USERNAME/Estimation-immo.git

# Ajouter upstream
git remote add upstream https://github.com/jbcholat/Estimation-immo.git

# Vérifier
git remote -v
```

## Processus de Contribution

### 1. Créer une Issue (si nécessaire)

Avant de coder, discutez de vos idées :

- 🐛 **Bug Report**: Décrivez le bug, étapes pour reproduire, comportement attendu
- ✨ **Feature Request**: Expliquez la fonctionnalité et pourquoi c'est utile
- 📚 **Documentation**: Améliorations documentations proposées
- 💡 **Suggestion**: Autres suggestions

### 2. Créer une Branche

```bash
# Mettre à jour develop
git checkout develop
git pull origin develop

# Créer une branche
git checkout -b feature/mon-feature
# ou
git checkout -b fix/mon-bug
```

### 3. Développer

```bash
# Développer vos changements
# Tester localement
pytest tests/

# Formater le code
black src/
ruff check src/

# Linter
ruff check --fix src/
```

### 4. Tester

```bash
# Tests unitaires
pytest tests/unit/ -v

# Tests intégration
pytest tests/integration/ -v

# Coverage
pytest --cov=src/ tests/

# Tout
pytest tests/ -v
```

### 5. Commit et Push

```bash
# Commit avec message structuré
git add .
git commit -m "feat(module): description courte

Description longue si nécessaire

Closes #123"

# Push
git push origin feature/mon-feature
```

### 6. Créer une Pull Request

```bash
# Créer une PR avec GitHub CLI
gh pr create --title "feat: mon titre" --body "Description détaillée"

# Ou via le web
# 1. Aller sur GitHub
# 2. Cliquer "Compare & pull request"
# 3. Remplir le formulaire
```

### 7. Reviewer Process

- ✅ Code review (au moins 1 approbation)
- ✅ Tests CI/CD passent
- ✅ Pas de conflits de merge
- ✅ Changements demandés résolus

### 8. Merge

Après approbation:

```bash
# Via CLI
gh pr merge <pr-number>

# Ou attendre l'auteur merge
```

## Standards de Code

### Format Python

```python
# Black + Ruff
# Line length: 100

def estimate_property(
    comparables: pd.DataFrame,
    surface: float,
    location: tuple,
) -> dict:
    """Calculate property estimation.

    Args:
        comparables: DataFrame with properties
        surface: Property surface in m²
        location: (lat, lon) tuple

    Returns:
        Dictionary with estimation data

    Raises:
        ValueError: If surface <= 0
    """
    if surface <= 0:
        raise ValueError("Surface must be positive")

    # Implementation
    return {"price": price, "confidence": conf}
```

### Docstrings (Google style)

```python
def my_function(param1: str, param2: int) -> bool:
    """Brief description.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When something is wrong
        TypeError: When type is incorrect

    Example:
        >>> my_function("test", 42)
        True
    """
```

### Type Hints (obligatoire pour les fonctions publiques)

```python
# ✅ BON
def process_data(data: list[dict]) -> pd.DataFrame:
    pass

# ❌ MAUVAIS
def process_data(data):
    pass
```

### Tests

```python
# tests/unit/test_estimation.py
import pytest
from src.estimation_engine import estimate_property

class TestEstimation:
    """Test suite for estimation engine."""

    def test_estimate_positive_surface(self):
        """Test estimation with valid surface."""
        result = estimate_property([...], 100.0)
        assert result["price"] > 0

    def test_estimate_raises_on_negative_surface(self):
        """Test estimation raises on invalid input."""
        with pytest.raises(ValueError):
            estimate_property([...], -50.0)
```

## Commits et PRs

### Messages de Commit

Format [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation
- `style`: Formatage (Black, Ruff)
- `refactor`: Refactorisation
- `test`: Tests
- `chore`: Maintenance

**Exemples:**

```
feat(estimation): ajouter scoring multi-critères

Implémente un scoring plus robuste basé sur:
- Distance pondérée
- Ancienneté
- Localisation

Closes #42
```

```
fix(geocoding): corriger timeout API

Le timeout était trop court pour les adresses longues.
Augmentation de 3s à 5s.

Fixes #38
```

### Pull Request

**Titre:**
```
feat(module): courte description
```

**Body:**
```markdown
## Description
Brief description of changes

## Type of Change
- [x] Bug fix
- [ ] New feature
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing done

## Checklist
- [x] Code follows style guidelines
- [x] No new warnings generated
- [x] Tests added/updated
- [x] Documentation updated

## Screenshots/Logs
If applicable, add screenshots or logs
```

## Aide et Support

### Questions?

- 💬 Créer une **Issue** avec le label `question`
- 📧 Contacter le mainteneur
- 🐦 Twitter/X

### Problèmes?

- 🐛 Créer une **Issue** avec label `bug`
- 📝 Inclure les détails reproduction
- 📸 Screenshots/logs utiles

### Idées?

- 💡 Créer une **Issue** avec label `enhancement`
- 📚 Décrire le use case

## Ressources

- [VERSIONING.md](./VERSIONING.md) - Stratégie de versioning
- [GIT_WORKFLOW.md](./docs/GIT_WORKFLOW.md) - Commandes git
- [CLAUDE.md](./CLAUDE.md) - Instructions pour Claude
- [GitHub API](https://docs.github.com/en/rest)

---

**Merci de votre contribution ! 🎉**

*Pour toute question, créez une issue ou contactez jbcholat*

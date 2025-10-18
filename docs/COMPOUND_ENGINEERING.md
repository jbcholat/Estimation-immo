# Compound Engineering Framework

Guide complet du framework Compound Engineering implémenté pour Analyse Immobilière.

## 📚 Table des matières

1. [Concepts](#concepts)
2. [Architecture](#architecture)
3. [Composants](#composants)
4. [Workflows](#workflows)
5. [Utilisation](#utilisation)
6. [Exemples](#exemples)
7. [Intégration IA](#intégration-ia)

## Concepts

### Qu'est-ce que Compound Engineering ?

Compound Engineering est une approche d'architecture système où **plusieurs composants IA/outils spécialisés sont orchestrés ensemble** pour résoudre des problèmes complexes.

**Principes clés:**

- ✅ **Modularité**: Chaque composant a un rôle spécifique
- ✅ **Orchestration**: Coordination centrale des composants
- ✅ **Collaboration**: Composants travaillent ensemble
- ✅ **Adaptabilité**: Facile d'ajouter/remplacer composants

### Avantages pour Analyse Immobilière

| Avantage | Bénéfice |
|----------|----------|
| **Modularité** | Géocodage, retrieval, scoring = modules indépendants |
| **Réutilisabilité** | Composants utilisés dans plusieurs workflows |
| **Testabilité** | Tester chaque composant isolément |
| **Scalabilité** | Ajouter nouvelles IA facilement |
| **Maintenabilité** | Mise à jour sans affecter le reste |

## Architecture

### Hiérarchie des composants

```
CompoundSystem (Orchestrateur Global)
    ├── Workflow 1: property_estimation
    │   ├── GeocodingComponent
    │   ├── DataRetrieverComponent
    │   ├── ScoringComponent
    │   ├── EstimationComponent
    │   └── FormatterComponent
    │
    ├── Workflow 2: comparable_finder
    │   ├── GeocodingComponent
    │   ├── DataRetrieverComponent
    │   ├── ScoringComponent
    │   └── FormatterComponent
    │
    └── Workflow 3: advanced_analysis
        ├── property_estimation (workflow imbriqué)
        ├── ClaudeAnalyzerComponent
        ├── GrokReasonerComponent
        └── PerplexityResearcherComponent
```

### Flux de données

```
User Input
    ↓
┌─────────────────────────────────────┐
│  WorkflowContext (Contexte partagé) │
│  ├── user_input                     │
│  ├── intermediate_results[]         │
│  └── metadata                       │
└─────────────────────────────────────┘
    ↓
Component 1 (Geocoding)
    ├── Input: WorkflowContext
    ├── Process: Geocode address
    └── Output: ComponentResult
    ↓ (Stocké dans context)
Component 2 (Data Retriever)
    ├── Input: WorkflowContext (avec résultat 1)
    ├── Process: Récupérer données
    └── Output: ComponentResult
    ↓ (Stocké dans context)
... (autres composants) ...
    ↓
Formatage Final
    ↓
Output Final
```

## Composants

### Type de composants

```python
from src.compound_engineering import ComponentType

# Types disponibles:
ComponentType.DATA_PROCESSOR    # Traitement données
ComponentType.ANALYZER          # Analyse
ComponentType.REASONER          # Reasoning IA
ComponentType.RETRIEVER         # Récupération données
ComponentType.SCORER            # Scoring
ComponentType.FORMATTER         # Formatage output
ComponentType.VALIDATOR         # Validation
```

### Composants disponibles

#### 1. GeocodingComponent

**Rôle**: Convertir adresses en coordonnées

```python
from src.compound_components import GeocodingComponent

comp = GeocodingComponent()
# Input: {"address": "10 rue de la Paix, Annecy"}
# Output: {"latitude": 46.2, "longitude": 6.1, "confidence": 0.95}
```

#### 2. DataRetrieverComponent

**Rôle**: Récupérer biens comparables

```python
from src.compound_components import DataRetrieverComponent

comp = DataRetrieverComponent()
# Dépend de: GeocodingComponent
# Input: Coordonnées du geocoding
# Output: DataFrame avec propriétés comparables
```

#### 3. ScoringComponent

**Rôle**: Scorer les propriétés par pertinence

```python
from src.compound_components import ScoringComponent

comp = ScoringComponent()
# Dépend de: DataRetrieverComponent
# Critères: distance, surface, ancienneté
# Output: Propriétés classées par score
```

#### 4. EstimationComponent

**Rôle**: Calculer l'estimation de prix

```python
from src.compound_components import EstimationComponent

comp = EstimationComponent()
# Dépend de: ScoringComponent
# Méthode: Médiane + écart-type des prix/m²
# Output: Prix estimé + intervalles de confiance
```

#### 5. FormatterComponent

**Rôle**: Formater résultats finaux

```python
from src.compound_components import FormatterComponent

comp = FormatterComponent()
# Dépend de: EstimationComponent
# Output: Structure complète et présentable
```

### Créer un composant personnalisé

```python
from src.compound_engineering import Component, ComponentType, ComponentResult, ComponentStatus, WorkflowContext

class MyCustomComponent(Component):
    def __init__(self):
        super().__init__(
            name="my_component",
            component_type=ComponentType.ANALYZER,
            description="My custom component"
        )
        self.add_dependency("geocoding")  # Optionnel

    async def execute(self, context: WorkflowContext) -> ComponentResult:
        start_time = time.time()

        try:
            # Récupérer résultat du composant dépendant
            geo_result = context.get_data("geocoding")

            # Votre logique ici
            result_data = {"my_key": "my_value"}

            return ComponentResult(
                component_name=self.name,
                status=ComponentStatus.SUCCESS,
                data=result_data,
                execution_time_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return ComponentResult(
                component_name=self.name,
                status=ComponentStatus.FAILED,
                error=str(e)
            )
```

## Workflows

### Workflow prédéfinis

#### 1. property_estimation

Estimation complète de propriété:

```
Geocoding
    ↓
Data Retriever
    ↓
Scoring
    ↓
Estimation
    ↓
Formatter
```

#### 2. comparable_finder

Recherche de comparables seulement:

```
Geocoding
    ↓
Data Retriever
    ↓
Scoring
    ↓
Formatter
```

#### 3. advanced_analysis

Analyse complète avec IA:

```
property_estimation workflow
    ↓
Claude Analyzer
    ↓
Grok Reasoner
    ↓
Perplexity Researcher
```

### Utiliser un workflow

```python
from src.compound_engineering import CompoundSystem
from src.compound_workflows import WorkflowFactory

# Créer système
system = CompoundSystem(name="MyAnalyzer")

# Enregistrer workflow
workflow = WorkflowFactory.create_property_estimation_workflow()
system.register_workflow(workflow)

# Exécuter
context = await system.execute_workflow(
    workflow_name="property_estimation",
    user_input={
        "address": "10 rue de la Paix, Annecy",
        "surface": 100.0,
        "radius_km": 5
    }
)

# Récupérer résultats
formatter_result = context.get_result("formatter")
if formatter_result.is_success():
    output = formatter_result.data
    print(f"Estimation: €{output['estimation']['estimated_price']:,.0f}")
```

### Créer un workflow personnalisé

```python
from src.compound_engineering import Workflow
from src.compound_components import (
    GeocodingComponent,
    DataRetrieverComponent,
    ScoringComponent
)

# Créer workflow
workflow = Workflow(
    name="my_workflow",
    description="Mon workflow personnalisé"
)

# Ajouter composants
workflow.add_component(GeocodingComponent())
workflow.add_component(DataRetrieverComponent())
workflow.add_component(ScoringComponent())

# Utiliser
context = await workflow.execute(user_input)
```

## Utilisation

### Installation et setup

```bash
# Assurez-vous que les modules sont importables
import sys
sys.path.append('/path/to/analyse_immobiliere')

from src.compound_engineering import CompoundSystem
from src.compound_workflows import WorkflowFactory
```

### Exécution basique

```python
import asyncio
from src.compound_engineering import CompoundSystem
from src.compound_workflows import WorkflowFactory

async def main():
    # Créer système
    system = CompoundSystem()

    # Créer et enregistrer workflow
    workflow = WorkflowFactory.create_property_estimation_workflow()
    system.register_workflow(workflow)

    # Exécuter
    context = await system.execute_workflow(
        workflow_name="property_estimation",
        user_input={
            "address": "Annecy, France",
            "surface": 100.0,
            "radius_km": 5
        }
    )

    # Accéder aux résultats
    for comp_name, result in context.intermediate_results.items():
        print(f"{comp_name}: {result.status.value}")
        if result.is_success():
            print(f"  Data: {result.data}")

asyncio.run(main())
```

### Accéder aux résultats

```python
# Résultat d'un composant spécifique
result = context.get_result("geocoding")

# Données d'un composant
data = context.get_data("estimation")

# Tous les résultats
for component_name, result in context.intermediate_results.items():
    print(f"{component_name}: {result.status.value}")
    if result.is_success():
        print(f"  Execution time: {result.execution_time_ms}ms")
        print(f"  Data: {result.data}")
    else:
        print(f"  Error: {result.error}")
```

### Gestion des erreurs

```python
context = await system.execute_workflow(...)

# Vérifier succès global
all_success = all(
    r.is_success()
    for r in context.intermediate_results.values()
)

if not all_success:
    # Identifier composants échoués
    failed = [
        (name, r.error)
        for name, r in context.intermediate_results.items()
        if r.is_error()
    ]
    print(f"Failed components: {failed}")
```

## Exemples

### Exemple 1: Estimation simple

```python
import asyncio
from src.compound_engineering import CompoundSystem
from src.compound_workflows import WorkflowFactory

async def estimate_property():
    system = CompoundSystem("RealEstateAnalyzer")
    workflow = WorkflowFactory.create_property_estimation_workflow()
    system.register_workflow(workflow)

    context = await system.execute_workflow(
        workflow_name="property_estimation",
        user_input={
            "address": "42 rue de la République, Annecy",
            "surface": 85.0,
            "radius_km": 3
        }
    )

    result = context.get_result("formatter")
    est = result.data["estimation"]

    print(f"📍 Adresse: {result.data['address']}")
    print(f"💰 Prix estimé: €{est['estimated_price']:,.0f}")
    print(f"📊 Intervalle: €{est['low_estimate']:,.0f} - €{est['high_estimate']:,.0f}")
    print(f"✅ Confiance: {est['confidence']*100:.0f}%")

asyncio.run(estimate_property())
```

### Exemple 2: Workflow personnalisé

```python
from src.compound_engineering import Workflow
from src.compound_components import GeocodingComponent, DataRetrieverComponent

async def find_nearby_properties():
    # Créer workflow minimal
    workflow = Workflow(
        name="quick_search",
        description="Recherche rapide de propriétés"
    )

    workflow.add_component(GeocodingComponent())
    workflow.add_component(DataRetrieverComponent())

    # Exécuter
    context = await workflow.execute({
        "address": "Thonon-les-Bains",
        "radius_km": 10
    })

    # Afficher résultats
    retriever_data = context.get_data("data_retriever")
    properties = retriever_data["comparable_properties"]

    for prop in properties[:5]:
        print(f"🏠 {prop['address']}: €{prop['price']:,}")

asyncio.run(find_nearby_properties())
```

## Intégration IA

### Composants AI disponibles

#### ClaudeAnalyzerComponent

Analyse intelligente avec Claude:

```python
from src.compound_workflows import AIComponentAdapter

comp = AIComponentAdapter.create_claude_analyzer_component()
# Analyses intelligentes, insights market, recommandations
```

#### GrokReasonerComponent

Reasoning avancé avec Grok:

```python
comp = AIComponentAdapter.create_grok_reasoner_component()
# Analyse profonde des marchés, justification prix, facteurs risque
```

#### PerplexityResearcherComponent

Recherche de données avec Perplexity:

```python
comp = AIComponentAdapter.create_perplexity_researcher_component()
# Tendances marché, facteurs économiques, infos régionales
```

### Utiliser les composants AI

```python
from src.compound_workflows import create_advanced_estimation_workflow

# Créer workflow avec IA
workflow = create_advanced_estimation_workflow()

# Utiliser comme les autres workflows
context = await workflow.execute(user_input)

# Accéder aux résultats IA
claude_result = context.get_data("claude_analyzer")
grok_result = context.get_data("grok_reasoner")
perplexity_result = context.get_data("perplexity_researcher")
```

### Intégrer vos propres composants AI

```python
from src.compound_engineering import Component, ComponentType
from src.compound_workflows import AIComponentAdapter

class CustomAIComponent(Component):
    def __init__(self):
        super().__init__(
            name="custom_ai",
            component_type=ComponentType.ANALYZER,
            description="Custom AI analysis"
        )

    async def execute(self, context):
        # Votre logique d'appel à l'AI ici
        # Utiliser les MCPs: Claude, Grok, Perplexity
        pass

# Ajouter à un workflow
workflow.add_component(CustomAIComponent())
```

---

## Performance

### Benchmarks typiques

| Component | Temps (ms) | Observations |
|-----------|-----------|--------------|
| Geocoding | 50-100 | Appel API externe |
| Data Retriever | 200-500 | Requête base de données |
| Scoring | 10-20 | Calculs locaux |
| Estimation | 5-10 | Statistiques simples |
| Formatter | 2-5 | Formatage mémoire |
| **Total** | **300-650** | Dépend des données |

### Optimisations

- **Cache**: Cacher résultats de geocoding
- **Async**: Opérations asynchrones par défaut
- **Batch**: Traiter plusieurs propriétés ensemble
- **Parallel**: Exécuter composants indépendants en parallèle

---

**Dernière mise à jour**: 2025-10-18

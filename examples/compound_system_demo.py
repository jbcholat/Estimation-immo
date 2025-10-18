"""Demo of the Compound Engineering System.

This example demonstrates how to use the compound system
for property estimation with orchestrated components.
"""

import asyncio
import logging
from typing import Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def demo_basic_estimation() -> None:
    """Run basic property estimation workflow."""
    from src.compound_engineering import CompoundSystem
    from src.compound_workflows import WorkflowFactory

    logger.info("=== Basic Property Estimation Demo ===\n")

    # Create compound system
    system = CompoundSystem(name="RealEstateAnalyzer")

    # Register workflow
    workflow = WorkflowFactory.create_property_estimation_workflow()
    system.register_workflow(workflow)

    # Prepare input
    user_input = {
        "address": "10 rue de la Paix, Annecy, France",
        "surface": 100.0,
        "radius_km": 5,
    }

    # Execute workflow
    context = await system.execute_workflow(
        workflow_name="property_estimation",
        user_input=user_input,
    )

    # Display results
    print("\n" + "=" * 60)
    print("PROPERTY ESTIMATION RESULTS")
    print("=" * 60)

    formatter_result = context.get_result("formatter")
    if formatter_result and formatter_result.is_success():
        output = formatter_result.data

        print(f"\nAddress: {output['address']}")
        print(f"Status: {output['status']}")

        est = output["estimation"]
        print(f"\n📊 Price Estimation:")
        print(f"  Estimated Price: €{est['estimated_price']:,.0f}")
        print(
            f"  Range: €{est['low_estimate']:,.0f} - "
            f"€{est['high_estimate']:,.0f}"
        )
        print(f"  Price per m²: €{est['price_per_m2']:,.0f}")
        print(f"  Confidence: {est['confidence'] * 100:.0f}%")
        print(f"  Comparables: {est['comparables_count']}")

        print(
            f"\n⏱️ Performance: {output['total_execution_time_ms']:.0f}ms "
            f"({output['components_executed']} components)"
        )

    # Display component execution details
    print("\n" + "-" * 60)
    print("Component Execution Details:")
    print("-" * 60)

    for comp_name, result in context.intermediate_results.items():
        status_icon = "✅" if result.is_success() else "❌"
        print(
            f"{status_icon} {comp_name}: "
            f"{result.execution_time_ms:.1f}ms - "
            f"{result.status.value}"
        )

    # System status
    print("\n" + "-" * 60)
    status = system.get_system_status()
    print(f"System Status: {status}")


async def demo_advanced_estimation() -> None:
    """Run advanced estimation with AI components."""
    from src.compound_engineering import CompoundSystem
    from src.compound_workflows import create_advanced_estimation_workflow

    logger.info("\n=== Advanced Estimation with AI Demo ===\n")

    system = CompoundSystem(name="AdvancedAnalyzer")

    # Register advanced workflow
    workflow = create_advanced_estimation_workflow()
    system.register_workflow(workflow)

    user_input = {
        "address": "15 avenue des Alpes, Thonon-les-Bains, France",
        "surface": 120.0,
        "radius_km": 8,
    }

    context = await system.execute_workflow(
        workflow_name=workflow.name,
        user_input=user_input,
    )

    print("\n" + "=" * 60)
    print("ADVANCED ANALYSIS RESULTS")
    print("=" * 60)

    # Show all results
    for comp_name, result in context.intermediate_results.items():
        print(f"\n{comp_name.upper()}:")
        print(f"  Status: {result.status.value}")
        print(f"  Time: {result.execution_time_ms:.1f}ms")

        if result.is_success() and result.data:
            if comp_name == "formatter":
                output = result.data
                est = output["estimation"]
                print(
                    f"  Estimated: €{est['estimated_price']:,.0f} "
                    f"(±€{(est['high_estimate'] - est['low_estimate']) / 2:,.0f})"
                )
            else:
                # Show first few keys of data
                for key in list(result.data.keys())[:3]:
                    print(f"    - {key}")


async def demo_workflow_composition() -> None:
    """Demonstrate workflow composition and custom workflows."""
    from src.compound_engineering import CompoundSystem, Workflow

    logger.info("\n=== Workflow Composition Demo ===\n")

    system = CompoundSystem(name="ComposingSystem")

    # Create custom workflow
    from src.compound_components import (
        GeocodingComponent,
        DataRetrieverComponent,
    )

    custom_workflow = Workflow(
        name="quick_search",
        description="Quick property search (geocoding + retrieval only)",
    )

    custom_workflow.add_component(GeocodingComponent())
    custom_workflow.add_component(DataRetrieverComponent())

    system.register_workflow(custom_workflow)

    user_input = {
        "address": "Evian-les-Bains, France",
        "radius_km": 3,
    }

    context = await system.execute_workflow(
        workflow_name="quick_search",
        user_input=user_input,
    )

    print("\n" + "=" * 60)
    print("QUICK SEARCH RESULTS")
    print("=" * 60)

    retriever_result = context.get_result("data_retriever")
    if retriever_result and retriever_result.is_success():
        data = retriever_result.data
        print(
            f"\nFound {data['count']} comparable properties "
            f"within {retriever_result.metadata.get('radius_km')}km"
        )

        properties = data["comparable_properties"]
        print("\nTop properties:")
        for i, prop in enumerate(properties[:3], 1):
            print(
                f"  {i}. {prop['address']}: "
                f"€{prop['price']:,} ({prop['distance_km']}km away)"
            )


async def main() -> None:
    """Run all demos."""
    try:
        await demo_basic_estimation()
        await demo_workflow_composition()
        await demo_advanced_estimation()

        print("\n" + "=" * 60)
        print("✅ All demos completed successfully!")
        print("=" * 60)

    except Exception as e:
        logger.error(f"Demo failed: {str(e)}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())

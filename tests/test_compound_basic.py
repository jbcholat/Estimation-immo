"""Basic tests for Compound Engineering (without pytest).

Run with: python tests/test_compound_basic.py
"""

import asyncio
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_component_creation():
    """Test creating components."""
    from src.compound_engineering import (
        Component,
        ComponentType,
        ComponentStatus,
        ComponentResult,
    )

    class TestComponent(Component):
        async def execute(self, context):
            return ComponentResult(
                component_name=self.name,
                status=ComponentStatus.SUCCESS,
            )

    comp = TestComponent("test", ComponentType.ANALYZER)

    assert comp.name == "test"
    assert comp.component_type == ComponentType.ANALYZER
    print("✅ Component creation test passed")


def test_workflow_creation():
    """Test creating workflows."""
    from src.compound_engineering import Workflow

    workflow = Workflow("test_workflow", "Test workflow")

    assert workflow.name == "test_workflow"
    assert len(workflow.components) == 0
    print("✅ Workflow creation test passed")


def test_dependency_resolution():
    """Test dependency resolution."""
    from src.compound_engineering import (
        Workflow,
        Component,
        ComponentType,
        ComponentStatus,
        ComponentResult,
    )

    class TestComponent(Component):
        async def execute(self, context):
            return ComponentResult(
                component_name=self.name,
                status=ComponentStatus.SUCCESS,
            )

    workflow = Workflow("test")

    comp1 = TestComponent("comp1", ComponentType.DATA_PROCESSOR)
    comp2 = TestComponent("comp2", ComponentType.ANALYZER)
    comp2.add_dependency("comp1")
    comp3 = TestComponent("comp3", ComponentType.FORMATTER)
    comp3.add_dependency("comp2")

    workflow.add_component(comp1)
    workflow.add_component(comp2)
    workflow.add_component(comp3)

    order = workflow.resolve_dependencies()

    assert order == ["comp1", "comp2", "comp3"]
    print("✅ Dependency resolution test passed")


async def test_workflow_execution():
    """Test executing a workflow."""
    from src.compound_engineering import (
        Workflow,
        Component,
        ComponentType,
        ComponentStatus,
        ComponentResult,
    )

    class TestComponent(Component):
        async def execute(self, context):
            return ComponentResult(
                component_name=self.name,
                status=ComponentStatus.SUCCESS,
                data={"result": f"output_from_{self.name}"},
            )

    workflow = Workflow("test")

    comp1 = TestComponent("comp1", ComponentType.DATA_PROCESSOR)
    comp2 = TestComponent("comp2", ComponentType.ANALYZER)
    comp2.add_dependency("comp1")

    workflow.add_component(comp1)
    workflow.add_component(comp2)

    context = await workflow.execute(user_input={"test": "input"})

    result1 = context.get_result("comp1")
    result2 = context.get_result("comp2")

    assert result1.is_success()
    assert result2.is_success()
    assert result1.data["result"] == "output_from_comp1"

    print("✅ Workflow execution test passed")


def test_compound_system():
    """Test CompoundSystem."""
    from src.compound_engineering import CompoundSystem, Workflow

    system = CompoundSystem("test_system")
    workflow = Workflow("wf1")

    system.register_workflow(workflow)

    assert system.get_workflow("wf1") is not None
    status = system.get_system_status()
    assert status["name"] == "test_system"

    print("✅ CompoundSystem test passed")


async def test_specialized_components():
    """Test specialized components."""
    from src.compound_components import (
        GeocodingComponent,
        DataRetrieverComponent,
    )
    from src.compound_engineering import Workflow

    workflow = Workflow("test")
    workflow.add_component(GeocodingComponent())
    workflow.add_component(DataRetrieverComponent())

    context = await workflow.execute(
        user_input={
            "address": "Annecy, France",
            "radius_km": 5,
        }
    )

    geo_result = context.get_result("geocoding")
    retriever_result = context.get_result("data_retriever")

    assert geo_result.is_success()
    assert retriever_result.is_success()
    assert "latitude" in geo_result.data
    assert "comparable_properties" in retriever_result.data

    print("✅ Specialized components test passed")


async def test_property_estimation_workflow():
    """Test full property estimation workflow."""
    from src.compound_workflows import WorkflowFactory
    from src.compound_engineering import CompoundSystem

    system = CompoundSystem("test_analyzer")
    workflow = WorkflowFactory.create_property_estimation_workflow()
    system.register_workflow(workflow)

    context = await system.execute_workflow(
        workflow_name="property_estimation",
        user_input={
            "address": "42 rue de la Paix, Annecy",
            "surface": 100.0,
            "radius_km": 5,
        },
    )

    # Check all components executed
    assert len(context.intermediate_results) == 5

    # Check final result
    formatter_result = context.get_result("formatter")
    assert formatter_result.is_success()

    output = formatter_result.data
    assert output["status"] == "success"
    assert "estimation" in output
    assert "estimated_price" in output["estimation"]

    est = output["estimation"]
    print(f"\n  Estimated Price: €{est['estimated_price']:,.0f}")
    print(
        f"  Range: €{est['low_estimate']:,.0f} - "
        f"€{est['high_estimate']:,.0f}"
    )
    print(f"  Confidence: {est['confidence']*100:.0f}%")

    print("✅ Property estimation workflow test passed")


async def run_async_tests():
    """Run all async tests."""
    print("\n" + "=" * 60)
    print("Running Async Tests")
    print("=" * 60 + "\n")

    try:
        await test_workflow_execution()
        await test_specialized_components()
        await test_property_estimation_workflow()
    except Exception as e:
        logger.error(f"Async test failed: {str(e)}", exc_info=True)
        sys.exit(1)


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Compound Engineering Framework Tests")
    print("=" * 60 + "\n")

    try:
        # Sync tests
        print("Running Sync Tests")
        print("-" * 60 + "\n")

        test_component_creation()
        test_workflow_creation()
        test_dependency_resolution()
        test_compound_system()

        # Async tests
        asyncio.run(run_async_tests())

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60 + "\n")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

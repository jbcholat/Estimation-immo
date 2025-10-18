"""Tests for the Compound Engineering Framework.

Tests core functionality:
- Component execution
- Workflow orchestration
- Dependency resolution
- Error handling
"""

import asyncio
import pytest

from src.compound_engineering import (
    Component,
    ComponentResult,
    ComponentStatus,
    ComponentType,
    CompoundSystem,
    Workflow,
    WorkflowContext,
)


class TestComponent:
    """Test Component base class."""

    @pytest.mark.asyncio
    async def test_component_creation(self):
        """Test creating a component."""

        class DummyComponent(Component):
            async def execute(self, context):
                return ComponentResult(
                    component_name=self.name,
                    status=ComponentStatus.SUCCESS,
                )

        comp = DummyComponent(
            name="test_comp",
            component_type=ComponentType.ANALYZER,
        )

        assert comp.name == "test_comp"
        assert comp.component_type == ComponentType.ANALYZER
        assert comp.enabled is True
        assert comp.dependencies == []

    def test_component_dependencies(self):
        """Test adding dependencies to component."""

        class DummyComponent(Component):
            async def execute(self, context):
                pass

        comp = DummyComponent("test", ComponentType.ANALYZER)

        comp.add_dependency("dep1")
        comp.add_dependency("dep2")

        assert "dep1" in comp.dependencies
        assert "dep2" in comp.dependencies
        assert len(comp.dependencies) == 2

    @pytest.mark.asyncio
    async def test_component_result(self):
        """Test ComponentResult creation."""
        result = ComponentResult(
            component_name="test",
            status=ComponentStatus.SUCCESS,
            data={"key": "value"},
        )

        assert result.component_name == "test"
        assert result.is_success()
        assert not result.is_error()

    @pytest.mark.asyncio
    async def test_component_result_failure(self):
        """Test ComponentResult failure."""
        result = ComponentResult(
            component_name="test",
            status=ComponentStatus.FAILED,
            error="Something went wrong",
        )

        assert not result.is_success()
        assert result.is_error()
        assert result.error == "Something went wrong"


class TestWorkflow:
    """Test Workflow orchestration."""

    @pytest.mark.asyncio
    async def test_workflow_creation(self):
        """Test creating a workflow."""
        workflow = Workflow(name="test_workflow")

        assert workflow.name == "test_workflow"
        assert len(workflow.components) == 0

    @pytest.mark.asyncio
    async def test_add_component_to_workflow(self):
        """Test adding components to workflow."""

        class DummyComponent(Component):
            async def execute(self, context):
                return ComponentResult(
                    component_name=self.name,
                    status=ComponentStatus.SUCCESS,
                )

        workflow = Workflow("test")
        comp1 = DummyComponent("comp1", ComponentType.ANALYZER)
        comp2 = DummyComponent("comp2", ComponentType.SCORER)

        workflow.add_component(comp1)
        workflow.add_component(comp2)

        assert len(workflow.components) == 2
        assert "comp1" in workflow.components
        assert "comp2" in workflow.components

    @pytest.mark.asyncio
    async def test_dependency_resolution(self):
        """Test resolving component dependencies."""

        class DummyComponent(Component):
            async def execute(self, context):
                return ComponentResult(
                    component_name=self.name,
                    status=ComponentStatus.SUCCESS,
                )

        workflow = Workflow("test")

        comp1 = DummyComponent("comp1", ComponentType.DATA_PROCESSOR)
        comp2 = DummyComponent("comp2", ComponentType.ANALYZER)
        comp2.add_dependency("comp1")
        comp3 = DummyComponent("comp3", ComponentType.FORMATTER)
        comp3.add_dependency("comp2")

        workflow.add_component(comp1)
        workflow.add_component(comp2)
        workflow.add_component(comp3)

        order = workflow.resolve_dependencies()

        assert order == ["comp1", "comp2", "comp3"]

    @pytest.mark.asyncio
    async def test_circular_dependency_detection(self):
        """Test detection of circular dependencies."""

        class DummyComponent(Component):
            async def execute(self, context):
                return ComponentResult(
                    component_name=self.name,
                    status=ComponentStatus.SUCCESS,
                )

        workflow = Workflow("test")

        comp1 = DummyComponent("comp1", ComponentType.ANALYZER)
        comp2 = DummyComponent("comp2", ComponentType.ANALYZER)

        comp1.add_dependency("comp2")
        comp2.add_dependency("comp1")

        workflow.add_component(comp1)
        workflow.add_component(comp2)

        with pytest.raises(ValueError, match="Circular dependency"):
            workflow.resolve_dependencies()

    @pytest.mark.asyncio
    async def test_workflow_execution(self):
        """Test executing a workflow."""

        class TestComponent1(Component):
            async def execute(self, context):
                return ComponentResult(
                    component_name=self.name,
                    status=ComponentStatus.SUCCESS,
                    data={"result": "comp1"},
                )

        class TestComponent2(Component):
            async def execute(self, context):
                data1 = context.get_data("comp1")
                return ComponentResult(
                    component_name=self.name,
                    status=ComponentStatus.SUCCESS,
                    data={"result": "comp2", "prev": data1},
                )

        workflow = Workflow("test")
        comp1 = TestComponent1("comp1", ComponentType.DATA_PROCESSOR)
        comp2 = TestComponent2("comp2", ComponentType.ANALYZER)
        comp2.add_dependency("comp1")

        workflow.add_component(comp1)
        workflow.add_component(comp2)

        context = await workflow.execute(
            user_input={"test": "input"}
        )

        assert "comp1" in context.intermediate_results
        assert "comp2" in context.intermediate_results

        result1 = context.get_result("comp1")
        result2 = context.get_result("comp2")

        assert result1.is_success()
        assert result2.is_success()
        assert result1.data["result"] == "comp1"

    @pytest.mark.asyncio
    async def test_workflow_execution_with_failure(self):
        """Test workflow handling component failure."""

        class FailingComponent(Component):
            async def execute(self, context):
                return ComponentResult(
                    component_name=self.name,
                    status=ComponentStatus.FAILED,
                    error="Component failed",
                )

        class SkippedComponent(Component):
            async def execute(self, context):
                return ComponentResult(
                    component_name=self.name,
                    status=ComponentStatus.SUCCESS,
                )

        workflow = Workflow("test")
        comp1 = FailingComponent("comp1", ComponentType.ANALYZER)
        comp2 = SkippedComponent("comp2", ComponentType.FORMATTER)
        comp2.add_dependency("comp1")

        workflow.add_component(comp1)
        workflow.add_component(comp2)

        context = await workflow.execute({})

        result1 = context.get_result("comp1")
        result2 = context.get_result("comp2")

        assert result1.is_error()
        assert result2.status == ComponentStatus.SKIPPED


class TestCompoundSystem:
    """Test CompoundSystem orchestration."""

    def test_system_creation(self):
        """Test creating a compound system."""
        system = CompoundSystem("test_system")

        assert system.name == "test_system"
        assert len(system.workflows) == 0

    def test_register_workflow(self):
        """Test registering a workflow."""
        system = CompoundSystem("test")
        workflow = Workflow("wf1")

        system.register_workflow(workflow)

        assert "wf1" in system.workflows
        assert system.get_workflow("wf1") == workflow

    @pytest.mark.asyncio
    async def test_execute_workflow(self):
        """Test executing a workflow through system."""

        class TestComponent(Component):
            async def execute(self, context):
                return ComponentResult(
                    component_name=self.name,
                    status=ComponentStatus.SUCCESS,
                    data={"result": "success"},
                )

        system = CompoundSystem("test")
        workflow = Workflow("test_wf")
        comp = TestComponent("comp1", ComponentType.ANALYZER)
        workflow.add_component(comp)
        system.register_workflow(workflow)

        context = await system.execute_workflow(
            workflow_name="test_wf",
            user_input={"input": "data"},
        )

        assert context.user_input == {"input": "data"}
        assert "comp1" in context.intermediate_results

    def test_system_status(self):
        """Test getting system status."""
        system = CompoundSystem("test")

        status = system.get_system_status()

        assert status["name"] == "test"
        assert status["workflows"] == 0
        assert "success_rate" in status


class TestWorkflowContext:
    """Test WorkflowContext."""

    def test_context_creation(self):
        """Test creating a context."""
        context = WorkflowContext(
            workflow_id="wf1",
            user_input={"key": "value"},
        )

        assert context.workflow_id == "wf1"
        assert context.user_input == {"key": "value"}
        assert len(context.intermediate_results) == 0

    def test_add_result(self):
        """Test adding results to context."""
        context = WorkflowContext("wf1", {})

        result = ComponentResult(
            component_name="comp1",
            status=ComponentStatus.SUCCESS,
            data={"test": "data"},
        )

        context.add_result(result)

        assert "comp1" in context.intermediate_results
        assert context.get_result("comp1") == result

    def test_get_data(self):
        """Test getting data from context."""
        context = WorkflowContext("wf1", {})

        result = ComponentResult(
            component_name="comp1",
            status=ComponentStatus.SUCCESS,
            data={"test": "data"},
        )

        context.add_result(result)

        data = context.get_data("comp1")
        assert data == {"test": "data"}

        assert context.get_data("nonexistent") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

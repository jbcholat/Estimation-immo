"""Compound Engineering Framework for Analyse Immobilière.

This module implements a modular, orchestrated AI system where multiple
specialized components work together to solve complex real estate analysis tasks.

Architecture:
    - CompoundSystem: Central orchestrator
    - Component: Base interface for all specialized components
    - Workflow: Coordinated sequence of components
    - Pipeline: End-to-end data processing
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar

import pandas as pd

logger = logging.getLogger(__name__)


class ComponentType(Enum):
    """Types of components in the compound system."""

    DATA_PROCESSOR = "data_processor"
    ANALYZER = "analyzer"
    REASONER = "reasoner"
    RETRIEVER = "retriever"
    SCORER = "scorer"
    FORMATTER = "formatter"
    VALIDATOR = "validator"


class ComponentStatus(Enum):
    """Status of a component during execution."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ComponentResult:
    """Result from a component execution."""

    component_name: str
    status: ComponentStatus
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0

    def is_success(self) -> bool:
        """Check if component executed successfully."""
        return self.status == ComponentStatus.SUCCESS

    def is_error(self) -> bool:
        """Check if component failed."""
        return self.status == ComponentStatus.FAILED


@dataclass
class WorkflowContext:
    """Context shared across all components in a workflow."""

    workflow_id: str
    user_input: Dict[str, Any]
    intermediate_results: Dict[str, ComponentResult] = field(
        default_factory=dict
    )
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_result(self, component_name: str) -> Optional[ComponentResult]:
        """Get result from a specific component."""
        return self.intermediate_results.get(component_name)

    def get_data(self, component_name: str) -> Optional[Dict[str, Any]]:
        """Get data from a specific component result."""
        result = self.get_result(component_name)
        return result.data if result else None

    def add_result(self, result: ComponentResult) -> None:
        """Store component result in context."""
        self.intermediate_results[result.component_name] = result


class Component(ABC):
    """Base interface for all compound system components.

    Each component has a specific role and implements a standardized
    execute method that processes input and produces output.
    """

    def __init__(
        self,
        name: str,
        component_type: ComponentType,
        description: str = "",
    ):
        """Initialize component.

        Args:
            name: Unique identifier for this component
            component_type: Type of component
            description: Human-readable description
        """
        self.name = name
        self.component_type = component_type
        self.description = description
        self.enabled = True
        self.dependencies: List[str] = []

    @abstractmethod
    async def execute(
        self, context: WorkflowContext
    ) -> ComponentResult:
        """Execute component logic.

        Args:
            context: Workflow context with user input and previous results

        Returns:
            ComponentResult with status and output data
        """
        pass

    def add_dependency(self, component_name: str) -> "Component":
        """Add a dependency on another component.

        Args:
            component_name: Name of the component this depends on

        Returns:
            Self for chaining
        """
        self.dependencies.append(component_name)
        return self

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} name={self.name} "
            f"type={self.component_type.value}>"
        )


class Workflow:
    """Orchestrates a sequence of components.

    Manages component execution order, dependency resolution,
    and error handling.
    """

    def __init__(self, name: str, description: str = ""):
        """Initialize workflow.

        Args:
            name: Unique workflow identifier
            description: Human-readable description
        """
        self.name = name
        self.description = description
        self.components: Dict[str, Component] = {}
        self.execution_order: List[str] = []

    def add_component(self, component: Component) -> "Workflow":
        """Add a component to the workflow.

        Args:
            component: Component to add

        Returns:
            Self for chaining
        """
        self.components[component.name] = component
        logger.debug(f"Added component: {component.name}")
        return self

    def resolve_dependencies(self) -> List[str]:
        """Resolve component execution order based on dependencies.

        Returns:
            List of component names in execution order

        Raises:
            ValueError: If circular dependency detected
        """
        resolved = []
        visited = set()
        visiting = set()

        def visit(component_name: str) -> None:
            if component_name in visited:
                return
            if component_name in visiting:
                raise ValueError(
                    f"Circular dependency detected: {component_name}"
                )

            visiting.add(component_name)
            component = self.components.get(component_name)

            if component:
                for dep in component.dependencies:
                    if dep not in self.components:
                        raise ValueError(
                            f"Dependency {dep} not found for "
                            f"{component_name}"
                        )
                    visit(dep)

            visiting.remove(component_name)
            visited.add(component_name)
            resolved.append(component_name)

        for component_name in self.components:
            visit(component_name)

        self.execution_order = resolved
        return resolved

    async def execute(
        self, user_input: Dict[str, Any], workflow_id: str = ""
    ) -> WorkflowContext:
        """Execute workflow with given input.

        Args:
            user_input: Input data for the workflow
            workflow_id: Unique identifier for this execution

        Returns:
            WorkflowContext with all component results

        Raises:
            ValueError: If dependency resolution fails
        """
        if not workflow_id:
            import uuid

            workflow_id = str(uuid.uuid4())

        context = WorkflowContext(
            workflow_id=workflow_id, user_input=user_input
        )

        # Resolve execution order
        try:
            self.resolve_dependencies()
        except ValueError as e:
            logger.error(f"Dependency resolution failed: {e}")
            raise

        logger.info(
            f"Executing workflow '{self.name}' "
            f"with {len(self.execution_order)} components"
        )

        # Execute components in order
        for component_name in self.execution_order:
            component = self.components[component_name]

            if not component.enabled:
                logger.debug(f"Skipping disabled component: {component_name}")
                result = ComponentResult(
                    component_name=component_name,
                    status=ComponentStatus.SKIPPED,
                )
                context.add_result(result)
                continue

            # Check dependencies success
            deps_failed = [
                dep
                for dep in component.dependencies
                if not context.get_result(dep).is_success()
            ]
            if deps_failed:
                logger.warning(
                    f"Skipping {component_name} due to failed dependencies: "
                    f"{deps_failed}"
                )
                result = ComponentResult(
                    component_name=component_name,
                    status=ComponentStatus.SKIPPED,
                    error="Dependency failed",
                )
                context.add_result(result)
                continue

            # Execute component
            logger.debug(f"Executing component: {component_name}")
            try:
                result = await component.execute(context)
                context.add_result(result)

                if result.is_success():
                    logger.debug(
                        f"Component {component_name} completed in "
                        f"{result.execution_time_ms:.2f}ms"
                    )
                else:
                    logger.warning(
                        f"Component {component_name} failed: {result.error}"
                    )

            except Exception as e:
                logger.error(
                    f"Component {component_name} crashed: {str(e)}"
                )
                result = ComponentResult(
                    component_name=component_name,
                    status=ComponentStatus.FAILED,
                    error=str(e),
                )
                context.add_result(result)

        return context

    def __repr__(self) -> str:
        return (
            f"<Workflow name={self.name} "
            f"components={len(self.components)}>"
        )


class CompoundSystem:
    """Central orchestrator for the compound engineering system.

    Manages multiple workflows, component registration, and
    end-to-end pipeline execution.
    """

    def __init__(self, name: str = "CompoundSystem"):
        """Initialize compound system.

        Args:
            name: Name of the system
        """
        self.name = name
        self.workflows: Dict[str, Workflow] = {}
        self.global_components: Dict[str, Component] = {}
        self.execution_history: List[Dict[str, Any]] = []

    def register_component(self, component: Component) -> "CompoundSystem":
        """Register a global component.

        Args:
            component: Component to register globally

        Returns:
            Self for chaining
        """
        self.global_components[component.name] = component
        logger.debug(f"Registered global component: {component.name}")
        return self

    def register_workflow(self, workflow: Workflow) -> "CompoundSystem":
        """Register a workflow.

        Args:
            workflow: Workflow to register

        Returns:
            Self for chaining
        """
        self.workflows[workflow.name] = workflow
        logger.debug(f"Registered workflow: {workflow.name}")
        return self

    def get_workflow(self, name: str) -> Optional[Workflow]:
        """Get a registered workflow by name.

        Args:
            name: Workflow name

        Returns:
            Workflow if found, None otherwise
        """
        return self.workflows.get(name)

    async def execute_workflow(
        self,
        workflow_name: str,
        user_input: Dict[str, Any],
        workflow_id: str = "",
    ) -> WorkflowContext:
        """Execute a registered workflow.

        Args:
            workflow_name: Name of workflow to execute
            user_input: Input data
            workflow_id: Unique execution ID

        Returns:
            WorkflowContext with results

        Raises:
            ValueError: If workflow not found
        """
        workflow = self.get_workflow(workflow_name)
        if not workflow:
            raise ValueError(f"Workflow '{workflow_name}' not found")

        logger.info(f"Executing workflow: {workflow_name}")
        context = await workflow.execute(user_input, workflow_id)

        # Record execution
        self.execution_history.append(
            {
                "workflow_name": workflow_name,
                "workflow_id": context.workflow_id,
                "components": len(context.intermediate_results),
                "success": all(
                    r.is_success()
                    for r in context.intermediate_results.values()
                ),
            }
        )

        return context

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status.

        Returns:
            Dictionary with system statistics
        """
        return {
            "name": self.name,
            "workflows": len(self.workflows),
            "global_components": len(self.global_components),
            "executions": len(self.execution_history),
            "success_rate": (
                sum(
                    1
                    for e in self.execution_history
                    if e.get("success")
                )
                / len(self.execution_history)
                if self.execution_history
                else 0
            ),
        }

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} name={self.name} "
            f"workflows={len(self.workflows)} "
            f"components={len(self.global_components)}>"
        )

"""
Data pipeline orchestration and workflow management.

Coordinates complex data processing workflows with dependency management,
error handling, and progress tracking.
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class StageStatus(str, Enum):
    """Status of pipeline stage."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StageResult:
    """Result of a pipeline stage."""
    stage_name: str
    status: StageStatus
    output: Optional[Any] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'stage': self.stage_name,
            'status': self.status.value,
            'output_type': type(self.output).__name__ if self.output else None,
            'error': self.error,
            'duration_ms': self.duration * 1000 if self.duration else 0
        }


class PipelineStage:
    """Represents a single stage in pipeline."""
    
    def __init__(
        self,
        name: str,
        func: Callable,
        dependencies: Optional[List[str]] = None,
        skip_on_error: bool = False
    ):
        """
        Initialize pipeline stage.
        
        Args:
            name: Stage name
            func: Processing function
            dependencies: Names of stages that must complete first
            skip_on_error: Skip if dependency fails
        """
        self.name = name
        self.func = func
        self.dependencies = dependencies or []
        self.skip_on_error = skip_on_error
        self.result: Optional[StageResult] = None
    
    def execute(self, context: Dict[str, Any]) -> StageResult:
        """
        Execute stage.
        
        Args:
            context: Pipeline context with outputs from previous stages
        
        Returns:
            Stage result
        """
        result = StageResult(
            stage_name=self.name,
            status=StageStatus.PENDING,
            start_time=datetime.utcnow()
        )
        
        try:
            logger.info(f"Starting stage: {self.name}")
            result.status = StageStatus.RUNNING
            
            # Pass relevant context to function
            result.output = self.func(context)
            result.status = StageStatus.COMPLETED
            
            logger.info(f"Completed stage: {self.name}")
        
        except Exception as e:
            result.error = str(e)
            result.status = StageStatus.FAILED
            logger.error(f"Stage {self.name} failed: {e}")
        
        finally:
            result.end_time = datetime.utcnow()
            if result.start_time:
                result.duration = (result.end_time - result.start_time).total_seconds()
        
        self.result = result
        return result


class DataPipeline:
    """Orchestrates complex data processing workflows."""
    
    def __init__(self, name: str = "DataPipeline"):
        """
        Initialize pipeline.
        
        Args:
            name: Pipeline name
        """
        self.name = name
        self.stages: Dict[str, PipelineStage] = {}
        self.context: Dict[str, Any] = {}
        self.results: List[StageResult] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    def add_stage(
        self,
        name: str,
        func: Callable,
        dependencies: Optional[List[str]] = None,
        skip_on_error: bool = False
    ) -> 'DataPipeline':
        """
        Add stage to pipeline.
        
        Args:
            name: Stage name
            func: Processing function
            dependencies: Dependent stages
            skip_on_error: Skip if dependency fails
        
        Returns:
            Self for chaining
        """
        self.stages[name] = PipelineStage(name, func, dependencies, skip_on_error)
        return self
    
    def _check_dependencies(self, stage: PipelineStage) -> Tuple[bool, Optional[str]]:
        """Check if stage dependencies are met."""
        for dep_name in stage.dependencies:
            if dep_name not in self.stages:
                return False, f"Dependency {dep_name} not found"
            
            dep_stage = self.stages[dep_name]
            if dep_stage.result is None:
                return False, f"Dependency {dep_name} not executed"
            
            if dep_stage.result.status == StageStatus.FAILED:
                if not stage.skip_on_error:
                    return False, f"Dependency {dep_name} failed"
                else:
                    logger.warning(f"Skipping {stage.name} due to {dep_name} failure")
                    return True, "skip"
        
        return True, None
    
    def execute(self, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute pipeline.
        
        Args:
            initial_context: Initial context data
        
        Returns:
            Final context with all stage outputs
        """
        self.start_time = datetime.utcnow()
        self.context = initial_context or {}
        self.results = []
        
        logger.info(f"Starting pipeline: {self.name}")
        
        # Topological sort of stages based on dependencies
        executed = set()
        execution_order = []
        
        def visit(stage_name: str):
            if stage_name in executed:
                return
            
            stage = self.stages[stage_name]
            for dep in stage.dependencies:
                if dep in self.stages:
                    visit(dep)
            
            executed.add(stage_name)
            execution_order.append(stage_name)
        
        for stage_name in self.stages:
            visit(stage_name)
        
        # Execute stages
        for stage_name in execution_order:
            stage = self.stages[stage_name]
            
            # Check dependencies
            can_execute, msg = self._check_dependencies(stage)
            
            if not can_execute:
                result = StageResult(
                    stage_name=stage.name,
                    status=StageStatus.SKIPPED,
                    error=msg
                )
                self.results.append(result)
                logger.warning(f"Skipped stage {stage.name}: {msg}")
                continue
            
            if msg == "skip":
                result = StageResult(
                    stage_name=stage.name,
                    status=StageStatus.SKIPPED
                )
                self.results.append(result)
                continue
            
            # Execute stage
            result = stage.execute(self.context)
            self.results.append(result)
            
            # Add output to context
            self.context[stage.name] = result.output
            
            if result.status == StageStatus.FAILED:
                logger.error(f"Pipeline failed at stage: {stage.name}")
                break
        
        self.end_time = datetime.utcnow()
        
        logger.info(f"Completed pipeline: {self.name}")
        
        return self.context
    
    def get_summary(self) -> Dict[str, Any]:
        """Get pipeline execution summary."""
        duration = None
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
        
        status_counts = {}
        for result in self.results:
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'pipeline': self.name,
            'duration_ms': duration * 1000 if duration else 0,
            'total_stages': len(self.stages),
            'executed_stages': len(self.results),
            'status_summary': status_counts,
            'stages': [result.to_dict() for result in self.results]
        }
    
    def get_failed_stages(self) -> List[StageResult]:
        """Get list of failed stages."""
        return [r for r in self.results if r.status == StageStatus.FAILED]
    
    def is_successful(self) -> bool:
        """Check if pipeline executed successfully."""
        return all(r.status != StageStatus.FAILED for r in self.results)


class WorkflowBuilder:
    """Builder for creating complex workflows."""
    
    def __init__(self, name: str = "Workflow"):
        """Initialize workflow builder."""
        self.pipeline = DataPipeline(name)
    
    def stage(self, name: str, dependencies: Optional[List[str]] = None):
        """Decorator for adding a stage."""
        def decorator(func):
            self.pipeline.add_stage(name, func, dependencies)
            return func
        return decorator
    
    def build(self) -> DataPipeline:
        """Build and return pipeline."""
        return self.pipeline


class ParallelStageGroup:
    """Execute multiple stages in parallel (experimental)."""
    
    def __init__(self, stages: List[PipelineStage]):
        """
        Initialize parallel stage group.
        
        Args:
            stages: Stages to execute in parallel
        """
        self.stages = stages
        self.results: Dict[str, StageResult] = {}
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, StageResult]:
        """
        Execute stages in parallel.
        
        Args:
            context: Pipeline context
        
        Returns:
            Results dictionary
        """
        from concurrent.futures import ThreadPoolExecutor
        
        with ThreadPoolExecutor(max_workers=len(self.stages)) as executor:
            futures = {
                stage.name: executor.submit(stage.execute, context)
                for stage in self.stages
            }
            
            for stage_name, future in futures.items():
                self.results[stage_name] = future.result()
        
        return self.results


class ConditionalStage:
    """Execute stage conditionally."""
    
    def __init__(
        self,
        name: str,
        func: Callable,
        condition: Callable[[Dict[str, Any]], bool],
        dependencies: Optional[List[str]] = None
    ):
        """
        Initialize conditional stage.
        
        Args:
            name: Stage name
            func: Processing function
            condition: Function that determines if stage should run
            dependencies: Dependent stages
        """
        self.name = name
        self.func = func
        self.condition = condition
        self.dependencies = dependencies or []
    
    def should_execute(self, context: Dict[str, Any]) -> bool:
        """Check if stage should execute."""
        return self.condition(context)
    
    def execute(self, context: Dict[str, Any]) -> StageResult:
        """Execute if condition is met."""
        if not self.should_execute(context):
            return StageResult(
                stage_name=self.name,
                status=StageStatus.SKIPPED
            )
        
        stage = PipelineStage(self.name, self.func, self.dependencies)
        return stage.execute(context)

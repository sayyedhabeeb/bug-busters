"""
Asynchronous and concurrent processing module.

Provides async/await support, thread pool, and process pool functionality
for parallel processing of jobs and candidates.
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Future
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Dict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ProcessStatus(str, Enum):
    """Status of async process."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProcessResult:
    """Result of async process execution."""
    task_id: str
    status: ProcessStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    progress: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'task_id': self.task_id,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'progress': self.progress
        }


class AsyncTaskManager:
    """Manages asynchronous task execution."""
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize async task manager.
        
        Args:
            max_workers: Maximum number of concurrent workers
        """
        self.max_workers = max_workers
        self.tasks: Dict[str, ProcessResult] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_counter = 0
    
    def submit_task(
        self,
        func: Callable,
        *args,
        task_name: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Submit async task.
        
        Args:
            func: Function to execute
            args: Positional arguments
            task_name: Optional task name
            kwargs: Keyword arguments
        
        Returns:
            Task ID
        """
        task_id = f"task_{self.task_counter}"
        self.task_counter += 1
        
        result = ProcessResult(
            task_id=task_id,
            status=ProcessStatus.PENDING,
            start_time=datetime.utcnow()
        )
        
        self.tasks[task_id] = result
        
        def execute():
            try:
                result.status = ProcessStatus.RUNNING
                result.result = func(*args, **kwargs)
                result.status = ProcessStatus.COMPLETED
            except Exception as e:
                result.error = str(e)
                result.status = ProcessStatus.FAILED
                logger.error(f"Task {task_id} failed: {e}")
            finally:
                result.end_time = datetime.utcnow()
                if result.start_time:
                    result.duration = (result.end_time - result.start_time).total_seconds()
        
        self.executor.submit(execute)
        logger.info(f"Submitted task {task_id}: {task_name or func.__name__}")
        
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[ProcessResult]:
        """Get task status."""
        return self.tasks.get(task_id)
    
    def wait_task(self, task_id: str, timeout: int = 300) -> Optional[ProcessResult]:
        """Wait for task completion."""
        result = self.tasks.get(task_id)
        
        if result is None:
            return None
        
        start_time = datetime.utcnow()
        while result.status in [ProcessStatus.PENDING, ProcessStatus.RUNNING]:
            if (datetime.utcnow() - start_time).total_seconds() > timeout:
                logger.warning(f"Task {task_id} timed out after {timeout}s")
                break
            asyncio.sleep(0.1)
        
        return result
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel pending task."""
        result = self.tasks.get(task_id)
        if result and result.status == ProcessStatus.PENDING:
            result.status = ProcessStatus.CANCELLED
            return True
        return False
    
    def get_all_tasks(self) -> Dict[str, ProcessResult]:
        """Get all tasks."""
        return self.tasks.copy()
    
    def clear_completed(self) -> int:
        """Clear completed tasks, return count."""
        completed = [
            task_id for task_id, result in self.tasks.items()
            if result.status in [ProcessStatus.COMPLETED, ProcessStatus.FAILED]
        ]
        for task_id in completed:
            del self.tasks[task_id]
        return len(completed)
    
    def shutdown(self, wait: bool = True) -> None:
        """Shutdown executor."""
        self.executor.shutdown(wait=wait)


class BatchAsyncProcessor:
    """Process batches asynchronously."""
    
    def __init__(self, batch_size: int = 100, max_workers: int = 4):
        """
        Initialize batch async processor.
        
        Args:
            batch_size: Items per batch
            max_workers: Maximum concurrent workers
        """
        self.batch_size = batch_size
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_manager = AsyncTaskManager(max_workers=max_workers)
    
    async def process_batch_async(
        self,
        items: List[Any],
        process_func: Callable[[Any], Any],
        task_id: str = "batch_process"
    ) -> List[Any]:
        """
        Process items asynchronously.
        
        Args:
            items: Items to process
            process_func: Processing function
            task_id: Task identifier
        
        Returns:
            Processed results
        """
        batches = [
            items[i:i + self.batch_size]
            for i in range(0, len(items), self.batch_size)
        ]
        
        results = []
        loop = asyncio.get_event_loop()
        
        futures = []
        for batch in batches:
            future = loop.run_in_executor(
                self.executor,
                lambda b=batch: [process_func(item) for item in b]
            )
            futures.append(future)
        
        for future in futures:
            batch_results = await future
            results.extend(batch_results)
        
        return results
    
    def process_batch_sync(
        self,
        items: List[Any],
        process_func: Callable[[Any], Any]
    ) -> List[Any]:
        """
        Process items synchronously using thread pool.
        
        Args:
            items: Items to process
            process_func: Processing function
        
        Returns:
            Processed results
        """
        futures = [self.executor.submit(process_func, item) for item in items]
        return [future.result() for future in futures]


class RetryPolicy:
    """Policy for retrying failed operations."""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0
    ):
        """
        Initialize retry policy.
        
        Args:
            max_retries: Maximum retry attempts
            initial_delay: Initial delay between retries (seconds)
            max_delay: Maximum delay between retries (seconds)
            exponential_base: Base for exponential backoff
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for attempt using exponential backoff."""
        delay = min(
            self.initial_delay * (self.exponential_base ** attempt),
            self.max_delay
        )
        return delay


def retry_with_backoff(policy: Optional[RetryPolicy] = None):
    """
    Decorator for retry with exponential backoff.
    
    Args:
        policy: Retry policy configuration
    
    Example:
        @retry_with_backoff()
        def unstable_operation():
            return external_api_call()
    """
    if policy is None:
        policy = RetryPolicy()
    
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(policy.max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < policy.max_retries - 1:
                        delay = policy.get_delay(attempt)
                        logger.warning(
                            f"Attempt {attempt + 1} failed: {e}. "
                            f"Retrying in {delay}s..."
                        )
                        await asyncio.sleep(delay)
            
            logger.error(f"All {policy.max_retries} attempts failed")
            raise last_exception
        
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(policy.max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < policy.max_retries - 1:
                        delay = policy.get_delay(attempt)
                        logger.warning(
                            f"Attempt {attempt + 1} failed: {e}. "
                            f"Retrying in {delay}s..."
                        )
                        asyncio.sleep(delay)
            
            logger.error(f"All {policy.max_retries} attempts failed")
            raise last_exception
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Failures before opening circuit
            recovery_timeout: Seconds before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.is_open = False
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            args: Positional arguments
            kwargs: Keyword arguments
        
        Returns:
            Function result
        
        Raises:
            Exception: If circuit is open
        """
        if self.is_open:
            if self._should_attempt_recovery():
                self.is_open = False
                logger.info("Circuit breaker attempting recovery")
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            
            if self.failure_count >= self.failure_threshold:
                self.is_open = True
                logger.error(f"Circuit breaker opened after {self.failure_count} failures")
            
            raise e
    
    def _should_attempt_recovery(self) -> bool:
        """Check if recovery should be attempted."""
        if self.last_failure_time is None:
            return False
        
        elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout
    
    def reset(self) -> None:
        """Manually reset circuit breaker."""
        self.is_open = False
        self.failure_count = 0
        self.last_failure_time = None
        logger.info("Circuit breaker reset")


# Global async task manager
_global_task_manager: Optional[AsyncTaskManager] = None


def get_task_manager(max_workers: int = 4) -> AsyncTaskManager:
    """Get or create global async task manager."""
    global _global_task_manager
    if _global_task_manager is None:
        _global_task_manager = AsyncTaskManager(max_workers=max_workers)
    return _global_task_manager

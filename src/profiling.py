"""
Performance profiling and optimization tools.

Monitors execution time, memory usage, and identifies bottlenecks.
"""

import logging
import time
import psutil
import os
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for function execution."""
    function_name: str
    execution_time: float
    memory_before: float
    memory_after: float
    memory_delta: float
    peak_memory: float
    cpu_percent: float
    timestamp: datetime
    call_count: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'function': self.function_name,
            'execution_time_ms': self.execution_time * 1000,
            'memory_before_mb': self.memory_before / 1024 / 1024,
            'memory_after_mb': self.memory_after / 1024 / 1024,
            'memory_delta_mb': self.memory_delta / 1024 / 1024,
            'peak_memory_mb': self.peak_memory / 1024 / 1024,
            'cpu_percent': self.cpu_percent,
            'timestamp': self.timestamp.isoformat()
        }


class PerformanceProfiler:
    """Profiles function performance."""
    
    def __init__(self):
        """Initialize profiler."""
        self.metrics: Dict[str, List[PerformanceMetrics]] = {}
        self.process = psutil.Process(os.getpid())
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in bytes."""
        try:
            return self.process.memory_info().rss
        except:
            return 0
    
    def _get_cpu_percent(self) -> float:
        """Get CPU usage percentage."""
        try:
            return self.process.cpu_percent(interval=0.01)
        except:
            return 0
    
    def profile_function(self, func: Callable) -> Callable:
        """
        Decorator to profile function.
        
        Example:
            profiler = PerformanceProfiler()
            @profiler.profile_function
            def expensive_operation(x, y):
                return x + y
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            
            # Measure memory before
            mem_before = self._get_memory_usage()
            peak_mem = mem_before
            
            # Measure time
            start_time = time.time()
            cpu_start = self._get_cpu_percent()
            
            try:
                result = func(*args, **kwargs)
                return result
            
            finally:
                # Measure after
                end_time = time.time()
                mem_after = self._get_memory_usage()
                cpu_end = self._get_cpu_percent()
                
                execution_time = end_time - start_time
                memory_delta = mem_after - mem_before
                peak_mem = max(peak_mem, mem_after)
                cpu_percent = (cpu_start + cpu_end) / 2
                
                metrics = PerformanceMetrics(
                    function_name=func_name,
                    execution_time=execution_time,
                    memory_before=mem_before,
                    memory_after=mem_after,
                    memory_delta=memory_delta,
                    peak_memory=peak_mem,
                    cpu_percent=cpu_percent,
                    timestamp=datetime.utcnow()
                )
                
                if func_name not in self.metrics:
                    self.metrics[func_name] = []
                
                self.metrics[func_name].append(metrics)
                
                # Log if slow
                if execution_time > 1.0:
                    logger.warning(
                        f"Slow function: {func_name} took {execution_time:.2f}s",
                        extra={'extra_data': {'time_ms': execution_time * 1000}}
                    )
        
        return wrapper
    
    def get_metrics(self, func_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metrics for function(s).
        
        Args:
            func_name: Specific function or None for all
        
        Returns:
            Metrics dictionary
        """
        if func_name:
            if func_name not in self.metrics:
                return {}
            
            metrics_list = self.metrics[func_name]
        else:
            metrics_list = []
            for m_list in self.metrics.values():
                metrics_list.extend(m_list)
        
        if not metrics_list:
            return {}
        
        # Calculate statistics
        times = [m.execution_time for m in metrics_list]
        memories = [m.memory_delta for m in metrics_list]
        
        return {
            'count': len(metrics_list),
            'avg_time_ms': sum(times) / len(times) * 1000,
            'min_time_ms': min(times) * 1000,
            'max_time_ms': max(times) * 1000,
            'avg_memory_delta_mb': sum(memories) / len(memories) / 1024 / 1024,
            'latest': metrics_list[-1].to_dict()
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get profiling summary."""
        summary = {}
        
        for func_name in self.metrics:
            summary[func_name] = self.get_metrics(func_name)
        
        return summary


@contextmanager
def timer(name: str = "Operation"):
    """
    Context manager for timing operations.
    
    Example:
        with timer("Database query"):
            query_results = db.execute(query)
    """
    start = time.time()
    logger.info(f"Starting: {name}")
    
    try:
        yield
    finally:
        elapsed = time.time() - start
        logger.info(f"Completed: {name} ({elapsed:.2f}s)")


class MemoryTracker:
    """Track memory usage."""
    
    def __init__(self):
        """Initialize memory tracker."""
        self.snapshots: List[Tuple[datetime, float]] = []
        self.process = psutil.Process(os.getpid())
    
    def snapshot(self, label: str = "") -> float:
        """Take memory snapshot."""
        try:
            memory = self.process.memory_info().rss
            self.snapshots.append((datetime.utcnow(), memory))
            
            if label:
                logger.debug(f"Memory {label}: {memory / 1024 / 1024:.2f} MB")
            
            return memory
        except:
            return 0
    
    def get_peak(self) -> float:
        """Get peak memory usage."""
        if not self.snapshots:
            return 0
        return max(mem for _, mem in self.snapshots)
    
    def get_delta(self) -> float:
        """Get memory change since first snapshot."""
        if len(self.snapshots) < 2:
            return 0
        return self.snapshots[-1][1] - self.snapshots[0][1]
    
    def reset(self) -> None:
        """Reset snapshots."""
        self.snapshots = []


class CallCounter:
    """Count function calls and track statistics."""
    
    def __init__(self):
        """Initialize call counter."""
        self.counts: Dict[str, int] = {}
    
    def count_calls(self, func: Callable) -> Callable:
        """
        Decorator to count function calls.
        
        Example:
            counter = CallCounter()
            @counter.count_calls
            def my_function():
                pass
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            self.counts[func_name] = self.counts.get(func_name, 0) + 1
            return func(*args, **kwargs)
        
        return wrapper
    
    def get_count(self, func_name: str) -> int:
        """Get call count for function."""
        return self.counts.get(func_name, 0)
    
    def get_all_counts(self) -> Dict[str, int]:
        """Get all call counts."""
        return self.counts.copy()


def slow_function_detector(threshold_ms: float = 100):
    """
    Decorator to detect slow functions.
    
    Args:
        threshold_ms: Time threshold in milliseconds
    
    Example:
        @slow_function_detector(threshold_ms=500)
        def process_data(data):
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = (time.time() - start) * 1000
            
            if elapsed > threshold_ms:
                logger.warning(
                    f"Slow function detected: {func.__name__} took {elapsed:.2f}ms "
                    f"(threshold: {threshold_ms}ms)",
                    extra={'extra_data': {'elapsed_ms': elapsed}}
                )
            
            return result
        
        return wrapper
    
    return decorator


# Global profiler instance
_global_profiler: Optional[PerformanceProfiler] = None


def get_profiler() -> PerformanceProfiler:
    """Get or create global profiler."""
    global _global_profiler
    if _global_profiler is None:
        _global_profiler = PerformanceProfiler()
    return _global_profiler

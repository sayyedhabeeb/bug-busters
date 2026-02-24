# 🔗 INTEGRATION GUIDE - New Components

## Quick Integration Reference

This guide shows how to integrate the newly added components into your existing codebase.

---

## 1. Error Handling Integration

### Update API Server

Replace error handling in `src/api/server.py`:

```python
from src.exceptions import (
    ValidationError,
    DataError,
    ParseError,
    MatchingError,
    ModelError,
    DatabaseError,
    RateLimitError,
    TimeoutError,
    RecommendationSystemException
)

@app.route('/v2/parse-resume', methods=['POST'])
def parse_resume():
    """Parse resume with proper error handling."""
    try:
        data = request.json
        
        if not data or 'text' not in data:
            raise ValidationError(
                "Resume text is required",
                details={'missing_field': 'text'}
            )
        
        resume_text = data['text']
        
        # Validate text
        if len(resume_text) < 50:
            raise ValidationError(
                "Resume too short",
                details={'min_length': 50, 'actual': len(resume_text)}
            )
        
        # Parse
        parsed = resume_parser.parse(resume_text)
        
        return jsonify({
            'parsed_data': parsed,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except ValidationError as e:
        logger.warning(f"Validation error: {e.message}")
        return jsonify(e.to_dict()), e.status_code
    
    except ParseError as e:
        logger.error(f"Parse error: {e.message}")
        return jsonify(e.to_dict()), e.status_code
    
    except RecommendationSystemException as e:
        logger.error(f"System error: {e.message}")
        return jsonify(e.to_dict()), e.status_code
    
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({
            'error_code': 'INTERNAL_ERROR',
            'message': 'Internal server error'
        }), 500
```

### Update Data Processing

```python
from src.exceptions import DataError

def process_resume_batch(resumes):
    """Process resume batch with error handling."""
    results = []
    errors = []
    
    for i, resume in enumerate(resumes):
        try:
            if not isinstance(resume, dict):
                raise DataError(
                    f"Invalid resume format at index {i}",
                    details={'index': i, 'type': type(resume).__name__}
                )
            
            result = process_single(resume)
            results.append(result)
        
        except DataError as e:
            errors.append(e.to_dict())
            logger.warning(f"Skipping resume {i}: {e.message}")
        
        except Exception as e:
            logger.error(f"Unexpected error at {i}: {e}")
            raise
    
    return {
        'results': results,
        'errors': errors,
        'success_count': len(results),
        'error_count': len(errors)
    }
```

---

## 2. Caching Integration

### Integrate with Feature Engineering

```python
from src.cache import get_cache, cached

cache = get_cache()

@cached(ttl=3600)
def compute_resume_features(resume_id, resume_text):
    """Compute features with caching."""
    # This function result will be cached for 1 hour
    features = feature_engine.compute(resume_text)
    return features

# Or manual caching
def get_resume_features(resume_id):
    cache_key = f"features_{resume_id}"
    
    return cache.get(
        cache_key,
        compute_fn=lambda: compute_resume_features(resume_id),
        ttl=3600  # 1 hour
    )

# Cache embeddings
@cached(ttl=86400)  # 24 hours
def get_resume_embeddings(resume_id):
    return embeddings_model.encode(resume_text)
```

### Cache Job Descriptions

```python
def cache_job_descriptions(jobs):
    """Cache all job descriptions."""
    cache_manager = get_cache()
    
    for job in jobs:
        job_id = job['id']
        cache_manager.set(
            f"job_{job_id}",
            job,
            ttl=86400  # 24 hours
        )
    
    logger.info(f"Cached {len(jobs)} jobs")

# Retrieve with fallback
def get_job_with_cache(job_id):
    cache = get_cache()
    
    job = cache.get(f"job_{job_id}")
    
    if job is None:
        job = db.get_job(job_id)
        cache.set(f"job_{job_id}", job, ttl=86400)
    
    return job
```

---

## 3. Async Processing Integration

### Process Large Batches Asynchronously

```python
from src.async_processor import (
    get_task_manager,
    BatchAsyncProcessor,
    retry_with_backoff,
    CircuitBreaker
)

# Async task submission
def batch_match_async(candidate_ids, job_ids):
    """Submit batch matching as async task."""
    task_manager = get_task_manager(max_workers=4)
    
    def do_matching():
        return batch_matcher.match_all(candidate_ids, job_ids)
    
    task_id = task_manager.submit_task(
        do_matching,
        task_name=f"batch_match_{len(candidate_ids)}_x_{len(job_ids)}"
    )
    
    return task_id

# Check task status
def get_batch_status(task_id):
    task_manager = get_task_manager()
    result = task_manager.get_task_status(task_id)
    
    if result is None:
        return None
    
    return {
        'task_id': task_id,
        'status': result.status.value,
        'progress': result.progress,
        'error': result.error
    }

# Retry with exponential backoff
@retry_with_backoff()
def call_external_matching_service(candidates, jobs):
    """Call external service with automatic retry."""
    response = external_api.request_matching(candidates, jobs)
    return response.json()

# Circuit breaker for external services
circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)

def call_embedding_service(texts):
    """Call embedding service with circuit breaker."""
    try:
        return circuit_breaker.call(
            embedding_api.encode,
            texts
        )
    except Exception as e:
        logger.error(f"Embedding service failed: {e}")
        # Fall back to local embeddings
        return local_embedding_model.encode(texts)
```

---

## 4. Utility Functions Integration

### String & Email Validation

```python
from src.utils import (
    extract_emails,
    extract_phone_numbers,
    is_email_valid,
    is_url_valid,
    normalize_text,
    slugify
)

def validate_contact_info(resume_text):
    """Extract and validate contact information."""
    emails = extract_emails(resume_text)
    phones = extract_phone_numbers(resume_text)
    
    valid_emails = [e for e in emails if is_email_valid(e)]
    
    return {
        'emails_found': len(emails),
        'emails_valid': len(valid_emails),
        'phones_found': len(phones),
        'is_complete': len(valid_emails) > 0 and len(phones) > 0
    }

def normalize_resume(resume_text):
    """Normalize resume text."""
    return normalize_text(resume_text, lowercase=False, strip=True)
```

### Data Transformation

```python
from src.utils import (
    flatten_dict,
    unflatten_dict,
    merge_dicts,
    chunk_list,
    remove_duplicates
)

def flatten_feature_dict(features):
    """Flatten nested feature dictionary."""
    return flatten_dict(features, sep='_')

def process_candidates_in_batches(candidates, batch_size=100):
    """Process candidates in chunks."""
    batches = chunk_list(candidates, batch_size)
    
    results = []
    for batch in batches:
        result = batch_processor.process(batch)
        results.extend(result)
    
    return results

def deduplicate_jobs(jobs):
    """Remove duplicate jobs by ID."""
    return remove_duplicates(jobs, key=lambda j: j.get('job_id'))
```

### Hash and Token Generation

```python
from src.utils import generate_hash, generate_uuid, generate_token

def create_candidate_id(email):
    """Create deterministic candidate ID."""
    return generate_hash(email, algorithm='sha256')

def create_session_token():
    """Create random session token."""
    return generate_token(length=64)

def create_correlation_id():
    """Create unique request correlation ID."""
    return generate_uuid(version=4)
```

---

## 5. Middleware Integration

### Add to Flask App

```python
from flask import Flask
from src.middleware import (
    rate_limit,
    request_logger_middleware,
    validate_json,
    require_headers,
    timeout_handler,
    add_response_metadata
)

app = Flask(__name__)

# Add rate limit to all endpoints
@app.before_request
def check_rate_limit():
    """Apply rate limit to all endpoints."""
    pass

# Apply middleware stack
@app.route('/v2/recommend', methods=['POST'])
@rate_limit(max_requests=100, window_size=60)
@request_logger_middleware
@validate_json
@require_headers('X-Request-ID')
@timeout_handler(seconds=30)
@add_response_metadata
def recommend():
    """Get recommendations with full middleware."""
    # Your logic here
    return {'recommendations': []}
```

### Request Context

```python
from src.middleware import RequestContext
from src.utils import generate_uuid

@app.before_request
def setup_context():
    """Setup request context."""
    request_id = request.headers.get('X-Request-ID', generate_uuid())
    RequestContext.set('request_id', request_id)
    RequestContext.set('start_time', datetime.utcnow())

@app.after_request
def cleanup_context(response):
    """Cleanup request context."""
    elapsed = (datetime.utcnow() - RequestContext.get('start_time')).total_seconds()
    RequestContext.clear()
    return response
```

---

## 6. Pipeline Orchestration Integration

### Build Matching Pipeline

```python
from src.orchestration import WorkflowBuilder

def create_matching_workflow(resume_text, job_texts):
    """Build and execute matching workflow."""
    
    builder = WorkflowBuilder("matching_pipeline")
    
    @builder.stage("validate_resume", [])
    def stage_validate_resume(ctx):
        from src.exceptions import ValidationError
        if len(resume_text) < 50:
            raise ValidationError("Resume too short")
        return resume_text
    
    @builder.stage("parse_resume", ["validate_resume"])
    def stage_parse_resume(ctx):
        return resume_parser.parse(ctx["validate_resume"])
    
    @builder.stage("extract_features", ["parse_resume"])
    def stage_extract_features(ctx):
        resume = ctx["parse_resume"]
        return feature_engine.extract(resume)
    
    @builder.stage("parse_jobs", [])
    def stage_parse_jobs(ctx):
        return [job_parser.parse(j) for j in job_texts]
    
    @builder.stage("compute_matches", ["extract_features", "parse_jobs"])
    def stage_compute_matches(ctx):
        features = ctx["extract_features"]
        jobs = ctx["parse_jobs"]
        return batch_matcher.match_all(features, jobs)
    
    @builder.stage("explain_matches", ["compute_matches"])
    def stage_explain_matches(ctx):
        matches = ctx["compute_matches"]
        return explainer.explain_batch(matches)
    
    pipeline = builder.build()
    result = pipeline.execute(initial_context={'resume_text': resume_text})
    summary = pipeline.get_summary()
    
    return {
        'matches': result.get('explain_matches'),
        'summary': summary,
        'success': pipeline.is_successful()
    }
```

---

## 7. Profiling Integration

### Profile Critical Functions

```python
from src.profiling import (
    get_profiler,
    slow_function_detector,
    timer,
    MemoryTracker
)

profiler = get_profiler()

# Profile expensive function
@profiler.profile_function
def compute_all_features(resumes):
    """Compute features for all resumes."""
    return [feature_engine.compute(r) for r in resumes]

# Detect slow functions
@slow_function_detector(threshold_ms=500)
def expensive_matching_operation(resume, jobs):
    """Match resume to jobs."""
    return matcher.match_batch(resume, jobs)

# Track memory usage
def process_large_dataset(data):
    """Process large dataset with memory tracking."""
    tracker = MemoryTracker()
    tracker.snapshot("start")
    
    with timer("loading_data"):
        loaded = load_data(data)
    
    with timer("processing_data"):
        result = process(loaded)
    
    tracker.snapshot("end")
    
    logger.info(f"Memory delta: {tracker.get_delta() / 1024 / 1024:.2f} MB")
    
    return result

# Get performance summary
def get_performance_report():
    """Generate performance report."""
    summary = profiler.get_summary()
    
    for func_name, metrics in summary.items():
        print(f"\n{func_name}:")
        print(f"  Calls: {metrics['count']}")
        print(f"  Avg time: {metrics['avg_time_ms']:.2f}ms")
        print(f"  Min time: {metrics['min_time_ms']:.2f}ms")
        print(f"  Max time: {metrics['max_time_ms']:.2f}ms")
```

---

## 8. Full Example: Integrated API Endpoint

```python
from flask import Flask, request, jsonify
from src.exceptions import ValidationError, MatchingError, RecommendationSystemException
from src.middleware import (
    rate_limit,
    request_logger_middleware,
    validate_json,
    add_response_metadata
)
from src.cache import get_cache
from src.async_processor import get_task_manager
from src.profiling import get_profiler
from src.orchestration import WorkflowBuilder
from src.utils import generate_uuid

app = Flask(__name__)
cache = get_cache()
profiler = get_profiler()

@app.route('/v2/recommend-async', methods=['POST'])
@rate_limit(max_requests=100, window_size=60)
@request_logger_middleware
@validate_json
@add_response_metadata
def recommend_async():
    """Get recommendations asynchronously."""
    try:
        data = request.json
        
        resume_id = data.get('resume_id')
        resume_text = data.get('resume_text')
        job_ids = data.get('job_ids', [])
        
        if not resume_id or not resume_text:
            raise ValidationError(
                "resume_id and resume_text required",
                details={'missing': ['resume_id', 'resume_text']}
            )
        
        # Create correlation ID
        correlation_id = generate_uuid()
        
        # Define async task
        def do_recommend():
            # Build orchestration pipeline
            builder = WorkflowBuilder("recommendation_pipeline")
            
            @builder.stage("parse_resume", [])
            def parse(ctx):
                return resume_parser.parse(resume_text)
            
            @builder.stage("compute_features", ["parse_resume"])
            @profiler.profile_function
            def features(ctx):
                return feature_engine.compute(ctx["parse_resume"])
            
            @builder.stage("match_jobs", ["compute_features"])
            def match(ctx):
                return batch_matcher.match(
                    ctx["compute_features"],
                    job_ids
                )
            
            @builder.stage("explain", ["match_jobs"])
            def explain(ctx):
                return explainer.explain_batch(ctx["match_jobs"])
            
            pipeline = builder.build()
            result = pipeline.execute()
            
            return {
                'matches': result.get('explain'),
                'summary': pipeline.get_summary()
            }
        
        # Submit async task
        task_manager = get_task_manager()
        task_id = task_manager.submit_task(
            do_recommend,
            task_name=f"recommend_{resume_id}_{correlation_id}"
        )
        
        return jsonify({
            'task_id': task_id,
            'correlation_id': correlation_id,
            'status_url': f'/v2/task-status/{task_id}'
        }), 202  # Accepted
    
    except ValidationError as e:
        return jsonify(e.to_dict()), e.status_code
    except RecommendationSystemException as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/v2/task-status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Check task status."""
    task_manager = get_task_manager()
    result = task_manager.get_task_status(task_id)
    
    if result is None:
        return jsonify({'error': 'Task not found'}), 404
    
    if result.status.value == 'completed':
        return jsonify({
            'task_id': task_id,
            'status': result.status.value,
            'result': result.result
        }), 200
    elif result.status.value == 'failed':
        return jsonify({
            'task_id': task_id,
            'status': result.status.value,
            'error': result.error
        }), 500
    else:
        return jsonify({
            'task_id': task_id,
            'status': result.status.value,
            'progress': result.progress
        }), 202
```

---

## ✅ Integration Checklist

- [ ] Import exceptions in API server
- [ ] Replace basic error handling with custom exceptions
- [ ] Initialize cache manager in app startup
- [ ] Add @cached decorators to expensive functions
- [ ] Setup async task manager for batch operations
- [ ] Import and use utility functions
- [ ] Apply middleware decorators to endpoints
- [ ] Build pipelines for complex workflows
- [ ] Profile critical functions
- [ ] Test error handling end-to-end
- [ ] Monitor performance metrics
- [ ] Document API changes

---

## 🎯 Next Steps

1. **Start with error handling**: Update all endpoints to use exceptions
2. **Add caching**: Cache embeddings and features first
3. **Enable async**: Use for batch operations
4. **Apply middleware**: Add rate limiting to all endpoints
5. **Build pipelines**: Orchestrate complex workflows
6. **Profile**: Identify and optimize bottlenecks

---

*Last Updated: February 5, 2026*

"""
Batch Processing Engine
-----------------------
Batch processing pipeline for bulk recommendations.
Helper classes for ranking and exporting results.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from datetime import datetime
import pandas as pd
import json

logger = logging.getLogger(__name__)


class BatchProcessingEngine:
    """Process batch recommendation requests efficiently."""
    
    def __init__(self, output_dir: Path = Path('outputs/batch')):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def process_batch(
        self,
        candidates: List[Dict[str, Any]],
        jobs: List[Dict[str, Any]],
        matcher_func,
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """Process batch of candidates and jobs."""
        
        logger.info(f"Starting batch processing: {len(candidates)} candidates x {len(jobs)} jobs")
        
        start_time = datetime.utcnow()
        results = []
        total_matches = 0
        successful_matches = 0
        failed_matches = 0
        
        # Process in batches
        for i in range(0, len(candidates), batch_size):
            batch_candidates = candidates[i:i+batch_size]
            
            for candidate in batch_candidates:
                for job in jobs:
                    try:
                        match_result = matcher_func(candidate, job)
                        results.append(match_result)
                        successful_matches += 1
                    except Exception as e:
                        logger.warning(f"Match failed: {str(e)}")
                        failed_matches += 1
                    
                    total_matches += 1
        
        # Aggregate results
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        batch_summary = {
            'batch_id': self._generate_batch_id(),
            'total_candidates': len(candidates),
            'total_jobs': len(jobs),
            'total_matches': total_matches,
            'successful_matches': successful_matches,
            'failed_matches': failed_matches,
            'success_rate': successful_matches / total_matches if total_matches > 0 else 0,
            'duration_seconds': duration,
            'results': results
        }
        
        self._save_batch_results(batch_summary)
        return batch_summary
    
    def _generate_batch_id(self) -> str:
        return f"BATCH_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    def _save_batch_results(self, batch_summary: Dict) -> None:
        batch_id = batch_summary['batch_id']
        json_path = self.output_dir / f"{batch_id}.json"
        
        with open(json_path, 'w') as f:
            json_data = {k: v for k, v in batch_summary.items() if k != 'results'}
            json_data['result_count'] = len(batch_summary['results'])
            json.dump(json_data, f, indent=2, default=str)
        
        logger.info(f"Batch results saved to {json_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Batch Processing Engine Ready")

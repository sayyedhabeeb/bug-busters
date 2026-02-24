"""
Batch processing pipeline for bulk recommendations.
Handles large-scale candidate-job matching with efficient processing.
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging
from datetime import datetime
import pandas as pd
import json

logger = logging.getLogger(__name__)


class BatchProcessor:
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
        """
        Process batch of candidates and jobs.
        
        Args:
            candidates: List of candidate data
            jobs: List of job data
            matcher_func: Function to call for matching
            batch_size: Number of matches to process at once
        
        Returns:
            Batch processing results
        """
        
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
                        logger.warning(f"Match failed for {candidate.get('id')} - {job.get('id')}: {str(e)}")
                        failed_matches += 1
                    
                    total_matches += 1
            
            # Progress logging
            progress = min((i + batch_size) / len(candidates) * 100, 100)
            logger.info(f"Batch progress: {progress:.1f}% - {successful_matches} successful, {failed_matches} failed")
        
        # Aggregate results
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        batch_summary = {
            'batch_id': self._generate_batch_id(),
            'total_candidates': len(candidates),
            'total_jobs': len(jobs),
            'total_matches': total_matches,
            'successful_matches': successful_matches,
            'failed_matches': failed_matches,
            'success_rate': successful_matches / total_matches if total_matches > 0 else 0,
            'duration_seconds': duration,
            'avg_time_per_match': duration / total_matches if total_matches > 0 else 0,
            'timestamp': start_time.isoformat(),
            'results': results
        }
        
        # Save results
        self._save_batch_results(batch_summary)
        
        logger.info(f"Batch processing completed in {duration:.2f}s (Success rate: {batch_summary['success_rate']:.1%})")
        
        return batch_summary
    
    def process_incremental(
        self,
        candidate_stream,
        jobs: List[Dict],
        matcher_func,
        callback_func=None
    ) -> Dict[str, Any]:
        """
        Process candidates from a streaming source (file, API, etc.).
        
        Args:
            candidate_stream: Iterable source of candidates
            jobs: List of job descriptions
            matcher_func: Matching function
            callback_func: Optional callback for each match
        
        Returns:
            Summary of incremental processing
        """
        
        processed = 0
        successful = 0
        failed = 0
        
        for candidate in candidate_stream:
            for job in jobs:
                try:
                    match_result = matcher_func(candidate, job)
                    successful += 1
                    
                    if callback_func:
                        callback_func(match_result)
                        
                except Exception as e:
                    logger.warning(f"Match failed: {str(e)}")
                    failed += 1
                
                processed += 1
        
        return {
            'total_processed': processed,
            'successful': successful,
            'failed': failed,
            'success_rate': successful / processed if processed > 0 else 0
        }
    
    def _generate_batch_id(self) -> str:
        """Generate unique batch ID."""
        return f"BATCH_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    def _save_batch_results(self, batch_summary: Dict) -> None:
        """Save batch results to file."""
        batch_id = batch_summary['batch_id']
        
        # Save as JSON
        json_path = self.output_dir / f"{batch_id}.json"
        with open(json_path, 'w') as f:
            # Convert non-serializable objects
            json_data = {k: v for k, v in batch_summary.items() if k != 'results'}
            json_data['result_count'] = len(batch_summary['results'])
            json.dump(json_data, f, indent=2, default=str)
        
        # Save results as CSV for analysis
        csv_path = self.output_dir / f"{batch_id}_results.csv"
        if batch_summary['results']:
            df = pd.DataFrame(batch_summary['results'])
            df.to_csv(csv_path, index=False)
        
        logger.info(f"Batch results saved to {json_path} and {csv_path}")


class RecommendationRanker:
    """Rank and filter batch recommendations."""
    
    @staticmethod
    def rank_recommendations(
        matches: List[Dict],
        ranking_strategy: str = 'overall_score'
    ) -> List[Dict]:
        """
        Rank matches by various strategies.
        
        Args:
            matches: List of match results
            ranking_strategy: Strategy to use (overall_score, match_type, multi-criteria)
        
        Returns:
            Sorted matches
        """
        
        if ranking_strategy == 'overall_score':
            return sorted(matches, key=lambda x: x.get('overall_score', 0), reverse=True)
        
        elif ranking_strategy == 'match_type':
            type_order = {'perfect': 4, 'strong': 3, 'moderate': 2, 'weak': 1}
            return sorted(
                matches,
                key=lambda x: (
                    type_order.get(x.get('match_type', 'weak'), 0),
                    x.get('overall_score', 0)
                ),
                reverse=True
            )
        
        elif ranking_strategy == 'multi-criteria':
            # Weighted combination of multiple factors
            return sorted(
                matches,
                key=lambda x: (
                    int(x.get('passes_hard_filters', False)),
                    x.get('overall_score', 0),
                    x.get('component_scores', {}).get('skills_match', 0)
                ),
                reverse=True
            )
        
        return matches
    
    @staticmethod
    def filter_recommendations(
        matches: List[Dict],
        min_score: float = 0.0,
        only_passes_filters: bool = False,
        match_types: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Filter recommendations by criteria.
        
        Args:
            matches: List of matches
            min_score: Minimum overall score
            only_passes_filters: Only include matches passing hard filters
            match_types: Only include specific match types
        
        Returns:
            Filtered matches
        """
        
        filtered = matches
        
        # Score filter
        if min_score > 0:
            filtered = [m for m in filtered if m.get('overall_score', 0) >= min_score]
        
        # Hard filter check
        if only_passes_filters:
            filtered = [m for m in filtered if m.get('passes_hard_filters', False)]
        
        # Match type filter
        if match_types:
            filtered = [m for m in filtered if m.get('match_type') in match_types]
        
        return filtered


class RecommendationExporter:
    """Export recommendations in various formats."""
    
    @staticmethod
    def export_csv(matches: List[Dict], filepath: Path) -> None:
        """Export matches to CSV."""
        df = pd.DataFrame(matches)
        df.to_csv(filepath, index=False)
        logger.info(f"Exported {len(matches)} matches to {filepath}")
    
    @staticmethod
    def export_json(matches: List[Dict], filepath: Path) -> None:
        """Export matches to JSON."""
        with open(filepath, 'w') as f:
            json.dump(matches, f, indent=2, default=str)
        logger.info(f"Exported {len(matches)} matches to {filepath}")
    
    @staticmethod
    def export_html_report(matches: List[Dict], filepath: Path) -> None:
        """Export matches as HTML report."""
        html = """
        <html>
        <head>
            <title>Recommendation Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #4CAF50; color: white; }
                .perfect { background-color: #90EE90; }
                .strong { background-color: #FFD700; }
                .moderate { background-color: #FFA500; }
                .weak { background-color: #FF6347; }
            </style>
        </head>
        <body>
            <h1>Recommendation Report</h1>
            <table>
                <tr>
                    <th>Candidate</th>
                    <th>Job</th>
                    <th>Score</th>
                    <th>Type</th>
                    <th>Filters</th>
                </tr>
        """
        
        for match in matches:
            match_class = match.get('match_type', 'weak')
            html += f"""
                <tr class="{match_class}">
                    <td>{match.get('candidate_id')}</td>
                    <td>{match.get('job_id')}</td>
                    <td>{match.get('overall_score', 0):.1f}</td>
                    <td>{match.get('match_type')}</td>
                    <td>{'✓' if match.get('passes_hard_filters') else '✗'}</td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """
        
        with open(filepath, 'w') as f:
            f.write(html)
        logger.info(f"Exported {len(matches)} matches to {filepath}")
    
    @staticmethod
    def export_by_candidate(
        matches: List[Dict],
        output_dir: Path
    ) -> Dict[str, Path]:
        """Export recommendations grouped by candidate."""
        output_dir.mkdir(parents=True, exist_ok=True)
        files = {}
        
        # Group by candidate
        by_candidate = {}
        for match in matches:
            cand_id = match.get('candidate_id')
            if cand_id not in by_candidate:
                by_candidate[cand_id] = []
            by_candidate[cand_id].append(match)
        
        # Export each candidate's recommendations
        for cand_id, cand_matches in by_candidate.items():
            filepath = output_dir / f"recommendations_{cand_id}.json"
            with open(filepath, 'w') as f:
                json.dump(cand_matches, f, indent=2, default=str)
            files[cand_id] = filepath
        
        logger.info(f"Exported recommendations for {len(by_candidate)} candidates")
        return files

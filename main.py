"""Job Recommendation System - unified CLI entrypoint."""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess
import sys
from pathlib import Path

import uvicorn

from config.config_production import get_config
from src.app_logging.logger import LoggerSetup, get_logger
from src.database.connection import DatabaseManager


def _setup_logging(config_obj) -> logging.Logger:
    """Initialize process logging once."""
    level_name = str(getattr(config_obj, "LOG_LEVEL", "INFO")).upper()
    log_level = getattr(logging, level_name, logging.INFO)
    json_logs = str(getattr(config_obj, "LOG_FORMAT", "standard")).lower() == "json"
    LoggerSetup.setup(log_dir=Path("logs"), level=log_level, json_format=json_logs)
    return get_logger(__name__)


def _sync_feature_artifacts(logger: logging.Logger) -> None:
    """
    Keep legacy output paths in sync.
    Some modules read `data/processed/features`, while others read `outputs/features`.
    """
    source_dir = Path("data/processed/features")
    target_dir = Path("outputs/features")
    target_dir.mkdir(parents=True, exist_ok=True)

    for filename in ("feature_matrix.csv", "tfidf_vectorizer.pkl"):
        source_file = source_dir / filename
        target_file = target_dir / filename
        if source_file.exists():
            shutil.copy2(source_file, target_file)
            logger.info("Synced feature artifact: %s -> %s", source_file, target_file)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI Job Recommendation System")
    parser.add_argument("--eda", action="store_true", help="Run data processing / EDA stage")
    parser.add_argument("--features", action="store_true", help="Build feature artifacts")
    parser.add_argument("--train", action="store_true", help="Train recommendation model")
    parser.add_argument("--evaluate", action="store_true", help="Run evaluation and export report")
    parser.add_argument("--api", action="store_true", help="Start FastAPI backend")
    parser.add_argument("--ui", action="store_true", help="Start TalentMatch AI React UI")
    parser.add_argument("--start", action="store_true", help="Start everything (API + UI)")
    parser.add_argument("--tests", action="store_true", help="Run unit/integration test suite")
    parser.add_argument("--config", action="store_true", help="Print current configuration")
    parser.add_argument("--all", action="store_true", help="Run full pipeline: eda -> features -> train -> evaluate")
    parser.add_argument("--host", type=str, help="Override API host")
    parser.add_argument("--port", type=int, help="Override API port")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    config = get_config()
    logger = _setup_logging(config)

    if args.config:
        print(json.dumps(config.get_config(), indent=2))
        return 0

    if args.all:
        args.eda = True
        args.features = True
        args.train = True
        args.evaluate = True

    if not any(
        [args.eda, args.features, args.train, args.evaluate, args.api, args.ui, args.start, args.tests]
    ):
        parser.print_help()
        return 0

    try:
        if args.eda:
            from src.data_processing.eda_engine import EDAEngine
            logger.info("Ensuring database tables exist...")
            DatabaseManager.create_tables()
            logger.info("Running data processing...")
            EDAEngine().run_full_eda()

        if args.features:
            from src.feature_engineering.engine import FeatureEngine
            logger.info("Running feature engineering...")
            FeatureEngine().run()
            _sync_feature_artifacts(logger)

        if args.train:
            from src.modeling.engine import ModelTrainingEngine
            logger.info("Running model training...")
            _sync_feature_artifacts(logger)
            ModelTrainingEngine().train()

        if args.evaluate:
            from src.evaluation.engine import EvaluationEngine
            logger.info("Running evaluation...")
            EvaluationEngine().evaluate()

        if args.tests:
            logger.info("Running tests...")
            result = subprocess.run([sys.executable, "-m", "pytest", "tests", "-v"], check=False)
            if result.returncode != 0:
                return result.returncode

        if args.start:
            args.api = True
            args.ui = True

        if args.api:
            host = args.host if args.host else getattr(config, "API_HOST", "0.0.0.0")
            port = args.port if args.port else int(getattr(config, "API_PORT", 8000))
            logger.info("Starting Bug-Busters API on http://%s:%s", host, port)
            # Use uvicorn.run for development, subprocess for parallel start in --start
            if args.start:
                subprocess.Popen(
                    [sys.executable, "-m", "uvicorn", "src.api.server:app", "--host", host, "--port", str(port)],
                    shell=True
                )
            else:
                uvicorn.run("src.api.server:app", host=host, port=port, reload=True)

        if args.ui:
            logger.info("Starting TalentMatch AI React UI...")
            project_root = Path(__file__).parent.absolute()
            frontend_path = project_root / "frontend"

            subprocess.Popen(
                ["npm", "install", "--legacy-peer-deps"], cwd=frontend_path, shell=True
            ).wait()
            subprocess.Popen(
                ["npm", "run", "dev"], cwd=frontend_path, shell=True
            )
            
            logger.info("React UI: http://localhost:5173")

    except Exception:
        logger.exception("Execution failed")
        return 1

    logger.info("Execution completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())

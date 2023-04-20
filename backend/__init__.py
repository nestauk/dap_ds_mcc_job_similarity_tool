from pathlib import Path
import logging

PROJECT_DIR = Path(__file__).resolve().parents[1]
BUCKET_NAME = "mcc-sussex"
logger = logging.getLogger(__name__)

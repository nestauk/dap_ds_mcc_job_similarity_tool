from pathlib import Path
import logging

PROJECT_DIR = Path(__file__).resolve().parents[1]
IMAGE_DIR = f"{PROJECT_DIR}/mcc_sussex/images/"
BUCKET_NAME = "mcc-sussex"
logger = logging.getLogger(__name__)

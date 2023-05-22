"""assigns ids to esco occupations based on row ids
"""
import pandas as pd
from mcc_sussex.backend.getters.esco import esco_occupations
from mcc_sussex import PROJECT_DIR

esco = esco_occupations().drop_duplicates(subset="conceptUri")
esco_ids = esco.assign(id=range(len(esco))).astype(
    {"id": 'int'})[["conceptUri", "id"]]

esco_ids.to_csv(
    f"{PROJECT_DIR}/mcc_sussex/data/processed/esco_ids.csv")

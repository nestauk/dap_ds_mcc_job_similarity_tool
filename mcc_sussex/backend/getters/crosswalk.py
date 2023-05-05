import pandas as pd
from mcc_sussex import PROJECT_DIR


def esco_onet_crosswalk():
    return pd.read_csv(f"{PROJECT_DIR}/mcc_sussex/data/processed/ESCO_ONET_xwalk_full.csv")

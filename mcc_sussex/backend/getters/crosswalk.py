import pandas as pd
from mcc_sussex import PROJECT_DIR


def esco_onet_crosswalk() -> pd.DataFrame:
    return pd.read_csv(f"{PROJECT_DIR}/mcc_sussex/data/processed/ESCO_ONET_xwalk_full.csv")


def esco_soc_crosswalk() -> pd.ExcelFile:
    return pd.ExcelFile(f'{PROJECT_DIR}/mcc_sussex/data/raw/Draft ESCO crosswalk.xlsx')

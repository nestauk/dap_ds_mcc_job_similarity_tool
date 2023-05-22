import pandas as pd
from mcc_sussex import PROJECT_DIR


def esco_onet_crosswalk() -> pd.DataFrame:
    """gets crosswalk of ESCO to ONET published here https://esco.ec.europa.eu/en/use-esco/other-crosswalks

    Returns:
        pd.DataFrame: crosswalk of ONET occupation codes to ESCO occupation codes
    """
    return pd.read_csv(f"{PROJECT_DIR}/mcc_sussex/data/raw/esco_onet_crosswalk.csv")


def esco_soc_crosswalk() -> pd.ExcelFile:
    """gets draft ESCO to SOC crosswalk provided by the ONS

    Returns:
        pd.ExcelFile: crosswalk of ESCO occupation codes to SOC codes
    """
    return pd.ExcelFile(f'{PROJECT_DIR}/mcc_sussex/data/raw/Draft ESCO crosswalk.xlsx')

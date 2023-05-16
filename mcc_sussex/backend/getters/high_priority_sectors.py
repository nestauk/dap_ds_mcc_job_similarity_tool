import pandas as pd
import openpyxl
from mcc_sussex import PROJECT_DIR
from typing import Union
import yaml


def get_raw_sector_data(type: Union[str, bool] = None) -> Union[openpyxl.Workbook, pd.ExcelFile]:
    if type == "openpyxl":
        return openpyxl.load_workbook(f'{PROJECT_DIR}/mcc_sussex/data/raw/SOC Codes for 6 Key Sectors.xlsx')
    else:
        return pd.ExcelFile(f'{PROJECT_DIR}/mcc_sussex/data/raw/SOC Codes for 6 Key Sectors.xlsx')


def priority_sector_map() -> pd.DataFrame:
    return pd.read_csv(f'{PROJECT_DIR}/mcc_sussex/data/processed/esco_codes_to_priority_sectors.csv')


def sector_descriptions() -> dict:
    return yaml.safe_load(open(f'{PROJECT_DIR}/mcc_sussex/data/processed/sector_descriptions.yaml', 'r'))

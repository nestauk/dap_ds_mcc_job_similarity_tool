import pandas as pd
from mcc_sussex import PROJECT_DIR


def work_context():
    return pd.read_excel(f'{PROJECT_DIR}/mcc_sussex/data/raw//Work Context.xlsx', sheet_name='Work Context')


def occupations_work_context_vector():
    return pd.read_csv(f'{PROJECT_DIR}/mcc_sussex/data/interim/work_context_features/occupations_work_context_vector.csv').rename(columns={"conceptUri_x": "conceptUri"})

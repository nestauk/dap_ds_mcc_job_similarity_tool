import pandas as pd
from mcc_sussex import PROJECT_DIR


def work_context() -> pd.DataFrame:
    """Mapping of ONET SOC codes to work context ratings from here https://www.onetcenter.org/dictionary/24.2/excel/work_context.html

    Returns:
        pd.DataFrame: Mapping of ONET SOC codes to work context ratings
    """
    return pd.read_excel(f'{PROJECT_DIR}/mcc_sussex/data/raw/Work Context.xlsx', sheet_name='Work Context')


def occupations_work_context_vector() -> pd.DataFrame:
    """Work context vectors for each ESCO occupation created from similarity_matrics/generate_work_context_vectors.py

    Returns:
        pd.DataFrame: 57 dimensional vector for each ESCO occupation with a score for each 
    """
    return pd.read_csv(f'{PROJECT_DIR}/mcc_sussex/data/interim/work_context_features/occupations_work_context_vector.csv').rename(columns={"conceptUri_x": "conceptUri"})

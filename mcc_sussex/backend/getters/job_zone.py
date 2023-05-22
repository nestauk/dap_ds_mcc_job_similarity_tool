import pandas as pd
from mcc_sussex import PROJECT_DIR


def onet_job_zones() -> pd.DataFrame:
    """Job Zones for all ONET occupations from here https://www.onetonline.org/find/zone?z=0

    Returns:
        pd.DataFrame: ONET job zones per occupation
    """
    return pd.read_excel(f"{PROJECT_DIR}/mcc_sussex/data/raw/Job Zones.xlsx", sheet_name='Job Zones')


def onet_job_zone_reference() -> pd.DataFrame:
    """Additional information about each job zone from https://www.onetcenter.org/dictionary/21.3/excel/job_zone_reference.html

    Returns:
        pd.DataFrame: additional metadata for each job zone level
    """
    return pd.read_excel(f"{PROJECT_DIR}/mcc_sussex/data/raw/Job Zone Reference.xlsx", sheet_name="Job Zone Reference")


def education_training_experience() -> pd.DataFrame:
    """A mapping of ONET codes to education,training, and experience ratings from https://www.onetcenter.org/dictionary/20.1/excel/education_training_experience.html

    Returns:
        pd.DataFrame: table with ONET occupation codes and education, training, and experience ratings
    """
    return pd.read_excel(f"{PROJECT_DIR}/mcc_sussex/data/raw/Education, Training, and Experience.xlsx", sheet_name="Education, Training, and Experi")


def education_training_experience_categories() -> pd.DataFrame:
    """Additional information about each education, training, and experience category from https://www.onetcenter.org/dictionary/20.1/excel/ete_categories.html

    Returns:
        pd.DataFrame: table with data on onet education, training, and experience categories
    """
    return pd.read_excel(f"{PROJECT_DIR}/mcc_sussex/data/raw/Education, Training, and Experience Categories.xlsx", sheet_name="Education, Training, and Experi")


def linked_job_zones() -> pd.DataFrame:
    """ESCO occupations with matched ONET job zones created by data_preprocessing/link_occupations_to_job_zones.py

    Returns:
        pd.DataFrame: table with ESCO occupation codes and job zone ratings
    """
    return pd.read_csv(f"{PROJECT_DIR}/mcc_sussex/data/processed/linked_data/ESCO_occupations_Job_Zones.csv")

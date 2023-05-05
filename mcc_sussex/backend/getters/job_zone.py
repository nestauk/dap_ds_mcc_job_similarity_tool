import pandas as pd
from mcc_sussex import PROJECT_DIR


def onet_job_zones():
    return pd.read_excel(f"{PROJECT_DIR}/mcc_sussex/data/raw/Job Zones.xlsx", sheet_name='Job Zones')


def onet_job_zone_reference():
    return pd.read_excel(f"{PROJECT_DIR}/mcc_sussex/data/raw/Job Zone Reference.xlsx", sheet_name="Job Zone Reference")


def education_training_experience():
    return pd.read_excel(f"{PROJECT_DIR}/mcc_sussex/data/raw/Education, Training, and Experience.xlsx", sheet_name="Education, Training, and Experi")


def education_training_experience_categories():
    return pd.read_excel(f"{PROJECT_DIR}/mcc_sussex/data/raw/Education, Training, and Experience Categories.xlsx", sheet_name="Education, Training, and Experi")

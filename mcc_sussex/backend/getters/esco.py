import pandas as pd
import pickle
from mcc_sussex import PROJECT_DIR


def esco_occupations():
    return pd.read_csv(f"{PROJECT_DIR}/mcc_sussex/data/processed/ESCO_occupations.csv")


def esco_skills():
    return pd.read_csv(f"{PROJECT_DIR}/mcc_sussex/data/processed/ESCO_skills.csv")


def esco_occuptions_to_skills():
    return pd.read_csv(f"{PROJECT_DIR}/mcc_sussex/data/processed/ESCO_ocupation_To_skills.csv")


def esco_occupation_ids():
    return pd.read_csv(f"{PROJECT_DIR}/mcc_sussex/data/processed/esco_ids.csv")


def esco_skill_ids():
    return pd.read_csv(f"{PROJECT_DIR}/mcc_sussex/data/processed/esco_skill_ids.csv")


def esco_skill_hierarchy():
    return pd.read_csv(f"{PROJECT_DIR}/mcc_sussex/data/interim/esco_data_formatted.csv")


def esco_essential_skills_lookup():
    return pickle.load(open(f"{PROJECT_DIR}/mcc_sussex/data/processed/occupation_to_essential_skills.pickle", 'rb'))


def esco_optional_skills_lookup():
    return pickle.load(open(f"{PROJECT_DIR}/mcc_sussex/data/processed/occupation_to_essential_skills.pickle", 'rb'))


def esco_all_skills_lookup():
    return pickle.load(open(f"{PROJECT_DIR}/mcc_sussex/data/processed/occupation_to_all_skills.pickle", 'rb'))


def level_2_skills():
    return pd.read_csv(f"{PROJECT_DIR}/mcc_sussex/data/processed/level_2_hierarchy.csv")


def level_3_skills():
    return pd.read_csv(f"{PROJECT_DIR}/mcc_sussex/data/processed/level_3_hierarchy.csv")

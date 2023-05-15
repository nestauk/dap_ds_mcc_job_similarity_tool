import pandas as pd
from mcc_sussex.backend.getters.esco import esco_occuptions_to_skills
from mcc_sussex import PROJECT_DIR

skills = esco_occuptions_to_skills().drop_duplicates(subset="skillUri")
skill_ids = skills.assign(skill_id=range(len(skills))).astype(
    {"skill_id": 'int'})[["skillUri", "skill_id"]]

skill_ids.to_csv(
    f"{PROJECT_DIR}/mcc_sussex/data/processed/esco_skill_ids.csv")

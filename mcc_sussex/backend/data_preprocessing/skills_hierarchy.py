from mcc_sussex.backend.getters.esco import esco_skill_hierarchy, esco_skills, esco_skill_ids
from ast import literal_eval
from mcc_sussex import PROJECT_DIR

if __name__ == "__main__":

    hierarchy = esco_skill_hierarchy()
    skills_hierarchy = hierarchy.loc[hierarchy.type == 'preferredLabel'][[
        'description', 'hierarchy_levels']]
    skills_hierarchy['hierarchy_levels'] = skills_hierarchy['hierarchy_levels'].apply(
        literal_eval)
    skills_hierarchy = skills_hierarchy.explode(
        'hierarchy_levels', ignore_index=True)
    skills_hierarchy.dropna(inplace=True)
    skills_hierarchy = skills_hierarchy[skills_hierarchy["hierarchy_levels"].apply(
        lambda x: 'S' in x)]

    skills_hierarchy = skills_hierarchy.explode('hierarchy_levels')
    skills_hierarchy['hierarchy_levels'] = skills_hierarchy['hierarchy_levels'].str.split(
        ".")
    skills_hierarchy.dropna(inplace=True)

    skills_hierarchy = skills_hierarchy.loc[(skills_hierarchy["hierarchy_levels"].map(
        len) == 2) | (skills_hierarchy["hierarchy_levels"].map(len) == 3)]

    skills = esco_skills().merge(esco_skill_ids().rename(columns={
        "skillUri": "conceptUri"}), how="left", on="conceptUri")[["skill_id", "conceptUri", "preferredLabel"]]

    skills_hierarchy = skills_hierarchy.merge(
        skills, how="left", left_on="description", right_on="preferredLabel")

    level_2_hierarchy = skills_hierarchy.loc[(
        skills_hierarchy["hierarchy_levels"].map(len) == 2)]
    level_3_hierarchy = skills_hierarchy.loc[(
        skills_hierarchy["hierarchy_levels"].map(len) == 3)]

    level_2_hierarchy.to_csv(
        f"{PROJECT_DIR}/mcc_sussex/data/processed/level_2_hierarchy.csv")
    level_3_hierarchy.to_csv(
        f"{PROJECT_DIR}/mcc_sussex/data/processed/level_3_hierarchy.csv")

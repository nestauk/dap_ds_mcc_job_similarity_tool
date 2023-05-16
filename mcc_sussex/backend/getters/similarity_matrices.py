import numpy as np
from mcc_sussex import PROJECT_DIR


def essential_skill_similarity():
    return np.load(f'{PROJECT_DIR}/mcc_sussex/data/processed/sim_matrices/OccupationSimilarity_EssentialSkillsDescription_asymmetric.npy')


def optional_skill_similarity():
    return np.load(f'{PROJECT_DIR}/mcc_sussex/data/processed/sim_matrices/OccupationSimilarity_AllToEssentialSkillsDescription_asymmetric.npy')


def work_context_similarity():
    return np.load(f'{PROJECT_DIR}/mcc_sussex/data/processed/sim_matrices/OccupationSimilarity_ONET_Work_Context.npy')


def work_area_similarity():
    return np.load(f'{PROJECT_DIR}/mcc_sussex/data/processed/sim_matrices/OccupationSimilarity_ESCO_clusters_Level_2.npy')

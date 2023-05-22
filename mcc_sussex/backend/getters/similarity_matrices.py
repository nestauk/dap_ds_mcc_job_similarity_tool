import numpy as np
from mcc_sussex import PROJECT_DIR


def essential_skill_similarity() -> np.Array:
    """gets similarity matrix calculated from similarity_matrices/essential_skills_similarity.py

    Returns:
        np.Array: matrix of essential skill similarities between ESCO occupations 
    """
    return np.load(f'{PROJECT_DIR}/mcc_sussex/data/processed/sim_matrices/OccupationSimilarity_EssentialSkillsDescription_asymmetric.npy')


def optional_skill_similarity() -> np.Array:
    """gets similarity matrix calculated from similarity_matrices/optional_skills_similarity.py

    Returns:
        np.Array: similarity matrix of all to essential skill similarities between ESCO occupations
    """
    return np.load(f'{PROJECT_DIR}/mcc_sussex/data/processed/sim_matrices/OccupationSimilarity_AllToEssentialSkillsDescription_asymmetric.npy')


def work_context_similarity() -> np.Array:
    """gets similarity matrix calculated from similarity_matrices/generate_work_context_vectors.py

    Returns:
        np.Array: similarity matrix of work context vector similarities between ESCO occupations
    """
    return np.load(f'{PROJECT_DIR}/mcc_sussex/data/processed/sim_matrices/OccupationSimilarity_ONET_Work_Context.npy')


def work_activity_similarity() -> np.Array:
    """gets similarity matrix calculated from similarity_matrices/work_activity_similarity.py

    Returns:
        np.Array: similarity matrix of work activity vector similarities between ESCO occupations
    """
    return np.load(f'{PROJECT_DIR}/mcc_sussex/data/processed/sim_matrices/OccupationSimilarity_ESCO_clusters_Level_2.npy')

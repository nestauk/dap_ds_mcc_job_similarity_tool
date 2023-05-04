import numpy as np
from mcc_sussex import PROJECT_DIR


def load_embeddings() -> np.array:
    """return matrix of pre-calculatted embeddings of skills descriptions

    Returns:
        np.array: matrix of skill description embeddings
    """
    return np.load(f"{PROJECT_DIR}/mcc_sussex/data/interim/embeddings/embeddings_skills_description_SBERT.npy")

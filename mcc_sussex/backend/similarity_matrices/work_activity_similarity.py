"""calculates the euclidian distance between each work activity (level 2 skill) vector of each occupation and saves similarity matrix
"""
from mcc_sussex.backend.getters.esco import level_2_skills, esco_occuptions_to_skills, esco_essential_skills_lookup, esco_occupations, esco_occupation_ids
from mcc_sussex.backend.getters.similarity_matrices import essential_skill_similarity, optional_skill_similarity
from ast import literal_eval
from sklearn.preprocessing import normalize
import numpy as np
from scipy.spatial.distance import pdist, squareform
from mcc_sussex.backend.recommendations.transitions_utils import find_closest
from mcc_sussex import PROJECT_DIR
import pandas as pd

if __name__ == "__main__":

    level_2 = level_2_skills().set_index("skill_id")
    level_2["hierarchy_levels"] = level_2["hierarchy_levels"].apply(
        literal_eval).str.join(".")

    occs_to_skills = esco_occuptions_to_skills()
    node_to_essential_items = esco_essential_skills_lookup()

    occupations = pd.merge(left=esco_occupations(), right=esco_occupation_ids(),
                           how="left", on="conceptUri").set_index("id", drop=False)

    W_essential = essential_skill_similarity()
    W_all_to_essential = optional_skill_similarity()

    vector_dict = dict(
        zip(level_2.hierarchy_levels.unique(), range(len(level_2.hierarchy_levels.unique()))))

    occupation_vectors = np.zeros((len(occupations), len(vector_dict.keys())))

    for i in range(len(occupations)):
        #  NB: We're using the essential skills
        x_list = level_2.iloc[node_to_essential_items.items_list.loc[i]]['hierarchy_levels'].to_list(
        )
        for x in x_list:
            if x in vector_dict.keys():
                occupation_vectors[i, vector_dict[x]
                                   ] = occupation_vectors[i, vector_dict[x]] + 1
        occupation_vectors_norm = np.zeros(occupation_vectors.shape)

        for i in range(occupation_vectors_norm.shape[0]):
            occupation_vectors_norm[i, :] = normalize(
                occupation_vectors[i, :].reshape(1, -1))

    d_esco_level_2 = squareform(
        pdist(occupation_vectors, metric='euclidean'))

    d_esco_level_2_norm = (d_esco_level_2-np.min(d_esco_level_2)) / \
        (np.max(d_esco_level_2)-np.min(d_esco_level_2))

    W_esco_level_2 = 1 - d_esco_level_2_norm

    print(find_closest(None, W_esco_level_2,
          occupations[['id', 'preferredLabel']]).head(10))

    np.save(f'{PROJECT_DIR}/mcc_sussex/data/processed/sim_matrices/OccupationSimilarity_ESCO_clusters_Level_2.npy', W_esco_level_2)

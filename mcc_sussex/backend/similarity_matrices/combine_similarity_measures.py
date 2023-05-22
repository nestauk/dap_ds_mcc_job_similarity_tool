"""averages the four similarity scores (work context, work area, essential skill, optional skill) to generate the final similarity matrix
"""
from mcc_sussex.backend.getters.similarity_matrices import essential_skill_similarity, optional_skill_similarity, work_context_similarity, work_activity_similarity
from mcc_sussex.backend.getters.esco import esco_occupations, esco_occupation_ids
from mcc_sussex.backend.getters.work_context import occupations_work_context_vector
from mcc_sussex.backend.recommendations import compare_nodes_utils
import pandas as pd
from tqdm import tqdm
import numpy as np
from mcc_sussex import PROJECT_DIR

if __name__ == "__main__":
    W_essential = essential_skill_similarity()
    W_all_to_essential = optional_skill_similarity()
    W_work_context = work_context_similarity()
    W_work_area = work_activity_similarity()

    occupations = pd.merge(left=esco_occupations(), right=esco_occupation_ids(),
                           how="left", on="conceptUri").set_index("id", drop=False)

    # Get a list of occupations without the work context
    esco_to_work_context_vector = occupations_work_context_vector().set_index("id",
                                                                              drop=False)
    esco_with_work_context = esco_to_work_context_vector[esco_to_work_context_vector.has_vector == True].id.to_list(
    )
    occ_no_work_context = set(occupations.id.to_list()).difference(
        set(esco_with_work_context))

    # DEFINE THE WEIGHTS FOR EACH TYPE OF SIMILARITY MEASURE
    # FOR NOW THESE ARE .3, BUT WHEN WE ADD WORK ACTIVITIES THIS WILL BE .25
    p_1 = 0.25  # W_essential
    p_2 = 0.25  # W_all_to_essential
    p_3 = 0.25  # W_work_context
    p_4 = 0.25  # W_esco_level_2 (work activities)

    # If work context vector doesn't exist, redistribute the weights equally
    p_1x = p_1/(1-p_3)
    p_2x = p_2/(1-p_3)
    p_3x = p_3/(1-p_4)

    # Combined similarity matrix
    W_combined = np.zeros(W_essential.shape)
    for i in tqdm(range(len(W_combined)), total=len(W_combined)):
        for j in range(len(W_combined)):
            # If both occupations have a work context feature vector
            if (i in esco_with_work_context) & (j in esco_with_work_context):
                W_combined[i, j] = (p_1 * W_essential[i, j]) + (p_2 * W_all_to_essential[i, j]) + (
                    p_3 * W_work_area[i, j]) + (p_4 * W_work_context[i, j])
            # If one of the occupations don't have a work context feature vector
            else:
                W_combined[i, j] = (p_1x * W_essential[i, j]) + (p_2x *
                                                                 W_all_to_essential[i, j]) + (p_3x * W_work_area[i, j])

    print(W_combined.shape)

    # Choose a random occupation (or set occupation_id to some id)
    occupation_id = np.random.randint(len(occupations))
    occupation_id = 222

    # Print occupation's name
    row = occupations.loc[occupation_id]
    print(f"id: {row.id}, label: {row.preferredLabel}")

    # Find the closest neighbours
    closest = compare_nodes_utils.find_closest(
        occupation_id, W_combined, occupations[['preferredLabel']])
    print(closest.head(20))

    np.save(f'{PROJECT_DIR}/mcc_sussex/data/processed/sim_matrices/OccupationSimilarity_Combined.npy', W_combined)

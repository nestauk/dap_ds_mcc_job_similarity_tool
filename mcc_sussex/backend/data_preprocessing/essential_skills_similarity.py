from itertools import combinations_with_replacement
from mcc_sussex.backend.getters.embeddings import load_embeddings
from mcc_sussex.backend.getters.esco import esco_skills, esco_occupations, esco_occuptions_to_skills, esco_essential_skills_lookup, esco_all_skills_lookup
from mcc_sussex.backend.recommendations import compare_nodes_utils
from time import time
import numpy as np
from mcc_sussex import PROJECT_DIR

embeddings = load_embeddings()

# Load occupation and skills data
occupations = esco_occupations()
skills = esco_skills()
occupation_to_skills = esco_occuptions_to_skills()


# Import dataframe with the skills IDs for each occupation
node_to_essential_items = esco_essential_skills_lookup()
node_to_all_items = esco_all_skills_lookup()

n_occupations = len(occupations)
print(n_occupations)

# Choose sectors to compare (here, sectors correspond simply the major ISCO-08 groups; we use all sectors)
sectors = node_to_essential_items.sector.unique()
combinations_of_sectors = list(combinations_with_replacement(sectors, 2))
print(len(combinations_of_sectors))

# Perform the comparison!
comp_essential = compare_nodes_utils.CompareSectors(
    node_to_essential_items,
    embeddings,
    combinations_of_sectors,
    metric='cosine',
    symmetric=False)

t = time()
comp_essential.run_comparisons(dump=False)
comp_essential.collect_comparisons()
t_elapsed = time()-t
print('===============')
print(f"Total time elapsed: {t_elapsed:.0f} seconds")


# Check the most similar occupations for a random occupation
W = comp_essential.D.copy()
print(compare_nodes_utils.find_closest(None, W, comp_essential.nodes).head(7))

np.save(f'{PROJECT_DIR}/mcc_sussex/data/processed/sim_matrices/OccupationSimilarity_EssentialSkillsDescription_asymmetric.npy', W)
comp_essential.nodes.to_csv(
    f'{PROJECT_DIR}/mcc_sussex/data/processed/sim_matrices/OccupationSimilarity_EssentialSkillsDescription_Nodes.csv')

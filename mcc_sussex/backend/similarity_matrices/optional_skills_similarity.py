"""calculates the similarity between all essential skills of the origin occupation to all skills (essential + optional) in the destination occupation
"""
from mcc_sussex.backend.getters.esco import esco_skills, esco_occupations, esco_occuptions_to_skills, esco_essential_skills_lookup, esco_all_skills_lookup
from mcc_sussex.backend.getters.embeddings import load_embeddings
from mcc_sussex.backend.recommendations import compare_nodes_utils
from itertools import combinations_with_replacement
from time import time
import numpy as np
from mcc_sussex import PROJECT_DIR
import pandas as pd

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

# Set up "origin" sector and "destination" sectors

# Origin nodes
from_node_to_items = node_to_all_items.copy()
from_node_to_items.sector = 'origin'

# Destination nodes
to_node_to_items = node_to_essential_items.copy()
to_node_to_items.sector = 'destination'
to_node_to_items.id = to_node_to_items.id + n_occupations

# Combine all into one dataframe
node_to_items = pd.concat(
    [from_node_to_items, to_node_to_items]).reset_index(drop=True)

# Set up the combination of sectors to check
combos = [('origin', 'destination')]

# Perform the comparison!
comp_all_to_essential = compare_nodes_utils.CompareSectors(
    node_to_items,
    embeddings,
    combos,
    metric='cosine',
    symmetric=False)

t = time()
comp_all_to_essential.run_comparisons(dump=False)
comp_all_to_essential.collect_comparisons()
t_elapsed = time()-t
print('===============')
print(f"Total time elapsed: {t_elapsed:.0f} seconds")

# Select only the edges from the origin to the destination occupations
W_all_to_essential = comp_all_to_essential.D
i_edges = [edge[0] for edge in comp_all_to_essential.real_edge_list]
from_edges = np.array(comp_all_to_essential.real_edge_list)[
    np.where(np.array(i_edges) < n_occupations)[0]]

W_from_all_to_essential = np.zeros((n_occupations, n_occupations))
for edge in from_edges:
    W_from_all_to_essential[edge[0], edge[1] -
                            n_occupations] = W_all_to_essential[edge[0], edge[1]]

# Take care of nulls
W_from_all_to_essential[np.isinf(W_from_all_to_essential)] = 0
W_from_all_to_essential.shape

np.save(f'{PROJECT_DIR}/mcc_sussex/data/processed/sim_matrices/OccupationSimilarity_AllToEssentialSkillsDescription_asymmetric.npy', W_from_all_to_essential)

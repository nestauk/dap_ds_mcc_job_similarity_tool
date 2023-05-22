"""generates vectors for each ESCO occupation represesnting the score for each of the 57 ONET work contexts
"""
from mcc_sussex.backend.getters.esco import esco_occupations, esco_occupation_ids
from mcc_sussex.backend.getters.crosswalk import esco_onet_crosswalk
from mcc_sussex.backend.getters.work_context import work_context
from mcc_sussex.backend.recommendations import compare_nodes_utils
from sklearn.preprocessing import normalize
from scipy.spatial.distance import pdist, squareform
from mcc_sussex import PROJECT_DIR
import numpy as np
import pandas as pd

# ESCO occupations
occupations = pd.merge(left=esco_occupations(), right=esco_occupation_ids(),
                       how="left", on="conceptUri").set_index("id", drop=False)
occupations.index = occupations.index.set_names("row_num")
# Crosswalk between ESCO and O*NET
esco_onet_xwalk = pd.merge(
    left=esco_onet_crosswalk().rename(columns={"concept_uri": "conceptUri"}), right=esco_occupation_ids(), how="left", on="conceptUri"
).set_index("id", drop=False).drop_duplicates(subset="id")

esco_onet_xwalk = esco_onet_xwalk.loc[esco_onet_xwalk["Type of Match"] != "wrongMatch"]
esco_onet_xwalk.index = esco_onet_xwalk.index.set_names("row_num")
esco_onet_xwalk.dropna(subset="id", inplace=True)


# O*NET Work Context dataset
onet_work_context = work_context()

output_folder = f'{PROJECT_DIR}/mcc_sussex/data/processed/sim_matrices/'

unique_features = onet_work_context['Element Name'].unique()
unique_features_id = onet_work_context['Element ID'].unique()

x = np.argsort(unique_features_id)
unique_features = unique_features[x]
unique_features_id = unique_features_id[x]

# Find the unique ONET codes in the Work Context dataset
unique_onets = onet_work_context['O*NET-SOC Code'].unique()

# Take the rows which correspond to the aggregated scores for each occupations' work context feature
df_work_context = onet_work_context[onet_work_context['Scale ID'].isin([
    'CT', 'CX'])]

# Dictionary mapping work context feature ID to integers (i.e., to the element in the work context vector)
map_work_context_to_int = dict(
    zip(unique_features_id, range(len(unique_features_id))))

# Empty arrays to hold the vectors
work_context_vectors = np.zeros((len(unique_onets), len(unique_features)))

# For each ONET occupation...
for j in range(len(unique_onets)):
    # ...select all features
    dff = df_work_context[df_work_context['O*NET-SOC Code'] == unique_onets[j]]
    for i, row in dff.iterrows():
        # Assign each work context vector element its value
        v = map_work_context_to_int[row['Element ID']]
        work_context_vectors[j, v] = row['Data Value']


work_context_vectors_rescaled = work_context_vectors.copy()

# All features are rated starting from 1
min_val = 1
max_vals = []

for j, element_id in enumerate(list(map_work_context_to_int.keys())):

    # Check which is the maximal value for the particular feature
    if 'CT' in onet_work_context[(onet_work_context['Element ID'] == element_id)]['Scale ID'].to_list():
        max_val = 3
    else:
        max_val = 5

    max_vals.append(max_val)

    # Rescale
    work_context_vectors_rescaled[:, j] = (
        work_context_vectors[:, j]-min_val)/(max_val-min_val)

    work_context_vectors_norm = np.zeros(
        (len(unique_onets), len(unique_features)))

for j in range(work_context_vectors_rescaled.shape[0]):
    work_context_vectors_norm[j, :] = normalize(
        work_context_vectors_rescaled[j, :].copy().reshape(1, -1))


# Check the vector of a random ONET occupation
# sort the work context features based on their intensity ('vector_value_norm')
i = np.random.randint(len(unique_onets))
onet = unique_onets[i]
df = onet_work_context[(onet_work_context['O*NET-SOC Code'] == onet) &
                       (onet_work_context['Scale ID'].isin(['CX', 'CT']))].sort_values('Element ID').copy().reset_index(drop=True)
df = df[['O*NET-SOC Code', 'Title', 'Element ID', 'Element Name', 'Data Value']]
df['vector_value'] = work_context_vectors[i, :]
df['vector_value_rescaled'] = work_context_vectors_rescaled[i, :]
df['vector_value_norm'] = work_context_vectors_norm[i, :]
df.sort_values('vector_value_norm', ascending=False)

# Add a zero-vector that will be assigned to ESCO occupations without a crosswalked ONET occupation
work_context_vectors_norm_z = np.concatenate(
    (work_context_vectors_norm, np.zeros((1, len(unique_features)))), axis=0)
work_context_vectors_rescaled_z = np.concatenate(
    (work_context_vectors_rescaled, np.zeros((1, len(unique_features)))), axis=0)

work_context_vectors_rescaled_z.shape

# Dataframe with the unique ONET codes in the Work Context dataset
unique_onets_df = pd.DataFrame(
    data={'onet_code': unique_onets, 'j': list(range(len(unique_onets)))})

# Dataframe linking ESCO occupation to a work context vector
esco_to_work_context_vector = occupations.merge(esco_onet_xwalk.merge(
    unique_onets_df, on='onet_code', how='left'), how="left", on="id")

print(len(esco_to_work_context_vector))
# ESCO occupations without work contexts
esco_no_work_context = esco_to_work_context_vector[esco_to_work_context_vector['j'].isnull(
)].id.to_list()


print(f"{len(esco_no_work_context)} ESCO occupations do not have work context vectors")

# ONET occupations without work context vectors
# pd.set_option('max_colwidth', 200)
# esco_onet_xwalk.iloc[esco_no_work_context][[
#    'onet_code', 'onet_occupation']].drop_duplicates().sort_values('onet_code')

# Assign the zero-vector to the ESCO occupations without work context data
esco_to_work_context_vector['has_vector'] = True
esco_to_work_context_vector.loc[esco_to_work_context_vector.index.isin(
    esco_no_work_context), 'has_vector'] = False
esco_to_work_context_vector.loc[esco_to_work_context_vector.index.isin(
    esco_no_work_context), 'j'] = len(
    work_context_vectors_norm_z)-1

# Create the normalised ESCO work context vectors
work_context_vectors_esco_norm = work_context_vectors_norm_z[esco_to_work_context_vector['j'].astype(
    int).to_list(), :]
print(work_context_vectors_esco_norm.shape)

# Create the non-normalised ESCO work context vectors
work_context_vectors_esco = work_context_vectors_rescaled_z[esco_to_work_context_vector['j'].astype(
    int).to_list(), :]
print(work_context_vectors_esco.shape)

# check example
print(occupations[occupations.preferredLabel.str.contains('concierge')])

# Check the work context vector of a random ESCO occupation
i = np.random.randint(len(occupations))
i = 329
print(i, occupations.loc[i].preferredLabel)
df = pd.DataFrame({'Element Name': unique_features,
                   'vector_value_norm': work_context_vectors_esco_norm[i, :],
                  'vector_value_rescaled': work_context_vectors_esco[i, :]})
print(df.sort_values('vector_value_norm', ascending=False).head())

# compare the work context vectors
# Distances
D_work_context = squareform(
    pdist(work_context_vectors_esco_norm, metric='euclidean'))
D_work_context.shape

# Normalise the distances between 0 and 1 and caclulate similarities
D_work_context_norm = (D_work_context-np.min(D_work_context)) / \
    (np.max(D_work_context)-np.min(D_work_context))
W_work_context_norm = 1 - D_work_context_norm

# Choose a random occupation (or set occupation_id to some id)
occupation_id = np.random.randint(len(occupations))

# Print occupation's name
row = occupations.loc[occupation_id]
print(f"id: {row.id}, label: {row.preferredLabel}")


# Find the closest neighbours
closest = compare_nodes_utils.find_closest(
    occupation_id, W_work_context_norm, occupations[['preferredLabel']])
print(closest.head(20))

# Create a version of the similarity matrix with nulls for occupations without work context vectors
W_work_context_norm_nan = W_work_context_norm.copy()
W_work_context_norm_nan[esco_no_work_context, :] = np.nan
W_work_context_norm_nan[:, esco_no_work_context] = np.nan

# Save the similarity matrices
np.save(f'{output_folder}OccupationSimilarity_ONET_Work_Context.npy',
        W_work_context_norm)
np.save(f'{output_folder}OccupationSimilarity_ONET_Work_Context_nan.npy',
        W_work_context_norm_nan)

# Save the work context vectors
np.save(f'{PROJECT_DIR}/mcc_sussex/data/interim/work_context_features/ESCO_work_context_vectors_norm.npy',
        work_context_vectors_esco_norm)
np.save(f'{PROJECT_DIR}/mcc_sussex/data/interim/work_context_features/ESCO_work_context_vectors.npy',
        work_context_vectors_esco)

df = pd.DataFrame({
    'vector_element': list(range(len(unique_features))),
    'element_name': unique_features,
    'element_id': unique_features_id})
df.to_csv(
    f'{PROJECT_DIR}/mcc_sussex/data/processed/work_context_vector_features.csv', index=False)

esco_to_work_context_vector.to_csv(
    f'{PROJECT_DIR}/mcc_sussex/data/interim/work_context_features/occupations_work_context_vector.csv', index=False)

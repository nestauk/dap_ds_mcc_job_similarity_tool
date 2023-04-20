"""builds the file work_context.csv
"""
from backend.getters.data_loader import getter_occupation_en
from backend.getters.work_context import get_onet_esco_crosswalk, get_onet_work_context
from backend import logger, BUCKET_NAME
import pandas as pd
import numpy as np
from sklearn.preprocessing import normalize
from nesta_ds_utils.loading_saving import S3


def match_to_number(match: str) -> int:
    """converts the strings describing the match type to an integer so they can be easily sorted

    Args:
        match (str): type of match (options: exactMatch, closeMatch, narrowMatch, broadMatch, relatedMatch, wrongMatch)

    Returns:
        int: integer replacement for string value
    """
    if match == 'exactMatch':
        return 0
    elif match == 'closeMatch':
        return 1
    elif match == 'narrowMatch':
        return 2
    elif match == 'broadMatch':
        return 3
    elif match == 'relatedMatch':
        return 4
    elif match == 'wrongMatch':
        return 99
    else:
        return 99


def keep_best_match(tab: pd.DataFrame) -> pd.DataFrame:
    """gets the best match of onet occupations to esco occupations

    Args:
        tab (pd.DataFrame): all possible matches of esco occupations to a given onet occupation from onet to esco crosswalk

    Returns:
        pd.DataFrame: 1-1 crosswalk with the best match for the onet occupation from esco
    """
    tab['Match Number'] = tab.apply(
        lambda x: match_to_number(x['Type of Match']), 1)
    if len(tab) > 0:
        return tab.sort_values('Match Number').iloc[0]
    else:
        return tab.iloc[0]


if __name__ == "__main__":
    logger.info("Matching ESCO uris to ONET uris")
    occs = getter_occupation_en()
    crosswalk = get_onet_esco_crosswalk()
    q = pd.merge(occs, crosswalk, left_on='conceptUri',
                 right_on='ESCO or ISCO URI', how='left')
    unique_crosswalk = q.groupby('conceptUri').apply(keep_best_match)

    logger.info("Formatting onet work contexts")
    onet_work_context = get_onet_work_context()
    unique_features = onet_work_context['Element Name'].unique()
    unique_features_id = onet_work_context['Element ID'].unique()
    # sort the work context names and ids
    x = np.argsort(unique_features_id)
    unique_features = unique_features[x]
    unique_features_id = unique_features_id[x]
    unique_onets = onet_work_context['O*NET-SOC Code'].unique()
    # Take the rows which correspond to the aggregated scores for each occupations' work context feature
    # note: the raw data contains a percentage frequency of the times that an occupation had the given "level" of the work context
    # the rows containing CX represent the weighted average level
    # CX represents the levels being on a 1-5 scale and CT represents a 1-3 scale
    df_work_context = onet_work_context[onet_work_context['Scale ID'].isin([
                                                                           'CT', 'CX'])]

    logger.info(
        "Creating a vector for each job that holds the aggregated score for each work context")
    # Dictionary mapping work context feature ID to integers (i.e., to the element in the work context vector)
    map_work_context_to_int = dict(
        zip(unique_features_id, range(len(unique_features_id))))
    # Empty arrays to hold the vectors
    work_context_vectors = np.zeros((len(unique_onets), len(unique_features)))
    # For each ONET occupation...
    for j in range(len(unique_onets)):
        # ...select all features
        dff = df_work_context[df_work_context['O*NET-SOC Code']
                              == unique_onets[j]]
        for i, row in dff.iterrows():
            # Assign each work context vector element its value
            v = map_work_context_to_int[row['Element ID']]
            work_context_vectors[j, v] = row['Data Value']

    logger.info(
        "Rescaling and normalizing vectors as some values are scaled 1-5 and some are 1-3")
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

    # apply l2 norm on rescaled vectors
    for j in range(work_context_vectors_rescaled.shape[0]):
        work_context_vectors_norm[j, :] = normalize(
            work_context_vectors_rescaled[j, :].copy().reshape(1, -1))

    logger.info(
        "Formatting and saving dataframe with work context vectors and esco ids")
    unique_onets_df = pd.DataFrame(
        data={'onet_code': unique_onets, 'j': list(range(len(unique_onets)))})
    occ_data_with_indices = pd.merge(
        unique_crosswalk, unique_onets_df, left_on='O*NET Id', right_on='onet_code', how='left')

    occ_data_with_indices['Work Context'] = occ_data_with_indices.apply(lambda x: np.repeat(np.NaN, 57) if np.isnan(
        x['j']) else work_context_vectors_norm[int(x['j'])], 1)

    work_context = pd.DataFrame(
        np.vstack(occ_data_with_indices['Work Context'].values))
    work_context['conceptUri'] = occ_data_with_indices['conceptUri']
    S3.upload_obj(work_context, BUCKET_NAME, "occupation_work_contexts.csv")

    logger.info("Formatting and saving lookup of work context ids to names")
    id_df = pd.DataFrame.from_dict(map_work_context_to_int, orient="index").join(onet_work_context[[
        "Element ID", "Element Name"]].drop_duplicates().set_index("Element ID"), how="left")
    S3.upload_obj(id_df, BUCKET_NAME, "work_context_id_lookup.csv")

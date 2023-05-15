# -*- coding: utf-8 -*-
import logging

import pandas as pd
import pickle
from mcc_sussex import PROJECT_DIR
from mcc_sussex.backend.getters.esco import esco_occupations, esco_occuptions_to_skills, esco_skills, esco_occupation_ids, esco_skill_ids

logger = logging.getLogger(__name__)


def main():
    """
    Runs data processing scripts to turn raw data from (../raw) into
    cleaned data
    """
    occupation_skill_lists()
    return


def occupation_skill_lists():
    """
    Create essential and optional skill lists for each occupation, and
    dataframes with skills of different types (necessary for skills comparison)
    """

    # Import data on occupations and skills
    occupations = pd.merge(left=esco_occupations(), right=esco_occupation_ids(),
                           how="left", on="conceptUri").set_index("id", drop=False)

    occupations["sector"] = occupations.apply(
        lambda x: int(list(str(x.iscoGroup))[0]), axis=1)
    occupations.index.name = None

    occupation_to_skills_temp = pd.merge(left=esco_occuptions_to_skills().rename(columns={"occupationUri": "conceptUri"}), right=esco_occupation_ids(),
                                         how="left", on="conceptUri")
    occupation_to_skills = pd.merge(left=occupation_to_skills_temp, right=esco_skill_ids(
    ), how="left", on="skillUri").set_index("id", drop=False)
    occupation_to_skills.index.name = None

    # Lists of essential and optional skills IDs for each parent node (occupations)
    all_essential_items = []
    all_optional_items = []

    for i, row in occupations.iterrows():
        essential_items = occupation_to_skills[
            (occupation_to_skills.id == row.id) &
            (occupation_to_skills.relationType == 'essential')
        ].skill_id.to_list()
        all_essential_items.append(sorted(essential_items))

        optional_items = occupation_to_skills[
            (occupation_to_skills.id == row.id) &
            (occupation_to_skills.relationType == 'optional')
        ].skill_id.to_list()
        all_optional_items.append(sorted(optional_items))

    # Lists of all skill IDs for each occupation
    all_items = []
    for j in range(len(occupations)):
        all_items.append(sorted(list(
            set(all_essential_items[j]).union(set(all_optional_items[j]))
        )))

    logger.info('Lists of essential, optional and all skills have been created!')

    # Create dataframes with occupation nodes and their children nodes (skills)

    # Dataframe for essential children nodes
    node_to_essential_items = pd.DataFrame(data={
        'id': occupations.id,
        'occupation': occupations.preferredLabel,
        'items_list': all_essential_items,
        'sector': occupations.sector
    })

    # Dataframe for optional children nodes
    node_to_optional_items = pd.DataFrame(data={
        'id': occupations.id,
        'occupation': occupations.preferredLabel,
        'items_list': all_optional_items,
        'sector': occupations.sector
    })

    # Dataframe for all children nodes
    node_to_all_items = pd.DataFrame(data={
        'id': occupations.id,
        'occupation': occupations.preferredLabel,
        'items_list': all_items,
        'sector': occupations.sector
    })

    # Save the lists of processed dataframes
    pickle.dump(node_to_essential_items, open(
        f'{PROJECT_DIR}/mcc_sussex/data/processed/occupation_to_essential_skills.pickle', 'wb'))
    pickle.dump(node_to_optional_items, open(
        f'{PROJECT_DIR}/mcc_sussex/data/processed/occupation_to_optional_skills.pickle', 'wb'))
    pickle.dump(node_to_all_items, open(
        f'{PROJECT_DIR}/mcc_sussex/data/processed/occupation_to_all_skills.pickle', 'wb'))
    logger.info('Dataframes of children nodes have been created!')


if __name__ == "__main__":

    try:
        msg = f"Creating occupation-skills dataframes..."
        logger.info(msg)
        main()
    except (Exception, KeyboardInterrupt) as e:
        logger.exception("Failed!", stack_info=True)
        raise e

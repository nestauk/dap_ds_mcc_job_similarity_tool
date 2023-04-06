from nesta_ds_utils.loading_saving import S3
from mcc_sussex import BUCKET_NAME
from typing import Dict, List, Union
import json

def get_similarity_data(local: bool=True) -> Dict[
    str, 
    List[Dict[str, Union[str, float, List[str]]]]
    ]:
    """gets the pre-calculated job similarity dictionary to use as the backend of the app

    Args:
        local[bool, Optional]: If True load data form local directory, Default to True.
    Returns:
        Dict[str, List[Dict[str, Union[str, float, List[str]]]]]: structured as
        {current_job_name: [{job_name: str, # Best match
                     similarity_score: float,
                     matching_skills: List[str],
                     missing_skills: List[str]},
                     ...
                     {job2_id: str, # Worst match
                     similarity_score: float,
                     matching_skills: List[str],
                     missing_skills: List[str]},
                     ]
        ...}
    """

    if local:
        with open("mcc_sussex/data/job_similarity_dict.json") as json_file:
            return json.load(json_file)
    else:
        return S3.download_obj(BUCKET_NAME, "job_similarity_dict.json", download_as= "dict")
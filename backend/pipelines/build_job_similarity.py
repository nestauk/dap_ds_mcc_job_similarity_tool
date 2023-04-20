from backend.pipelines.job_search import JobSearch
from nesta_ds_utils.loading_saving import S3
from backend.pipelines.job import num_of_jobs
import json

CONFIGS = json.load(open('backend/config/CONFIG.json'))

def build_job_similarity_dict(knn: int=3) -> dict:
    """Build dictionary with the top `knn` best matches for all jobs.

    Args:
        knn (int, optional): Number of best matches per job. Defaults to 3.

    Returns: 
        dict: Dictionary with best `knn` matches per job, per sector with the following structure:
        {
            job_id: {
                    sector_name: [
                                    {job_name: str, # Best match
                                    similarity_score: float,
                                    matching_skills: List[str],
                                    missing_skills: List[str]},
                                    ...
                                    {job2_id: str, # Worst match
                                    similarity_score: float,
                                    matching_skills: List[str],
                                    missing_skills: List[str]},
                                 ]
                                 
        }
    """

    j_dict = dict()
    for j in range(10): #num_of_jobs):
        print(j)
        aux_dict = dict()
        for sector in ['Show all'] + CONFIGS['SECTORS']:
            J = JobSearch(job_history=[j], sector=sector)
            top_matches = J.get_best_matches(numb_of_matches= knn)
            aux_dict[sector] = [
                dict(
                    {"job_name": top_matches[m].job2.job_name, 
                    "skill_similarity": float(1 - top_matches[m].compare_jobs()[0])},
                     **J.job_similarity(sector)[m].explain_skills(essential=True)
                     ) for m in range(knn)
                ]
        j_dict[J.jobs[0].job_name] = aux_dict.copy()
    return j_dict




def build_and_upload():
    """Build the job dictionary and upload it to S3. 
    """
    # Execute only if run as a script
    BUCKET_NAME = "mcc-sussex"
    data_file_name = "job_similarity_dict_sector_filter.json"

    job_dict = build_job_similarity_dict()
    S3.upload_obj(job_dict, BUCKET_NAME, data_file_name)
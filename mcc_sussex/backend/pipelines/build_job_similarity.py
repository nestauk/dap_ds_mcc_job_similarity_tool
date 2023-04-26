from mcc_sussex.backend.pipelines.job_search import JobSearch
from nesta_ds_utils.loading_saving import S3
from mcc_sussex.backend.pipelines.job import num_of_jobs
from mcc_sussex import PROJECT_DIR
import json


def build_job_similarity_dict(knn: int = 3) -> dict:
    """Build dictionary with the top `knn` best matches for all jobs.

    Args:
        knn (int, optional): Number of best matches per job. Defaults to 3.

    Returns: 
        dict: Dictionary with best `knn` matches per job with the following structure:
        {
            job_id: [
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
    for j in range(num_of_jobs):
        J = JobSearch(job_history=[j])
        top_matches = J.get_best_matches(numb_of_matches=knn)
        j_dict[J.jobs[0].job_name] = [
            dict(
                {"job_name": top_matches[m].job2.job_name,
                 "work_context_similarity": top_matches[m].explain_work_context(),
                 "skill_similarity": float(1 - top_matches[m].essential_skill_similarity_score)},
                **top_matches[m].explain_skills(essential=True),
            ) for m in range(knn)
        ]
    return j_dict


def build_and_upload():
    """Build the job dictionary and upload it to S3. 
    """
    # Execute only if run as a script
    BUCKET_NAME = "mcc-sussex"
    data_name = "job_similarity_dict_work_context.json"

    job_dict = build_job_similarity_dict(10)
    S3.upload_obj(job_dict, BUCKET_NAME, data_name)

    with open(f"{PROJECT_DIR}/mcc_sussex/data/{data_name}", "w") as f:
        json.dump(job_dict, f)


if __name__ == "__main__":
    build_and_upload()


from backend.pipelines.job_search import JobSearch
from nesta_ds_utils.loading_saving import S3
from backend.pipelines.job import num_of_jobs


def build_job_similarity_dict(knn: int=3) -> dict:
    """Build dictionary with the top `knn` best matches for all jobs.

    Args:
        knn (int, optional): Number of best matches per job. Defaults to 3.

    Returns: 
        dict: Dictionary with best `knn` matches per job with the following structure:
        {
            job_id: [
                [job_match_1_id, job_match_1_score],  #best match
                [job_match_2_id, job_match_2_score],
                ...
                [job_match_knn_id, job_match_knn_score] 
             ]
        }
    """

    j_dict = dict()
    for j in range(10): #num_of_jobs):
        print(j)
        top_matches = JobSearch(job_history=[j]).get_best_matches(numb_of_matches= knn + 1)
        j_dict[j] = [[int(top_matches[m].job2.job_index), 
                    float(top_matches[m].compare_jobs()[0])]
                    for m in range(1, knn + 1)]

    return j_dict


def build_and_upload():
    """Build the job dictionary and upload it to S3. 
    """
    # Execute only if run as a script
    BUCKET_NAME = "mcc-sussex"

    job_dict = build_job_similarity_dict()
    S3.upload_obj(job_dict, BUCKET_NAME, "job_similarity_dict.json")
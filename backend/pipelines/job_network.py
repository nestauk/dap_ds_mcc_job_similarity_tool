from backend.pipelines.job_search import JobSearch

def build_job_similarity_dict(knn: int=3)->dict:
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
    for j in range(1):
        top_matches = JobSearch(job_history=[j]).get_best_matches(numb_of_matches= knn + 1)
        j_dict[j] = [[top_matches[m].job2.job_index, 
                    top_matches[m].compare_jobs()[0]] 
                    for m in range(1, knn + 1)]

    return j_dict
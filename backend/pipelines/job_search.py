import backend.pipelines.job as job
import json
import numpy as np

CONFIGS = json.load(open('backend/config/CONFIG.json'))

# Initialize job list
def initialise_job_list(num_of_jobs):
    job_list = [job.Job(i) for i in np.arange(num_of_jobs)]
    return job_list

# Initialize job list
def initialise_job_list_sectors(num_of_jobs):
    full_list = [job.Job(i) for i in np.arange(num_of_jobs)]
    job_list = dict({"Show all": full_list},
    **{sec: [j for j in full_list if sec in j.sector] for sec in CONFIGS['SECTORS']})

    return job_list

# Get job list with specified number of jobs
job_list = initialise_job_list_sectors(num_of_jobs=job.num_of_jobs)

class JobSearch():

    def __init__(self, job_history, sector="Show all"):
        # Initialize job objects with job_history IDs
        self.jobs = [job.Job(x) for x in job_history]
        # Calculate similarity between each job in job_history and all jobs in job_list
        self.job_matches = self.job_similarity(sector)

    # Get the top n job matches
    def get_best_matches(self, numb_of_matches):
        return self.job_matches[:numb_of_matches]

    # Calculate similarity between each job in job_history and all jobs in job_list
    def job_similarity(self, sector):
        # Create an array of compareJobs objects for each job in job_list
        compared_jobs = np.array([
            job.CompareJobs(self.jobs, new_job) for new_job in job_list[sector] 
            if new_job.job_index != self.jobs[0].job_index
            ])
        # Create an array of comparison scores for each compared job pair
        similarities = np.vstack([x.comparison for x in compared_jobs])
        # Sort compared jobs based on mean similarity score
        sorted_jobs = np.argsort(np.nanmean(similarities, 1))
        # Return compared jobs in sorted order
        return compared_jobs[sorted_jobs]


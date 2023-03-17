import backend.job as job
import json
import numpy as np

CONFIGS = json.load(open('backend/CONFIG.json'))

def initialise_job_list(num_of_jobs):
    job_list = [job.Job(i) for i in np.arange(num_of_jobs)]
    return job_list

job_list = initialise_job_list(num_of_jobs=job.num_of_jobs)

class JobSearch():

    def __init__(self, job_history):

        self.jobs = [job.Job(x) for x in job_history]
        self.job_matches = self.job_similarity()

    def get_best_matches(self, numb_of_matches):
        return self.job_matches[:numb_of_matches]


    def job_similarity(self):
        compared_jobs = np.array([job.compareJobs(self.jobs, job_i) for job_i in job_list])
        similarites = np.vstack([x.comparison for x in compared_jobs])
        

        sorted_job = np.argsort(np.nanmean(similarites,1))
        return compared_jobs[sorted_job]


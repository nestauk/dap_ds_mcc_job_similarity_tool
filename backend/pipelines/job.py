import numpy as np
import json
from backend.getters.data_loader import load_data
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.optimize import linear_sum_assignment as LSA
import math

CONFIGS = json.load(open('backend/config/CONFIG.json'))

occs, skill_occs, skills, bert_skills = load_data()
num_of_jobs = len(occs)

def sigmoid(x):
    ax_b = (50*x) - 43.5
    return 1 / (1 + math.exp(-1*ax_b))


class Job:
    # Define the Job class that takes a job_index as an input parameter for initialization
    def __init__(self, job_index):
        # Extract the job name and URI from the occs dataframe using the given job_index
        self.job_name = occs.iloc[job_index]['preferredLabel']
        self.uri = occs.iloc[job_index]['conceptUri']
        
        # Set the job_index instance variable
        self.job_index = job_index
        
        # Extract the essential and optional skills for the job using the get_skills method
        self.essential_skills = self.get_skills(essential=True)
        self.optional_skills = self.get_skills(essential=False)
        
        # Compute the embeddings for the essential and optional skills using the get_embedding method
        self.essential_embedding = self.get_embedding(essential=True)
        self.optional_embedding = self.get_embedding(essential=False)

    # Define the get_skills method to extract the essential or optional skills for a given occupation URI
    def get_skills(self, essential):
        # Extract all skills for the given occupation URI
        job_skills = skill_occs[skill_occs['occupationUri'] == self.uri]
        
        if essential:
            # If essential is True, filter the skills to only include essential skills
            skills = job_skills[job_skills['relationType'] == 'essential']['skillUri']
        else:
            # Otherwise, include all skills (essential and optional)
            skills = job_skills['skillUri']
        
        return skills
    
    # Define the get_embedding method to compute the embeddings for a given set of skills (either essential or optional)
    def get_embedding(self, essential):
        if essential:
            # If essential is True, extract the essential skills and corresponding embeddings from the bert_skills table
            embedding_table = pd.merge(self.essential_skills, bert_skills, on='skillUri')
        else:
            # Otherwise, extract all skills and corresponding embeddings from the bert_skills table
            embedding_table = pd.merge(self.optional_skills, bert_skills, on='skillUri')
        
        # Drop the 'skillUri' column from the resulting embedding table
        embedding_table = embedding_table.drop(['skillUri'], axis=1)
        
        return embedding_table

class CompareJobs:
    
    def __init__(self, job_history, job2):
        """
        Initializes the CompareJobs class with job_history and job2.
        """
        self.job_history = job_history
        self.job1 = job_history[0]
        self.job2 = job2
        self.weighting_array = np.array([1, 2, 3]) # default weights
        
        # call compare_jobs method to calculate similarity scores
        self.comparison = self.compare_jobs()
    
    def skill_similarity(self, essential):
        """
        Calculates the similarity score between job_history and job2 based on essential or optional skills.
        
        Args:
            essential (bool): If True, calculate similarity based on essential skills. 
                              If False, calculate similarity based on optional skills.
        
        Returns:
            similarity_score (float): The similarity score between job_history and job2.
            matches (list): List of tuples where each tuple contains the indices of matching skills.
            values (list): List of similarity scores for each matching skill pair.
        """
        if essential:
            embedding_1 = np.concatenate([x.essential_embedding for x in self.job_history])
            #weights = np.repeat(self.weighting_array, [len(x.essential_embedding) for x in self.job_history]).reshape(-1, 1)
        else:
            embedding_1 = np.concatenate([x.optional_embedding for x in self.job_history])
            #weights = np.repeat(self.weighting_array, [len(x.optional_embedding) for x in self.job_history]).reshape(-1, 1)

        embedding_2 = self.job2.essential_embedding
        
        # check if either embedding is empty, return 1 for similarity score and empty lists for matches and values
        if embedding_2.shape[0] == 0 or embedding_1.shape[0] == 0:
            return 1, [], []

        # calculate cosine similarity and pass to LSA to reduce dimensionality
        cs = -1 * cosine_similarity(embedding_1, embedding_2)
        lsa = LSA(cs)
        skill_pairs = np.array([sigmoid(-1 * cs[x1, x2]) for x1, x2 in zip(lsa[0], lsa[1])])
        similarity_score = 1 - (sum(skill_pairs) / embedding_2.shape[0]) # calculate similarity score
        matches = zip(lsa[0], lsa[1])
        values = skill_pairs.tolist()
        return similarity_score, matches, values

    def work_area_similarity(self):

        if np.isnan(self.job2.work_area).any() or np.isnan(np.vstack([x.work_area for x in self.job_history])).all(0).any():
            return np.nan
        work_area_differences = np.vstack([x.work_area for x in self.job_history]) - self.job2.work_area

        minimum_difference = np.nanmin(work_area_differences, 0)
        return np.linalg.norm(minimum_difference)

    def work_context_similarity(self):

        if np.isnan(self.job2.work_context).any() or np.isnan(np.vstack([x.work_context for x in self.job_history])).all(0).any():
            return np.nan

        work_context_differences = np.vstack([x.work_context for x in self.job_history]) - self.job2.work_context
        minimum_difference = np.nanmin(work_context_differences, 0)
        return np.linalg.norm(minimum_difference)

    def compare_jobs(self):
        essential_skill_similarity_score = self.skill_similarity(essential = True)[0]
        optional_skill_similarity_score = self.skill_similarity(essential = False)[0]
        #work_context_similarity_score = self.work_context_similarity()
        #work_area_similarity_score = self.work_area_similarity()
        return essential_skill_similarity_score, optional_skill_similarity_score , 0, 0#,work_context_similarity_score, work_area_similarity_score


    def explain_skills(self, essential):
        _, matches, values = self.skill_similarity(essential)
        matches = list(matches)
        if essential:
            job1_skills = skills.iloc[[self.job1.essential_skills[x[0]] for x in matches]]['preferredLabel'].values
        else:
            job1_skills = skills.iloc[[self.job1.optional_skills[x[0]] for x in matches]]['preferredLabel'].values
        
        job2_skills = skills.iloc[[self.job2.essential_skills[x[1]] for x in matches]]['preferredLabel'].values

        skill_pairs = np.array(list(zip(job1_skills, job2_skills)))
        order = np.argsort(values)[::-1]
        return skill_pairs[order], values[order]

    def explain_work_context(self):
        return 0

    def explain_work_area(self):
        return 0


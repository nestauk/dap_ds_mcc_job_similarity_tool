import numpy as np
import json
from mcc_sussex.backend.getters.data_loader import load_data
from mcc_sussex.backend.getters.work_context import get_processed_work_context
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.optimize import linear_sum_assignment as LSA
import math
from statistics import mean
from mcc_sussex import PROJECT_DIR

CONFIGS = json.load(
    open(f'{PROJECT_DIR}/mcc_sussex/backend/config/CONFIG.json'))
matching_threshold = CONFIGS["SKILL_MATCHING"]["TRESHOLD"]

occs, skill_occs, skills, bert_skills = load_data()
work_contexts = get_processed_work_context()

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

        # # Add work context of job <- for Emily
        self.work_context = self.get_work_context()

        # Compute the embeddings for the essential and optional skills using the get_embedding method
        self.essential_embedding = self.get_embedding(essential=True)
        self.optional_embedding = self.get_embedding(essential=False)

    # Define the get_skills method to extract the essential or optional skills for a given occupation URI
    def get_skills(self, essential):
        # Extract all skills for the given occupation URI
        job_skills = skill_occs[skill_occs['occupationUri'] == self.uri]

        if essential:
            # If essential is True, filter the skills to only include essential skills
            skills = job_skills[job_skills['relationType']
                                == 'essential']['skillUri']
        else:
            # Otherwise, include all skills (essential and optional)
            skills = job_skills['skillUri']

        return skills

    # # Get work context from data <- for Emily
    def get_work_context(self):
        return work_contexts[work_contexts["conceptUri"] == self.uri].drop(columns="conceptUri")

    # Define the get_embedding method to compute the embeddings for a given set of skills (either essential or optional)
    def get_embedding(self, essential):
        if essential:
            # If essential is True, extract the essential skills and corresponding embeddings from the bert_skills table
            embedding_table = pd.merge(
                self.essential_skills, bert_skills, on='skillUri')
        else:
            # Otherwise, extract all skills and corresponding embeddings from the bert_skills table
            embedding_table = pd.merge(
                self.optional_skills, bert_skills, on='skillUri')

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
        self.weighting_array = np.array([1, 2, 3])  # default weights

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
            embedding_1 = np.concatenate(
                [x.essential_embedding for x in self.job_history])
            # weights = np.repeat(self.weighting_array, [len(x.essential_embedding) for x in self.job_history]).reshape(-1, 1)
        else:
            embedding_1 = np.concatenate(
                [x.optional_embedding for x in self.job_history])
            # weights = np.repeat(self.weighting_array, [len(x.optional_embedding) for x in self.job_history]).reshape(-1, 1)

        embedding_2 = self.job2.essential_embedding

        # check if either embedding is empty, return 1 for similarity score and empty lists for matches and values
        if embedding_2.shape[0] == 0 or embedding_1.shape[0] == 0:
            return 1, [], []

        # calculate cosine similarity and pass to LSA to compute the skill matches
        cs = -1 * cosine_similarity(embedding_1, embedding_2)
        lsa = LSA(cs)
        skill_pairs = np.array([sigmoid(-1 * cs[x1, x2])
                               for x1, x2 in zip(lsa[0], lsa[1])])
        # calculate similarity score
        similarity_score = 1 - (sum(skill_pairs) / embedding_2.shape[0])

        matches = zip(lsa[0], lsa[1])
        values = skill_pairs.tolist()
        return similarity_score, matches, values

    def work_area_similarity(self):

        if np.isnan(self.job2.work_area).any() or np.isnan(np.vstack([x.work_area for x in self.job_history])).all(0).any():
            return np.nan
        work_area_differences = np.vstack(
            [x.work_area for x in self.job_history]) - self.job2.work_area

        minimum_difference = np.nanmin(work_area_differences, 0)
        return np.linalg.norm(minimum_difference)

    # Check this comparison for work context <- for Emily
    def work_context_similarity(self) -> int:
        """calculates the euclidean distance between the work context of the job in the job history with the new job

        Returns:
            int: euclidean distance bewteen work context vectors
        """

        if np.isnan(self.job2.work_context).all(0).any() or np.isnan(np.vstack([x.work_context for x in self.job_history])).all(0).any():
            return np.nan

        work_context_differences = np.vstack(
            [x.work_context for x in self.job_history]) - self.job2.work_context
        minimum_difference = np.nanmin(work_context_differences, 0)
        return np.linalg.norm(minimum_difference)

    def work_context_cosine_similarity(self) -> int:
        if np.isnan(self.job2.work_context).all(0).any() or np.isnan(np.vstack([x.work_context for x in self.job_history])).all(0).any():
            return np.nan
        else:
            return cosine_similarity(self.job_history[0].work_context, self.job2.work_context)[0][0]

    def compare_jobs(self):
        self.essential_skill_similarity_score, self.skill_matches, self.skill_values = self.skill_similarity(
            essential=True)
        # optional_skill_similarity_score = self.skill_similarity(essential=False)[
        #    0]
        self.work_context_similarity_score = self.work_context_cosine_similarity()
        # work_area_similarity_score = self.work_area_similarity()

        # Change this to return avareged scores
        self.score = mean([self.work_context_similarity_score,
                          self.essential_skill_similarity_score])
        return self.score

    def explain_skills(self, essential: bool):
        """Explain skills matches for a given job pair

        Args:
            essential (bool): Focus only on essential skills

        Returns:
            Return list of pairs of skills matches and list of associated matching score
        """
        # _, matches, values = self.skill_similarity(essential)
        matches = list(self.skill_matches)
        if essential:
            job1_skills = [
                skills.set_index(
                    "conceptUri").loc[self.job1.essential_skills.iloc[x[0]]]['preferredLabel']
                for x in matches
            ]
        else:
            job1_skills = [
                skills.set_index(
                    "conceptUri").loc[self.job1.optional_skills.iloc[x[0]]]['preferredLabel']
                for x in matches
            ]

        job2_skills = [
            skills.set_index(
                "conceptUri").loc[self.job2.essential_skills.iloc[x[1]]]['preferredLabel']
            for x in matches
        ]
        order = np.argsort(self.skill_values)[::-1]
        skill_pairs = np.array(list(zip(job1_skills, job2_skills)))[order]
        values = np.array(self.skill_values)[order]
        # return skill_pairs[order], np.array(values)[order]
        return {
            "matching_skills": [p[1] for i, p in enumerate(skill_pairs) if values[i] > matching_threshold],
            "missing_skills": [p[1] for i, p in enumerate(skill_pairs) if values[i] <= matching_threshold]
        }

    def explain_work_context(self) -> int:
        """return the work context similarity score (L2 norm between work context vectors) to be 
            displayed in app to explain work context similarity

        Returns:
            int: work context similarity score (L2 norm between work context vectors)
        """
        return self.work_context_similarity_score

    def explain_work_area(self):
        return 0

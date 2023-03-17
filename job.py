import numpy as np
import json
from backend.dataloader import load_data
import backend.utils as utils
import pandas as pd

from sklearn.metrics.pairwise import cosine_similarity
from scipy.optimize import linear_sum_assignment as LSA
import math

CONFIGS = json.load(open('backend/CONFIG.json'))

occs, embeddings, skills = load_data()
num_of_jobs = len(occs)

occs = pd.read_csv('/Users/joshuatwaites/SUSSEX_MCC/occupations_en.csv')
skill_occs = pd.read_csv('/Users/joshuatwaites/SUSSEX_MCC/occupationSkillRelations.csv')
skills = pd.read_csv('/Users/joshuatwaites/SUSSEX_MCC/skills_en.csv')
bert_skills = pd.read_csv('/Users/joshuatwaites/SUSSEX_MCC/BERT_skills.csv')


class Job:

    def __init__(self, job_index):

        self.job_name = occs.iloc[job_index]['preferredLabel']
        self.uri = occs.iloc[job_index]['conceptUri']

        self.job_index = job_index
        self.essential_skills = self.get_skills(essential  = True)
        self.optional_skills = self.get_skills(essential  = False)

        self.essential_embedding = self.get_embedding(essential = True)
        self.optional_embedding = self.get_embedding(essential = False)

        #self.work_context = self.get_work_context()
        #self.work_area = self.get_work_area()

    def get_embedding(self, essential):
        if essential:
            embedding_table = pd.merge(self.essential_skills, bert_skills, on =  'skillUri')
            embedding_table = embedding_table.drop(['skillUri'],axis = 1)
            return embedding_table
        else:
            embedding_table = pd.merge(self.optional_skills, bert_skills, on =  'skillUri')
            embedding_table = embedding_table.drop(['skillUri'],axis = 1)
            return embedding_table

    def get_skills(self, essential):
        
        job_skills = skill_occs[skill_occs['occupationUri'] ==self.uri]
        if essential:
            skills = job_skills[job_skills['relationType']=='essential']['skillUri']
        else:
            skills = job_skills['skillUri']
        return skills
        
    def get_work_context(self):
        return np.fromstring(occs.iloc[self.job_index]['Work Context'][1:-1], sep= " ")

    def get_work_area(self):
        return np.fromstring(occs.iloc[self.job_index]['Work Area'][1:-1], sep= " ")


class compareJobs:

    def __init__(self, job_history, job2):
        self.job_history = job_history
        self.job2 = job2

        self.comparison = self.compare_jobs()

        
    # Check this wrt which one should be optional or essential
    def skill_similarity(self, essential):
        if essential:
            embedding_1 = np.concatenate([x.essential_embedding for x in self.job_history])
            weights = np.repeat(self.weighting_array,[len(x.essential_embedding) for x in self.job_history]).reshape(-1,1)
        else:
            embedding_1 = np.concatenate([x.optional_embedding for x in self.job_history])
            weights = np.repeat(self.weighting_array,[len(x.optional_embedding) for x in self.job_history]).reshape(-1,1)
        
        embedding_2 = self.job2.essential_embedding
        if embedding_2.shape[0] == 0 or embedding_1.shape[0] == 0:
            return 1, [], []
        cs = -1  * cosine_similarity(embedding_1, embedding_2)
        lsa = LSA(cs)
        skill_pairs = np.array([utils.sigmoid(-1 * cs[x1, x2]) for x1, x2 in zip(lsa[0], lsa[1])])
        return 1-(sum(skill_pairs)/embedding_2.shape[0]), zip(lsa[0], lsa[1]), skill_pairs

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
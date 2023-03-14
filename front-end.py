import streamlit as st
import pandas as pd
import numpy as np
#import backend.job_search


WA = ['Documenting/Recording Information'
,'Making Decisions and Solving Problems'
,'Resolving Conflicts and Negotiating with Others'
,'Performing for or Working Directly with the Public'
,'Identifying Objects, Actions, and Events'
,'Processing Information'
,'Communicating with Supervisors, Peers, or Subordinates'
,'Performing General Physical Activities'
,'Getting Information'
,'Updating and Using Relevant Knowledge'
,'Operating Vehicles, Mechanized Devices, or Equipment'
,'Assisting and Caring for Others'
,'Monitoring Processes, Materials, or Surroundings'
,'Communicating with People Outside the Organization'
,'Establishing and Maintaining Interpersonal Relationships'
,'Interpreting the Meaning of Information for Others'
,'Training and Teaching Others'
,'Guiding, Directing, and Motivating Subordinates'
,'Working with Computers'
,'Developing Objectives and Strategies'
,'Analyzing Data or Information'
,'Thinking Creatively'
,'Coaching and Developing Others'
,'Judging the Qualities of Objects, Services, or People'
,'Evaluating Information to Determine Compliance with Standards'
,'Organizing, Planning, and Prioritizing Work'
,'Scheduling Work and Activities'
,'Performing Administrative Activities'
,'Providing Consultation and Advice to Others'
,'Developing and Building Teams'
,'Inspecting Equipment, Structures, or Materials'
,'Handling and Moving Objects'
,'Coordinating the Work and Activities of Others'
,'Estimating the Quantifiable Characteristics of Products, Events, or Information']

def create_job(index, number):
    job = occupations.iloc[index]

    job_title = job['preferredLabel']
    job_description = job['description']
    uri = job['conceptUri']

    return job_title, job_description, uri

# similar skills list(skill name, similairty score)
def gui_element(skill, similairty_score):
    if np.round(similairty_score, decimals=1)>0.8:
        color = 'green'
    elif np.round(similairty_score, decimals=1)>0.6:
        color = 'orange'
    else:
        color = 'red'
 
    return f":{color}[{skill} ({np.round(similairty_score, decimals=1)})]"



def create_bullet_points(skill_lists):
    skill_lists = sorted(skill_lists, key=lambda x: -1*x[1]) 
    string = ""
    for i, j in skill_lists:
        string+= '\n - ' + gui_element(i, j)
    return string

def find_best_worst(job_id):
    best_skills = create_random_skills(best = True)
    worst_skills = create_random_skills(best = False)

    best_WA = create_random_WA(best = True)
    worst_WA = create_random_WA(best = False)

    best_WC = create_random_WC(best = True)
    worst_WC = create_random_WC(best = False)
    return best_skills, worst_skills, best_WA, worst_WA, best_WC, worst_WC
    
    
def create_random_skills(best = True, size = 30):
    skill_name = skills.sample(size)['preferredLabel'].values
    if best:
        skill_similarity = np.random.uniform(low = 0.5, high = 1, size = size)
    else:
        skill_similarity = np.random.uniform(low = 0.0, high = 0.5, size = size)
    return list(zip(skill_name, skill_similarity))

def create_random_WA(best=True, size = 5):
    work_area = np.random.choice(WA, size = size)
    if best:
        WA_similarity = np.random.uniform(low = 0.5, high = 1, size = size)
    else:
        WA_similarity = np.random.uniform(low = 0, high = 0.5, size = size)
    return list(zip(work_area, WA_similarity))

def create_random_WC(best=True, size = 5):
    work_context = np.random.choice(WA, size = size)
    if best:
        WC_similarity = np.random.uniform(low = 0.5, high = 1, size = size)
    else:
        WC_similarity = np.random.uniform(low = 0, high = 0.5, size = size)
    return list(zip(work_context, WC_similarity))


def create_job_match(job_id):

    best_matching_skills, least_matching_skills,best_matching_WC, least_matching_WC, best_matching_WA, least_matching_WA = find_best_worst(job_id)

    job_title, job_body, website= create_job(job_id, 1)
    matching_score = np.round(np.random.uniform(low = 0.7, high = 1, size = 1)[0], decimals=2)
    jobExpander = st.expander(job_title)
    jobExpander.subheader('Description')
    jobExpander.markdown(job_body)

    jobExpander.subheader("Overall matching")
    jobExpander.markdown(f"Overall score is {matching_score}")

    jobExpander.subheader("Job Level")
    jobExpander.markdown(f"Job level is  {np.random.randint(low = 0, high = 6, size = 1)[0]}")

    

    col1, col2 = jobExpander.columns(2)

    with col1:
        col1.subheader("Best matching skills")
        col1.markdown(create_bullet_points(best_matching_skills))

    with col2:
        st.subheader("Least matching skills")
        st.markdown(create_bullet_points(least_matching_skills))

    col1, col2 = jobExpander.columns(2)
    with col1:
        st.subheader("Best matching work contexts")
        st.markdown(create_bullet_points(best_matching_WC))
    with col2:
        st.subheader("Least matching work contexts")
        st.markdown(create_bullet_points(least_matching_WC))

    col1, col2 = jobExpander.columns(2)
    with col1:
        st.subheader("Best matching work activities")
        st.markdown(create_bullet_points(best_matching_WA))
    with col2:
        st.subheader("Least matching work activities")
        st.markdown(create_bullet_points(least_matching_WA))
    
    jobExpander.write(f"Learn more at the: [ESCO website]({website})")

st.title('MCC Sussex tool')
occupations = pd.read_csv('occupations_en.csv')
skills = pd.read_csv('skills_en.csv')
options = pd.Series(occupations['preferredLabel'])

st.sidebar.title("Which industry do you wish to investigate?")
HealthAndCare = st.sidebar.checkbox("Health and Care")
Construction = st.sidebar.checkbox("Construction")
LandBased = st.sidebar.checkbox("Land Based")
Digital = st.sidebar.checkbox("Digital")
VistorAndCult = st.sidebar.checkbox("Visitor")
Manufacturing = st.sidebar.checkbox("Manufacturing")
Any = st.sidebar.checkbox("Any industry")

history_expander = st.expander("Job History (Optional)")
with history_expander:
    
    selected_job1 = st.selectbox(label = 'Select your job', options = options, key = 'h1')
    selected_job2 = st.selectbox(label = 'Select your job', options = options,key = 'h2')
    selected_job3 = st.selectbox(label = 'Select your job', options = options,key = 'h3')
    selected_job4 = st.selectbox(label = 'Select your job', options = options,key = 'h4')
    selected_job5 = st.selectbox(label = 'Select your job', options = options,key = 'h5')

    job_id1 = options[options == selected_job1].index[0]
    job_id2 = options[options == selected_job2].index[0]
    job_id3 = options[options == selected_job3].index[0]
    job_id4 = options[options == selected_job4].index[0]
    job_id5 = options[options == selected_job5].index[0]



form = st.form("my_form")
selected_job = form.selectbox(label = 'Select your job', options = options)
job_id = options[options == selected_job].index[0]
submit = form.form_submit_button("Submit")





if submit:
    p = [create_job_match(i) for i in np.random.randint(low = 0, high = occupations.shape[0], size = 5)]




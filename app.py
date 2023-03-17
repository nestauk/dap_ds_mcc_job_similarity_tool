import streamlit as st
import pandas as pd
import backend.job_search

def create_job(index, number):
    job = tab.iloc[index]

    job_title = job['preferredLabel']
    job_description = job['description']

    expander_title = f"Job {number}: {job_title}\n\n {job_description}"
    return expander_title

@st.cache
def find_jobs(id):
    search = backend.job_search.JobSearch([id])
    suggested_jobs = search.get_best_matches(5)
    suggested_job_list = [x.job2.job_name for x in suggested_jobs]
    return suggested_job_list


st.title('MCC Sussex tool')
tab = pd.read_csv('occupations_en.csv')
options = pd.Series(tab['preferredLabel'])

form = st.form("my_form")
selected_job = form.selectbox(label = 'Select your job', options = options)
job_id = options[options == selected_job].index[0]
submit = form.form_submit_button("Submit")

st.sidebar.title("Which industry do you wish to investigate?")
HealthAndCare = st.sidebar.checkbox("Health and Care")
Construction = st.sidebar.checkbox("Construction")
LandBased = st.sidebar.checkbox("Land Based")
Digital = st.sidebar.checkbox("Digital")
VistorAndCult = st.sidebar.checkbox("Visitor")
Manufacturing = st.sidebar.checkbox("Manufacturing")

Any = st.sidebar.checkbox("Any industry")
if submit:
    expander = st.expander("Suggested jobs")
    suggested_jobs = ['Hello', 'Cheese', 'Cheese', 'Cheese', 'Cheese']#find_jobs(job_id)
    string_to_write = f"""Our suggested jobs transtions are to 

    - {suggested_jobs[1]}

    - {suggested_jobs[2]}

    - {suggested_jobs[3]}

    - {suggested_jobs[4]}
    
    """
    expander.markdown(string_to_write)
    
    job1 = tab.iloc[0]

    job1Expander = st.expander(create_job(0, 1))


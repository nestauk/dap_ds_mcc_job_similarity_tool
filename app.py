import streamlit as st
import pandas as pd
import numpy as np
import backend.job_search

@st.cache
def find_jobs(id):
    search = backend.job_search.JobSearch([id], False, False)
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

st.markdown('''
<style>
[data-testid="stMarkdownContainer"] ul{
    list-style-position: inside;
}
</style>
''', unsafe_allow_html=True)




if submit:
    
    expander = st.expander("Suggested jobs")
    expander.markdown('''
    <style>
    [data-testid="stMarkdownContainer"] ul{
    list-style-position: inside;
    }
    </style>
    ''', unsafe_allow_html=True)
    suggested_jobs = find_jobs(job_id)
    
    string_to_write = f"""Our suggested jobs transtions are to 

    - {suggested_jobs[1]}

    - {suggested_jobs[2]}

    - {suggested_jobs[3]}

    - {suggested_jobs[4]}
    
    """
    expander.markdown(string_to_write)
    

import streamlit as st
from mcc_sussex import IMAGE_DIR
from PIL import Image
from nesta_ds_utils.viz.altair import formatting
from getters.app_data import get_similarity_data
from collections import defaultdict
import altair as alt
import pandas as pd
from typing import Dict, Union, List, Tuple
formatting.setup_theme()

PAGE_TITLE = "Career Transitions"

nesta_fav = Image.open(f"{IMAGE_DIR}/favicon.ico")

st.set_page_config(page_title=PAGE_TITLE, layout="wide", page_icon=nesta_fav)

#load in the data - we wrap this in a function so that it is cached and streamlit doesn't re-load it each time you filter
@st.cache_data(show_spinner = "Loading data")
def load_data() -> Dict[
    str, 
    List[Dict[str, Union[str, float, List[str]]]]
    ]:
    """gets the pre-calculated job similarity dictionary to use as the backend of the app

    Returns:
        Dict[str, List[Dict[str, Union[str, float, List[str]]]]]: structured as
        {current_job_name: [{job_name: str, # Best match
                     similarity_score: float,
                     matching_skills: List[str],
                     missing_skills: List[str]},
                     ...
                     {job2_id: str, # Worst match
                     similarity_score: float,
                     matching_skills: List[str],
                     missing_skills: List[str]},
                     ]
        ...}
    """
    return get_similarity_data()

@st.cache_data(show_spinner = "Calculating job similarity")
def filter_job(latest_job: str, data: Dict[str, List[Dict[str, Union[str, float, List[str]]]]]) -> Tuple[List[Dict[str, Union[str, float, List[str]]]],List[str], Dict[str, int]]:
    """filter the full data to only include data about the input job

    Args:
        latest_job (str): job inputted by user via filter
        data (Dict[str, List[Dict[str, Union[str, float, List[str]]]]]): full dictionary with all match metadata

    Returns:
        Tuple[List[Dict[str, Union[str, float, List[str]]]],List[str], Dict[str, int]]: 
            - List[Dict[str, Union[str, float, List[str]]]]: list of metadata on matches for current job
            - List[str]: ordered list of names of top matches
            - Dict[str, int]: key: match, value: percent of skills already posessed
    """
    filtered_data =  data[latest_job]
    ordered_matches = []
    match_overlap_data = defaultdict(int)
    for match in filtered_data:
        ordered_matches.append(match['job_name'])
        match_overlap_data[match['job_name']] = round(len(match['matching_skills']) / (len(match['matching_skills']) + len(match['missing_skills'])), 2)
    
    match_overlap_data = pd.DataFrame.from_dict(match_overlap_data, orient = "index").reset_index()
    match_overlap_data.columns = ['match', 'overlap']
    
    return filtered_data, ordered_matches, match_overlap_data


data = load_data()

#Set up banner at the top with title and logo
logo, white_space, warning = st.columns([1, 3, 2])
with logo:
    st.image(Image.open(f"{IMAGE_DIR}/nesta_sussex_logo.png"))
with warning:
    st.markdown("🚨 WARNING: This app is currently in **beta** and the algorithm to reccommend jobs is **experimental** 🚨")

white_space, title, white_space = st.columns([1, 5, 1])

with title:
    st.title("Welcome to MCC Sussex’s Career Transition App")

#Generate markdown for subtitles
st.markdown("_As part of our Future Skills Sussex project, we aim to give people the freedom to **progress in their career** by providing opportunities to **gain new skills** and ultimately **improve the productivity of the local Sussex economy** with **home grown talent**_")
st.markdown("")
st.subheader("Use this app to find new career opportunities that are in line with your existing skill sets, and find out where you may need to focus training in order to progress.")
st.markdown("""<hr style="height:3px;border:none;color:#e5cbff;background-color:#e5cbff;" /> """, unsafe_allow_html=True)
st.markdown("")
st.markdown("")

#Allow user to enter job title which is stored in the variable "latest_job" - the options are defined by the keys in the data dictionary
diamond, label, job_selector = st.columns([.75, 10, 4])
with diamond:
    st.image(Image.open(f"{IMAGE_DIR}/diamond.png"))
with label:
    st.title("To get started, enter your most recent job title:")
with job_selector:
    options = list(data.keys())
    options.insert(0, "")
    latest_job = st.selectbox(label = " ", options = options, label_visibility = "hidden")
st.markdown("")
st.markdown("")
sector_select = st.radio(
    label = "Select to only show results within one of these high priority sectors", 
    options = [
        "Show all",
        "Manufacturing and Engineering",
        "Visitor and Cultural Industries",
        "Digital",
        "Land Based",
        "Construction",
        "Health and Care"
    ],
    horizontal = True)

st.markdown("""<hr style="height:3px;border:none;color:#e5cbff;background-color:#e5cbff;" /> """, unsafe_allow_html=True)

if latest_job != "": # only run the next bits once the user has entered a latest job
    #filter dictionary to return data on selected job (stored as latest_job)
    job_data, ordered_matches, match_overlaps = filter_job(latest_job, data)

    #generate bar chart to show top matches and skill overlaps
    match_overlap_bars = alt.Chart(match_overlaps).mark_bar().encode(
        x=alt.X("overlap:Q", 
            axis = alt.Axis(
                format = "%", 
                title = "Percent of Skills we Think You Already Possess",
                titleColor = "#102e4a",
                labelColor = "#102e4a",
                grid = False),
            scale=alt.Scale(domain=[0, 1])),
        y=alt.Y("match:N", 
            axis = alt.Axis(
                labelLimit = 0,
                title = None,
                labelColor = "#102e4a"),
            sort = "-x")
        ).properties(
            height = 300,
            width = 1000
        ).configure_mark(color = "#60D394")


    white_space, chart, white_space = st.columns([1,5,1])
    
    with chart:
        #text to introduce bar chart
        st.markdown("Based on the skills needed to be a **{}** we think you may be a fit for the following jobs:".format(latest_job))
        #display bar chart in app
        st.altair_chart(match_overlap_bars)
    
    white_space, text, white_space = st.columns([2,5,1])
    with text:
        st.markdown("*To learn more about how to transition into each of these jobs, expand the corresponding sections below*")
    
    with st.expander(label = ordered_matches[0]):
        #display matching and missing skills for top match
        match_data = job_data[0]
        matches, bar, missing = st.columns([5,1,5])
        with matches:
            st.markdown("We think you **already have** the following skills and experiences that would be needed as a {}:".format(ordered_matches[0]))
            # IF YOU WANTED TO DISPLAY WORK CONTEXTS NEXT TO SKILLS, YOU COULD SET UP TWO COLUMNS WITHIN THE EXPANDER HERE.
            # skills, work_contexts = st.columns(2)
            # the below line would then go in "with skills:" 
            # st.markdown("Skills")
            for skill in match_data["matching_skills"]:
                st.markdown(":green[- " + skill + "]")
            #with work_contexts:
                # st.markdown("Work Contexts")
                # for work_context in match_data["matching_work_contexts"]:
                    #st.markdown(":green[- " + work_context + "]")
        with bar:
            #this bit is needed to create the bar in between the columns    
            st.markdown("""<hr width="2" size="500" style="border:none;color:#102e4a;background-color:#102e4a;" /> """, unsafe_allow_html=True)
        with missing:
            st.markdown("We think you **may need to learn** more about:")
            for skill in match_data["missing_skills"]:
                st.markdown(":red[- " + skill + "]")
    
    with st.expander(label = ordered_matches[1]):
        #display matching and missing skills for second match
        match_data = job_data[1]
        matches, bar, missing = st.columns([5,1,5])
        with matches:
            st.markdown("We think you **already have** the following skills and experiences that would be needed as a {}:".format(ordered_matches[1]))
            for skill in match_data["matching_skills"]:
                st.markdown(":green[- " + skill + "]")
        with bar:    
            st.markdown("""<hr width="2" size="500" style="border:none;color:#102e4a;background-color:#102e4a;" /> """, unsafe_allow_html=True)
        with missing:
            st.markdown("We think you **may need to learn** more about:")
            for skill in match_data["missing_skills"]:
                st.markdown(":red[- " + skill + "]")
    
    with st.expander(label = ordered_matches[2]):
        #display matching and missing skills for third match
        match_data = job_data[2]
        matches, bar, missing = st.columns([5,1,5])
        with matches:
            st.markdown("We think you **already have** the following skills and experiences that would be needed as a {}:".format(ordered_matches[2]))
            for skill in match_data["matching_skills"]:
                st.markdown(":green[- " + skill + "]")
        with bar:    
            st.markdown("""<hr width="2" size="500" style="border:none;color:#102e4a;background-color:#102e4a;" /> """, unsafe_allow_html=True)
        with missing:
            st.markdown("We think you **may need to learn** more about:")
            for skill in match_data["missing_skills"]:
                st.markdown(":red[- " + skill + "]")
    
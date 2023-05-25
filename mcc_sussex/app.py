import streamlit as st
import os
from PIL import Image
from nesta_ds_utils.viz.altair import formatting
from mcc_sussex.backend.recommendations import transitions_utils
import mcc_sussex.backend.getters.load_data_utils as load_all_data
from mcc_sussex.backend.getters.high_priority_sectors import priority_sector_map, sector_descriptions
from mcc_sussex.backend.getters.job_zone import linked_job_zones
from collections import defaultdict
import altair as alt
import pandas as pd
from typing import Dict, Union, List, Tuple
formatting.setup_theme()

PAGE_TITLE = "Career Transitions"


current_dir = os.getcwd()
nesta_fav = Image.open(f"{current_dir}/mcc_sussex/images/favicon.ico")

st.set_page_config(page_title=PAGE_TITLE, layout="wide", page_icon=nesta_fav)


@st.cache_data(show_spinner="Loading data")
def load_data():
    return load_all_data.Data()


@st.cache_data(show_spinner="Loading data")
def load_sector_data():
    return priority_sector_map(), sector_descriptions()


@st.cache_data(show_spinner="Loading data")
def load_job_zone_data():
    data = linked_job_zones()
    return data.loc[data["Type of Match"] != "wrongMatch"]


def get_transitions(latest_job: str, n, destination_ids="all"):
    sim_data = transitions_utils.find_most_similar(
        latest_job,  # Origin occupation for which we're searching the other most similar other occupations
        similarity_measure="combined",  # Type of similarity measure to use
        n=n,  # Number of most similar occupations to show
        # Pool of admissible destination occupations
        destination_ids=destination_ids,
        transpose=False  # If job_i describes a jobseeker, set to False; if job_i describes a vacancy, set to True
    ).round(2)
    return sim_data.loc[sim_data["preferredLabel"] != latest_job]


def work_context_similarity(latest_job_id, transition_id):
    comparison = transitions_utils.CompareFeatures()
    context_difs = comparison.get_feature_differences(
        latest_job_id, transition_id, esco_level=None).round(2)
    sim_by_cat = context_difs.groupby(context_difs["category"])[
        "dif_abs"].mean().reset_index()
    similar_categories = sim_by_cat.loc[sim_by_cat["dif_abs"]
                                        < .25]["category"].values
    different_categories = sim_by_cat.loc[sim_by_cat["dif_abs"]
                                          >= .25]["category"].values

    key_work_contexts_origin = context_difs.loc[
        (context_difs["origin"] > .5) & (context_difs["dif"] < -.25)]["element_name"].values

    key_work_contexts_dest = context_difs.loc[
        (context_difs["destination"] > .5) & (context_difs["dif"] > .25)]["element_name"].values

    return {"similar_categories": similar_categories,
            "different_categories": different_categories,
            "origin_work_contexts": key_work_contexts_origin,
            "destination_work_contexts": key_work_contexts_dest}


def generate_work_context_paragraph(latest_job, transition, similar_categories, different_categories, key_work_contexts_origin, key_work_contexts_dest):
    transition = transition.lower()
    if len(different_categories) == 0:
        first_sentence = "Transitioning from a {} to a {} would likely mean **little changes** to your work contexts. ".format(
            latest_job, transition)
    elif len(similar_categories) == 0:
        first_sentence = "Transitioning from a {} to a {} would likely mean **significant changes** to your work contexts. ".format(
            latest_job, transition)
    else:
        first_sentence = "Transitioning from a {} to a {} would likely mean **some changes** to your work contexts, most significantly in the **{}** category/categories. ".format(
            latest_job, transition, similar_categories)

    if len(key_work_contexts_origin) == 0:
        second_sentence = "Most of the important work contexts from being a {} would **still likely be important** as a {}. ".format(
            latest_job, transition)
    else:
        key_work_contexts_origin_str = ", ".join(key_work_contexts_origin)
        second_sentence = "{}, which were likely important as a {}, would **likely not be so important** as a {}. ".format(
            key_work_contexts_origin_str, latest_job, transition)

    if len(key_work_contexts_dest) == 0:
        third_sentence = "You **likely have experience** working in most of the key work contexts as a {} from being a {}. ".format(
            transition, latest_job)
    else:
        key_work_contexts_dest_str = ", ".join(key_work_contexts_dest)
        third_sentence = "You would likely **need to gain experience** working in the following work contexts: {} for a smooth transition.".format(
            key_work_contexts_dest_str)

    return first_sentence + second_sentence + third_sentence


def transition_details(transition_data, latest_job):
    latest_job_id = data.occ_title_to_id(latest_job)

    skills_dict = defaultdict(lambda: defaultdict(list))
    for job in transition_data["preferredLabel"]:
        job_id = data.occ_title_to_id(job)

        skill_overlap = transitions_utils.show_skills_overlap(
            latest_job,  # Origin occupation ID
            job,  # Destination occupation ID
            skills_match='optional',
            verbose=False)

        matching_skills = skill_overlap.loc[skill_overlap["similarity"]
                                            >= 0.8]["destination_skill"]
        skills_dict[job]["matching_skills"] = matching_skills

        missing_skills = skill_overlap.loc[skill_overlap["similarity"]
                                           < 0.8]["destination_skill"]
        skills_dict[job]["missing_skills"] = missing_skills

        skills_dict[job]["work_context_data"] = work_context_similarity(
            latest_job_id, job_id)

    return skills_dict


def job_zone(job_zone_data: pd.DataFrame, recommendation):
    try:
        job_zone = int(
            job_zone_data.loc[job_zone_data["preferred_label"] == recommendation].iloc[0]["job_zone"])
        if job_zone == 1:
            return "The Job Zone for a {} is **Little or No Preparation Needed**. Jobs in this category may require completion of GCSEs or A-Levels and usually require little to no previous work experience and minimal training.".format(recommendation)
        elif job_zone == 2:
            return "The Job Zone for a {} is **Some Preparation Needed**. Jobs in this category usually require completion of some A-Levels and some previous work experience or training.".format(recommendation)
        elif job_zone == 3:
            return "The Job Zone for a {} is **Medium Preparation Needed**. Jobs in this category usually require vocational school or completion of A-Levels and 1-2 years of related work experience or training.".format(recommendation)
        elif job_zone == 4:
            return "The Job Zone for a {} is **Considerable Preparation Needed**. Jobs in this category usually require a Bachelor's degree and several years of related work experience or training.".format(recommendation)
        elif job_zone == 5:
            return "The Job Zone for a {} is **Extensive Preparation Needed**. Jobs in this category usually require a Graduate degree (Masters, PhD, etc.) and extensive experience (often more than 5 years).".format(recommendation)
    except:
        return "Unknown"


data = load_data()
job_zone_data = load_job_zone_data()

# Set up banner at the top with title and logo
logo, white_space, warning = st.columns([1, 3, 2])
with logo:
    st.image(Image.open(
        f"{current_dir}/mcc_sussex/images/nesta_sussex_logo.png"))
with warning:
    st.markdown(
        "🚨 WARNING: This app is meant for demonstrative purposes only. Check out this article for more information about the algorithm behind it.🚨")

white_space, title, white_space = st.columns([1, 5, 1])

with title:
    st.title("Welcome to Sussex’s Career Transition App")

# Generate markdown for subtitles
st.subheader("As part of our Future Skills Sussex project, we aim to give people the freedom to **progress in their career** by providing opportunities to **gain new skills** and ultimately **improve the productivity of the local Sussex economy** with **home grown talent**")
st.subheader("Use this app to find new career opportunities that are in line with your existing skill sets, and find out where you may need to focus training in order to progress.")
st.markdown("""<hr style="height:3px;border:none;color:#e5cbff;background-color:#e5cbff;" /> """,
            unsafe_allow_html=True)
st.markdown("")
st.markdown("")

# Allow user to enter job title which is stored in the variable "latest_job" - the options are defined by the keys in the data dictionary
label, job_selector = st.columns([3/7, 4/7])
with label:
    st.title("Start by entering a job title:")
with job_selector:
    options = list(set(data.occupations["preferredLabel"].str.capitalize()))
    options.insert(0, "")
    latest_job = st.selectbox(
        label=" ", options=options, label_visibility="hidden")
    latest_job = latest_job.lower()
st.markdown("")
st.markdown("")
sector_filter_data, sec_descriptions = load_sector_data()
sector_options = list(set(sector_filter_data["Sector"]))
sector_options.insert(0, "Show all")
sector_select = st.radio(
    label="Select to only show results within one of these high priority sectors",
    options=sector_options,
    horizontal=True)

n_matches = st.slider(
    label="Select how many matches to show", min_value=1, max_value=15)

if sector_select == "Show all":
    st.markdown("Showing results for **All Sectors**")

else:
    st.markdown(
        "Only showing results for the **{}** Sector".format(sector_select))
    st.markdown(sec_descriptions[sector_select])

st.markdown("""<hr style="height:3px;border:none;color:#e5cbff;background-color:#e5cbff;" /> """,
            unsafe_allow_html=True)

if latest_job != "":  # only run the next bits once the user has entered a latest job
    # filter dictionary to return data on selected job (stored as latest_job)
    if sector_select == "Show all":
        transition_data = get_transitions(latest_job, n_matches+1)

    else:
        transition_options = sector_filter_data.loc[sector_filter_data["Sector"]
                                                    == sector_select]["id"].to_list()
        if data.occ_title_to_id(latest_job) in transition_options:
            transition_data = get_transitions(
                latest_job, n_matches+1, destination_ids=transition_options)
        else:
            transition_data = get_transitions(
                latest_job, n_matches, destination_ids=transition_options)

    if transition_data.iloc[0]["similarity"] < 0.5:

        st.markdown(
            "🚨 **WARNING**: there are no highly similar matches based on the criteria provided 🚨")
    transition_data["label_field"] = transition_data["preferredLabel"].str.capitalize()
    # generate bar chart to show top matches and skill overlaps
    match_overlap_bars = alt.Chart(transition_data).mark_bar().encode(
        x=alt.X("similarity:Q",
                axis=alt.Axis(
                    format="%",
                    title="Similarity between jobs",
                    titleColor="#102e4a",
                    labelColor="#102e4a",
                    grid=False),
                scale=alt.Scale(domain=[0, 1])),
        y=alt.Y("label_field:N",
                axis=alt.Axis(
                    labelLimit=0,
                    title=None,
                    labelColor="#102e4a"),
                sort="-x"),
        tooltip=[
            alt.Tooltip("label_field", title="Job title"),
            alt.Tooltip("similarity:Q", title="Similarity", format=".0%")]
    ).properties(
        height=300,
        width=1000
    ).configure_mark(color="#60D394")

    white_space, chart, white_space = st.columns([1, 5, 1])

    with chart:
        # text to introduce bar chart
        st.markdown(
            "Based on the skills needed to be a **{}** we think you may be a fit for the following jobs:".format(latest_job))
        # display bar chart in app
        st.altair_chart(match_overlap_bars)

    white_space, text, white_space = st.columns([1, 2, 1])
    with text:
        st.markdown(
            "*To learn more about how to transition into each of these jobs, expand the corresponding sections below*")

    ordered_matches = list(transition_data["label_field"])

    skill_matches = transition_details(transition_data, latest_job)

    for match in ordered_matches:

        with st.expander(label=match):
            st.header(match)
            # display matching and missing skills for top match
            st.markdown("**{}**".format(
                data.occupations.loc[data.occ_title_to_id(match.lower())].description))
            st.subheader("Level of Experience (Job Zone)")
            st.markdown(job_zone(job_zone_data, match))
            st.markdown(
                "Click [here](https://www.onetonline.org/help/online/zones) to learn more about Job Zones, as defined by the United States Department of Labor.")
            match_data = skill_matches[match.lower()]
            work_context_data = match_data["work_context_data"]
            st.subheader("Work Contexts")
            st.markdown(generate_work_context_paragraph(
                latest_job,
                match,
                work_context_data["similar_categories"],
                work_context_data["different_categories"],
                work_context_data["origin_work_contexts"],
                work_context_data["destination_work_contexts"]))
            st.markdown(
                "Click [here](https://www.onetonline.org/find/descriptor/browse/4.C/) to learn more about Work Contexts, as defined by the United States Department of Labor.")
            st.subheader("Skills")
            matches, bar, missing = st.columns([5, 1, 5])
            with matches:
                st.markdown(
                    "We think you **already have** the following skills that would be needed as a {}:".format(match))
                for skill in match_data["matching_skills"]:
                    st.markdown(
                        f'<t1 style="color:#005AB5;">{skill}</h1>', unsafe_allow_html=True)
            with missing:
                st.markdown("We think you **may need to learn** more about:")
                for skill in match_data["missing_skills"]:
                    st.markdown(
                        f'<t1 style="color:#DC3220;">{skill}</h1>', unsafe_allow_html=True)

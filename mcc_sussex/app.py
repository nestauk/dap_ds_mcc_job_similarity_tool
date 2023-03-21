import streamlit as st
from mcc_sussex import IMAGE_DIR
from PIL import Image
from nesta_ds_utils.viz.altair import formatting
formatting.setup_theme()

PAGE_TITLE = "Career Transitions"

nesta_fav = Image.open(f"{IMAGE_DIR}/favicon.ico")

st.set_page_config(page_title=PAGE_TITLE, layout="wide", page_icon=nesta_fav)

logo, white_space = st.columns([1, 3])
with logo:
    st.image(Image.open(f"{IMAGE_DIR}/nesta_sussex_logo.png"))

white_space, title, white_space = st.columns([1, 5, 1])

with title:
    st.title("Welcome to MCC Sussex’s Career Transition App")

st.markdown("_As part of our Future Skills Sussex project, we aim to give people the freedom to **progress in their career** by providing opportunities to **gain new skills** and ultimately **improve the productivity of the local Sussex economy** with **home grown talent**_")
st.markdown("")
st.subheader("Use this app to find new career opportunities that are in line with your existing skill sets, and find out where you may need to focus training in order to progress.")
st.markdown("""<hr style="height:3px;border:none;color:#e5cbff;background-color:#e5cbff;" /> """, unsafe_allow_html=True)
st.markdown("")
st.markdown("")

diamond, label, job_selector = st.columns([.75, 10, 4])
with diamond:
    st.image(Image.open(f"{IMAGE_DIR}/diamond.png"))
with label:
    st.title("To get started, enter your most recent job title:")
with job_selector:
    #NOTE: THE OPTIONS WILL BE POPULATED USING A LIST OF ALL UNIQUE JOBS IN THE DATASET
    #THIS MAKES SO THE VARIABLE "latest_job" IS NOW A STRING OF THE OPTION THAT WAS SELECTED BY THE FILTER
    #IN THIS EXAMPLE, "latest_job" = "Dog Walker" as that is the only option
    latest_job = st.selectbox(label = " ", options = ["Dog Walker"], label_visibility = "hidden")
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

#NOW YOU WOULD USE THE VARIABLE "sector_select" TO FILTER THE RESULTS, I.E.
if sector_select == "Show all":
    df = "KEEP THE FULL DATAFRAME"
else:
    df = "filtered dataframe where the sector field matches sector_select"

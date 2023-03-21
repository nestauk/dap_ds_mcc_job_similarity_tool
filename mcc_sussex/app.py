import streamlit as st
from mcc_sussex import IMAGE_DIR
from PIL import Image
from nesta_ds_utils.viz.altair import formatting
formatting.setup_theme()

PAGE_TITLE = "Career Transitions"

nesta_fav = Image.open(f"{IMAGE_DIR}/favicon.ico")

st.set_page_config(page_title=PAGE_TITLE, layout="wide", page_icon=nesta_fav)

st.title("Welcome to the Innovation Explorer!")

# Sussex Job Similarity Tool

This repo provides the code used to create the [SkillsMatcher](https://skillsmatcher.dap-tools.uk) tool developed in partnership with Sussex Chamber of Commerce.

The repo has two main attributes:

  1. `mcc_sussex/app.py`: the code for the frontend of the Streamlit app
  2. `mcc_sussex/backend/*`: all of the code for the data preprocessing and similarity calculations to evaluate job similarity using the algorithm described in this [blog post](https://medium.com/data-analytics-at-nesta/mapping-career-causeways-with-the-sussex-chamber-of-commerce-e62fe0b8ad92)

To run the app locally:
1. Clone this repo `git clone https://github.com/nestauk/dap_ds_mcc_job_similarity_tool.git`
2. Download the [data](https://nesta-open-data.s3.eu-west-2.amazonaws.com/job-pathfinder-data/data.zip) with the pre-computed similarity calculations
3. Install the project: from within the project folder run `pip install -e .`
4. Run the app: `streamlit run mcc_sussex/app.py`

To build a new app using the algorithm:
1. Download the [data](https://nesta-open-data.s3.eu-west-2.amazonaws.com/job-pathfinder-data/data.zip) with the pre-computed similarity calculations
2. Leverage the utility functions in `backend\recommendations` to compare jobs  

# Sussex Job Similarity Tool

This repo provides the code used to create the [Job Similarity Tool](https://sussex-career-transitions.dap-tools.uk) developed in partnership with Sussex Chamber of Commerce.

The repo has two main attributes:

  1. `mcc_sussex/app.py`: the code for the frontend of the Streamlit app
  2. `mcc_sussex/backend/*`: all of the code for the data preprocessing and similarity calculations to recommend viable job transitions using the algorithm described in this [blog post](INSERT LINK TO BLOG)


To run the app locally:
1. Clone this repo `git clone https://github.com/nestauk/dap_ds_mcc_job_similarity_tool.git`
2. Download the [data]()
3. Install the project: from within the project folder run `pip install -e .`
4. Run the app: `streamlit run mcc_sussex/app.py`

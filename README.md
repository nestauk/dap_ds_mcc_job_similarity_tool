# Sussex OJO

This repo provides a Streamlit app de eloped for the Future Skills Sussex. The app reccomends new job transitions based on the current occupation by comparing jobs for similarity of required skills, education level and work context. 

The app is currenctly hosted on Streamlit Cloud at the following link:
(tba)


## Development instructions

The app development consist of two steps:
- [backend] building of a precomptued dictionary of job similarity: `job_similarity_dict.json`
- [frontend] Streamlit app design and hosting on Streamlit cloud

### 🛠 Backend

To build the precomputed data:

- create a conda environment with `requiremnent.txt` installed
- build the dataset and upload it to S3 by running:
``` 
from backend.pipelines.build_job_similarity import build_and_upload
build_and_upload()
```
- download `job_similarity_dict.json` from S3 and save it on `mcc_sussex/data`





### 💫 Frontend

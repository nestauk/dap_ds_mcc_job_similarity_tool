"""identifies an ONET job zone for each ESCO occupation
"""
from mcc_sussex import PROJECT_DIR
from mcc_sussex.backend.getters.crosswalk import esco_onet_crosswalk
from mcc_sussex.backend.getters.job_zone import onet_job_zone_reference, onet_job_zones, education_training_experience, education_training_experience_categories
import pandas as pd
import numpy as np

data_folder = f"{PROJECT_DIR}/mcc_sussex/data/"

# esco-onet crosswalk
occupations = esco_onet_crosswalk()

# job zones dataset
onet_job_zone = onet_job_zones()
onet_job_zone_ref = onet_job_zone_reference()

# education, training, and experience datasets
ed_train_exp = education_training_experience()
ed_train_exp_ref = education_training_experience_categories()

# Link Job Zones to ESCO occupations
occupations_ = occupations.merge(
    onet_job_zone[['O*NET-SOC Code', 'Job Zone']],
    left_on='onet_code', right_on='O*NET-SOC Code', how='left')

occupations_.rename(columns={'Job Zone': 'job_zone'}, inplace=True)

occupations_[-occupations_['job_zone'].isnull()].sort_values('job_zone')[[
    'preferred_label', 'onet_occupation', 'job_zone']]

# Unique types of elements in the Education/experience dataset
for j in ed_train_exp['Element Name'].unique():
    print(j)

# link education level
# Separate out level of education
lev_education = ed_train_exp[ed_train_exp['Element Name']
                             == 'Required Level of Education']

unique_onet_codes = lev_education['O*NET-SOC Code'].unique()
x = []
for code in unique_onet_codes:
    lev_education_ = lev_education[lev_education['O*NET-SOC Code'] == code]
    x.append(np.sum(lev_education_.Category *
             (lev_education_['Data Value']/100)))

ed_df = pd.DataFrame(
    data={'onet_code': unique_onet_codes, 'education_level': x})
ed_df.head()

# Link education level to ESCO occupations
occupations_ = occupations_.merge(
    ed_df,
    left_on='onet_code', right_on='onet_code',
    how='left')

# link related work experience
# Separate out level of related work experience
lev_education = ed_train_exp[ed_train_exp['Element Name']
                             == 'Related Work Experience']

unique_onet_codes = lev_education['O*NET-SOC Code'].unique()
x = []
for code in unique_onet_codes:
    lev_education_ = lev_education[lev_education['O*NET-SOC Code'] == code]
    x.append(np.sum(lev_education_.Category *
             (lev_education_['Data Value']/100)))

ed_df = pd.DataFrame(
    data={'onet_code': unique_onet_codes, 'related_work_experience': x})
ed_df.head()

# Link education level to ESCO occupations
occupations_ = occupations_.merge(
    ed_df,
    left_on='onet_code', right_on='onet_code',
    how='left')

# link on the job training
# Separate out on-the-job training
lev_education = ed_train_exp[ed_train_exp['Element Name']
                             == 'On-the-Job Training']

unique_onet_codes = lev_education['O*NET-SOC Code'].unique()
x = []
for code in unique_onet_codes:
    lev_education_ = lev_education[lev_education['O*NET-SOC Code'] == code]
    x.append(np.sum(lev_education_.Category *
             (lev_education_['Data Value']/100)))

ed_df = pd.DataFrame(
    data={'onet_code': unique_onet_codes, 'on_the_job_training': x})
ed_df.head()

# Link education level to ESCO occupations
occupations_ = occupations_.merge(
    ed_df,
    left_on='onet_code', right_on='onet_code',
    how='left')

occupations_.to_csv(
    data_folder + 'processed/linked_data/ESCO_occupations_Job_Zones.csv', index=False)

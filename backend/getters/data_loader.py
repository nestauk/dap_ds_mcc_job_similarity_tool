from nesta_ds_utils.loading_saving import S3

BUCKET_NAME = "mcc-sussex"

def getter_occupation_en():
    """Getter of `occupation_en.csv` from S3
    """

    return S3.download_obj(BUCKET_NAME, "occupations_en.csv", download_as= "dataframe")

def getter_occupationSkillRelations():
    """Getter of `occupationSkillRelations.csv` from S3
    """

    return S3.download_obj(BUCKET_NAME, "occupationSkillRelations.csv", download_as= "dataframe")

def getter_skills_en():
    """Getter of `skills_en.csv` from S3
    """

    return S3.download_obj(BUCKET_NAME, "skills_en.csv", download_as= "dataframe")

def getter_bert():
    """Getter of `BERT.csv` from S3
    """

    return S3.download_obj(BUCKET_NAME, "BERT.csv", download_as= "np.array")

def getter_bert_skills():
    """Getter of `BERT_skills.csv` from S3
    """

    return S3.download_obj(BUCKET_NAME, "BERT_skills.csv", download_as= "dataframe")

def getter_work_context():
    """Getter of `work_context.csv` from S3
    """

    return S3.download_obj(BUCKET_NAME, "work_context.csv", download_as= "dataframe")


def getter_work_area():
    """Getter of `work_area.csv` from S3
    """

    return S3.download_obj(BUCKET_NAME, "Work_area.csv", download_as= "dataframe")


def getter_esco_to_soc():
    """Getter of `esco_to_soc.csv` from S3
    """

    return S3.download_obj(BUCKET_NAME, "esco_to_soc.csv", download_as= "dataframe")


def getter_soc_to_sector():
    """Getter of `soc_to_sector.csv` from S3
    """

    return S3.download_obj(BUCKET_NAME, "soc_to_sector.csv", download_as= "dataframe")

def load_data():
    """Load all datasets
    """
    return getter_occupation_en(), getter_occupationSkillRelations(), getter_skills_en(), getter_bert_skills(), getter_esco_to_soc(), getter_soc_to_sector()
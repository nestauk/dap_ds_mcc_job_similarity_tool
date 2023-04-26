from nesta_ds_utils.loading_saving import S3
from mcc_sussex import BUCKET_NAME
import pandas as pd
import boto3
import io


def get_onet_esco_crosswalk() -> pd.DataFrame:
    """gets the crosswalk of onet occupations to esco occupations

    Returns:
        pd.DataFrame: dataframe with columns:
            O*NET Id: id of occupation in onet
            O*NET Title: title of occupation in onet
            O*NET Description: description of occupation in onet
            ESCO or ISCO URI: uri to map occupation to esco data
            ESCO or ISCO Title: title of occupation in esco/isco
            ESCO or ISCO Description: description of occupation in esco/isco
            Type of Match: options - "closeMatch", "exactMatch", "bestISCO", "relatedMatch", "wrongMatch", "broadMatch", "exactISCO", "narrowMatch"
    """
    return S3.download_obj(BUCKET_NAME, "onet_occupations.csv", download_as="dataframe", kwargs_reading={"skiprows": 16, "header": 1})


def get_onet_work_context() -> pd.DataFrame:
    """gets the raw work context data for all onet occupation codes found here: 
        https://www.onetcenter.org/dictionary/27.2/excel/work_context.html

    Returns:
        pd.DataFrame: work contexts for each onet occupational code
    """
    s3 = boto3.client("s3")
    fileobj = io.BytesIO()
    s3.download_fileobj(BUCKET_NAME, "Work Context.xlsx", fileobj)
    fileobj.seek(0)
    return pd.read_excel(fileobj, sheet_name="Work Context")


def get_processed_work_context() -> pd.DataFrame:
    """gets the work context vectors generated in pipeline/work_context.py

    Returns:
        pd.DataFrame: vector for each esco occupation with a score for each of the 57 work contexts
    """

    return S3.download_obj(BUCKET_NAME, "occupation_work_contexts.csv", download_as="dataframe")


def get_work_context_index_lookup() -> pd.DataFrame:
    """gets a lookup of the index of the work context (0-57) in the processed work context vectors 
        to the names of the work contexts

    Returns:
        pd.DataFrame: lookup table with columns:
            id: work context id
            index: index corresponding to the columns in the processed file
            name: name of the work context
    """
    return S3.download_obj(BUCKET_NAME, "work_context_id_lookup.csv", download_as="dataframe")

import pandas as pd
from nesta_ds_utils.loading_saving import S3

def create_esco_to_soc():
    """Create the ESCO to SOC converter

    Returns:
        pd.Dataframe: Dataframe containsing ESCO and SOC code corresponcence
    """
    # Read the excel file and get a list of sheet names
    excel_file = pd.ExcelFile('backend/data/Draft ESCO crosswalk.xlsx')
    sheet_names = excel_file.sheet_names

    # Create an empty list to store the data frames for each sheet
    df_list = []

    # Loop through each sheet and append the data frame to the list
    for sheet in sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet,header=1)
        df_list.append(df.astype(str))

    # Concatenate all the data frames into a single data frame
    return pd.concat(df_list, ignore_index=True)[['ESCO code', 'SOC2020 code']]


def create_soc_to_sector():
    """Create SOC to sector map

    Returns:
        pd.Dataframe: 
    """
    # Read the excel file and get a list of sheet names
    sector_data_file = pd.ExcelFile('backend/data/SOC Codes for 6 Key Sectors.xlsx')
    sector_names = sector_data_file.sheet_names

    # Create an empty list to store the dataframes
    dfs = []

    # Loop through each sheet and append the modified dataframe to the list of dataframes
    for sector in sector_names:
        df = pd.read_excel(sector_data_file, sheet_name=sector)
        df['Sector'] = sector
        dfs.append(df[['SOC', 'Sector']])

    # Concatenate all the dataframes into a single dataframe
    return pd.concat(dfs).drop_duplicates()

def preprocess_and_upload():
    """Build the esco-to-soc and soc-to-sector and upload them to S3. 
    """
    # Execute only if run as a script
    BUCKET_NAME = "mcc-sussex"

    esco_to_soc = create_esco_to_soc() 
    soc_to_sector = create_soc_to_sector()

    S3.upload_obj(esco_to_soc, BUCKET_NAME, "esco_to_soc.csv")
    S3.upload_obj(soc_to_sector, BUCKET_NAME, "soc_to_sector.csv")
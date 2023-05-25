"""maps the ESCO codes to the high priority sectors provided by Sussex
"""
import pandas as pd
from mcc_sussex.backend.getters.high_priority_sectors import get_cleaned_sector_data
from mcc_sussex.backend.getters.crosswalk import esco_soc_crosswalk
from mcc_sussex.backend.getters.esco import esco_occupations, esco_occupation_ids
from mcc_sussex import PROJECT_DIR


def create_esco_to_soc(crosswalk: pd.ExcelFile):
    """Create the ESCO to SOC converter

    Returns:
        pd.Dataframe: Dataframe with ESCO and SOC code mapping
    """
    # Read the excel file and get a list of sheet names
    excel_file = crosswalk
    sheet_names = excel_file.sheet_names

    # Create an empty list to store the data frames for each sheet
    df_list = []

    # Loop through each sheet and append the data frame to the list
    for sheet in sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet, header=1)
        df["SOC"] = df["SOC2020 code"].apply(lambda x: str(x).split("/")[0])
        df_list.append(df.astype(str))

    # Concatenate all the data frames into a single data frame
    return pd.concat(df_list, ignore_index=True)[['ESCO code', 'SOC']]


def create_soc_to_sector() -> pd.DataFrame:
    """Create SOC to sector map

    Returns:
        pd.Dataframe: Dataframe with SOC and Sector code mapping
    """
    # Read the excel file and get a list of sheet names
    sector_data_file = get_cleaned_sector_data(type="openpyxl")
    sector_names = sector_data_file.sheetnames

    # Create an empty list to store the dataframes
    dfs = []

    # Loop through each sheet and append the modified dataframe to the list of dataframes
    for sector in sector_names:
        df = pd.read_excel(get_cleaned_sector_data(), sheet_name=sector)
        worksheet = sector_data_file[sector]

        # filter out hidden rows!!
        hidden_rows_idx = [
            row - 2
            for row, dimension in worksheet.row_dimensions.items()
            if dimension.hidden
        ]

        hidden_rows_idx = [idx for idx in hidden_rows_idx if idx in df.index]

        df.drop(hidden_rows_idx, axis=0, inplace=True)
        df.reset_index(drop=True, inplace=True)

        df['Sector'] = sector
        dfs.append(df[['SOC', 'Sector']].astype(str))

    # Concatenate all the dataframes into a single dataframe
    return pd.concat(dfs).drop_duplicates(subset=["SOC", "Sector"])


if __name__ == "__main__":
    crosswalk = esco_soc_crosswalk()
    esco_codes_to_soc = create_esco_to_soc(crosswalk)
    occupations = pd.merge(left=esco_occupations(
    ), right=esco_occupation_ids(), how="left", on="conceptUri")

    esco_ids_to_soc = pd.merge(
        left=esco_codes_to_soc, right=occupations, left_on="ESCO code", right_on="code")

    esco_to_sector = pd.merge(
        left=esco_ids_to_soc, right=create_soc_to_sector(), left_on="SOC", right_on="SOC")

    esco_to_sector.to_csv(
        f"{PROJECT_DIR}/mcc_sussex/data/processed/esco_codes_to_priority_sectors.csv")

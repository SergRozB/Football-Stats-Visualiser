import pandas as pd
raw_data = pd.read_csv("Data/2021-2022 Football Player Stats.csv", encoding='latin-1', sep=";")
normalised_data = pd.read_csv("Data/2021-2022 Football Player Stats Normalised.csv", encoding='latin-1')
normalised_per_league_data = pd.read_csv("Data/2021-2022 Football Player Stats Normalised Per League.csv", encoding='latin-1')
normalised_per_league_per_pos_data = pd.read_csv("Data/2021-2022 Football Player Stats Normalised Per League and Position.csv", encoding='latin-1')

def GetRawData():
    return raw_data.values.tolist()

def GetNormalisedData():
    return normalised_data.values.tolist()

def GetNormalisedPerLeagueData():
    return normalised_per_league_data.values.tolist()

def GetNormalisedPerLeaguePerPosData():
    return normalised_per_league_per_pos_data.values.tolist()

def GetHeaderList():
    return raw_data.columns.tolist()

def GetRowData(rowIndex, dataType="raw"):
    if dataType == "raw":
        return raw_data.iloc[rowIndex].tolist()
    elif dataType == "normalised":
        return normalised_data.iloc[rowIndex].tolist()
    elif dataType == "normalised_per_league":
        return normalised_per_league_data.iloc[rowIndex].tolist()
    elif dataType == "normalised_per_league_per_pos":
        return normalised_per_league_per_pos_data.iloc[rowIndex].tolist()
    else:
        raise ValueError(f"Invalid data type: {dataType}. Must be 'raw', 'normalised', or 'normalised_per_league'.")

import pandas as pd
raw_data = pd.read_csv("Football-Stats-Visualiser/Data/2021-2022 Football Player Stats.csv", encoding='latin-1', sep=";")
normalised_data = pd.read_csv("Football-Stats-Visualiser/Data/2021-2022 Football Player Stats Normalised.csv", encoding='latin-1')
normalised_per_league_data = pd.read_csv("Football-Stats-Visualiser/Data/2021-2022 Football Player Stats Normalised Per League.csv", encoding='latin-1')
normalised_per_league_per_pos_data = pd.read_csv("Football-Stats-Visualiser/Data/2021-2022 Football Player Stats Normalised Per League and Position.csv", encoding='latin-1')

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

def GetPercentile(stat_name, stat, data_type, filters=None):
    if filters is None:
        filters = []
    data = GetDataByDataType(data_type)
    if data is None:
        raise ValueError(f"Invalid data type: {data_type}. Must be 'raw', 'normalised', or 'normalised_per_league'.")
    if stat_name not in data.columns:
        raise ValueError(f"Invalid stat name: {stat_name}. Must be one of {raw_data.columns.tolist()}.")

    data = ApplyFiltersToData(data, filters)  # Apply filters to the data
    max = data[stat_name].max()
    min = data[stat_name].min()
    percentile = (stat - min) / (max - min) if max != min else 0
    return float(percentile)

def ApplyFiltersToData(data, filters):
    filtered_data = data.copy()
    
    for stat_index_filter, (operation, operation_text), value in filters:
        mask = operation(filtered_data.iloc[:, stat_index_filter], value)
        filtered_data = filtered_data[mask]
    return filtered_data

def GetDataByDataTypeValuesList(dataType):
    if dataType == "raw":
        return raw_data.values.tolist()
    elif dataType == "normalised":
        return normalised_data.values.tolist()
    elif dataType == "normalised_per_league":
        return normalised_per_league_data.values.tolist()
    elif dataType == "normalised_per_league_per_pos":
        return normalised_per_league_per_pos_data.values.tolist()
    else:
        return None

def GetDataByDataType(dataType):
    if dataType == "raw":
        return raw_data
    elif dataType == "normalised":
        return normalised_data
    elif dataType == "normalised_per_league":
        return normalised_per_league_data
    elif dataType == "normalised_per_league_per_pos":
        return normalised_per_league_per_pos_data
    else:
        return None;

def GetRowIndexByPlayerID(player_id, dataType="raw"):
    data = GetDataByDataType(dataType)
    if data is None:
        raise ValueError(f"Invalid data type: {dataType}. Must be 'raw', 'normalised', or 'normalised_per_league'.")
    
    row_indices = data.index[data.iloc[:, 0] == player_id].tolist()  # Assuming the first column contains player IDs
    print("row indices:", row_indices)
    if not row_indices:
        return -1  # Return -1 if the player ID is not found
    return row_indices[0]  # Return the first matching index

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

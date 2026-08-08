import pandas as pd
data_file = pd.read_csv("Data/2021-2022 Football Player Stats.csv", encoding='latin-1',sep=";")
non_normalised_data = ["Rk", "Player", "Nation", "Pos", "Squad", "Comp", "Age", "Born",
                        "MP", "Starts", "Min", "90s"]
#new_data = data_file.loc[data_file["MP"] >= 15]
new_data = data_file
list_of_leagues = data_file["Comp"].unique()
list_of_positions = data_file["Pos"].unique()
league_data_max = {}
league_data_min = {}
league_data_max_per_pos = {}
league_data_min_per_pos = {}

# Normalise the data for each league separately 
min_MP = 15 # Minimum number of matches played to be chosen as either a maximum or minimum value for normalisation
normalised_per_league = data_file.loc[data_file["MP"] >= min_MP]
normalised_pl_per_pos = data_file.loc[data_file["MP"] >= min_MP]

# Get data for normalised per league (not per pos)

for league in list_of_leagues:
    # get data for the league and add it to the dictionary
    filtered_data = normalised_per_league.loc[(normalised_per_league["Comp"] == league) & (normalised_per_league["MP"] >= min_MP)]
    league_data_max[league] = filtered_data.max(axis=0).to_list()
    league_data_min[league] = filtered_data.min(axis=0).to_list()

index = normalised_per_league.columns.get_loc("Goals")

for column in normalised_per_league.columns:
    if column not in non_normalised_data:
        columnIndex = normalised_per_league.columns.get_loc(column)
        for league in list_of_leagues:
            columnMaxVal = league_data_max[league][columnIndex]
            columnMinVal = league_data_min[league][columnIndex]
            normalised_per_league.loc[(normalised_per_league["Comp"] == league), column] = (
                normalised_per_league[column] - columnMinVal) / (columnMaxVal - columnMinVal)

normalised_per_league.to_csv("Data/2021-2022 Football Player Stats Normalised Per League.csv", index=False)

# Normalise the data for each league and position

for league in list_of_leagues:
    for position in list_of_positions:
        # get data for the league and add it to the dictionary
        filtered_data = normalised_pl_per_pos.loc[(normalised_pl_per_pos["Comp"] == league) & (normalised_pl_per_pos["MP"] >= min_MP) 
                                              & (normalised_pl_per_pos["Pos"] == position)]
        league_data_max_per_pos[(league, position)] = filtered_data.max(axis=0).to_list()
        league_data_min_per_pos[(league, position)] = filtered_data.min(axis=0).to_list()

index = normalised_pl_per_pos.columns.get_loc("Goals")

for column in normalised_pl_per_pos.columns:
    if column not in non_normalised_data:
        columnIndex = normalised_pl_per_pos.columns.get_loc(column)
        for league in list_of_leagues:
            for position in list_of_positions:
                columnMaxVal = league_data_max_per_pos[(league, position)][columnIndex]
                columnMinVal = league_data_min_per_pos[(league, position)][columnIndex]
                normalised_pl_per_pos.loc[(normalised_pl_per_pos["Comp"] == league) & (normalised_pl_per_pos["Pos"] == position), column] = (
                normalised_pl_per_pos[column] - columnMinVal) / (columnMaxVal - columnMinVal)

normalised_pl_per_pos.to_csv("Data/2021-2022 Football Player Stats Normalised Per League and Position.csv", index=False)

#new_data = new_data.drop(columns=non_normalised_data)
#new_data = new_data.insert(15, "GoalsPer90", new_data["Goals"], True)
#new_data["Goals"] = round(new_data["Goals"] * new_data["90s"])


maxValues = new_data.max(axis=0).to_list()
minValues = new_data.min(axis=0).to_list()
for column in new_data.columns:
    if column not in non_normalised_data:
        columnIndex = new_data.columns.get_loc(column)
        columnMaxVal = maxValues[columnIndex]
        columnMinVal = minValues[columnIndex]
        new_data[column] = (new_data[column] - columnMinVal) / (columnMaxVal - columnMinVal)
        #new_data[column] = round(new_data[column] / new_data["90s"], 2)
new_data.to_csv("Data/2021-2022 Football Player Stats Normalised.csv", index=False)

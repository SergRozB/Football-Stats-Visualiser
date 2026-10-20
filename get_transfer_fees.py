import unicodedata, re
import pandas as pd
import tqdm
from rapidfuzz import fuzz


def normalise(name: str) -> str:
    if not isinstance(name, str):
        return ""
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = name.lower()
    name = re.sub(r"[^a-z\s]", " ", name) # drop punctuation
    name = re.sub(r"\b(jr|sr|ii|iii)\b", "", name) # drop suffixes
    return re.sub(r"\s+", " ", name).strip()

df_2122season = pd.read_csv("Football-Stats-Visualiser/Data/2021-2022 Football Player Stats.csv", encoding='latin-1', sep=";")
df_all_players = pd.read_csv("Football-Stats-Visualiser/Data/players.csv", encoding='utf-8', sep=",", encoding_errors='replace')
normalised_all_player_names = []

for index, row in tqdm.tqdm(df_all_players.iterrows(), total=len(df_all_players)):
    player_name = row['name']
    player_name_normalised = normalise(player_name)
    date_of_birth = str(row['date_of_birth'])
    
    birth_year = date_of_birth[0:4]
    #print("date of borth:", date_of_birth, "| birth year:", birth_year)
    country = row['country_of_citizenship']
    normalised_all_player_names.append((player_name_normalised, player_name, row['player_id'], birth_year, country))

all_matching_players_raw = []
all_matching_players_raw_transfermarkt = []
all_matching_players_normalised = []
all_matching_player_ids = []
non_matching_players = []
multiple_matching_players = []
fuzz_score_list = []
birth_year_appeared_list = []

for index, row in tqdm.tqdm(df_2122season.iterrows(), total=len(df_2122season)):
    player_name = row['Player']
    player_name_normalised = normalise(player_name)
    matching_players = []
    fuzzymatching_players = []
    highest_fuzz_score = 0
    birth_year_appeared = False
    for p in normalised_all_player_names:
        #if p[0] == player_name_normalised:
            #print("P3:", p[3], "| row born:", row['Born'])
        if p[3] == row['Born']: # Check if birth year match
            birth_year_appeared = True
            if p[0] == player_name_normalised:
                matching_players.append(p)

            elif player_name_normalised in p[0] or p[0] in player_name_normalised:
                matching_players.append(p)

            else:
                fuzz_score = fuzz.ratio(p[0], player_name_normalised)
                if fuzz_score > highest_fuzz_score:  
                    highest_fuzz_score = fuzz_score
                    fuzzymatching_players = [p]

    birth_year_appeared_list.append(birth_year_appeared)
    if matching_players:
        if len(matching_players) > 1:
            multiple_matching_players.append(matching_players)
            all_matching_players_raw.append(player_name)
            all_matching_players_raw_transfermarkt.append("Multiple Matches")
            all_matching_players_normalised.append(player_name_normalised)
            all_matching_player_ids.append("Multiple Matches")
            fuzz_score_list.append(-1)

        else:
            matched_player = matching_players[0]
            all_matching_players_raw.append(player_name)
            all_matching_players_raw_transfermarkt.append(matched_player[1])
            all_matching_players_normalised.append(player_name_normalised)
            all_matching_player_ids.append(matched_player[2])
            fuzz_score_list.append(-1)

    elif fuzzymatching_players:
        if len(fuzzymatching_players) > 1:
            multiple_matching_players.append(fuzzymatching_players)
            all_matching_players_raw.append(player_name)
            all_matching_players_raw_transfermarkt.append("Multiple Fuzzy Matches")
            all_matching_players_normalised.append(player_name_normalised)
            all_matching_player_ids.append("Multiple Fuzzy Matches")
            fuzz_score_list.append(-2)
        else:
            matched_player = fuzzymatching_players[0]
            all_matching_players_raw.append(player_name)
            all_matching_players_raw_transfermarkt.append(matched_player[1])
            all_matching_players_normalised.append(player_name_normalised)
            all_matching_player_ids.append(matched_player[2])
            fuzz_score_list.append(highest_fuzz_score)
    else:
        non_matching_players.append(player_name)
        all_matching_players_raw.append(player_name)
        all_matching_players_raw_transfermarkt.append("No Matches")
        all_matching_players_normalised.append(player_name_normalised)
        all_matching_player_ids.append("No Matches")
        fuzz_score_list.append(-1)

matched_player_data = {
    "raw_name": all_matching_players_raw,
    "raw_name_transfermarkt": all_matching_players_raw_transfermarkt,
    "normalised_name": all_matching_players_normalised,
    "player_id": all_matching_player_ids,
    "fuzz_score": fuzz_score_list,
    "birth_year_appeared": birth_year_appeared_list
}

multiple_matching_player_data = {
    "normalised_name": multiple_matching_players
}

non_matching_player_data = {
    "raw_name": non_matching_players  
}

folder_path = "Football-Stats-Visualiser/Data/"
pd.DataFrame(matched_player_data).to_csv(f"{folder_path}matched_players.csv", index=False, encoding='utf-8', sep=";")
pd.DataFrame(multiple_matching_player_data).to_csv(f"{folder_path}multiple_matching_players.csv", index=False, encoding='utf-8', sep=";")
pd.DataFrame(non_matching_player_data).to_csv(f"{folder_path}non_matching_players.csv", index=False, encoding='utf-8', sep=";")

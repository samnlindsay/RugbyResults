import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import duckdb

# Position dictionary
d = {
    1: "Prop",
    2: "Hooker",
    3: "Prop",
    4: "Second Row",
    5: "Second Row",
    6: "Back Row",
    7: "Back Row",
    8: "Back Row",
    9: "Scrum Half",
    10: "Fly Half",
    11: "Back Three",
    12: "Centre",
    13: "Centre",
    14: "Back Three",
    15: "Back Three",
}

def position_category(x):
    if x <= 8:
        return "Forwards"
    elif x <= 15:
        return "Backs"
    else:
        return "Bench"

con = duckdb.connect()

import gspread
from google.oauth2.service_account import Credentials
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('client_secret.json', scopes=scope)
client = gspread.authorize(creds)

sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1pcO8iEpZuds9AWs4AFRmqJtx5pv5QGbP4yg2dEkl8fU/edit#gid=2100247664").worksheets()

my_sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1keX2eGbyiBejpfMPMbL7aXYLy7IDJZDBXQqiKVQavz0/edit#gid=390656160").worksheets()


def results(squad=1, season=None):

    results = sheet[4 if squad==1 else 7].batch_get(['B4:E'])[0]

    df = pd.DataFrame(results, columns=results.pop(0)).replace('', pd.NA)
    df = df.dropna(subset=['Season','Score'])
    df["Squad"] = "1st" if squad == 1 else "2nd"
    if season:
        df = df[df["Season"] == season]

    df["Home/Away"] = df["Opposition"].apply(lambda x: "Home" if x.strip().split(" ")[-1] == "(H)" else "Away")
    df["GameID"] = df["Competition"] + "-__-" + df["Opposition"]
    df["GameType"] = df["Opposition"]
    df["Opposition"] = df["Opposition"].apply(lambda x: x.replace(" (H)", "").replace(" (A)", ""))
    df["PF"] = df.apply(lambda x: int(x["Score"].split(" - ")[0 if x["Home/Away"] == "Home" else 1]), axis=1)
    df["PA"] = df.apply(lambda x: int(x["Score"].split(" - ")[1 if x["Home/Away"] == "Home" else 0]), axis=1)
    df["Result"] = df.apply(lambda x: "W" if x["PF"] > x["PA"] else ("L" if x["PF"] < x["PA"] else "D"), axis=1)

    return df

#####################################################
### TEAM SHEETS - 4th and 7th sheets in the workbook
#####################################################
def team_sheets(squad=1):

    if squad == 1:
        team = sheet[4].batch_get(['B4:AG'])[0]
        team = pd.DataFrame(team, columns=team.pop(0)).replace('', pd.NA)
        team["Squad"]="1st"
    elif squad == 2:    
        team = sheet[7].batch_get(['B4:AK'])[0]
        team = pd.DataFrame(team, columns=team.pop(0)).replace('', pd.NA)
        team["Squad"]="2nd"
    elif squad == 0:
        team1 = sheet[4].batch_get(['B4:AG'])[0]
        team1 = pd.DataFrame(team1, columns=team1.pop(0)).replace('', pd.NA)
        team1.drop("", axis=1, inplace=True)
        team1["Squad"]="1st"
        
        team2 = sheet[7].batch_get(['B4:AK'])[0]
        team2 = pd.DataFrame(team2, columns=team2.pop(0)).replace('', pd.NA)
        team2["Squad"]="2nd"
        
        team = pd.concat([team1, team2])

    # Filter null/empty rows
    team = team.dropna(subset=['Season','Score'])

    # Add home/away column (=["H","A"]) based on the Opposition column
    team['Home/Away'] = team['Opposition'].apply(lambda x: "H" if "(H)" in x else "A")
    team["Opposition"] = team["Opposition"].apply(lambda x: x.replace("(H)","").replace("(A)",""))

    team["GameType"] = team["Competition"].apply(
        lambda x: "Friendly" if x=="Friendly" else (
            "League" if (
                "Cup" not in x and "Plate" not in x and "Vase" not in x and "Sussex" in x
                ) else "Cup"
            )
        )

    # Add PF and PA columns (based on Home/Away column) - if Home/Away is H, then PF is the first score and PA is the second score, else vice versa
    team['PF'] = team.apply(lambda x: int(x['Score'].split("-")[0]) if x['Home/Away'] == "H" else int(x['Score'].split("-")[1]), axis=1)
    team['PA'] = team.apply(lambda x: int(x['Score'].split("-")[1]) if x['Home/Away'] == "H" else int(x['Score'].split("-")[0]), axis=1)

    return team

# GAMES (1 row per game)
###########################################
def games(squad=1):
    team = team_sheets(squad)
    cols = ["Squad", "Season", "Competition", "GameType", "Home/Away", "Opposition", "PF", "PA"]
    return team[cols]


# PLAYERS (1 row per player per game)
###########################################
def players(squad=1):
    players = team_sheets(squad).melt(
        id_vars=["Squad", "Season", "Competition", "GameType", "Opposition", "Home/Away"], 
        value_vars=[str(i) for i in range(1, 26)], 
        value_name="Player",
        var_name="Number"
    ).dropna()
    players["Number"] = players["Number"].astype("int")
    players["Position"] = players["Number"].map(d).astype("category", )
    # If Position in ("Back Three", "Centre", "Fly Half", "Scrum Half"), then it's a Back, else it's a Forward
    players["PositionType"] = players["Number"].apply(position_category) 
    # positions_start = positions_start[positions_start["Position"].notna()]
    return players

# PLAYERS_AGG (1 row per player per season)
###########################################
def players_agg(squad=1):
    squad = players(squad)
    players_agg = con.query("""
    SELECT
        Squad,
        Season, 
        Player, 
        -- Cup games
        SUM(CASE WHEN GameType = 'Cup' AND Number <= 15 THEN 1 ELSE 0 END) AS CupStarts,
        SUM(CASE WHEN GameType = 'Cup' AND Number > 15 THEN 1 ELSE 0 END) AS CupBench,
        -- League games
        SUM(CASE WHEN GameType = 'League' AND Number <= 15 THEN 1 ELSE 0 END) AS LeagueStarts,
        SUM(CASE WHEN GameType = 'League' AND Number > 15 THEN 1 ELSE 0 END) AS LeagueBench,
        -- Friendlies
        SUM(CASE WHEN GameType = 'Friendly' AND Number <= 15 THEN 1 ELSE 0 END) AS FriendlyStarts,
        SUM(CASE WHEN GameType = 'Friendly' AND Number > 15 THEN 1 ELSE 0 END) AS FriendlyBench, 
        -- Competitive Totals
        SUM(CASE WHEN GameType != 'Friendly' AND Number <= 15 THEN 1 ELSE 0 END) AS CompetitiveStarts,
        SUM(CASE WHEN GameType != 'Friendly' AND Number > 15 THEN 1 ELSE 0 END) AS CompetitiveBench,
        -- Totals
        SUM(CASE WHEN Number <= 15 THEN 1 ELSE 0 END) AS TotalStarts,
        SUM(CASE WHEN Number > 15 THEN 1 ELSE 0 END) AS TotalBench,                          
        COUNT(*) AS TotalGames,      
        -- Most common Positions
        MODE(Position) AS MostCommonPosition,
        MODE(NULLIF(PositionType,'Bench')) AS MostCommonPositionType
    FROM squad
    GROUP BY Squad, Season, Player
    """).to_df()

    return players_agg

##################################################
### LINEOUTS - 6th and 9th sheets in the workbook
##################################################

def call_type(call):

    if call in ["Snap", "Yes", "No"]:
        return "4-man only"
    elif call in ["", "Red", "Orange", "RD", "Even", "Odd", "Green", "Plus", "Even +", "Odd +", "Green +", "Matlow"]:
        return "Old"
    elif call in ["C*", "A*", "C1", "C2", "C3", "H1", "H2", "H3", "A1", "A2", "A3", "W1", "W2", "W3"]:
        return "New"
    else:
        return "Other"
    
def dummy_movement(call):
    if call in ["RD", "Plus", "Even +", "Odd +", "Green +", "C3", "A1", "A2", "A3", "No"]:
        return "D"
    elif call in ["Yes", "C1", "C2"]:
        return "M"
    else:
        return "X"

def lineouts(squad, season=None):
    if squad == 1:
        lineouts = sheet[6].batch_get(['A3:S'])[0]
    elif squad == 2:
        lineouts = sheet[9].batch_get(['A3:S'])[0]

    df = pd.DataFrame(lineouts, columns=lineouts.pop(0)).replace('', pd.NA)

    df["Squad"] = "1st" if squad == 1 else "2nd"
    
    if season:
        df = df[df["Season"] == season]

    df = df.fillna("")

    df["Area"] = df.apply(lambda x: "Front" if x["Front"] == "x" else ("Middle" if x["Middle"]=="x" else "Back"), axis=1)
    df["Won"] = df.apply(lambda x: True if x["Won"] == "Y" else False, axis=1)
    df["Drive"] = df.apply(lambda x: True if x["Drive"] == "x" else False, axis=1)
    df["Crusaders"] = df.apply(lambda x: True if x["Crusaders"] == "x" else False, axis=1)
    df["Transfer"] = df.apply(lambda x: True if x["Transfer"] == "x" else False, axis=1)
    df["Flyby"] = df.apply(lambda x: None if x["Flyby"] == "" else int(x["Flyby"]), axis=1)
    df["Dummy"] = df.apply(lambda x: dummy_movement(x["Call"]), axis=1)

    df["CallType"] = df["Call"].apply(call_type)
    df["Setup"] = df["Call"].apply(lambda x: (x[0] if x[0] in ["A", "C", "H", "W"] else None) if len(x) > 0 else None)

    df = df[['Squad', 'Season', 'Opposition', 'Numbers', 'Call', 'CallType', 'Setup', 'Dummy', 'Area', 'Drive', 'Crusaders', 'Transfer', 'Flyby', 'Hooker', 'Jumper', 'Won']]

    return df


########################
### PITCHERO TEAM STATS
########################
import requests
from bs4 import BeautifulSoup
import pandas as pd

def pitchero_stats(squad=1, season=None):

    url = f"https://www.egrfc.com/teams/14206{8 if squad==1 else 9}/statistics"

    if season is not None:
        seasonID = {
            "2021/22": 79578,
            "2022/23": 83980,
            "2023/24": 87941,
            "2024/25": 91673,
        }[season]

        url += f"?season={seasonID}"
    
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')


    table = soup.find_all("div", {"class": "no-grid-hide"})[0]

    headers = [h.text for h in table.find_all("div", {"class": "league-table__header"})]
    players = [p.text for p in table.find_all("div", "sc-bwzfXH iWTrZm")]
    data = [int(d.text) for d in table.find_all("div", "sc-ifAKCX") if d.text.isnumeric()]

    # Split the data into columns
    data = [data[i:i+len(headers)-1] for i in range(0, len(data), len(headers)-1)]

    df = pd.DataFrame(data, columns=headers[1:], index=players)\
        .reset_index().rename(columns={"index": "Player"})

    df = df[["Player", "A", "T", "Con", "PK", "DG", "YC", "RC"]]

    df["Points"] = df["T"]*5 + df["Con"]*2 + df["DG"]*3 + df["PK"]*3 
    df["PPG"] = df["Points"] / df["A"]
    df["Season"] = season
    df["Squad"] = "1st" if squad == 1 else "2nd"

    return df
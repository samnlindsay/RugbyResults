# Create custom style for altair charts
import altair as alt
import pandas as pd
from data_prep import *
from copy import deepcopy

# Set the default configuration for altair
def alt_theme():

    title_font="PT Sans Narrow, Helvetica Neue, Helvetica, Arial, sans-serif"
    font="Lato, sans-serif"
    
    return {
        "config": {
            "axis": {
                "labelFont": font,
                "titleFont": title_font,
                "labelFontSize": 13,
                "titleFontSize": 24,
                "gridColor":"#202947",
                "gridOpacity": 0.2,
            },
            "header": {
                "labelFont": title_font,
                "titleFont": title_font,
                "labelFontSize": 24,
                "titleFontSize": 28,
                "labelFontWeight": "bold",
                "orient": "left",
            },
            "legend": {
                "labelFont": font,
                "titleFont": title_font,
                "labelFontSize": 14,
                "titleFontSize": 16,
                "titlePadding": 5,
                "fillColor": "white",
                "strokeColor": "black", 
                "padding": 10,
                "titleFontWeight": "lighter",
                "titleFontStyle": "italic",
                "titleColor": "gray",
                "offset": 10,
            },
            "title": {
                "font": title_font,
                "fontSize": 48,
                "fontWeight": "bold",
                "anchor": "start",
                "align": "center",
                "titlePadding": 20,
                "subtitlePadding": 10,
                "subtitleFontWeight": "lighter",
                "subtitleFontSize": 12,
                "subtitleColor": "",
                "subtitleFontStyle": "italic",
                "offset": 15,
                "color": "black",
            },
            "axisX": {
                "labelAngle": 0
            },
            "facet": {
                "title": None,
                "header": None,
                "align": {"row": "each", "column": "all"},  
            },
            "resolve": {
                "scale": {
                    "y": "independent",
                    "facet": "independent"
                }
            },
            "background": "#20294710"
        }
    }

alt.themes.register("my_custom_theme", alt_theme)
alt.themes.enable("my_custom_theme")

game_type_scale = alt.Scale(
    domain=["League", "Cup", "Friendly"], 
    range=["#202947", "#981515", "#146f14"]                
)

squad_scale = alt.Scale(
    domain=["1st", "2nd"],
    range=["#202947", "#146f14"]
)

def plot_starts_by_position(squad=1, season="2024/25", fb_only=False, df=None, min=0):

    # Filter by squad/season/starts only
    if df is None:
        df = players()
    if squad == 1:
        df = df[df["Squad"] == "1st"]
    elif squad == 2:
        df = df[df["Squad"] == "2nd"]
    if season:
        df = df[df["Season"] == season]
    df = df[df["Number"] <= 15]

    # legend selection filter
    legend = alt.selection_point(fields=["GameType"], bind="legend", on="click")

    title = f"{'1st XV' if squad==1 else '2nd XV' if squad == 2 else 'Total'} Starts (by position)"

    if fb_only:
        facet=alt.Facet("PositionType:N", sort=["Forwards", "Backs"], columns=2, title=None)
    else:
        facet=alt.Facet(
            "Position:N", 
            columns=2, 
            sort=["Prop", "Scrum Half", "Hooker", "Fly Half", "Second Row", "Centre", "Back Row", "Back Three"], 
            title=None, 
            align="each",
            spacing=5
        )

    # altair bar chart of starts by position
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('count()', axis=alt.Axis(title="Starts", orient="bottom")),
        y=alt.Y('Player:N', sort='-x', title=None),
        facet=facet,
        tooltip=[
            "Player", 
            "Position", 
            alt.Tooltip("count()"), 
            'GameType:N' if squad else "Squad:N"
        ],
        color=alt.Color(
            f"{'Squad' if squad==0 else 'GameType'}:N",
            scale=squad_scale if squad == 0 else game_type_scale,
            legend=alt.Legend(
                title="Click to filter", orient="bottom", direction="horizontal", titleOrient="left"
            )
        ),
        order=alt.Order('GameType:N' if squad else "Squad:N", sort='descending')
    ).resolve_scale(
        y="independent",
        x="shared"
    ).properties(
        width=200, 
        height=alt.Step(14),
        title=alt.Title(text=title, subtitle="Not including bench appearances.")
    ).add_params(
        legend
    ).transform_joinaggregate(
        TotalGames="count()", groupby=["Player", "PositionType" if fb_only else "Position"]
    ).transform_filter(
        f"datum.TotalGames >= {min}"
    ).transform_filter(
        legend
    )

    return chart

# Plot the number of games played by each player in the 2024/25 season
def plot_games_by_player(squad=1, season="2024/25", min=5, agg=False, df=None):

    # Filter by squad/season/starts only
    if df is None:
        df = players()
    if squad == 1:
        df = df[df["Squad"] == "1st"]
    elif squad == 2:
        df = df[df["Squad"] == "2nd"]
    if season:
        df = df[df["Season"] == season]

    c = alt.Color(
        f"{'Squad' if squad==0 else 'GameType'}:N",
        scale=squad_scale if squad == 0 else game_type_scale,
        legend=alt.Legend(
            title="Click to filter", orient="bottom", direction="horizontal", titleOrient="left"
        )
    )
    o = alt.Order('Squad' if squad==0 else 'GameType', sort='descending')

    # legend selection filter
    legend = alt.selection_point(fields=["GameType" if squad != 0 else "Squad"], bind="legend", on="click")
    
    chart = alt.Chart(df).mark_bar(strokeWidth=2).encode(
        x=alt.X(
            "count()",
            axis=alt.Axis(title="Appearances", orient="top")),
        y=alt.Y("Player", sort="-x", title=None),
        color=c,
        order=o,
        opacity=alt.Opacity(
            "PositionType:N",
            scale=alt.Scale(
                domain=["Start", "Bench"],
                range=[1.0, 0.6]
            ), 
            legend=None
        ),
        column=alt.Column("Season:N", title=None, header=alt.Header(title=None, labelFontSize=36) if season is None else None),
        tooltip=[
            "Player:N", 
            "Season:N",
            "GameType:N" if squad != 0 else "Squad:N",
            alt.Tooltip("count()", title="Games"), 
            alt.Tooltip("TotalGames:Q", title="Total Games")
        ],
    ).transform_filter(
        legend
    ).add_params(
        legend
    ).transform_joinaggregate(
        TotalGames="count()", groupby=["Player", "Season"]
    ).resolve_scale(
        y="independent"
    ).transform_filter(
        f"datum.TotalGames >= {min}"
    ).properties(
        title=alt.Title(
            text=f"{'1st XV' if squad==1 else ('2nd XV' if squad==2 else 'Total')} Appearances" + (" per Season" if season is None else ""),
            subtitle=f"Minimum {min} appearances in a given season. Lighter shaded bars represent bench appearances.",
            subtitleFontStyle="italic"
        ),
        width=400 if season else 250,
        height=alt.Step(15)
    )
    
    if season is not None:
        chart = chart.transform_filter(
            alt.datum.Season == season
        ).properties(
            width=400,
            height=alt.Step(15)
        )
        return chart
    elif agg:
        agg_chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("count()", axis=alt.Axis(title="Appearances", orient="top")),
            y=alt.Y("Player:N", title=None, sort="-x"),
            color=c,
            order=o,
            opacity=alt.Opacity(
                "PositionType:N",
                scale=alt.Scale(
                    domain=["Start", "Bench"],
                    range=[1.0, 0.6]
                ),
                legend=None
            ),
            tooltip=[
                "Player:N",
                "Squad:N",
                alt.Tooltip("count()", title="Games"), 
                alt.Tooltip("TotalGames:Q", title="Total Games")
            ],
        ).transform_filter(
            legend
        ).add_params(
            legend
        ).transform_joinaggregate(
            TotalGames="count()", groupby=["Player"]
        ).transform_filter(
            f"datum.TotalGames >= {2*min}"
        ).properties(
            width=500,
            height=alt.Step(15),
            title=alt.Title(
                text=f"{'1st XV' if squad==1 else ('2nd XV' if squad==2 else 'Total')} Appearances (since 2021)",
                subtitle=f"Minimum {2*min} appearances total). Lighter shaded bars represent bench appearances.",
                subtitleFontStyle="italic",
            ),
        )
        return alt.vconcat(chart, agg_chart)
    
    return chart

import json

def most_common_players(df, by="Position"):
    mcp = df.groupby(["Player", by]).size().reset_index(name=f"Count{by}")\
        .sort_values(f"Count{by}", ascending=False)\
        .groupby(by).head(4).reset_index(drop=True)\
        .sort_values([by, f"Count{by}"], ascending=[True,False]).reset_index(drop=True)
    
    if by == "Position":
        return mcp  
    else:
        mcp["Position"]=mcp["Number"].map(d)
        return mcp[mcp["Number"] <= 15]

# Function to get top N players in each position (by total starts):
# 1 for hooker/scrum half/fly half
# 2 for prop/second row/centre
# 3 for back row/back three
def top_by_position(x):
    if x["Position"].iloc[0] in ["Hooker", "Scrum Half", "Fly Half"]:
        return x.nlargest(1, "CountPosition", "first")
    elif x["Position"].iloc[0] in ["Prop", "Second Row", "Centre"]:
        return x.nlargest(2, "CountPosition", "first")
    else:
        return x.nlargest(3, "CountPosition", "first")

def team_of_the_season(squad=1, season="2024/25", bench_forwards=2, bench_backs=1):

    df = players(squad)
    df = df[df["Season"] == season]

    mcp = most_common_players(df, by='Position')
    mcn = most_common_players(df, by='Number')

    #### STARTERS ####
    starters = mcp.groupby("Position").apply(top_by_position)\
        .reset_index(drop=True)

    starters = starters.merge(mcn, on=["Player","Position"], how="left")
    starters = starters.sort_values(["CountPosition", "CountNumber"], ascending=[False,False])

    # If a Player appears only once, delete all other rows with their Number
    unique = starters.groupby("Player").filter(lambda x: len(x) == 1)

    starters = pd.concat([unique, starters[~starters["Number"].isin(unique["Number"])]])

    # If a Number appears only once, delete all other rows for that Player
    unique = starters.groupby("Number").filter(lambda x: len(x) == 1)

    starters = pd.concat([unique, starters[~starters["Player"].isin(unique["Player"])]])
    if len(starters) > len(set(starters["Player"])):
        starters.sort_values(["CountPosition", "CountNumber"], ascending=[False,False])
        for p in set(starters["Player"]):
            # Keep only the row with the highest Count for each Player
            # Delete other rows for that player from starters
            p_row = starters[starters["Player"] == p].nlargest(1, "CountPosition")
            starters = pd.concat([p_row, starters[(starters["Player"] != p) & (starters["Number"] != p_row["Number"].iloc[0])]])

        starters = starters[["Number", "Position", "Player", "CountPosition", "CountNumber"]].sort_values("Number")

    #### BENCH ####
    apps = players_agg(squad)
    apps = apps[apps["Season"]==season].sort_values(["TotalGames", "TotalStarts"], ascending=False)
    apps = apps[['Player', 'MostCommonPosition', 'MostCommonPositionType', 'TotalGames', 'TotalStarts']]


    # Keep first 2 rows with MostCommonPositionType=="Forwards" and first row with "Backs"
    bench = apps[~apps["Player"].isin(starters["Player"])]
    bench = bench.groupby("MostCommonPositionType")\
        .apply(lambda x: x.nlargest(
            bench_forwards if all(x["MostCommonPositionType"]=="Forwards") else bench_backs, 
            "TotalGames", "all"))\
        .reset_index(drop=True)\
        .sort_values("MostCommonPositionType", ascending=False)\
        .reset_index(drop=True)

    bench["Number"] = bench.index + 16
    bench = bench[["Number", "Player", "TotalStarts", "TotalGames"]]
    # bench.rename(columns={"TotalStarts": "Count_p", "TotalGames":"Count"}, inplace=True)

    # Count per Player
    apps = apps.groupby("Player").agg({"TotalGames":"sum", "TotalStarts":"sum"}).reset_index()
    coords = pd.DataFrame([
            {"Position": "Prop", "n": 1, "x": 10, "y": 95},
            {"Position": "Hooker", "n": 2, "x": 25, "y": 95},
            {"Position": "Prop", "n": 3, "x": 40, "y": 95},
            {"Position": "Second Row", "n": 4, "x": 17, "y": 82},
            {"Position": "Second Row", "n": 5, "x": 33, "y": 82},
            {"Position": "Back Row", "n": 6, "x": 6, "y": 72},
            {"Position": "Back Row", "n": 7, "x": 44, "y": 72},
            {"Position": "Back Row", "n": 8, "x": 25, "y": 67},
            {"Position": "Scrum Half", "n": 9, "x": 25, "y": 50},
            {"Position": "Fly Half", "n": 10, "x": 42, "y": 45},
            {"Position": "Back Three", "n": 11, "x": 8, "y": 20},
            {"Position": "Centre", "n": 12, "x": 59, "y": 38},
            {"Position": "Centre", "n": 13, "x": 75, "y": 30},
            {"Position": "Back Three", "n": 14, "x": 92, "y": 20},
            {"Position": "Back Three", "n": 15, "x": 50, "y": 10},
            {"Position": None, "n": 16, "x": 75, "y": 86},
            {"Position": None, "n": 17, "x": 75, "y": 78},
            {"Position": None, "n": 18, "x": 75, "y": 70},
            {"Position": None, "n": 19, "x": 75, "y": 62},
            {"Position": None, "n": 20, "x": 75, "y": 54},
            {"Position": None, "n": 21, "x": 75, "y": 46},
            {"Position": None, "n": 22, "x": 75, "y": 38},
            {"Position": None, "n": 23, "x": 75, "y": 30},
        ])
    bench = bench.merge(coords, left_on="Number", right_on="n", how="inner").drop(columns="n")

    starters = starters.merge(coords, left_on="Number", right_on="n", how="inner").sort_values("Number").drop(columns="n")
    starters = starters.merge(apps, left_on="Player", right_on="Player", how="inner").sort_values("Number", ascending=False)
    starters = pd.concat([starters, bench]).sort_values("Number")

    return starters

def team_of_the_season_chart(squad=1, season="2024/25", **kwargs):
    
    top = team_of_the_season(squad, season, **kwargs)

    top_count = top["TotalStarts"].sum() 
    p = players(squad)
    season_count = len(p[(p["Season"]==season) & (p["Number"]<=15)])

    prop = top_count/season_count

    with open("tots_lineup.json") as f:
        chart = json.load(f)
    
    chart["title"]["text"] = f"{'1st' if squad==1 else '2nd'} XV Team of the Season"
    chart["title"]["subtitle"][1] = chart["title"]["subtitle"][1].replace("XXX", f"{prop:.0%}")
    chart["data"]["values"] = top.to_dict(orient="records")
    
    return alt.Chart.from_dict(chart)
def team_sheet_chart(
        squad=1, 
        names=None, 
        captain=None, 
        vc=None, 
        opposition=None, 
        home=True, 
        competition="Counties 1 Sussex",
        season="2024/25"
    ):

    if names is None:
        df = team_sheets(squad=1) 

        # Last row as dict
        team = df.iloc[-1].to_dict()


        label = f'{"1st" if squad==1 else "2nd"} XV vs {team["Opposition"]}({team["Home/Away"]})'
        captain = team["Captain"]
        vc = team["VC"]
        season = team["Season"]
        competition = team["Competition"]

        # Keep keys that can be converted to integers
        team = {int(k): v for k, v in team.items() if k.isnumeric() and v}

        # Convert team to dataframe with Number and Player columns
        team = pd.DataFrame(team.items(), columns=["Number", "Player"])

    else:
        label = f'{"1st" if squad==1 else "2nd"} XV vs {opposition} ({"H" if home else "A"})'

        # Convert names to Player column of a dataframe with Number column (1-len(names))
        team = pd.DataFrame({"Player": names, "Number": range(1, len(names)+1)})

    coords = pd.DataFrame([
                {"n": 1, "x": 10, "y": 81},
                {"n": 2, "x": 25, "y": 81},
                {"n": 3, "x": 40, "y": 81},
                {"n": 4, "x": 18, "y": 69},
                {"n": 5, "x": 32, "y": 69},
                {"n": 6, "x": 6, "y": 61},
                {"n": 7, "x": 44, "y": 61},
                {"n": 8, "x": 25, "y": 56},
                {"n": 9, "x": 20, "y": 42},
                {"n": 10, "x": 38, "y": 36},
                {"n": 11, "x": 8, "y": 18},
                {"n": 12, "x": 56, "y": 30},
                {"n": 13, "x": 74, "y": 24},
                {"n": 14, "x": 92, "y": 18},
                {"n": 15, "x": 50, "y": 10},
                {"n": 16, "x": 80, "y": 82},
                {"n": 17, "x": 80, "y": 74},
                {"n": 18, "x": 80, "y": 66},
                {"n": 19, "x": 80, "y": 58},
                {"n": 20, "x": 80, "y": 50},
                {"n": 21, "x": 80, "y": 42},
                {"n": 22, "x": 80, "y": 34},
                {"n": 23, "x": 80, "y": 26},
            ])
    team = team.merge(coords, left_on="Number", right_on="n", how="inner").drop(columns="n")

    # Add captain (C) and vice captain (VC) else None
    team["Captain"] = team["Player"].apply(lambda x: "C" if x == captain else "VC" if x == vc else None)

    team["Player"] = team["Player"].str.split(" ")

    team.to_dict(orient="records")

    with open("team-sheet-lineup.json") as f:
        chart = json.load(f)
    chart["data"]["values"] = team.to_dict(orient="records")
    chart["title"]["text"] = label
    chart["title"]["subtitle"] = f"{season} - {competition}"

    n_replacements = len(team) - 15
    
    y = 126 + (n_replacements * 64)
    chart["layer"][0]["mark"]["y2"] = y
    # return chart
    return alt.Chart.from_dict(chart)
# LINEOUTS

# Color scales
n_scale = {
    "domain": ["4", "5", "6", "7"], 
    "range": ["#ca0020", "#f4a582", "#92c5de", "#0571b0"]
}

calls4 = ["Yes", "No", "Snap"]
cols4 = ["#146f14", "#981515", "#981515"]
calls7 = ["A*", "C*", "A1", "H1", "C1", "W1", "A2", "H2", "C2", "W2", "A3", "H3", "C3", "W3"]
cols7 = 2*["orange"] + 4*["#146f14"] + 4*["#981515"] + 4*["orange"]
calls = ["Matlow", "Red", "Orange", "Plus", "Even +", "RD", "Even", "Odd", "Odd +", "Green +", "", "Green"]
cols = 5*["#981515"] + 6*["orange"] + ["#146f14"]

call_scale = {
    "domain": calls4 + calls7 + calls,
    "range": cols4 + cols7 + cols
}
setup_scale = {
    "domain": ["A", "C", "H", "W"],
    "range": ["dodgerblue", "crimson", "midnightblue", "black"]
}
setups = {"A": "Auckland", "C": "Canterbury", "H": "Highlanders", "W": "Waikato"}

# Sort orders
area_order = ["Front", "Middle", "Back"]
area_scale = {
    "domain": area_order, 
    "range": ['#981515', 'orange', '#146f14']
}



def counts(type, squad=1, season=None, df=None):
    
    if df is None:
        df = lineouts()

    df = df[df["Squad"] == ("1st" if squad == 1 else "2nd")]
    if season:
        df = df[df["Season"] == season]

    df = df.groupby([type, "Season"]).agg(
        Won = pd.NamedAgg(column="Won", aggfunc="sum"),
        Lost = pd.NamedAgg(column="Won", aggfunc="sum"),
        Total = pd.NamedAgg(column="Won", aggfunc="count")
    ).reset_index()
    df["Success"] = df["Won"] / df["Total"]
    # Add column of sum(total) for each season
    df["SeasonTotal"] = df.groupby("Season")["Total"].transform("sum")
    df['Proportion'] = df['Total'] / df['SeasonTotal']
    # "Won" / "Total" as a string
    df["SuccessText"] = df.apply(lambda x: str(x["Won"]) + " / " + str(x["Total"]), axis=1)

    return df

def count_success_chart(type, squad=1, season=None, as_dict=False, min=1, df=None):
    
    if df is None:
        df = lineouts()
    
    df = df[df["Squad"] == ("1st" if squad == 1 else "2nd")]
    if season:
        df = df[df["Season"] == season]
    
    with open("lineout-template.json") as f:
        chart = json.load(f)

    if season is None:
        chart["title"]["text"] = f"Lineout Stats by {type}"

        subtitle = {
            "Area": "Area of the lineout targeted",
            "Numbers": "Number of players in the lineout (not including the hooker and receiver)",
            "Jumper": [f"Minimum {min} lineouts", "NOTE: Jumper success is dependent on other factors, such as the throw and lift."],
            "Hooker": [f"Minimum {min} lineouts", "NOTE: Hooker success is dependent on other factors, such as the jumper and lifting pod winning the ball."],
            "Call": [f"Minimum {min} lineouts", "Colour denotes calls to the front (red), middle (orange), or back (green)."],
            "Setup": "Lineout setups introduced in the 2023/24 season - Auckland, Canterbury, Highlanders, Waikato.",
            "Movement": [
                "Type of movements:", 
                "    - 'Jump' - the jumper is lifted where he stands",
                "    - 'Move' - moves to the jumping position after entering the lineout",
                "    - 'Dummy' - there is a dummy jump first"
            ]
        }
        chart["title"]["subtitle"] = subtitle[type]

    chart["spec"]["layer"][0]["layer"][0]["params"][0]["name"] = f"select{type}"
    chart["spec"]["layer"][0]["layer"][0]["params"][0]["select"]["fields"] = [type]
    chart["spec"]["encoding"]["opacity"]["condition"]["param"] = f"select{type}"
    chart["spec"]["encoding"]["x"]["field"] = type
    chart["spec"]["encoding"]["color"]["field"] = type
    chart["spec"]["encoding"]["tooltip"][0]["field"] = type
    chart["resolve"]["scale"]["x"] = "independent"
    chart["resolve"]["scale"]["color"] = "shared"
    chart["transform"][0]["groupby"].append(type)
    chart["transform"][2]["groupby"].append(type)

    # Unique IDs for Jumper/Hooker/Setup/Movement/Call
    df["JumperID"] = df["Jumper"].astype("category").cat.codes
    df["HookerID"] = df["Hooker"].astype("category").cat.codes
    df["SetupID"] = df["Setup"].astype("category").cat.codes
    df["MovementID"] = df["Movement"].astype("category").cat.codes
    df["CallID"] = df["Call"].astype("category").cat.codes
    if type in ["Jumper", "Hooker", "Setup", "Movement", "Call"]:
        chart["transform"].append({"calculate": f"datum.Total + datum.Success + 0.01*datum.{type}ID", "as": "sortcol"})
        chart["transform"][0]["groupby"].append(f"{type}ID")
        chart["transform"][2]["groupby"].append(f"{type}ID")
        

    if type == "Area":
        chart["spec"]["encoding"]["color"]["scale"] = area_scale
        chart["spec"]["encoding"]["color"]["sort"] = "descending"
        chart["spec"]["encoding"]["x"]["sort"] = area_order
        chart["spec"]["encoding"]["x"]["title"] = f"Target {type}"


    if type == "Numbers":
        chart["spec"]["encoding"]["color"]["scale"] = n_scale

    if type in ["Jumper", "Hooker"]:
        if type=="Jumper":
            chart["spec"]["width"]["step"] = 40
        chart["spec"]["encoding"]["color"]["scale"] = {"scheme": "tableau20"}
        chart["spec"]["encoding"]["color"]["sort"] = {"field": "Total", "order": "descending"}
        chart["spec"]["encoding"]["x"]["sort"] = {"field": "sortcol", "order": "descending"}

    if type == "Call":
        chart["spec"]["width"]["step"] = 30 if season is None else 40
        chart["spec"]["encoding"]["x"]["sort"] = {"field": "sortcol", "order": "descending"}
        chart["spec"]["encoding"]["x"]["title"] = None
        chart["spec"]["encoding"]["color"]["scale"] = call_scale
        chart["transform"][0]["groupby"].append("CallType")
        chart["transform"][2]["groupby"].append("CallType")

    if type == "Setup":
        chart["spec"]["encoding"]["x"]["sort"] = {"field": "sortcol", "order": "descending"}
        chart["spec"]["encoding"]["color"]["scale"] = setup_scale
        chart["spec"]["encoding"]["color"]["legend"] = None if season else {"title": "Setup", "orient": "right", "labelExpr": "datum.label == 'A' ? 'Auckland' : (datum.label == 'C' ? 'Canterbury' : (datum.label == 'H' ? 'Highlanders' : 'Waikato'))"}
        chart["transform"].append({"filter": "datum.Setup != null"})
    
    if type == "Movement":
        chart["spec"]["encoding"]["x"]["sort"] = {"field": "sortcol", "order": "descending"}
        chart["spec"]["encoding"]["color"]["scale"] = {"range": ["#981515", "#146f14", "black"]}            
        chart["spec"]["encoding"]["x"]["axis"] = {
            "ticks": False,
            "labelExpr": "datum.label == 'D' ? 'Dummy' : (datum.label == 'M' ? 'Move' : 'Jump')",
            "labelFontSize": 12,
            "labelPadding": 10
        }


    chart["transform"].insert(0, deepcopy(chart["transform"][0]))
    chart["transform"][0]["joinaggregate"][0]["as"] = "TotalOverall"
    chart["transform"][1]["joinaggregate"][0]["as"] = "Total"
    chart["transform"].insert(1, {"filter": f"datum.TotalOverall >= {min}"})

    if season:
        if type == "Call":
            chart["facet"] = {
                "field": "CallType", 
                "header": {"title": "Call", "orient": "bottom"},
                "sort": ["Standard", "4-man only", "6/7-man only"]
            }
        else:
            chart.update(chart["spec"])
            chart["resolve"]["scale"]["x"] = "shared"
            del chart["facet"]
            del chart["spec"]
    
    chart["data"]["values"] = df.to_dict(orient="records")
    
    if as_dict:
        return chart
    else:
        return alt.Chart.from_dict(chart)

def lineout_chart(squad=1, season=None, df=None):

    if df is None:
        df = lineouts()

    df = df[df["Squad"] == ("1st" if squad == 1 else "2nd")]
    if season:
        df = df[df["Season"] == season]

    types = ["Numbers", "Area", "Hooker", "Jumper", "Setup"]

    movement_chart = count_success_chart("Movement", squad, season, df=df)
    movement_chart["transform"][2:2] = [{"filter": {"param": f"select{f}"}} for f in types]
    movement_chart["layer"][1]["encoding"]["y"]["axis"]["labels"] = False
    movement_chart["layer"][1]["encoding"]["y"]["title"] = None

    call_chart = count_success_chart("Call", squad, season, df=df)
    call_chart["transform"][2:2] = [{"filter": {"param": f"select{f}"}} for f in types + ["Movement"]]
    call_chart["spec"]["layer"][0]["encoding"]["y"]["axis"]["labels"] = False
    call_chart["spec"]["layer"][0]["encoding"]["y"]["title"] = None
    
    charts = []
    for i,t in enumerate(types):
        min = 3 if t in ["Hooker", "Jumper"] else 1
        chart = count_success_chart(t, squad, season, as_dict=True, min=min, df=df)

        filters = [{"filter": {"param": f"select{f}"}} for f in types + ["Movement"] if f != t]
        chart["transform"][2:2] = filters

        if i < len(types) - 1:
            chart["layer"][1]["encoding"]["y"]["axis"]["labels"] = False
            chart["layer"][1]["encoding"]["y"]["title"] = None
        
        if i > 0:
            chart["layer"][0]["encoding"]["y"]["axis"]["labels"] = False
            chart["layer"][0]["encoding"]["y"]["title"] = None
        
        charts.append(alt.Chart.from_dict(chart))

    bottom = alt.hconcat(movement_chart, call_chart).resolve_scale(color='independent', y="shared")
    top = alt.hconcat(*charts).resolve_scale(color='independent', y="shared")

    chart = alt.vconcat(top, bottom).resolve_scale(color='independent')

    chart["title"] = {
        "text": f"{'1st' if squad==1 else '2nd'} XV Lineouts {season}",
        "subtitle": [
            "Distribution of lineouts (bar), and success rate (line). Click to highlight and filter.",
            "Success is defined as retaining possession when the lineout ends, and does not distinguish between an unsuccessful throw, a knock-on, or a penalty."
        ]  
    }
    
    return chart


def points_scorers_chart(squad=1, season="2024/25", df=None):

    if df is None:
        df = pitchero_stats()
    if squad != 0:
        df = df[df["Squad"] == ("1st" if squad == 1 else "2nd")]
    if season:
        df = df[df["Season"] == season]
    
    scorers = df[df["Points"] > 0]

    scorers = scorers.drop("Points", axis=1)
    scorers = scorers.melt(
        id_vars=[c for c in scorers.columns if c not in ["Tries", "Pens", "Cons"]], 
        var_name="Type", 
        value_name="Points"
    )
    
    scorers["label"] = scorers.apply(lambda x: f"{x['T']}T" if x['Type']== "Tries" else (f"{x['PK']}P" if x["Type"]=="Pens" else f"{x['Con']}C"), axis=1)

    selection = alt.selection_point(fields=['Type'], bind='legend')

    chart = alt.Chart(scorers).mark_bar().transform_calculate(
        label="if(datum.T>0, datum.T + 'T ', '') + if(datum.Con>0, datum.Con + 'C ', '') + if(datum.PK>0, datum.PK + 'P ', '')"
    ).encode(
        x=alt.X("sum(Points):Q", axis=alt.Axis(orient="top", title="Points")),
        y=alt.Y(
            "Player:N", 
            sort=alt.EncodingSortField(field="sortfield", order="descending"), 
            title=None
        ),
        color=alt.Color(
            "Type:N", 
            legend=alt.Legend(
                title="Click to filter",
                titleOrient="left",
                orient="bottom",
            ), 
            scale=alt.Scale(domain=['Tries', 'Pens', 'Cons'], range=["#202947", "#981515", "#146f14"]                )
        ),
        order=alt.Order("Type:N", sort="descending"),
        tooltip=[
            alt.Tooltip("Player:N", title=" "), 
            alt.Tooltip("label", title="  "),
            alt.Tooltip("A:Q", title="Games"),
        ],
        text=alt.Text("label:N"),
        row=alt.Row("Squad:N", spacing=5, header=alt.Header(title=None) if squad == 0 else None),
        column=alt.Column("Season:O", spacing=5, header=alt.Header(title=None, labelFontSize=24) if season is None else None),
    ).transform_joinaggregate(
        sortfield="sum(Points)",    
        groupby=["Player", "Type", "Season", "Squad"],
    ).transform_filter(
        selection
    ).properties(
        title=alt.Title(
            text=("1st XV " if squad==1 else "2nd XV " if squad==2 else "") + "Points Scorers",
            subtitle="According to Pitchero data"
        ),
        width=400 if season else 200
    ).add_params(
        selection
    ).resolve_scale(
        x="shared",
        y="independent"
    )

    return chart

def card_chart(squad=0, season="2024/25", df=None):

    if df is None:
        df = pitchero_stats()
    if squad != 0:
        df = df[df["Squad"] == ("1st" if squad == 1 else "2nd")]
    if season:
        df = df[df["Season"] == season]

    df.loc[:, "Cards"] = df["YC"] + df["RC"]
    df = (df[df["Cards"] > 0])[["Player","A","YC","RC", "Cards", "Season", "Squad"]]
        
    df = df.sort_values(["Season", "Cards", "RC"], ascending=[True, False, True])

    title = f"{'1st XV' if squad==1 else ('2nd XV' if squad==2 else 'Total')} Cards"

    chart = alt.Chart(df).mark_bar(stroke="black", strokeOpacity=0.2).encode(
        y=alt.Y("Player:N", title=None, sort=alt.EncodingSortField(field="Cards", order="descending")),
        x=alt.X("value:Q", title="Cards", axis=alt.Axis(values=[0,1,2,3,4,5], format="d")),        
        color=alt.Color(
            "key:N", 
            title=None, 
            legend=alt.Legend(orient="bottom")
        ).scale(domain=["YC", "RC"], range=["#e6c719", "#981515"]),
        tooltip=["Player:N", alt.Tooltip("A:Q", title="Appearances"), "YC:Q", "RC:Q", "Squad:N"],
        column=alt.Column("Season:O", spacing=5, header=alt.Header(title=None, labelFontSize=24) if season is None else None),
    ).transform_fold(
        ["YC", "RC"]
    ).resolve_scale(
        y="independent"
    ).properties(
        title=alt.Title(text=title, subtitle="According to Pitchero data"), 
        width=200 if season else 120
    )    

    return chart

def captains_chart(season="2024/25", df=None):

    if df is None:
        df = team_sheets()
    
    df = df.rename(columns={"VC1":"VC"})

    captains = df[["Squad", "Season", "Captain", "VC", "GameType"]].melt(
        id_vars=["Squad", "Season", "GameType"], 
        value_vars=["Captain", "VC"],
        var_name="Role",
        value_name="Player"
    ).dropna()
        
    if season:
        captains = captains[captains["Season"]==season]
    captains = captains[captains["GameType"]!="Friendly"]

    chart = alt.Chart(captains).mark_bar().encode(
        y=alt.X("Player:N", title=None, sort="-x"),
        x=alt.X("count()", title="Games", sort=alt.EncodingSortField(field="Role", order="descending")),
        color=alt.Color(
            "Role:N",
            scale=alt.Scale(
                domain=["Captain", "VC"], 
                range=["#202947", "#7d96e8"]                
            ),
            legend=alt.Legend(title=None, direction="horizontal", orient="bottom")
        ), 
        row=alt.Row("Squad:N", title=None, header=alt.Header(title=None, orient="left")),
        column=alt.Column("Season:O", header=alt.Header(title=None, labelFontSize=24)),
    ).properties(
        title=alt.Title("1st & 2nd XV Captains", subtitle=["League & Cup Captains and Vice-Captains", "(Friendly games excluded)"]),
        width=400 if season else 250,
    ).resolve_scale(
        x="shared",
        y="independent"
    )

    return chart

def results_chart(squad=1, season=None, df=None):

    if df is None:
        df = team_sheets()

    if season is not None:
        df = df[df["Season"]==season]
    if squad != 0:
        df = df[df["Squad"]==("1st" if squad==1 else "2nd")]

    df["loser"] = df.apply(lambda x: x["PF"] if x["Result"] == "L" else x["PA"], axis=1)
    df["winner"] = df.apply(lambda x: x["PF"] if x["Result"] == "W" else x["PA"], axis=1)

    selection = alt.selection_point(fields=['Result'], bind='legend')

    bar = alt.Chart(df).mark_bar(point=True).encode(
        y=alt.Y(
            'GameID:N', 
            sort=None, 
            axis=alt.Axis(
                title=None, 
                offset=15, 
                grid=False, 
                ticks=False, 
                domain=False, 
                # labelExpr="split(datum.value,'-__-')[1]"
            )
        ),
        x=alt.X('PF:Q', title="Points", axis=alt.Axis(orient='top', offset=5)),
        x2='PA:Q',
        color=alt.Color(
            'Result:N', 
            scale=alt.Scale(domain=['W', 'L'], range=['#146f14', '#981515']), 
            legend=alt.Legend(offset=20, title=["Click to","highlight"])
        ),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
            
    )

    loser = alt.Chart(df).mark_text(align='right', dx=-2, dy=0, color='black').encode(
        y=alt.Y('GameID:N', sort=None),
        x=alt.X('loser:Q', title=None, axis=alt.Axis(orient='bottom', offset=5)),
        text='loser:N',
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
    )

    winner = alt.Chart(df).mark_text(align='left', dx=2, dy=0, color='black').encode(
        y=alt.Y('GameID:N', sort=None),
        x=alt.X('winner:Q', title=None, axis=alt.Axis(orient='bottom', offset=5)),
        text='winner:N',
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
    )

    return (bar + loser + winner).add_params(
        selection
    ).properties(
        title=alt.Title(
            text=("1st" if squad==1 else "2nd") + " XV Results", 
            subtitle=["Bars show the scores of the losing team on the left and winning team on the right.", "Larger bars indicate larger winning margins."],
            offset=20
        ), 
        width=400
    )


seasons = ["2021/22", "2022/23", "2023/24", "2024/25"]

turnover_filter = alt.selection_point(fields=["Turnover"], bind="legend")
put_in_filter = alt.selection_point(fields=["Team"], bind="legend")
team_filter = alt.selection_point(encodings=["y"])

color_scale = alt.Scale(domain=["EG", "Opposition"], range=["#202946", "#981515"])
opacity_scale = alt.Scale(domain=[True, False], range=[1, 0.5])

def set_piece_h2h_chart(squad=1, season="2024/25", event="lineout", df=None):

    if df is None:
        df = set_piece_results()
    
    prefix = "l_" if event == "lineout" else "s_"
    df = df[["Squad", "Season", "Date", "Opposition", "Home/Away"]+[c for c in df.columns if prefix in c or "EG" in c]]
    df = df[df["Squad"] == squad]
    df = df[df["Season"] == season]


    df["EG_lost"] = df[f"EG_{prefix}total"] - df[f"EG_{prefix}won"]
    df["Opp_lost"] = df[f"Opp_{prefix}total"] - df[f"Opp_{prefix}won"]
    df = df.rename(columns={
        f"EG_{prefix}won": "EG_won",
        f"Opp_{prefix}won": "Opp_won",
    })

    # Drop columns containing prefix
    df = df.drop(columns=[c for c in df.columns if "l_" in c or "s_" in c])

    # Create ID column from Opposition and Home/Away (appending "(1)" or "(2)" if there are multiple games with the same Opposition and Home/Away)
    df["GameID"] = df["Opposition"] + " (" + df["Home/Away"] + ") "
    df["GameID"] = df["GameID"] + df.groupby(["GameID", "Season"]).cumcount().replace(0, "").astype(str)

    df = df.melt(
        id_vars=["Season", "GameID", "Opposition", "Home/Away", "Date"], 
        var_name="Outcome", 
        value_name="Count"
    )
    df["Turnover"] = df["Outcome"].str.contains("lost")
    df["Team"] = df["Outcome"].apply(lambda x: "EG" if x in ["EG_won", "EG_lost"] else "Opposition")

    base = (
        alt.Chart(df).encode(
            y=alt.Y("GameID:N", axis=None),
            yOffset="Team:N",
            color=alt.Color(
                "Team:N", 
                scale=color_scale, 
                legend=alt.Legend(
                    title="Attacking team",
                    orient="bottom", 
                    direction="horizontal",
                )
            ),
            opacity=alt.Opacity(
                "Turnover:N", 
                scale=opacity_scale, 
                legend=alt.Legend(
                    labelExpr="datum.value ? 'Turnover' : 'Retained'", 
                    title="Result", 
                    orient="bottom", 
                    direction="horizontal",
                )
            ),
            tooltip=[
                alt.Tooltip("Opposition:N", title="Opposition"),
                alt.Tooltip("Date:T", title="Date"),
                alt.Tooltip("Team:N", title="Attacking team"),
                alt.Tooltip("Count:Q", title="EG wins"),
            ]
        )
        .add_params(turnover_filter, put_in_filter, team_filter)
        .transform_filter(turnover_filter)
        .transform_filter(put_in_filter)
        .transform_filter(team_filter)
        .properties(height=alt.Step(12), width=120)
    )

    eg = (
        base.mark_bar(stroke="#202946")
        .encode(
            x=alt.X(
                "Count:Q",
                axis=alt.Axis(title="EG wins", orient="top", titleColor="#202946"),
                scale=alt.Scale(domain=[0, df["Count"].max()]),
            )
        )
        .transform_filter({"field":"Outcome", "oneOf":["Opp_lost", "EG_won"]})
    )

    opp = (
        base.mark_bar(stroke="#981515")
        .encode(
            x=alt.X(
                "Count:Q",
                scale=alt.Scale(domain=[0, df["Count"].max()], reverse=True),
                axis=alt.Axis(title="Opposition wins", orient="top", titleColor="#981515")
            ),
            y=alt.Y("GameID:N", title=None, axis=alt.Axis(orient="left")),
        )
        .transform_filter({"field":"Outcome", "oneOf":["Opp_won", "EG_lost"]})
    )
    return (
        alt.hconcat(opp, eg, spacing=0)
        .resolve_scale(y="shared", yOffset="independent")
        .properties(title=alt.Title(text=season, anchor="middle", fontSize=36))
    )

def set_piece_h2h_charts(squad=1, event="lineout", df=None):

    if df is None:
        df = set_piece_results()

    charts = [set_piece_h2h_chart(squad, s, event, df) for s in seasons]

    chart = (
        alt.hconcat(*charts)
        .resolve_scale(color="shared", opacity="shared", y="independent")
        .properties(
            title=alt.Title(
                text=f"{event.capitalize()} Head-to-Head", 
                subtitle=[
                    f"Number of {event}s and turnovers for both teams in each game",
                    f"Click the legends to view only turnovers, or to view only one team's {event}s.",
                    "Click the bar charts to select all games against that specific opposition."
                ]
            )
        )
    )
    return chart
# Create custom style for altair charts
import altair as alt
import pandas as pd
from data_prep import *

# Set the default configuration for altair
def alt_theme():

    font="Helvetica Neue, Helvetica, Arial, sans-serif"
    
    return {
        "config": {
            "opacity": 0.7,
            "axis": {
                "font": font,
                "labelFontSize": 14,
                "titleFontSize": 18
            },
            "header": {
                "font": font,
                "labelFontSize": 18,
                "titleFontSize": 20,
                "labelFontWeight": "bold",
                "orient": "left"
            },
            "legend": {
                "font": font,
                "labelFontSize": 14,
                "titleFontSize": 12,
                "titlePadding": 5,
                "fillColor": "white",
                "strokeColor": "black", 
                "padding": 10,
                "titleFontWeight": "lighter",
                "titleFontStyle": "italic",
                "titleColor": "gray",
            },
            "title": {
                "font": font,
                "fontSize": 24,
                "fontWeight": "bold",
                "anchor": "middle",
                "align": "center",
                "titlePadding": 20,
                "subtitlePadding": 10,
                "subtitleFontWeight": "lighter",
                "subtitleFontSize": 12,
                "subtitleColor": "gray",
                "subtitleFontStyle": "italic",
            },
            "axisX": {
                "labelAngle": 0
            },
            "facet": {
                "title": None,
                "header": {"title": None},
                "font": font,
                "align": {"row": "each", "column": "all"},  
            },
            "resolve": {
                "scale": {
                    "y": "independent",
                    "facet": "independent"
                }
            },
            "background": "aliceblue"
        }
    }

alt.themes.register("my_custom_theme", alt_theme)
alt.themes.enable("my_custom_theme")


def plot_starts_by_position(squad=1, season="2023/24", fb_only=False):

    df = players(squad)

    # legend selection filter
    legend = alt.selection_point(fields=["GameType"], bind="legend", on="click")

    title = f"{'1st' if squad==1 else '2nd'} XV Starts (by position)"

    if fb_only:
        facet=alt.Facet("PositionType:N", sort=["Forwards", "Backs"], columns=2, title=None)
    else:
        facet=alt.Facet("Position:N", columns=2, sort=["Prop", "Scrum Half", "Hooker", "Fly Half", "Second Row", "Centre", "Back Row", "Back Three"], title=None, align="each")

    # altair bar chart of starts by position
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('count()', axis=alt.Axis(title="Starts", orient="bottom")),
        y=alt.Y('Player:N', sort='-x', title=None),
        facet=facet,
        tooltip=["Player", "Position", "count()"],
        # Map game type to color ordered by league, cup, friendly
        color=alt.Color(
             "GameType:N",
            scale=alt.Scale(
                domain=["League", "Cup", "Friendly"], 
                range=["darkblue", "lightblue", "green"]                
            ), legend=alt.Legend(title=None)
        ),
        order=alt.Order('GameType:N', sort='descending')
    ).transform_filter(
        (alt.datum.Season == season) & (alt.datum.Number <= 15)
    ).transform_filter(
        legend
    ).resolve_scale(
        y="independent",
        x="shared"
    ).properties(
        width=200, 
        height=alt.Step(18),
        title=title
    ).add_params(legend)

    return chart

def plot_games_by_season(games):
    chart = alt.Chart(games).mark_bar().encode(
        x=alt.X('Season:N', title='Season', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('count():Q', title='Games Played'),
        color=alt.Color(
            "GameType:N",
            scale=alt.Scale(
                domain=["League", "Cup", "Friendly"], 
                range=["darkblue", "lightblue", "green"]                
            )
        ),
        order=alt.Order('GameType:N', sort='descending')
    ).properties(
        title=alt.Title('1st Team Games by Season'),
        width=alt.Step(50),
        height=300,
    )
    return chart

# Plot the number of games played by each player in the 2023/24 season
def plot_games_by_player(squad, season="2023/24", min_games=5):

    if squad == 1:
        p = players(1)
    elif squad == 2:
        p = players(2)
    else:
        p = pd.concat([players(1), players(2)])

    if squad == 0:
        c = alt.Color(
            "Squad:N",
            scale=alt.Scale(
                domain=["1st", "2nd"], 
                range=["darkblue", "green"]                
            ),
            legend=alt.Legend(
                title="Click to filter", 
                orient="none",
                legendX=300,
                legendY=250
            )
        )
        o = alt.Order('Squad', sort='descending')

    else:
        c = alt.Color(
            "GameType:N",
            scale=alt.Scale(
                domain=["League", "Cup", "Friendly"], 
                range=["darkblue", "lightblue", "green"]                
            ),
            legend=alt.Legend(
                title="Click to filter", 
                orient="none",
                legendX=300,
                legendY=250
            )
        )
        o = alt.Order('GameType', sort='descending')

    # legend selection filter
    legend = alt.selection_point(fields=["GameType" if squad != 0 else "Squad"], bind="legend", on="click")
    
    chart = alt.Chart(p).mark_bar(strokeWidth=2).encode(
        x=alt.X(
            "count()", 
            axis=alt.Axis(title="Appearances", orient="bottom")),
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
        tooltip=["Player", "GameType", "PositionType", "count()"]
    ).properties(
        title=alt.Title(
            text=f"{'1st' if squad==1 else ('2nd' if squad==2 else '1st & 2nd')} XV appearances",
            subtitle=f"Min. {min_games} appearances. Lighter shaded bars represent bench appearances.",
            subtitleFontStyle="italic",

        ),
        width=400,
        height=alt.Step(20)
    ).transform_filter(
        alt.FieldEqualPredicate(field="Season", equal=season)   
    ).transform_filter(
        legend
    ).add_params(
        legend
    ).transform_joinaggregate(
        TotalGames="count()",
        groupby=["Player"]
    ).transform_filter(
        f"datum.TotalGames >= {min_games}"
    )
    
    return chart

def squads_by_season(squad=1, min_games=5, add_rule=False):

    p = players(squad)

    if squad == 1:
        t = "1st"
    elif squad == 2:
        t = "2nd"
    else:
        t = "1st & 2nd"

    p["Game"] = p["Opposition"] + " (" + p["Home/Away"] + ") - " + p["Competition"]
    
    c_counts = p[p["GameType"].isin(["League", "Cup"])]\
        .groupby(["Season"]).agg({"Game": "nunique", "Player": "nunique"})\
        .reset_index().set_index("Season")\
        .to_dict()
    
    
    # League counts
    l_counts = p[p["GameType"] == "League"]\
        .groupby(["Season"]).agg({"Game": "nunique", "Player": "nunique"})\
        .reset_index().set_index("Season")\
        .to_dict()
    
    
    t_counts = p.groupby(["Season"]).agg({"Game": "nunique", "Player": "nunique"})\
        .reset_index().set_index("Season")\
        .to_dict()

    charts = []
    for season in ["2021/22", "2022/23", "2023/24"]:

        chart = plot_games_by_player(squad=squad, season=season, min_games=min_games).properties(
            width=250,
            title=alt.Title(text=season, subtitle=[
                f"{t_counts['Game'][season]} games total ({c_counts['Game'][season]} in league/cup)",
                f"{t_counts['Player'][season]} players used ({c_counts['Player'][season]} in league/cup)",
                ]
            )
        )
        
        if add_rule:
            chart = chart + alt.Chart(pd.DataFrame({"x": [c_counts['Game'][season]]})).mark_rule(color="red").encode(x="x")
        
        charts.append(chart)

    chart = alt.hconcat(*charts).properties(title=f"{t} Team Games")

    return chart

import json

def most_common_players(df, by="Position"):
    mcp = df.groupby(["Player", by]).size().reset_index(name="Count")\
        .sort_values("Count", ascending=False)\
        .groupby(by).head(4).reset_index(drop=True)\
        .sort_values([by, "Count"], ascending=[True,False]).reset_index(drop=True)
    
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
        return x.nlargest(1, "Count", "all")
    elif x["Position"].iloc[0] in ["Prop", "Second Row", "Centre"]:
        return x.nlargest(2, "Count", "all")
    else:
        return x.nlargest(3, "Count", "all")

def team_of_the_season(squad=1, season="2023/24", bench_forwards=2, bench_backs=1):

    df = players(squad)
    df = df[df["Season"] == season]

    mcp = most_common_players(df, by='Position')
    mcn = most_common_players(df, by='Number')

    #### STARTERS ####
    starters = mcp.groupby("Position").apply(top_by_position)\
        .reset_index(drop=True).rename(columns={"Count": "CountPosition"})

    starters = starters.merge(mcn, on=["Player","Position"], how="left")
    starters.sort_values(["CountPosition", "Count"], ascending=[False,False])

    # If a Player appears only once, delete all other rows with their Number
    unique = starters.groupby("Player").filter(lambda x: len(x) == 1)

    starters = pd.concat([unique, starters[~starters["Number"].isin(unique["Number"])]])

    # If a Number appears only once, delete all other rows for that Player
    unique = starters.groupby("Number").filter(lambda x: len(x) == 1)

    starters = pd.concat([unique, starters[~starters["Player"].isin(unique["Player"])]])

    starters.sort_values(["CountPosition", "Count"], ascending=[False,False])
    for p in set(starters["Player"]):
        # Keep only the row with the highest Count for each Player
        # Delete other rows for that player from starters
        p_row = starters[starters["Player"] == p].nlargest(1, "Count")
        starters = pd.concat([p_row, starters[(starters["Player"] != p) & (starters["Number"] != p_row["Number"].iloc[0])]])

    starters = starters[["Number", "Position", "Player", "CountPosition"]].sort_values("Number")
    starters.rename(columns={"CountPosition": "Count_p"}, inplace=True)

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
    bench.rename(columns={"TotalStarts": "Count_p", "TotalGames":"Count"}, inplace=True)

    # Count per Player
    apps = df.groupby("Player").size().reset_index(name="Count")
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

def team_of_the_season_chart(squad=1, season="2023/24", **kwargs):
    
    top = team_of_the_season(squad, season, **kwargs)

    top_count = top["Count"].sum() 
    p = players(squad)
    season_count = len(p[(p["Season"]==season) & (p["Number"]<=15)])

    prop = top_count/season_count

    with open("lineup.json") as f:
        chart = json.load(f)
    
    chart["title"]["text"] = f"{'1st' if squad==1 else '2nd'} XV Team of the Season"
    chart["title"]["subtitle"][1] = chart["title"]["subtitle"][1].replace("XXX", f"{prop:.0%}")
    chart["data"]["values"] = top.to_dict(orient="records")
    
    return alt.Chart.from_dict(chart)


# LINEOUTS

# Color scales
n_scale = {
    "domain": ["4", "5", "6", "7"], 
    "range": ["#ca0020", "#f4a582", "#92c5de", "#0571b0"]
}

calls4 = ["Yes", "No", "Snap"]
cols4 = ["darkgreen", "red", "red"]
calls7 = ["A1", "H1", "C1", "W1", "A2", "H2", "C2", "W2", "A3", "H3", "C3", "W3"]
cols7 = 4*["darkgreen"] + 4*["red"] + 4*["orange"]
calls = ["Matlow", "Red", "Orange", "Plus", "Even +", "RD", "Even", "Odd", "Odd +", "Green +", "", "Green"]
cols = 5*["red"] + 6*["orange"] + ["darkgreen"]

call_scale = {
    "domain": calls4 + calls7 + calls,
    "range": cols4 + cols7 + cols
}

# Sort orders
area_order = ["Front", "Middle", "Back"]
area_scale = {
    "domain": area_order, 
    "range": ['red', 'orange', 'darkgreen']
}


def counts(type, squad=1, season=None):
    
    df_init = lineouts(squad, season)

    df = df_init.groupby([type, "Season"]).agg(
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

def count_success_chart(type, squad=1, season=None, as_dict=False, min=1):
    # df = counts(type, squad, season)
    df = lineouts(squad, season)

    with open("lineout-template.json") as f:
        chart = json.load(f)

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
    chart["transform"].append({"filter": f"datum.Total >= {min}"})

    if type == "Area":
        chart["spec"]["encoding"]["color"]["scale"] = area_scale
        chart["spec"]["encoding"]["color"]["sort"] = "descending"
        chart["spec"]["encoding"]["x"]["sort"] = area_order
        chart["spec"]["encoding"]["x"]["title"] = f"Target {type}"

    if type == "Numbers":
        chart["spec"]["encoding"]["color"]["scale"] = n_scale

    if type in ["Jumper", "Hooker"]:
        chart["spec"]["encoding"]["color"]["scale"] = {"scheme": "tableau20"}
        chart["spec"]["encoding"]["color"]["sort"] = {"field": "Total", "order": "descending"}
        chart["spec"]["encoding"]["x"]["sort"] = {"field": "sortcol", "order": "descending"}
        chart["transform"].append({"calculate": "datum.Total + datum.Success", "as": "sortcol"})

    if type == "Call":
        df["CallType"] = df["Call"].apply(call_type)

        chart["spec"]["encoding"]["x"]["sort"] = {"field": "sortcol", "order": "descending"}
        chart["spec"]["encoding"]["x"]["title"] = None
        chart["spec"]["encoding"]["color"]["scale"] = call_scale
        chart["transform"][0]["groupby"].append("CallType")
        chart["transform"][2]["groupby"].append("CallType")
        chart["transform"].append({"calculate": "datum.Total + datum.Success", "as": "sortcol"})
        chart["spec"]["encoding"]["tooltip"].append({"field": "sortcol"})
    
    if type == "Dummy":
        chart["spec"]["encoding"]["color"]["scale"] = {"range": ["red", "green", "black"]}
        chart["spec"]["encoding"]["x"]["title"] = None
        chart["spec"]["encoding"]["x"]["sort"] = {"field": type, "order": "descending"}
        chart["spec"]["encoding"]["x"]["axis"] = {
            "ticks": False,
            "labelExpr": "datum.label == 'D' ? 'Dummy' : (datum.label == 'M' ? 'Move' : 'Jump')",
            "labelFontSize": 12,
            "labelPadding": 10
        }

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

def lineout_chart(squad=1, season=None):

    types = ["Numbers", "Area", "Hooker", "Jumper"]

    dummy_chart = count_success_chart("Dummy", squad, season)
    dummy_chart["transform"] = [{"filter": {"param": f"select{f}"}} for f in types] + dummy_chart["transform"]
    dummy_chart["layer"][0]["encoding"]["y"]["axis"]["labels"] = False
    dummy_chart["layer"][0]["encoding"]["y"]["title"] = None
    dummy_chart["layer"][1]["encoding"]["y"]["axis"]["labels"] = False
    dummy_chart["layer"][1]["encoding"]["y"]["title"] = None

    call_chart = count_success_chart("Call", squad, season)
    call_chart["transform"] = [{"filter": {"param": f"select{f}"}} for f in types + ["Dummy"]] + call_chart["transform"]
    
    charts = []
    for i,t in enumerate(types):
        min = 3 if t in ["Hooker", "Jumper"] else 1
        chart = count_success_chart(t, squad, season, as_dict=True, min=min)

        filters = [{"filter": {"param": f"select{f}"}} for f in types + ["Dummy"] if f != t]
        chart["transform"] = filters + chart["transform"]

        if i < len(types) - 1:
            chart["layer"][1]["encoding"]["y"]["axis"]["labels"] = False
            chart["layer"][1]["encoding"]["y"]["title"] = None
        
        if i > 0:
            chart["layer"][0]["encoding"]["y"]["axis"]["labels"] = False
            chart["layer"][0]["encoding"]["y"]["title"] = None
        
        charts.append(alt.Chart.from_dict(chart))

    bottom = alt.hconcat(dummy_chart, call_chart).resolve_scale(color='independent', y="shared")
    top = alt.hconcat(*charts).resolve_scale(color='independent', y="shared")

    chart = alt.vconcat(top, bottom).resolve_scale(color='independent')

    chart["title"] = {
        "text": f"{'1st' if squad==1 else '2nd'} XV Lineouts - {season} season",
        "subtitle": ["Distribution of lineouts (bar), and success rate (line).", "Click to highlight and filter."]  
    }
    

    return chart

def points_scorers(squad=1):

    scorers = pitchero_stats(squad).sort_values("Points", ascending=False)
    scorers["sortfield"] = scorers["Points"] + scorers["PPG"]
    scorers = scorers.sort_values(["sortfield", "Player"], ascending=False).reset_index()
    scorers["sortfield"] = scorers.index
    
    scorers['Tries'] = scorers['T'].astype(int)*5
    scorers['Cons'] = scorers['Con'].astype(int)*2
    scorers['Pens'] = scorers['PK'].astype(int)*3

    return scorers

def points_scorers_chart(squad=1):

    scorers = points_scorers(squad)
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
        x=alt.X("sum(Points):Q", axis=alt.Axis(orient="top"),  title=None),
        y=alt.Y(
            "Player:N", 
            sort=alt.EncodingSortField(field="sortfield"), 
            title=None
        ),
        color=alt.Color(
            "Type:N", 
            legend=alt.Legend(
                title="Click to filter",
                orient="none", 
                legendX=400, 
                legendY=100,
            ), 
            scale=alt.Scale(domain=['Tries', 'Pens', 'Cons'])
        ),
        order=alt.Order("Type:N", sort="descending"),
        tooltip=[
            alt.Tooltip("Player", title=" "), 
            alt.Tooltip("label", title="  "),
            alt.Tooltip("A", title="Games"),
        ],
        text=alt.Text("label:N"),
    ).transform_filter(
        selection
    ).properties(
        title=alt.Title(
            text=("1st" if squad==1 else "2nd") + " XV Points Scorers", 
            offset=10, 
            anchor="middle",
            subtitle="According to Pitchero data"
        ),
        width=500
    ).add_params(
        selection
    )

    return chart

def card_chart():
    s1 = pitchero_stats(1)
    s1["Cards"] = s1["YC"] + s1["RC"]
    s1 = (s1[s1["Cards"] > 0])[["Player","A","YC","RC", "Cards"]]

    s2 = pitchero_stats(2)
    s2["Cards"] = s2["YC"] + s2["RC"]
    s2 = (s2[s2["Cards"] > 0])[["Player","A","YC","RC", "Cards"]]

    s = pd.concat([s1, s2]).sort_values(["Cards", "RC"], ascending=[False, False])    

    chart = alt.Chart(s).mark_bar().encode(
        y=alt.Y("Player", title=None, sort=alt.EncodingSortField(field="Cards", order="descending")),
        x=alt.X("value:Q", title="Total cards", axis=alt.Axis(values=[0,1,2,3,4,5], format="d")),        
        color=alt.Color(
            "key:N", 
            title=None, 
            legend=alt.Legend(orient="bottom-right")).scale(domain=["YC", "RC"], range=["#e6c719", "red"])
    ).transform_fold(
        ["YC", "RC"]
    ).properties(title=alt.Title(text="1st & 2nd XV Cards", subtitle="According to Pitchero data"), width=400)    

    return chart

def captains_chart(season="2023/24"): 
    captains = {}
    for squad in [1,2]:
        captains[squad] = team_sheets(squad)[["Season", "Captain", "VC", "GameType"]].melt(
            id_vars=["Season", "GameType"], 
            value_vars=["Captain", "VC"],
            var_name="Role",
            value_name="Player"
        ).dropna()
        captains[squad]["Team"] = "1st XV" if squad==1 else "2nd XV"

    captains = pd.concat(captains.values())    
        
    captains = captains[captains["Season"]==season]
    captains = captains[captains["GameType"]!="Friendly"]



    chart = alt.Chart(captains).mark_bar().encode(
        y=alt.X("Player:N", title=None, sort="-x"),
        x=alt.X("count()", title="Games", sort=alt.EncodingSortField(field="Role", order="descending")),
        color=alt.Color(
            "Role:N",
            scale=alt.Scale(
                domain=["Captain", "VC"], 
                range=["darkblue", "lightblue"]                
            ),
            legend=alt.Legend(title=None, orient="none", legendX=300, legendY=100)
        ), 
        row=alt.Row("Team:N", title=None, header=alt.Header(title=None, orient="left")),
    ).properties(
        title=alt.Title("1st & 2nd XV Captains", subtitle="League & Cup Captains and Vice-Captains"),
        width=400,
    ).resolve_scale(
        x="shared",
        y="independent"
    )

    return chart

def results_chart(squad=1, season=None):
    
    df = results(squad, season)

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
                labelExpr="split(datum.value,'-__-')[1]"
                )
        ),
        x=alt.X('PF:Q', title="Points", axis=alt.Axis(orient='bottom', offset=5)),
        x2='PA:Q',
        color=alt.Color(
            'Result:N', 
            scale=alt.Scale(domain=['W', 'L'], range=['darkgreen', 'red']), 
            legend=alt.Legend(offset=20, title=["Click to","highlight"])
        ),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
            
    )

    loser = alt.Chart(df).mark_text(align='right', dx=-2, dy=0, color='black').encode(
        y=alt.Y('GameID:N', sort=None),
        x=alt.X('loser:Q', title=None, axis=alt.Axis(orient='top', offset=5)),
        text='loser:N',
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
    )

    winner = alt.Chart(df).mark_text(align='left', dx=2, dy=0, color='black').encode(
        y=alt.Y('GameID:N', sort=None),
        x=alt.X('winner:Q', title=None, axis=alt.Axis(orient='top', offset=5)),
        text='winner:N',
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
    )

    return (bar + loser + winner).add_params(
        selection
    ).properties(title=alt.Title(text=("1st" if squad==1 else "2nd") + " XV Results", offset=20), width=400)
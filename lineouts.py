import json
import pandas as pd
import altair as alt
from copy import deepcopy

scale = 1.0

shape_circle = "M-10 0A1 1 0 0010 0 1 1 0 00-10 0"
shape_shoulders = "M-8-6C-15-2-15 2-8 6M8 6C15 2 15-2 8-6"
shape_face = "M0-10 0-10-4-9C0-13 0-13 4-9L0-10"

lineout_chart_dict = {
  "config": {"style": {"cell": {"stroke": "transparent"}}},
  "layer": [
    {
      "layer": [
        {
          "data": {"values": [{"x": 0}, {"x": 100}]},
          "mark": {
            "strokeDash": [scale*55, scale*55],
            "type": "rule",
            "strokeWidth": scale*6,
            "color": "whitesmoke",
          },
          "encoding": {
            "x": {"field": "x", "type": "quantitative", "axis": None}
          }
        },
        {
          "data": {"values": [{"xt": -50, "y": 0}]},
          "mark": {"type": "rule", "strokeWidth": scale*6, "color": "whitesmoke"},
          "encoding": {
            "x": {"field": "xt", "type": "quantitative", "axis": None}
          }
        }
      ]
    },
    {
      "layer": [
        {
          "mark": {
            "type": "point",
            "shape": shape_circle + shape_shoulders + shape_face,
            "filled": True,
            "opacity": 0.4,
            "size": scale*20
          }
        },
        {
          "mark": {
            "type": "point",
            "filled": True,
            "shape": shape_circle,
            "size": scale*20,
            "strokeWidth": scale*3,
            "opacity": 1
          }
        }
      ],
      "encoding": {
        "x": {
          "axis": None,
          "field": "x",
          "scale": {"domain": [0, 100]},
          "type": "quantitative"
        },
        "y": {
          "axis": None,
          "field": "y",
          "scale": {"domain": [20, 80]},
          "type": "quantitative"
        },
        "color": {
              "field": "Team",
              "scale": {"domain": ["D", "A"], "range": ["#d22", "#22d"]},
              "legend": None
        },
        "angle": {
              "field": "A",
              "type": "quantitative",
              "scale": {"domain": [-180, 180], "range": [180, 540]}
        }
      }
    },
    {
      "mark": {
        "type": "text",
        "align": "center",
        "color": "whitesmoke",
        "dy": 1,
        "fontSize": scale*26,
        "fontWeight": "bolder"
      },
      "encoding": {
        "text": {"field": "Label", "type": "nominal"},
        "x": {"axis": None, "field": "x", "type": "quantitative"},
        "y": {"axis": None, "field": "y", "type": "quantitative"}
      }
    },
    {
      "data": {"values": [{"x": 33, "y":34}, {"x": 48, "y": 34}, {"x":63, "y": 34}]},
      "mark": {
          "type": "point", 
          "shape": "arrow", 
          "size":(scale**2)*1500, 
          "filled":True, 
          "yOffset":-50*scale, 
          "fill":"black", 
          "opacity":1.0,
      },
      "encoding": {
        "x": {"field": "x", "type": "quantitative"},
        "y": {"field": "y", "type": "quantitative"}
      }
    },
    {
      "data": {"values": [{"x": -50, "y": 50, "img": "https://raw.githubusercontent.com/samnlindsay/RugbyResults/master/ball_icon.png"}]},
      "mark": {"type": "image", "width": scale*25, "height": scale*25},
      "encoding": {
        "x": {"field": "x", "type": "quantitative"},
        "y": {"field": "y", "type": "quantitative"},
        "url": {"field": "img", "type": "nominal"}
      }
}
  ],
  "background": "#e5e4e7",
  "data": {
    "values": None
  },
  "height": scale*400,
  "width": scale*500,
  "$schema": "https://vega.github.io/schema/vega-lite/v5.17.0.json"
}


def chart_from_data(df, arrows=None, chart_dict=lineout_chart_dict, ball_pos=[-50,50], as_schema=False):

    schema = deepcopy(chart_dict)
    schema["data"]["values"] = df.to_dict(orient="records")
    if ball_pos:
        schema["layer"][-1]["data"]["values"][0]["x"] = ball_pos[0]
        schema["layer"][-1]["data"]["values"][0]["y"] = ball_pos[1]
    if "mark" in schema["layer"][-2].keys() and schema["layer"][-2]["mark"]["type"] == "point":
        if arrows is None:
            del schema["layer"][-2]
        else:
            schema["layer"][-2]["data"]["values"] = arrows.to_dict(orient="records")

    if as_schema:
      return schema
    else:
      return alt.Chart.from_dict(schema)



d_line_y = 56.0
a_line_y = 44.0
a_walkin_y = 34.0

min_x = 3
max_x = 95
mid_x = (min_x + max_x) / 2.0

a2 = (-52,50)
d2 = (-25,75)

a9 = (50,25)
d9 = (80,75)

setup_lookup = {
   "A": "Auckland",
   "C": "Crusaders",
   "H": "Highlanders",
   "W": "Waikato"
}

maul_dx = [0,-7, 7,-3, 6,  4, -4, 2]
maul_dy = [0, 0, 1,-5,-4,-9,-10,-14]

def spacing(type, n=7):
  if type == "even":
    return (max_x - min_x) / (n-1)
  elif type == "lift":
    return 6.0
  elif type == "prelift":
    return 10.0
  elif type == "tight":
    return 14.0
  else:
    raise ValueError("Invalid spacing type provided.")
  
def defence(n=7, maul=False, x=None):

  d_line = []
  d_line.append({"Team": "D", "x": max([-25, x-30]) if maul else d2[0], "y": d_line_y if maul else d2[1], "Label": "", "Jumper": "", "Order": -1, "A": 180})
  d_line.append({"Team": "D", "x": (x+30) if maul else d9[0], "y": d_line_y if maul else d9[1], "Label": "", "Jumper": "", "Order": 9, "A": 180})

  for i in range(1,n+1):
    if maul:
      d_line.append({"Team": "D", "x": x - maul_dx[i-1], "y": 53-maul_dy[i-1], "Label": "", "Jumper": "", "Order": i, "A": 180})
    else:
      x = min_x + spacing("even",n) * (i-1)
      angle = 90 if i==1 else (-90 if i==n else 180)
      d_line.append({"Team": "D", "x": x, "y": d_line_y, "Label": "", "Jumper": "", "Order": i, "A": angle})


  return pd.DataFrame(d_line)


def attack_init(n=7):
    a_line = [
        {"Team": "A", "x": a2[0], "y": a2[1], "Label": "2", "Jumper": "", "Order": -1, "A": 90},
        {"Team": "A", "x": a9[0], "y": a9[1], "Label": "9", "Jumper": "", "Order": 9, "A": 0},
    ]
    for i in range(1,n+1):
        x = min_x + min([spacing("even",n),20]) * (i-1)
        a_line.append({"Team": "A", "x": x, "y": a_line_y, "Label": "L" if i in [1,n] else "", "Jumper": "", "Order": i, "A": 90 if i==1 else -90})
        
    return pd.DataFrame(a_line)
    

def get_walk_ins(n, setup):

    if n > 4:
        if setup == "H":
            return list(range(2,n))
        elif setup == "C":
            if n > 5:
                return [n-4,n-3,n-2]
            else:
                return [2,3,4]
        elif setup == "W":
            if n > 5:
                return [2,n-3,n-1]
            else:
                return [2,4]
        elif setup == "A":
            return None
    
def get_arrows(df, walk_in):
    if walk_in is None:
        return None
    
    a = []
    for i in walk_in:
        x = df.loc[df["Order"]==i, "x"].values[0]
        a.append({"x": x, "y": a_walkin_y, })
    return pd.DataFrame(a)

# Order index of jumpers (these will be labelled with "J")
def jumpers(n, setup):
    """
    Determines the jumpers for a lineout based on the number of players and the setup.

    Parameters:
    - n (int): The number of players in the lineout.
    - setup (str): The setup of the lineout. [H, C, W, A]

    Returns:
    - list: A list of jumper positions in the lineout.

    """
    if n > 4:
        if setup == "H":
            if n > 5:
                return [2,n-3,n-1]
            else:
                return [2,3,4]
        elif setup == "C":
            if n == 7:
                return [2,4,n-1]
            elif n == 6:
                return [2, None, n-1]
            return [2,3,4]
        elif setup == "W":
            if n > 5:
                return [2,4,n-1]
            else:
                return [2,3,4]
        elif setup == "A":
            if n > 5:
                return [3,n-2,n-1]
            else:
                return [3,None,4]
    else:
        return [2, None, 3]
    
def label_jumpers(df, jumpers):
    for i,o in enumerate(jumpers):
        df.loc[df["Order"]==o, "Label"] = "J"
        
        df.loc[df["Order"]==o, "Jumper"] = ["2", "3", "1"][i]

    return df

def move_walkins(df, walk_in=None, a_walkin_y=a_walkin_y, n=7, setup="C"):

    df["x"] = df["x"].astype(float)
    
    if walk_in is None:
        return df
    else: 
        move = df["Order"].isin(walk_in) & df["Team"].eq("A")
        
        # Move y-coordinate of walk-ins
        df.loc[move, "y"] = a_walkin_y
        df.loc[move, "A"] = 0
        
        # Move x-coordinate of walk-ins (if 3 in a row)
        if walk_in == [min(walk_in) + a for a in [0,1,2]] and (setup != "H"):
            dx = spacing("prelift")
            x = float(df.loc[df["Order"].isin([1,n]), "x"].values.mean())
            df.loc[move, "x"] = [x-dx, x, x+dx]
            
        return df
    

def adjust_spacing(df, n, setup):

    ddx = spacing("prelift")
    dx = spacing("tight")
    
    if n > 4:
        if setup == "C": # 2-3-2 or 1-3-2 or 1-3-1
            if n > 5:
                df.loc[df["Order"]==n-1, "x"] = max_x - ddx
                if n==6:
                    df.loc[df["Order"].isin([2,3,4]), "x"] -= ddx/2
                elif n==7:
                    df.loc[df["Order"]==2, "x"] = min_x + ddx
        elif setup == "W":  
            if n > 5:
                df.loc[df["Order"]==4, "x"] = mid_x
            if n == 6:
                df.loc[df["Order"].isin([2,3,5]), "x"] = [mid_x-(2*dx), mid_x-dx, mid_x+dx]
        elif setup == "A": # 1-3-2-1 or 1-3-2 or 1-3-1
            dx = spacing("tight")
            ddx = spacing("prelift")
            df.loc[df["Order"].isin([2,3,4]), "x"] = [min_x + 2*dx + p for p in [-ddx, 0, ddx]]
            if n == 7:
                df.loc[df["Order"].isin([5,6]), "x"] = [min_x + 4.5*dx + 0.5*p for p in [-ddx, ddx]]
            elif n == 6:
                df.loc[df["Order"].isin([5,6]), "x"] = [min_x + 5*dx + p for p in [0, ddx]]
                # df.loc[df["Order"]==n, "x"] = max_x - dx
                # df.loc[df["Order"]==n-1, "x"] = mid_x
    else:
        x_j = max_x - dx - ddx
        df.loc[df["Order"].isin([2,3,4]), "x"] = [x_j-ddx, x_j, x_j+ddx]
    
    return df

def adjust_angles(df, n, setup):
    if n > 4:
        # if setup == "W":
            # df.loc[df["Order"].isin(range(2,n)), "A"] = 0
        if setup == "A":
            df.loc[df["Order"].isin([2,4]), "A"] = [60,-60]
    else:
        df.loc[df["Order"].isin([2,3,4]), "A"] = [90,-90,-90]
        
    return df


def lineup(n=7, setup="H", receiver="9"):

    a = attack_init(n)
    walk = get_walk_ins(n, setup)
    jump = jumpers(n, setup)
    a = move_walkins(a, walk, n=n, setup=setup)
    a = label_jumpers(a, jump)
    a = adjust_spacing(a, n, setup)
    a = adjust_angles(a, n, setup)

    if setup == "A":
        a.loc[a["Order"]==2, "Label"] = "D"
    
    if receiver == "F":
        a.loc[a["Order"]==9, "Label"] = "+1"
    elif receiver is None:
        a = a[a["Order"] != 9]
    
    arrows = get_arrows(a, walk)
    return a, arrows

def setup_to_throw(df, n=7, setup="H", call=1):

    df.loc[df["y"]==a_walkin_y, "y"] = a_line_y 
    dx = spacing("lift")
    ddx = spacing("prelift")

    if n > 4:
        ###############
        # HIGHLANDERS #
        ###############
        if setup == "H":
            # Move players either side of Jumper {call}
            if call == 2:
                j = df.loc[df["Jumper"]==str(call), "Order"].values[0]
                x = df.loc[df["Order"]==(j-1), "x"].values[0]
                pod = [j-1, j, j+1]
                df.loc[df["Order"].isin(pod), "x"] = [x, x+dx, x+(2*dx)]
            else:
                j = df.loc[df["Jumper"]==str(call), "Order"].values[0]
                x = df.loc[df["Order"]==j, "x"].values[0]
                pod = [j-1, j, j+1]
                df.loc[df["Order"].isin(pod), "x"] = [x-dx, x, x+dx]

            df.loc[df["Order"].isin(pod), "A"] = [90,-90,-90]

        ##############
        # CANTERBURY #
        ##############
        elif setup == "C":
            # Back pod
            j1 = df.loc[df["Jumper"]=="1", "Order"].values[0]
            if n > 5:
                x1 = df.loc[df["Order"]==j1, "x"].values[0]
            else:
                x1 = max_x - spacing("even", n)
            pod1 = [j1-1, j1, j1+1]
            df.loc[df["Order"].isin(pod1), "A"] = [90,-90,-90]

            # Front pod
            j2 = df.loc[df["Jumper"]=="2", "Order"].values[0]
            x2 = df.loc[df["Order"]==(j2-1), "x"].values[0]
            pod2 = [j2-1, j2, j2+1]
            df.loc[df["Order"].isin(pod2), "A"] = [90,-90,-90]

            dx1 = dx if call == 1 else ddx
            dx2 = dx if call == 2 else ddx

            if n > 5:
                df.loc[df["Order"].isin(pod1), "x"] = [x1-dx1, x1, x1+dx1]
                df.loc[df["Order"].isin(pod2), "x"] = [x2, x2+dx2, x2+(2*dx2)]
            else:
                if call == 1:   
                    df.loc[df["Order"].isin(pod1), "x"] = [x1-dx1, x1, x1+dx1]
                    df.loc[df["Order"].isin(pod2[:2]), "x"] = [x2, x2+dx2]
                elif call in [2,3]:
                    df.loc[df["Order"].isin(pod1[1:]), "x"] = [x1, x1+dx1]
                    df.loc[df["Order"].isin(pod2), "x"] = [x2, x2+dx2, x2+(2*dx2)]

            j = j1 if call == 1 else j2
            pod = pod1 if call == 1 else pod2

            # Middle pod
            if call == 3:
                j = df.loc[df["Jumper"]==("3" if n!=6 else "1"), "Order"].values[0]
                if n < 7:
                    pod = [1, j, j+1]
                else:
                    pod = [1, j, n-1]
                x = mid_x if n > 5 else (min_x + df.loc[df["Order"]==4, "x"].values[0])/2
                df.loc[df["Order"].isin(pod), "x"] = [mid_x-dx, mid_x, mid_x+dx]
                df.loc[df["Order"].isin(range(2,n)), "A"] = -30
                df.loc[df["Order"].isin(pod), "A"] = [90,-90,-90]

        ############
        # AUCKLAND #
        ############
        elif setup == "A":        
            # Front jumper
            df.loc[df["Jumper"]=="2", "x"] = min_x + dx if call == 2 else min_x + ddx

            # Dummy jumper always moves out and back behind the front pod
            df.loc[df["Order"]==2, "x"] = (min_x + 2*dx + spacing("tight")) if call == 2 else mid_x

            if n == 7:
                # Middle man always supports J2
                df.loc[df["Order"]==4, "x"] = min_x + 2*ddx

            if call==2:
                j = df.loc[df["Jumper"]==str(call), "Order"].values[0]
                pod = [1, j, j+1]
                df.loc[df["Order"].isin(pod), "x"] = [min_x, min_x+dx, min_x+2*dx]
                df.loc[df["Order"].isin(pod), "A"] = [90,-90,-90]
            elif call==3:
                j = df.loc[df["Jumper"]==("3" if n>5 else "1"), "Order"].values[0]
                pod = [2, j, j+1]
                df.loc[df["Order"].isin(pod), "x"] = [mid_x-dx, mid_x, mid_x+dx]
                df.loc[df["Order"].isin(pod), "A"] = [90,-90,-90]
            elif call==1:
                j = df.loc[df["Jumper"]==str(call), "Order"].values[0]
                if n>5:
                    x = df.loc[df["Order"]==j, "x"].values[0]
                    pod = [j-1, j, j+1]
                else:
                    x = df.loc[df["Order"]==n, "x"].values[0] - spacing("even", n)
                    pod = [2, j, n]
                df.loc[df["Order"].isin(pod), "x"] = [x-dx, x, x+dx]
                df.loc[df["Order"].isin(pod), "A"] = [90,-90,-90]

            df.loc[df["Order"]==2, "A"] = -30 if call == 2 else 90

        ###########
        # WAIKATO #
        ###########
        elif setup == "W":
            j = df.loc[df["Jumper"]==str(call), "Order"].values[0]
            pod = [j-1, j, j+1]
            if call == 2:
                x = df.loc[df["Order"]==j-1, "x"].values[0]
                df.loc[df["Order"].isin(pod), "x"] = [x, x+dx, x+2*dx]
            else:
                x = df.loc[df["Order"]==j, "x"].values[0]
                if n==6 and call==1:
                    x = max_x - spacing("even", n)
                df.loc[df["Order"].isin(pod), "x"] = [x-dx, x, x+dx]
            df.loc[df["Order"].isin(pod), "A"] = [90,-90,-90]

    else:
        j = df.loc[df["Jumper"]==str(call), "Order"].values[0]
        pod = [j-1, j, j+1]
        if call == 2:
            x = df.loc[df["Order"]==j-1, "x"].values[0]
            df.loc[df["Order"].isin(pod), "x"] = [x, x+dx, x+2*dx]
        else:
            x = df.loc[df["Order"]==j, "x"].values[0]
            pod = [j-1, j, j+1]
            df.loc[df["Order"].isin(pod), "x"] = [x-dx, x, x+dx]

    # Move hooker one third of the horizontal distance to the jumper
    x_j = df.loc[df["Order"]==j, "x"].values[0]
    x_h = df.loc[df["Order"]==-1, "x"].values[0]

    df.loc[df["Order"]==-1, "x"] = (x_j - x_h)/3 + x_h
    df.loc[df["Order"]==-1, "y"] = a_line_y - 10
    df.loc[df["Order"]==-1, "A"] += 10

    return df


def maul_receiver(df, call, receiver):
    if receiver == "F":
        return 9
    else:
        j = df.loc[df["Jumper"]==str(call), "Order"].values[0]
        x_j = df.loc[df["Jumper"]==str(call), "x"].values[0]

        df["dist"] = df.apply(lambda p: abs(p["x"] - x_j) if p["Order"] not in [j-1, j, j+1, -1, 9] else 1000, axis=1)
        r = df.loc[df["dist"].idxmin(), "Order"]
        df.drop("dist", axis=1, inplace=True) 

        return r
    
def move_receiver(df, call, receiver="9", play="Hot"):
    
    if receiver:
        x_j = df.loc[df["Jumper"]==str(call), "x"].values[0]
        df.loc[df["Order"]==9, "y"] = 30
                
        if receiver == "9":
            # Move 9 up and to the right of the jumper
            if play == "Hot":
                df.loc[df["Order"]==9, "x"] = (x_j + a9[0])/2
        
            else:
                # Move 9 back
                df.loc[df["Order"]==9, "x"] = x_j
                df.loc[df["Order"]==9, "y"] -= 5 

        if play != "Hot":        
                # Move forward receiver towards the jumper
                r = maul_receiver(df, call, receiver)

                if r == 9:
                    df.loc[df["Order"]==9, "x"] = x_j
                    df.loc[df["Order"]==9, "y"] = a_line_y - 12
                else:
                    x_r = df.loc[df["Order"]==r, "x"].values[0]
                    df.loc[df["Order"]==r, "x"] = (x_j + x_r)/2
                    df.loc[df["Order"]==r, "y"] -= 10
                    df.loc[df["Order"]==r, "A"] = 45 if x_r < x_j else -45
    
    return df
    

def maul(df, call, receiver, size, play="Cold"):

    x0 = df.loc[df["Jumper"]==str(call), "x"].values[0]
    y0 = df.loc[df["Jumper"]==str(call), "y"].values[0] + 3
    x_j = df.loc[df["Jumper"]==str(call), "x"].values[0]

    # Initiating the maul (pod + 1)
    j = df.loc[df["Jumper"]==str(call), "Order"].values[0]
    r = maul_receiver(df, call, receiver)
    pod = [j, j-1, j+1, r]

    # Sort df by distance from jumper
    df["dist"] = df.apply(lambda p: abs(p["x"]-x_j) if p["Order"] not in pod else -10, axis=1)
    df.loc[df["Order"].isin(pod), "dist"] += [pod.index(o) for o in df.loc[df["Order"].isin(pod), "Order"].values]
    
    # Scrum Half always bottom of list
    if receiver == "9":
        df.loc[df["Label"]=="9", "dist"] = 1000
    if play == "Flyby":
        df.loc[df["Label"]=="2", "dist"] = 900
    df = df.sort_values("dist").reset_index(drop=True)

    if df.loc[3,"x"] > df.loc[4,"x"]:
        df.loc[3:4,"dist"] = df.loc[3:4,"dist"][::-1]
    if (len(df) > 6 and receiver != "9") or len(df) > 7: 
        if df.loc[5,"x"] > df.loc[6,"x"]:
            df.loc[5:6,"dist"] = df.loc[5:6,"dist"][::-1]
    df = df.sort_values("dist").reset_index(drop=True)
    df = df.drop("dist", axis=1)
    
    # Replace first n x,y values with maul values
    for i in range(size):
        nx = x0 + maul_dx[i]
        ny = y0 + maul_dy[i]
        
        df.loc[i, "x"] = nx
        df.loc[i, "A"] = 0
        df.loc[i, "y"] = ny
                
    return df, r


def crusaders_positions(df, n, call, receiver):
    # Mini maul
    df, r = maul(df, call, receiver, size=4, play="Crusaders")

    # Pod 
    x_j = df.loc[df["Jumper"]==str(call), "x"].values[0]
    j = df.loc[df["Jumper"]==str(call), "Order"].values[0]

    # Additional players
    pod = [j,j-1,j+1, r, 9]

    extras = sorted(list(set(df["Order"]) - set(pod)))

    blind = extras[:len(extras)//2]
    open = extras[len(extras)//2:][::-1]

    x_blind = (x_j - 50)/2 - 20
    x_open = (x_j + 50)
    y_extra = a_line_y - 10

    for n,p in enumerate(blind):
        df.loc[df["Order"]==p, "x"] = x_blind + n*20
        df.loc[df["Order"]==p, "y"] = y_extra - n*5
        df.loc[df["Order"]==p, "A"] = 0
        
    for n,p in enumerate(open):
        df.loc[df["Order"]==p, "x"] = x_open - n*20
        df.loc[df["Order"]==p, "y"] = y_extra - n*5
        df.loc[df["Order"]==p, "A"] = 0

    if receiver == "9":
        df.loc[df["Order"]==9, "x"] = x_j + 10
        df.loc[df["Order"]==9, "y"] = 25

    return df

def flyby_positions(df, n, call, receiver):
    # Mini maul
    df, r = maul(df, call, receiver, size=4, play="Flyby")
 
    x0 = df.loc[df["Jumper"]==str(call), "x"].values[0]
    y0 = df.loc[df["Jumper"]==str(call), "y"].values[0] + 3

    # Maul
    np = n + 1 if receiver != "F" else n + 2
    for i in range(3,np-1):
        if call == 1 or i < np-1:
            x = df.loc[i, "x"]
            df.loc[i, "x"] = x0 + maul_dx[i] + (-15 if x < x0 else 15)
            df.loc[i, "y"] = y0 + maul_dy[i] - 5
            df.loc[i, "A"] = -40 if df.loc[i, "x"] > x0 else 40
        # Tailgunner
        else:
            df.loc[i, "x"] -= 10
            df.loc[i, "y"] = a_line_y - 15
            df.loc[i, "A"] = -10

    # Receiver
    df.loc[df["Order"]==r, "A"] = -150
    df.loc[df["Order"]==r, "y"] == a_line_y - 5
    df.loc[df["Order"]==r, "x"] = x0

    # Hooker
    df.loc[df["Order"]==-1, "x"] = x0 - 10
    df.loc[df["Order"]==-1, "y"] = a_line_y - 15
    df.loc[df["Order"]==-1, "A"] = 80


    if receiver == "9":
        df.loc[df["Order"]==9, "x"] += 20 if call == 2 else 40
        df.loc[df["Order"]==9, "y"] -= 10

    return df


    
n = 7
setup = "H"
call = 1

class Lineout:
    def __init__(self, n, setup=None, call=None, play=None, receiver="9"):
        self.n = n
        self.setup = setup
        self.receiver = receiver
        self.receiver_suffix = "" if self.receiver == "9" else ("+1" if self.receiver == "F" else "no9")

        if n > 4:            
            self.call = call
            self.play = play
        else:
            if receiver == "F":
                self.call = 2
                self.play = "Cold"
            else:
                self.call = 1
                self.play = "Hot"
        
    def setup_suffix(self):
        return f"_{self.setup}" if self.n > 4 else ""
    def setup_call_play_suffix(self):
        return f"_{self.setup}{self.call}_{self.play}" if self.n > 4 else ""
    

    def setup_path(self):
        return f"json/setup_{self.n}{self.receiver_suffix}{self.setup_suffix()}.json"
    def throw_path(self):
        return f"json/throw_{self.n}{self.receiver_suffix}{self.setup_call_play_suffix()}.json"
    def play_path(self):
        return f"json/play_{self.n}{self.receiver_suffix}{self.setup_call_play_suffix()}.json"
    
    def setup_df(self):
        df, _ = lineup(self.n, self.setup, self.receiver)
        return df

    def setup_chart(self, save=False):
        df, arrows = lineup(self.n, self.setup, self.receiver)
        df = pd.concat([df, defence(self.n)])
    
        chart = chart_from_data(df, arrows)

        return chart if not save else chart.save(self.setup_path(), embed_options={"actions": False, "modebar": "none"})
    
    def throw_df(self):
        df = self.setup_df()
        df.loc[df["Order"].isin(range(2,self.n+1)), "A"] = -90
        df = setup_to_throw(df, self.n, self.setup, self.call)
        
        if self.n==6 and self.setup=="C" and self.call==3:
            # call = "1"
            df.loc[df["Jumper"]=="1", "Jumper"] = "3"
        if self.n==5 and self.setup=="A" and self.call==3:
            # call = "1"
            df.loc[df["Jumper"]=="1", "Jumper"] = "3"

        in_line = df["Order"].isin(range(1,self.n+1))
        df.loc[in_line, "Order"] = df.loc[in_line, "x"].rank(method="min", ascending=True)
        df = df.sort_values("Order")

        df = move_receiver(df, self.call, self.receiver, self.play)
        
        return df
    
    def throw_chart(self, save=False):
        df = self.throw_df()
        df = pd.concat([df, defence(self.n)])
        ball_pos = [
            df.loc[df["Jumper"]==str(self.call), "x"].values[0] - 2,
            df.loc[df["Jumper"]==str(self.call), "y"].values[0] + 4,
        ]
        chart = chart_from_data(df, ball_pos=ball_pos)

        return chart if not save else chart.save(self.throw_path(), embed_options={"actions": False, "modebar": "none"})
    
    def play_df(self):
        df = self.throw_df()

        if self.play == "Cold":
            size = self.n + 1 if self.receiver != "F" else self.n + 2
            df, r = maul(df, self.call, self.receiver, size, self.play)

        elif self.play == "Crusaders":
            df = crusaders_positions(df, self.n, self.call, self.receiver)

        elif self.play == "Flyby":
            df = flyby_positions(df, self.n, self.call, self.receiver)

        elif self.play == "Hot":
            if self.receiver is None:
                r = maul_receiver(df, self.call, self.receiver)
                j_x = df.loc[df["Jumper"]==str(self.call), "x"].values[0]
                r_x = df.loc[df["Order"]==r, "x"].values[0]
                df.loc[df["Order"]==r, "x"] = (3*j_x + r_x)/4
                df.loc[df["Order"]==r, "y"] -= 15

            else:
                x_j = df.loc[df["Jumper"]==str(self.call), "x"].values[0]
                df.loc[df["Order"]==9, "x"] = x_j
                df.loc[df["Order"]==9, "A"] = 30

        return df
    
    def play_chart(self, save=False):
        df = self.play_df()

        # Ball pos
        if self.play == "Cold":
            # Position ball relative to the hindmost player
            min_y = min(df.loc[df["Order"]!=9, "y"])
            x = df.loc[df["y"]==min_y, "x"].values[0]
            size = n + 1 if self.receiver != "F" else n + 2
            ball_pos = [
                x + (-3 if size % 2 == 0 else 3),
                min_y #+ (0 if size % 2 == 0 else 2)
            ]
        elif self.play == "Crusaders":
            ball_pos = [
                df.loc[df["Jumper"]==str(self.call), "x"].values[0],
                df.loc[df["Jumper"]==str(self.call), "y"].values[0] - 3
            ]
        elif self.play == "Flyby":
            ball_pos = [
                df.loc[df["Order"]==-1, "x"].values[0] + 4,
                df.loc[df["Order"]==-1, "y"].values[0] + 2,
            ]
        elif self.play == "Hot":
            r = maul_receiver(df, self.call, self.receiver) if self.receiver is None else 9
            ball_pos = [
                df.loc[df["Order"]==r, "x"].values[0],
                df.loc[df["Order"]==r, "y"].values[0] + 4,
            ]
        if self.play == "Hot":
            df = pd.concat([df, defence(self.n)])
        else:
            df = pd.concat([defence(self.n, maul=True, x=df.loc[df["Jumper"]==str(self.call), "x"].values[0]), df])

        chart = chart_from_data(df, ball_pos=ball_pos)

        return chart if not save else chart.save(self.play_path(), embed_options={"actions": False, "modebar": "none"})


path = "json/angle/"

def save_charts(ns=[4,5,6,7], setups=["A", "C", "H", "W"], calls=[1,2,3], plays=["Hot", "Cold", "Crusaders", "Flyby"]):

    for n in ns: 
        for receiver in [None, "F", "9"]:
            if n==4:
                print(n, receiver)
                l = Lineout(n, receiver=receiver)

                l.setup_chart(save=True)
                l.throw_chart(save=True)
                l.play_chart(save=True)

            else:
                for setup in setups:
                    for call in calls:
                        for play in plays:
                            if n<7 or receiver!="F":
                                print(n, setup, call, play, receiver)
                                l = Lineout(n, setup, call, play, receiver)

                                l.setup_chart(save=True)
                                if play in ["Cold", "Hot"]:
                                    l.throw_chart(save=True)
                                l.play_chart(save=True)

def load_chart(path):
    with open(path, "r") as f:
        chart = json.load(f)
    return alt.Chart.from_dict(chart)


match_day_chart_dict = {
  "config": {
    "view": {"continuousWidth": 300, "continuousHeight": 300},
    "style": {"cell": {"stroke": "transparent"}}
  },
  "layer": [
    {
      "layer": [
        {
          "mark": {
            "type": "rule",
            "color": "whitesmoke",
            "strokeDash": [55, 55],
            "strokeWidth": 6,
            "y": 0,
            "y2": "height",
            "opacity": 0.5
          },
          "data": {"values": [{"x": 0}, {"x": 100}]},
          "encoding": {
            "x": {"axis": None, "field": "x", "type": "quantitative"}
          }
        },
        {
          "mark": {"type": "rule", "color": "whitesmoke", "strokeWidth": 6, "opacity": 0.5},
          "data": {"values": [{"xt": -50, "y": 0}]},
          "encoding": {
            "x": {"axis": None, "field": "xt", "type": "quantitative"}
          }
        },
        {
          "mark": {
            "type": "rule",
            "color": "#22d",
            "strokeWidth": 1,
            "x": -230,
            "x2":480,
            "opacity": 1.0
          },
          "data": {
            "values": [
              {"yt": 17, "x": 0},
              {"yt": 62, "x": 0},
              {"yt": 87, "x": 0}
            ]
          },
          "encoding": {
            "y": {"axis": None, "field": "yt", "type": "quantitative"}
          }
        }
      ]
    },
    {
      "mark": {
        "type": "text",
        "color": "whitesmoke",
        "fontSize": 40,
        "opacity": 0.5,
        "fontWeight": "bold",
      },
      "data": {
        "values": [
          {"y": 95, "text": "4-man", "x": -25},
          {"y": 75, "text": "5-man", "x": -25},
          {"y": 48, "text": "7-man", "x": -25},
          {"y": 10, "text": "Defence", "x": -25}
        ]
      },
      "encoding": {
        "text": {"field": "text"},
        "x": {"axis": None, "field": "x", "type": "quantitative"},
        "y": {"axis": None, "field": "y", "type": "quantitative"}
      }
    },
    {
      "mark": {
        "type": "text",
        "fontSize": 20,
        "opacity": 0.3
      },
      "data": {
        "values": [
          {"y": 80, "text": "Canterbury", "x": -25},
          {"y": 70, "text": "Highlanders", "x": -25},
          {"y": 55, "text": "Auckland", "x": -25},
          {"y": 40, "text": "Canterbury", "x": -25},
          {"y": 25, "text": "Highlanders", "x": -25}
        ]
      },
      "encoding": {
        "text": {"field": "text"},
        "x": {"axis": None, "field": "x", "type": "quantitative"},
        "y": {"axis": None, "field": "y", "type": "quantitative"}
      }
    },
    {
      "layer": [
        {
          "mark": {
            "type": "point",
            "color": "#22d",
            "filled": True,
            "opacity": 0.4,
            "shape": "M-10 0A1 1 0 0010 0 1 1 0 00-10 0M-8-6C-15-2-15 2-8 6M8 6C15 2 15-2 8-6M0-10 0-10-4-9C0-13 0-13 4-9L0-10",
            "size": 20
          }
        },
        {
          "mark": {
            "type": "point",
            "color": "#22d",
            "filled": True,
            "opacity": 1,
            "shape": "M-10 0A1 1 0 0010 0 1 1 0 00-10 0",
            "size": 20,
            "strokeWidth": 3
          },
          "encoding": {
            "color": {
              "field": "Label",
              "legend": None,
              "scale": {
                "domain": ["9", "", "2", "J", "D", "L"],
                "range": ["#22d", "#22d", "#22d", "#d22", "#929", "#22d"]
              }
            }
          }
        }
      ],
      "encoding": {
        "angle": {
          "field": "A",
          "type": "quantitative",
          "scale": {"domain": [-180, 180], "range": [180, 540]}
        },
        "x": {
          "axis": None,
          "field": "x",
          "scale": {"domain": [0, 100]},
          "type": "quantitative"
        },
        "y": {
          "axis": None,
          "field": "y",
          "scale": {"domain": [0, 100]},
          "type": "quantitative"
        }
      }
    },
    {
      "mark": {
        "type": "text",
        "color": "black",
        "fontSize": 16,
        "fontWeight": "bold",
        "yOffset": 40
      },
      "encoding": {
        "text": {"field": "Name"},
        "x": {"field": "x", "type": "quantitative"},
        "y": {"field": "y", "type": "quantitative"}
      }
    },
    {
      "mark": {
        "type": "text",
        "color": "whitesmoke",
        "fontSize": 24,
        "fontWeight": "bold"
      },
      "encoding": {
        "text": {"field": "Number"},
        "x": {"field": "x", "type": "quantitative"},
        "y": {"field": "y", "type": "quantitative"}
      }
    }
  ],
  "background": "#6c6",
  "data": {
    "values": None
  },
  "height": 800,
  "width": 500,
    "title": {
    "text": "Starting Lineout",
    "fontSize": 40,
    "subtitle": "{OPPOSITION}",
    "subtitleFontSize": 20,
    "anchor": "end",
    "offset": 20,
    "color": "#229",
    "subtitleColor": "#229"
  },
  "$schema": "https://vega.github.io/schema/vega-lite/v5.17.0.json"
}

def labelled_lineout(n, players, setup="C", D=False):

    # Lineout setup    
    if not D:
        df = Lineout(n, setup, receiver=None).setup_df()
        df["y"] = 0
    else:
        df = defence(7)
        df["x"] -= [0,0,0,2,2,4,6,8,10]
        df["y"] = 0
        df["A"] = [0, 0, 90, 0, -90, -90, 0, 0, -45]
        df["Label"] = ["2", "9", "L", "J", "J", "L", "", "", ""]
        df.loc[df["Order"].isin([-1,9]), "y"] = -10
        df.loc[df["Order"].isin([-1,9]), "x"] = [95, -25]

    df.drop("Team", axis=1, inplace=True)

    # Add players
    j = list(players.sort_values(["Call", "Jump"], ascending=[False, False])["Number"])
    l = list(players[3:-1].sort_values(["Call", "Jump", "Number"], ascending=[True, True, False])["Number"])

    if D:
        df["Number"] = [2, 9, 3, j[1], j[0], 1, l[0], l[1], l[2]]
    elif n == 4:
        df["Number"] = [2, 3, j[1], j[0], 1]
    elif n == 5:
        df["Number"] = [2, 3, j[1], j[2], j[0], 1]
    elif n == 7:
        if setup == "A":
            df["Number"] = [2, 3, l[0], j[1], l[1], j[2], j[0], 1]
        else:
            df["Number"] = [2, 3, j[1], l[0], j[2], l[1], j[0], 1]  
        

    if not D:
        players = players[players["Number"] != 9]

    df = df.merge(players, on="Number", how="left")

    return df

def match_day_df(players):

    dfs = [
        labelled_lineout(4, players),
        labelled_lineout(5, players, setup="C"),
        labelled_lineout(5, players, setup="H"),
        labelled_lineout(7, players, setup="A"),
        labelled_lineout(7, players, setup="C"),
        labelled_lineout(7, players, setup="H"),
        labelled_lineout(7, players, D=True)
    ] 
    yvals = [5, 20, 30, 45, 60, 75, 90]


    for i, df in enumerate(dfs):
        df["y"] += 100 - yvals[i]

    dfs = pd.concat(dfs)

    dfs["Color"] = dfs.apply(lambda p: "Caller" if p["Call"] else ("Jumper" if p["Jump"] else None), axis=1)
    
    return dfs


def summary_chart(players, opposition, generic=False, chart_dict=match_day_chart_dict):

    dfs = match_day_df(players)

    if generic:
        chart_dict["layer"][5]["encoding"]["text"]["field"] = "Label"
        del chart_dict["layer"][4]
        chart_dict["title"]["text"] = "Lineout Essentials"
        chart_dict["title"]["subtitle"] = "Go-to setups everyone should know"
    else:
        chart_dict["title"]["subtitle"] = opposition

    return chart_from_data(dfs, chart_dict=chart_dict, ball_pos=None)#.to_dict()

if __name__ == "__main__":
    save_charts()



### Custom definitions and classes if any ###
import pandas as pd
import os

#global variables
bat_list=[]
batsmen, batsmen1= dict(), dict()
batsman_data,data="",""
def predictRuns(testInput):
    global batsmen
    global batsmen1
    global bat_list
    global batsman_data
    global data

    data = pd.read_csv(testInput)
    batsman_data = pd.read_csv("batsman_data.csv", header=0)

    for row in range(0, batsman_data.index[-1]):
        player_name1 = batsman_data.at[row, 'Player_Name']
        player_name = player_name1[0:1] + " " + player_name1[len(player_name1) - 4: len(player_name1) + 1]
        batsmen.update({player_name: player_name1})
        batsmen1.update({player_name1: row})

    venue = data.iloc[0, 0]
    innings = data.iloc[0, 1]
    batting_team = data.iloc[0, 2]
    bowling_team = data.iloc[0, 3]
    bat_list = list(map(str, data.iloc[0, 4].split(",")))

    # predict score by batsman performance
    batsman_model = s_bat(bat_list[0], bat_list[1], 0)

    slope=0.80159279
    intercept=12.852516574175887
    prediction = slope*batsman_model + intercept

    return int(prediction)

def get_batsman_value(b,col):
    global batsmen
    global batsmen1
    global bat_list
    global batsman_data
    global data

    b=b.strip()
    player_name = b[0:1] +" "+ b[len(b)-4 : len(b)+1]
    player_name1= batsmen.get(player_name)
    row=batsmen1.get(player_name1)
    try:
        data=batsman_data.at[row,col]
    except KeyError:
        data=0
    return data

# functions for batting calculations
def p_bat(b, k):
    global batsmen
    global batsmen1
    global bat_list
    global batsman_data
    global data

    col = "p" + str(k + 1)
    prob = get_batsman_value(b, col)
    if prob == 0 or prob == None:
        col = 'wicket_probability'
        prob = get_batsman_value(b, col)
    if prob == 0 or prob == None:
        prob = batsman_data.at[0, 'average_wicket_probability']
    return prob


def r_bat(b, n):
    global batsmen
    global batsmen1
    global bat_list
    global batsman_data
    global data

    col = "r" + str(n + 1)
    score = get_batsman_value(b, col)
    if score == 0 or score == None:
        col = 'strike_rate'
        score = get_batsman_value(b, col)
    if score == 0:
        score = batsman_data.at[0, 'average_strike_rate']
    return score


def s_bat(bx, by, o):
    global batsmen
    global batsmen1
    global bat_list
    global batsman_data
    global data

    if o < 6 and bx in bat_list and by in bat_list:
        # figure out next and later batsmen
        idx = max(bat_list.index(bx), bat_list.index(by))
        if idx + 1 < len(bat_list):
            nxt = bat_list[idx + 1]
        else:
            nxt = "gen"
            later = "gen"
        if idx + 2 < len(bat_list):
            later = bat_list[idx + 2]
        else:
            later = "gen"

        a = 0.5
        px = s_bat(by, nxt, o + 1) + a * r_bat(bx, o) + r_bat(by, o)
        py = s_bat(bx, nxt, o + 1) + r_bat(bx, o) + a * r_bat(by, o)
        pxy = s_bat(nxt, later, o + 1) + a * (r_bat(bx, o) + r_bat(by, o))
        p0 = s_bat(bx, by, o + 1) + r_bat(bx, o) + r_bat(by, o)
        # if none can get out, we will not find any more probabilities
        if nxt == "gen":
            return p0
        # if one more can get out then we calculate the probability accordingly
        elif later == "gen":
            return p_bat(bx, o) * px + p_bat(by, o) * py + (1 - p_bat(bx, o) - p_bat(by, o)) * p0
        # if more than one can get out then also we calculate the probability accordingly
        else:
            return p_bat(bx, o) * px + p_bat(by, o) * py + p_bat(bx, o) * p_bat(by, o) * pxy + (
                        1 - p_bat(bx, o) - p_bat(by, o) - p_bat(bx, o) * p_bat(by, o)) * p0
    else:
        return 0

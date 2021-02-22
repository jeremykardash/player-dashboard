# import necessary libraries
import os
from flask.globals import session
from flask_sqlalchemy import SQLAlchemy

from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)

from sqlalchemy import create_engine, engine
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session


###NPA API
from nbapy import game, shot_chart, player

from nba_api.stats.static import players
import nba_api.stats.endpoints
from nba_api.stats.static import teams
from nba_api.stats.endpoints import commonplayerinfo
import pandas as pd
from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.library.parameters import ContextMeasureSimple, LastNGames, LeagueID, Month, Period, SeasonTypeAllStar, AheadBehindNullable, ClutchTimeNullable, EndPeriodNullable, EndRangeNullable, GameSegmentNullable, LocationNullable, OutcomeNullable, PlayerPositionNullable, PointDiffNullable, PositionNullable, RangeTypeNullable, SeasonNullable, SeasonSegmentNullable, StartPeriodNullable, StartRangeNullable, ConferenceNullable, DivisionNullable


#pylint: disable=unused-variable

# Flask Setup
#################################################
app = Flask(__name__)

# Database Setup
#################################################

# app.config['SQLALCHEMY_DATABASE_URL'] = os.environ.get('DATABASE_URL', '')

#app.config['SQLALCHEMY_DATABASE_URL'] = "postgres://gvuvmkxy:Z62u_yZyL3sTjlr-XDy0eUcBrAy9ucOU@ziggy.db.elephantsql.com:5432/gvuvmkxy"
#db = SQLAlchemy(app)

engine = create_engine("postgres://eskbntsz:4rZCsWbTEBAnuRThZm1j9ZH6XOwI7A59@ziggy.db.elephantsql.com:5432/eskbntsz")

Base = automap_base()
Base.prepare(engine, reflect=True)

#Tables for queries
players = Base.classes.players
teams = Base.classes.teams

# create route that renders index.html template
@app.route("/")
def home():
    return render_template("index.html")

# Service Routes
@app.route("/api/teams")
def teamsroute():
    session = Session(engine)
    results = session.query(teams.team_id, teams.abbreviation, teams.nickname, teams.city).all()
    session.close()
    team_list = []
    for team_id, abr, nickname, city in results:
        team = {}
        team["id"] = team_id
        team["abr"] = abr
        team["nickname"] = nickname
        team["city"] = city
        team_list.append(team)
    return jsonify(team_list)

@app.route("/api/players")
def playersroute():
    session = Session(engine)
    results = session.query(players.PERSON_ID, players.TEAM_ID, players.DISPLAY_FIRST_LAST).all()
    session.close()
    players_team_list = []
    for player_id, team_id, name in results:
        player = {}
        player["player_id"] = player_id
        player["team_id"] = team_id
        player["player_name"] = name
        players_team_list.append(player)
    return jsonify(players_team_list)

@app.route("/api/playerinfo/<id>")
def playerinfo(id=None):
    
    player_info = commonplayerinfo.CommonPlayerInfo(player_id=id)
    df = player_info.get_data_frames()[0]
    player_data = []
    for index, row in df.iterrows():
        data = {}
        data["a_Name"] = row["DISPLAY_FIRST_LAST"]
        data["e_School"] = row["SCHOOL"]
        data["f_Country"] = row["COUNTRY"]
        data["b_Height"] = row["HEIGHT"]
        data["c_Weight"] = row["WEIGHT"]
        data["d_Seasons"] = row["SEASON_EXP"]
        data["g_Draft_year"] = row["DRAFT_YEAR"]
        data["h_Draft_round"] = row["DRAFT_ROUND"]
        data["i_draft_number"] = row["DRAFT_NUMBER"]
        player_data.append(data)
    
    return jsonify(player_data)

@app.route("/api/seasonstats/<id>")
def seasonstats(id=None):
    splits = player.Splits(player_id=id, season="2020-21").overall()
    splits = splits[['W', 'L','MIN', 'FGM',
       'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT',
       'OREB', 'DREB', 'REB', 'AST',  'STL', 'BLK','TOV', 'PF',
       'PTS', 'PLUS_MINUS']]
    stats = []
    for index, row in splits.iterrows():
        game = {}
        game["aW"] = row["W"]
        game["bL"] = row["L"]
        game["dMIN"] = row["MIN"]
        game["eFGM"] = row["FGM"]
        game["fFGA"] = row["FGA"]
        game["gFG_PCT"] = row["FG_PCT"]
        game["hFG3M"] = row["FG3M"]
        game["iFG3A"] = row["FG3A"]
        game["jFTM"] = row["FTM"]
        game["kFTA"] = row["FTA"]
        game["lFT_PCT"] = row["FT_PCT"]
        game["mOREB"] = row["OREB"]
        game["nDREB"] = row["DREB"]
        game["oDREB"] = row["REB"]
        game["pAST"] = row["AST"]
        game["qSTL"] = row["STL"]
        game["rBLK"] = row["BLK"]
        game["sTOV"] = row["TOV"]
        game["tPF"] = row["PF"]
        game["uPTS"] = row["PTS"]
        game["vPLUS/MINUS"] = row["PLUS_MINUS"]
        stats.append(game)
    
    return jsonify(stats)

@app.route("/api/gamelog/<id>")
def gamelogs(id=None):
    game_log = player.GameLogs(player_id=id, season="2020-21").logs()
    game_log = game_log[['GAME_DATE', 'MATCHUP', 'WL',
       'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA',
       'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF',
       'PTS', 'PLUS_MINUS']]
    gamelog = []
    for index, row in game_log.iterrows():
        game = {}
        game["aDate"] = row["GAME_DATE"]
        game["bMatchup"] = row["MATCHUP"]
        game["cWL"] = row["WL"]
        game["dMIN"] = row["MIN"]
        game["eFGM"] = row["FGM"]
        game["fFGA"] = row["FGA"]
        game["gFG_PCT"] = row["FG_PCT"]
        game["hFG3M"] = row["FG3M"]
        game["iFG3A"] = row["FG3A"]
        game["jFTM"] = row["FTM"]
        game["kFTA"] = row["FTA"]
        game["lFT_PCT"] = row["FT_PCT"]
        game["mOREB"] = row["OREB"]
        game["nDREB"] = row["DREB"]
        game["oDREB"] = row["REB"]
        game["pAST"] = row["AST"]
        game["qSTL"] = row["STL"]
        game["rBLK"] = row["BLK"]
        game["sTOV"] = row["TOV"]
        game["tPF"] = row["PF"]
        game["uPTS"] = row["PTS"]
        game["vPLUS/MINUS"] = row["PLUS_MINUS"]
        gamelog.append(game)

    
    return jsonify(gamelog)

@app.route("/api/volume/<player_id>")
def volume(player_id=None):
    shot_charts = shot_chart.ShotChart(player_id=player_id, season="2020-21").shot_chart()

    df = pd.DataFrame(shot_charts["SHOT_TYPE"].value_counts())
    df['Volume'] = (df["SHOT_TYPE"]/df["SHOT_TYPE"].sum()).astype(float).map('{:,.2%}'.format)
    shot_type_pct = df[["Volume"]]
    df_2 = shot_charts[['SHOT_TYPE', "SHOT_MADE_FLAG"]]
    df_2 = df_2.rename(columns={"SHOT_TYPE": "Shot Type","SHOT_MADE_FLAG": "FG%"})
    fg_type = df_2.groupby(["Shot Type"]).mean()
    fg_type["FG%"] = fg_type["FG%"].map('{:,.2%}'.format)
    merged_type = pd.merge(shot_type_pct, fg_type, left_index=True, right_index=True)

    df = pd.DataFrame(shot_charts["SHOT_ZONE_BASIC"].value_counts())
    df['Volume'] = (df["SHOT_ZONE_BASIC"]/df["SHOT_ZONE_BASIC"].sum()).astype(float).map('{:,.2%}'.format)
    zone_pct = df[["Volume"]]
    df_2 = shot_charts[['SHOT_ZONE_BASIC', "SHOT_MADE_FLAG"]]
    df_2 = df_2.rename(columns={"SHOT_ZONE_BASIC": "Shot Type","SHOT_MADE_FLAG": "FG%"})
    fg_zone = df_2.groupby(["Shot Type"]).mean()
    fg_zone["FG%"] = fg_zone["FG%"].map('{:,.2%}'.format)
    merged_zone = pd.merge(zone_pct, fg_zone, left_index=True, right_index=True)

    df = pd.DataFrame(shot_charts["SHOT_ZONE_RANGE"].value_counts())
    df['Volume'] = (df["SHOT_ZONE_RANGE"]/df["SHOT_ZONE_RANGE"].sum()).astype(float).map('{:,.2%}'.format)
    distance_pct = df[["Volume"]]
    df_2 = shot_charts[['SHOT_ZONE_RANGE', "SHOT_MADE_FLAG"]]
    df_2 = df_2.rename(columns={"SHOT_ZONE_RANGE": "Shot Distance","SHOT_MADE_FLAG": "FG%"})
    fg_distance = df_2.groupby(["Shot Distance"]).mean()
    fg_distance["FG%"] = fg_distance["FG%"].map('{:,.2%}'.format)
    merged_distance = pd.merge(distance_pct, fg_distance, left_index=True, right_index=True)

    concat = pd.concat([merged_type, merged_zone])
    final = pd.concat([concat, merged_distance])

    volume = []
    for index, row in final.iterrows():
        data = {}
        data["Location"] = index
        data["Volume"] = row["Volume"]
        data["Percent"] = row["FG%"]
        volume.append(data)

    return jsonify(volume)

@app.route("/api/shotchart/<player_id>")
def shotcharts(player_id=None):
    
    shot_charts = shot_chart.ShotChart(player_id=player_id, season="2020-21").shot_chart()
    shot_charts["MADE_MISS"] = ['green' if x == 1 else 'red' for x in shot_charts['SHOT_MADE_FLAG']]
    df = shot_charts
    
    allshots = []
    for index, row in df.iterrows():
        shot = {}
        shot["index"] = index
        shot["year"] = row["GAME_DATE"][0:4]
        shot["day"] = row["GAME_DATE"][4:6]
        shot["month"] = row["GAME_DATE"][6:8]
        shot["game_id"] = row["GAME_ID"]
        shot["team"] = row["TEAM_NAME"]
        shot["name"] = row["PLAYER_NAME"]
        shot["quarter"] = row["PERIOD"]
        shot["minutes"] = row["MINUTES_REMAINING"]
        shot["seconds"] = row["SECONDS_REMAINING"]
        shot["action_type"] = row["ACTION_TYPE"]
        shot["shot_type"] = row["SHOT_TYPE"]
        shot["shot_distance"] = row["SHOT_DISTANCE"]
        shot["shot_made"] = row["SHOT_MADE_FLAG"]
        shot["class"] = row["MADE_MISS"]            
        shot["x"] = row["LOC_X"]
        shot["y"] = row["LOC_Y"]
        shot["home"] = row["HTM"]
        shot["away"] = row["VTM"] 
        allshots.append(shot)

    return jsonify(allshots)

@app.route("/api/next_game/<player_id>")
def next(player_id=None):
    next_game_id = player.Career(player_id=player_id).next_game()
    next_game_id["Team"] = next_game_id["VS_TEAM_CITY"] +" " + next_game_id["VS_TEAM_NICKNAME"]
    df = player.OpponentSplits(player_id=player_id).by_team()
    df["PRA"] = df["PTS"] + df["REB"] + df["AST"]
    df["PA"] = df["PTS"]  + df["AST"]
    df["PR"] = df["PTS"] + df["REB"]
    df["AR"] = df["AST"] + df["REB"]
    df["STL/BLK"] = df["STL"] + df["BLK"]
    df = df[["GROUP_VALUE", "GP", 'MIN', 'FGM',
           'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA',
           'PTS', 'REB', 'OREB', 'AST', "PRA", "PA", "PR", "AR", 'STL', 'BLK', 'STL/BLK']]
    
    table = []
    for index, row in df.iterrows():
        if (row["GROUP_VALUE"] == next_game_id["Team"][0]):
            data = {}
            data["aTeam"] = row["GROUP_VALUE"]
            data['bGP'] = row["GP"]
            data["cMIN"] = row["MIN"]
            data["dFGM"] = row["FGM"]
            data["eFGA"] = row["FGA"]
            data["fFG3M"] = row["FG3M"]
            data["gFG3A"] = row["FG3A"]
            data["hFTM"] = row["FTM"]
            data["iFTA"] = row["FTA"]
            data["jPTS"] = row["PTS"]
            data["kREB"] = row["REB"]
            data["lOREB"] = row["OREB"]
            data["mAST"] = row["AST"]
            data["nPRA"] = row["PRA"]
            data["oPA"] = row["PA"]
            data["pPR"] = row["PR"]
            data["qAR"] = row["AR"]
            data["rSTL"] = row["STL"]
            data["sBLK"] = row["BLK"]
            data["tSTL/BLK"] = row["STL/BLK"]
            table.append(data)
        else:
            pass
    
    return jsonify(table)

@app.route("/api/last_game/<player_id>")
def last_x(player_id=None):
    df_5 = player.LastNGamesSplits(player_id=player_id, season="2020-21").last_5()
    df_5["PRA"] = df_5["PTS"] + df_5["REB"] + df_5["AST"]
    df_5["PA"] = df_5["PTS"]  + df_5["AST"]
    df_5["PR"] = df_5["PTS"] + df_5["REB"]
    df_5["AR"] = df_5["AST"] + df_5["REB"]
    df_5["STL/BLK"] = df_5["STL"] + df_5["BLK"]
    df_5 = df_5[["GROUP_SET", 'MIN', 'FGM',
           'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA',
           'PTS', 'REB', 'OREB', 'AST', "PRA", "PA", "PR", "AR", 'STL', 'BLK', 'STL/BLK']]
    df_5 = df_5.rename(columns={"GROUP_SET": "Split"})
    df_5 = pd.DataFrame(df_5)
    
    df_10 = player.LastNGamesSplits(player_id=player_id, season="2020-21").last_10()
    df_10["PRA"] = df_10["PTS"] + df_10["REB"] + df_10["AST"]
    df_10["PA"] = df_10["PTS"]  + df_10["AST"]
    df_10["PR"] = df_10["PTS"] + df_10["REB"]
    df_10["AR"] = df_10["AST"] + df_10["REB"]
    df_10["STL/BLK"] = df_10["STL"] + df_10["BLK"]
    df_10 = df_10[["GROUP_SET", 'MIN', 'FGM',
           'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA',
           'PTS', 'REB', 'OREB', 'AST', "PRA", "PA", "PR", "AR", 'STL', 'BLK', 'STL/BLK']]
    df_10 = df_10.rename(columns={"GROUP_SET": "Split"})
    df_10 = pd.DataFrame(df_10)
    
    concat = pd.concat([df_5, df_10])
    
    df_20 = player.LastNGamesSplits(player_id=player_id, season="2020-21").last_20()
    df_20["PRA"] = df_20["PTS"] + df_20["REB"] + df_20["AST"]
    df_20["PA"] = df_20["PTS"]  + df_20["AST"]
    df_20["PR"] = df_20["PTS"] + df_20["REB"]
    df_20["AR"] = df_20["AST"] + df_20["REB"]
    df_20["STL/BLK"] = df_20["STL"] + df_20["BLK"]
    df_20 = df_20[["GROUP_SET", 'MIN', 'FGM',
           'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA',
           'PTS', 'REB', 'OREB', 'AST', "PRA", "PA", "PR", "AR", 'STL', 'BLK', 'STL/BLK']]
    df_20 = df_20.rename(columns={"GROUP_SET": "Split"})
    df_20 = pd.DataFrame(df_20)
    
    final = pd.concat([concat, df_20])
    
    all_data = []
    for index, row in final.iterrows():
        data = {}
        data["aSplit"] = row["Split"]
        data["bMIN"] = row["MIN"]
        data["cFGM"] = row["FGM"]
        data["dFGA"] = row["FGA"]
        data["daFG3M"] = row["FG3M"]
        data["eFG3A"] = row["FG3A"]
        data["fFTM"] = row["FTM"]
        data["gFTA"] = row["FTA"]
        data["hPTS"] = row["PTS"]
        data["iREB"] = row["REB"]
        data["jOREB"] = row["OREB"]
        data["kAST"] = row["AST"]
        data["lPRA"] = row["PRA"]
        data["mPA"] = row["PA"]
        data["nPR"] = row["PR"]
        data["oAR"] = row["AR"]
        data["pSTL"] = row["STL"]
        data["qBLK"] = row["BLK"]
        data["rSTL/BLK"] = row["STL/BLK"]
        all_data.append(data)

    return jsonify(all_data)


if __name__ == "__main__":
    app.run(debug=True)

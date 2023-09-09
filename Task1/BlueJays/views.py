from flask import render_template
from BlueJays import app
from datetime import datetime
import requests
import statsapi
import feedparser

abbreviations = {
    "Toronto Blue Jays": "TOR",
    "Baltimore Orioles": "BAL",
    "Boston Red Sox": "BOS",
    "New York Yankees": "NYY",
    "Tampa Bay Rays": "TB",
    "Chicago White Sox": "CWS",
    "Cleveland Guardians": "CLE",
    "Cleveland Indians": "CLE",
    "Detroit Tigers": "DET",
    "Kansas City Royals": "KC",
    "Minnesota Twins": "MIN",
    "Houston Astros": "HOU",
    "Los Angeles Angels": "LAA",
    "Oakland Athletics": "OAK",
    "Seattle Mariners": "SEA",
    "Texas Rangers": "TEX",
    "Atlanta Braves": "ATL",
    "Miami Marlins": "MIA",
    "New York Mets": "NYM",
    "Philadelphia Phillies": "PHI",
    "Washington Nationals": "WSH",
    "Chicago Cubs": "CHC",
    "Cincinnati Reds": "CIN",
    "Milwaukee Brewers": "MIL",
    "Pittsburgh Pirates": "PIT",
    "St. Louis Cardinals": "STL",
    "Arizona Diamondbacks": "ARI",
    "Colorado Rockies": "COL",
    "Los Angeles Dodgers": "LAD",
    "San Diego Padres": "SD",
    "San Francisco Giants": "SF",
}

divisions = {
    201: "AL East",
    202: "AL Central",
    200: "AL West",
    204: "NL East",
    205: "NL Central",
    203: "NL West",
}

ranks = {"1": "1st", "2": "2nd", "3": "3rd", "4": "4th", "5": "5th"}


@app.route("/")
@app.route("/teams/")
def home():

    standings_url = "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104"

    response = requests.get(standings_url)

    standings = response.json()

    arrange = [0, 3, 1, 4, 2, 5]

    news_url = "https://www.mlb.com/feeds/news/rss.xml"

    news_response = requests.get(news_url)

    raw = news_response.text

    raw = raw.replace("<image", "<img")

    news = feedparser.parse(raw)

    newsFeed = []

    for i in range(0, 5):
        dateString = news["entries"][i]["mlb_display-date"].split()[0]
        date = datetime.strptime(dateString, "%m/%d/%Y")
        date = date.strftime("%b %d, %Y")

        newsFeed.append(
            {
                "title": news["entries"][i]["title"],
                "author": news["entries"][i]["author"],
                "img": news["entries"][i]["img"]["href"],
                "date": date,
                "link": news["entries"][i]["link"],
            }
        )

    standings["records"] = [standings["records"][i] for i in arrange]

    return render_template(
        "index.html",
        standings=standings,
        divisions=divisions,
        abbreviations=abbreviations,
        newsFeed=newsFeed,
    )


@app.route("/teams/<id>")
def teams(id):

    team_url = "https://statsapi.mlb.com/api/v1/teams/" + id

    team_response = requests.get(team_url)

    team = team_response.json()

    teamName = team["teams"][0]["teamName"].replace(" ", "").replace("-", "").lower()

    news_url = "https://www.mlb.com/" + teamName + "/feeds/news/rss.xml"

    news_response = requests.get(news_url)

    raw = news_response.text

    raw = raw.replace("<image", "<img")

    news = feedparser.parse(raw)

    newsFeed = []

    for i in range(0, 5):
        dateString = news["entries"][i]["mlb_display-date"].split()[0]
        date = datetime.strptime(dateString, "%m/%d/%Y")
        date = date.strftime("%b %d, %Y")

        newsFeed.append(
            {
                "title": news["entries"][i]["title"],
                "author": news["entries"][i]["author"],
                "img": news["entries"][i]["img"]["href"],
                "date": date,
                "link": news["entries"][i]["link"],
            }
        )

    standings_url = "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104"

    standings_response = requests.get(standings_url)

    standings = standings_response.json()

    standing = {}

    for division in standings["records"]:
        for team in division["teamRecords"]:
            if str(team["team"]["id"]) == str(id):
                standing = team
                standing["division"] = division["division"]["id"]
                break
        if len(standing) > 0:
            break

    roster_url = (
        "https://statsapi.mlb.com/api/v1/teams/"
        + id
        + "/roster/Active?hydrate=person(stats(type=season))"
    )

    roster_response = requests.get(roster_url)

    roster = roster_response.json()

    hitters = []

    pitchers = []

    for player in roster["roster"]:
        if player["person"]["primaryPosition"]["name"] == "Pitcher":
            if "stats" not in player["person"]:
                pitchers.append(player["person"])
                continue

            strikeOuts = player["person"]["stats"][0]["splits"][0]["stat"]["strikeOuts"]
            walks = player["person"]["stats"][0]["splits"][0]["stat"]["baseOnBalls"]
            battersFaced = player["person"]["stats"][0]["splits"][0]["stat"][
                "battersFaced"
            ]
            strikeOutRate = round((strikeOuts / battersFaced) * 100)
            walkRate = round((walks / battersFaced) * 100)

            player["person"]["stats"][0]["splits"][0]["stat"][
                "strikeOutRate"
            ] = strikeOutRate
            player["person"]["stats"][0]["splits"][0]["stat"]["walkRate"] = walkRate
            pitchers.append(player["person"])

        elif player["person"]["primaryPosition"]["name"] == "Two-Way Player":

            pitcher_url = (
                "https://statsapi.mlb.com/api/v1/people/"
                + str(player["person"]["id"])
                + "?hydrate=stats(group=[pitching],type=[season])"
            )
            pitcher_response = requests.get(pitcher_url)
            pitcher = pitcher_response.json()

            hitter_url = (
                "https://statsapi.mlb.com/api/v1/people/"
                + str(player["person"]["id"])
                + "?hydrate=stats(group=[hitting],type=[season])"
            )
            hitter_response = requests.get(hitter_url)
            hitter = hitter_response.json()

            if (
                "stats" not in pitcher["people"][0]
                and "stats" not in hitter["people"][0]
            ):
                pitchers.append(pitcher["people"][0])
                hitters.append(hitter["people"][0])

            elif "stats" not in pitcher["people"][0]:
                pitchers.append(pitcher["people"][0])

                batting_strikeOuts = hitter["people"][0]["stats"][0]["splits"][0][
                    "stat"
                ]["strikeOuts"]
                batting_walks = hitter["people"][0]["stats"][0]["splits"][0]["stat"][
                    "baseOnBalls"
                ]
                plateAppearances = hitter["people"][0]["stats"][0]["splits"][0]["stat"][
                    "plateAppearances"
                ]

                batting_strikeOutRate = round(
                    (batting_strikeOuts / plateAppearances) * 100, 1
                )
                batting_walkRate = round((batting_walks / plateAppearances) * 100, 1)

                hitter["people"][0]["stats"][0]["splits"][0]["stat"][
                    "strikeOutRate"
                ] = batting_strikeOutRate
                hitter["people"][0]["stats"][0]["splits"][0]["stat"][
                    "walkRate"
                ] = batting_walkRate

                hitters.append(hitter["people"][0])

            elif "stats" not in hitter["people"][0]:
                hitters.append(hitter["people"][0])

                pitching_strikeOuts = pitcher["people"][0]["stats"][0]["splits"][0][
                    "stat"
                ]["strikeOuts"]
                pitching_walks = pitcher["people"][0]["stats"][0]["splits"][0]["stat"][
                    "baseOnBalls"
                ]
                battersFaced = pitcher["people"][0]["stats"][0]["splits"][0]["stat"][
                    "battersFaced"
                ]

                pitching_strikeOutRate = round(
                    (pitching_strikeOuts / battersFaced) * 100
                )
                pitching_walkRate = round((pitching_walks / battersFaced) * 100)

                pitcher["people"][0]["stats"][0]["splits"][0]["stat"][
                    "strikeOutRate"
                ] = pitching_strikeOutRate
                pitcher["people"][0]["stats"][0]["splits"][0]["stat"][
                    "walkRate"
                ] = pitching_walkRate

                pitchers.append(pitcher["people"][0])

            else:
                pitching_strikeOuts = pitcher["people"][0]["stats"][0]["splits"][0][
                    "stat"
                ]["strikeOuts"]
                pitching_walks = pitcher["people"][0]["stats"][0]["splits"][0]["stat"][
                    "baseOnBalls"
                ]
                battersFaced = pitcher["people"][0]["stats"][0]["splits"][0]["stat"][
                    "battersFaced"
                ]

                pitching_strikeOutRate = round(
                    (pitching_strikeOuts / battersFaced) * 100
                )
                pitching_walkRate = round((pitching_walks / battersFaced) * 100)

                pitcher["people"][0]["stats"][0]["splits"][0]["stat"][
                    "strikeOutRate"
                ] = pitching_strikeOutRate
                pitcher["people"][0]["stats"][0]["splits"][0]["stat"][
                    "walkRate"
                ] = pitching_walkRate

                pitchers.append(pitcher["people"][0])

                batting_strikeOuts = hitter["people"][0]["stats"][0]["splits"][0][
                    "stat"
                ]["strikeOuts"]
                batting_walks = hitter["people"][0]["stats"][0]["splits"][0]["stat"][
                    "baseOnBalls"
                ]
                plateAppearances = hitter["people"][0]["stats"][0]["splits"][0]["stat"][
                    "plateAppearances"
                ]

                batting_strikeOutRate = round(
                    (batting_strikeOuts / plateAppearances) * 100, 1
                )
                batting_walkRate = round((batting_walks / plateAppearances) * 100, 1)

                hitter["people"][0]["stats"][0]["splits"][0]["stat"][
                    "strikeOutRate"
                ] = batting_strikeOutRate
                hitter["people"][0]["stats"][0]["splits"][0]["stat"][
                    "walkRate"
                ] = batting_walkRate

                hitters.append(hitter["people"][0])

        else:
            if "stats" not in player["person"]:
                hitters.append(player["person"])
                continue

            strikeOuts = player["person"]["stats"][0]["splits"][0]["stat"]["strikeOuts"]
            walks = player["person"]["stats"][0]["splits"][0]["stat"]["baseOnBalls"]
            plateAppearances = player["person"]["stats"][0]["splits"][0]["stat"][
                "plateAppearances"
            ]
            strikeOutRate = round((strikeOuts / plateAppearances) * 100, 1)
            walkRate = round((walks / plateAppearances) * 100, 1)

            player["person"]["stats"][0]["splits"][0]["stat"][
                "strikeOutRate"
            ] = strikeOutRate
            player["person"]["stats"][0]["splits"][0]["stat"]["walkRate"] = walkRate
            hitters.append(player["person"])

    tableLengths = {"hitters": len(hitters), "pitchers": len(pitchers)}

    return render_template(
        "team.html",
        pitchers=pitchers,
        hitters=hitters,
        tableLengths=tableLengths,
        standing=standing,
        divisions=divisions,
        ranks=ranks,
        newsFeed=newsFeed,
    )


@app.route("/players/<id>")
def players(id):

    player_lookup = statsapi.lookup_player(id)

    team = statsapi.lookup_team(player_lookup[0]["currentTeam"]["id"])

    player_url = "https://statsapi.mlb.com/api/v1/people/" + id

    response = requests.get(player_url)

    player = response.json()

    years = {}

    currentYear = datetime.now().year

    if player["people"][0]["primaryPosition"]["name"] == "Two-Way Player":
        player_url = (
            "https://statsapi.mlb.com/api/v1/people/"
            + id
            + "?hydrate=stats(group=[hitting,pitching],type=[yearByYear])"
        )
        response = requests.get(player_url)
        player = response.json()

        arrange = [1, 0]

        if player["people"][0]["stats"][0]["group"]["displayName"] != "pitching":
            player["people"][0]["stats"] = [
                player["people"][0]["stats"][i] for i in arrange
            ]

        years["pitching"] = len(player["people"][0]["stats"][0]["splits"])
        years["hitting"] = len(player["people"][0]["stats"][1]["splits"])

    elif player["people"][0]["primaryPosition"]["name"] == "Pitcher":
        player_url = (
            "https://statsapi.mlb.com/api/v1/people/"
            + id
            + "?hydrate=stats(group=[pitching],type=[yearByYear])"
        )
        response = requests.get(player_url)
        player = response.json()

        if "stats" in player["people"][0]:
            years["pitching"] = len(player["people"][0]["stats"][0]["splits"])

    else:
        player_url = (
            "https://statsapi.mlb.com/api/v1/people/"
            + id
            + "?hydrate=stats(group=[hitting],type=[yearByYear])"
        )
        response = requests.get(player_url)
        player = response.json()

        if "stats" in player["people"][0]:
            years["hitting"] = len(player["people"][0]["stats"][0]["splits"])

    return render_template(
        "player.html",
        player=player["people"][0],
        team=team[0],
        abbreviations=abbreviations,
        years=years,
        currentYear=currentYear,
    )


@app.route("/leaderboards")
def leaderboards():

    statCategories = [
        "homeRuns",
        "runs",
        "battingAverage",
        "runsBattedIn",
        "doubles",
        "triples",
        "hits",
        "onBasePercentage",
        "sluggingPercentage",
        "onBasePlusSlugging",
        "stolenBases",
        "wins",
        "earnedRunAverage",
        "strikeouts",
        "walksAndHitsPerInningPitched",
        "saves",
    ]

    statCategoryTypes = {
        "homeRuns": "hitting",
        "battingAverage": "hitting",
        "runs": "hitting",
        "runsBattedIn": "hitting",
        "doubles": "hitting",
        "triples": "hitting",
        "hits": "hitting",
        "onBasePercentage": "hitting",
        "sluggingPercentage": "hitting",
        "onBasePlusSlugging": "hitting",
        "stolenBases": "hitting",
        "wins": "pitching",
        "earnedRunAverage": "pitching",
        "strikeouts": "pitching",
        "walksAndHitsPerInningPitched": "pitching",
        "saves": "pitching",
    }

    statNames = {
        "homeRuns": "Home Runs",
        "battingAverage": "Batting Average",
        "runs": "Runs",
        "runsBattedIn": "Runs Batted In",
        "doubles": "Doubles",
        "triples": "Triples",
        "hits": "Hits",
        "onBasePercentage": "On Base %",
        "sluggingPercentage": "Slugging %",
        "onBasePlusSlugging": "On Base + Slugging %",
        "stolenBases": "Stolen Bases",
        "wins": "Wins",
        "earnedRunAverage": "Earned Run Average",
        "strikeouts": "Strike Outs",
        "walksAndHitsPerInningPitched": "Walks + Hits per IP",
        "saves": "Saves",
    }

    statAcronyms = {
        "homeRuns": "HR",
        "battingAverage": "AVG",
        "runs": "R",
        "runsBattedIn": "RBI",
        "doubles": "2B",
        "triples": "3B",
        "hits": "H",
        "onBasePercentage": "OBP",
        "sluggingPercentage": "SLG",
        "onBasePlusSlugging": "OPS",
        "stolenBases": "SB",
        "wins": "W",
        "earnedRunAverage": "ERA",
        "strikeouts": "SO",
        "walksAndHitsPerInningPitched": "WHIP",
        "saves": "SV",
        }    

    leagueLeaders = []

    for stat in statCategories:
        leagueLeaders.append(
            (
                statsapi.get(
                    "stats_leaders",
                    {"leaderCategories": stat, "statGroup": statCategoryTypes[stat]},
                )
            )["leagueLeaders"][0]
        )
        
    for i in range(0, len(statCategories)):
        for j in range (0, 3):
            position_url = "https://statsapi.mlb.com/api/v1/people/" + str(leagueLeaders[i]["leaders"][j]["person"]["id"])
            
            position_response = requests.get(position_url)
            
            leagueLeaders[i]["leaders"][j]["person"]["position"] = position_response.json()["people"][0]["primaryPosition"]["abbreviation"]

    length = len(leagueLeaders)

    return render_template(
        "leaderboards.html",
        leagueLeaders=leagueLeaders,
        length=length,
        abbreviations=abbreviations,
        statNames=statNames,
        statAcronyms=statAcronyms,
    )

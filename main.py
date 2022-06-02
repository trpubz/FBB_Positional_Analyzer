# TRP_Positional_Analyzer
# TRP is a custom Fantasy Baseball projection data set that stands for Truncated Runs Produced.  It relies on another's
# projection system (generally a product from Fangraphs) which focuses on a derived wRAA (weighted Runs Above Avg)
# and current expected stats from Baseball Savant.  The combined projection & current performance metrics produce TRP.
# This Positional Analyzer takes the TRP Datasets called player 'Cards' stored in the 'resources' folder and generates
# graphs and reports to make quick-informed decisions.  All functions specific to this project & not inside a class are
# designated with the 'TRP' namespace prefix.
# main.py
# by pubins.taylor
# v0.5 - 1 JUN 2022

from sources.Model.TRPLeagueManager import TRPLeagueManager as LeagueManager
import sources.Export.report_util as report_util
from sources.Export.report_generator_example import generate_report


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# instantiate the global objects
lm = LeagueManager()
hitters = lm.hitters
pitchers = lm.pitchers


def TRPFilterPosGroup(pos: str) -> (str, pd.DataFrame):
    """
    Function that filters the Position Group
    :parameter pos: a string representation of the roster slot
    :returns: tuple with the pos: str and the posGroup DataFrame
    """
    if pos.__contains__("P"):
        posPlayers = pitchers[pitchers["pos"].str.contains(pos)]
        # the dataset is sorted on xERA so the top skill is already at the top of the list
        if pos == "SP":
            topPlayers = posPlayers.head(
                12 * 5 + 26)  # 12 (num of teams) * 5 (potential SP slots) + 16 (arbitrary overage buffer)
        else:
            topPlayers = posPlayers.head(
                12 * 4 + 26)  # 12 (num of teams) * 4 (potential RP slots) + 16 (arbitrary overage buffer)
    else:
        posPlayers = hitters[hitters["pos"].str.contains(pos)]
        # trim the excess number of players for analysis
        # the dataset is sorted on wRAA so the top skill is already at the top of the list
        if pos == "OF":
            topPlayers = posPlayers.head(60)  # 3x more OF than any other position so get 3x results
        else:
            topPlayers = posPlayers.head(20)

    print(f"POS: {pos}")
    print(topPlayers.to_string())
    return pos, topPlayers


def TRPScatterPlotBuilder(pos: str, data: pd.DataFrame):
    xCat: str
    yCat: str
    sCat: str  # size category
    if pos.__contains__("P"):
        xCat = "WHIP"
        yCat = "ERA"
        sCat = "xERA"
    else:
        xCat = "OBP"
        yCat = "SLG"
        sCat = "wRAA"

    # extract the data
    x = data[xCat].to_numpy()
    y = data[yCat].to_numpy()
    # size and color based on wRAA:
    sizes = data[sCat].apply(lambda r: r * 10)
    colors = data[sCat].apply(lambda r: r * 10)

    # plot
    fig, ax = plt.subplots()

    ax.scatter(x, y, s=sizes, c=colors, vmin=0, vmax=100, alpha=0.5)
    # We only want to place the scatter plot labels only for those players that are Free Agents
    for name in data["_name"]:
        if data.fantasyTeam[data["_name"] == name].values[0] == "FA":  # 1st index value holds the string rep
            plt.text(x=data[xCat][data["_name"] == name], y=data[yCat][data["_name"] == name], s=name)
    ax.set_xlabel(xCat)
    ax.set_ylabel(yCat)
    ax.set_title(f'POS: {pos}')
    plt.axvline(data[xCat].mean(), c='black', ls='-')
    plt.axhline(data[yCat].mean(), c='black', ls='-')
    plt.grid()
    plt.figure(figsize=(18, 12))
    plt.show()
    plt.savefig(f"sources/TRPReport/{pos}.png", dpi=150)


if __name__ == '__main__':
    hitterData: (str, pd.DataFrame) = []
    for player in lm.bats:
        posGroup, dfPos = TRPFilterPosGroup(pos=player)
        TRPScatterPlotBuilder(pos=posGroup, data=dfPos)
        if posGroup == "OF":
            hitterData.append(posGroup, dfPos)

    for player in lm.arms:
        posGroup, dfPos = TRPFilterPosGroup(pos=player)
        TRPScatterPlotBuilder(pos=posGroup, data=dfPos)

    report = generate_report(pos=hitterData[0], dataset=hitterData[1])

    html_generator = report_util.HTMLReportContext("")
    html_generator.generate(report, "sources/TRPReport/TRP_Positional_Report")

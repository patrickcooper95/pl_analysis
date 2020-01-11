English Premier League - Quickest to First

Given Liverpool's dominance this Premier League season (2019-2020) and that it had already accumulated enough points for it to be
mathematically impossible to finish last in the league (20th) by December, I began to wonder how this compares to previous seasons.

Using the season_schedules.zip and the results.csv files (sources below), we can generate match-by-match tables in Python for each season 
from 2009 to 2018 to determine the average date or matches played a team reaches this milestone, the quickest it has been done within our sampled years, 
and look a little more into what teams were involved.

The singular Python file, pl_finish.py, provides all the code we need. Below are the results:

[Analysis Table](https://github.com/patrickcooper95/pl_analysis/blob/master/pl_analysis.xlsx)

The league-leading team's points and matches played when it ensured it could not finish last (20th place).


![The number of points the league-leading team and the matches played when enough points were reached to mathematically unable to finish
last.](https://github.com/patrickcooper95/pl_analysis/blob/master/pl_scatter.JPG)


Sources for the data used:

[Datahub.io - sports-data](https://datahub.io/sports-data/english-premier-league#resource-english-premier-league_zip)

[Zaeem Nalla - Kaggle](https://www.kaggle.com/zaeemnalla/premier-league#results.csv)

# Examples

Real-world usage examples with sample outputs.

## Basic Usage

### Get All Players
```python
from fpl_data.load import FplApiDataRaw

data = FplApiDataRaw()
players = data.elements_json

# Print first player's name and team
print(f"{players[0]['web_name']} - Team {players[0]['team']}")
```
```
Alisson - Team 11
```

### Top Scorers Analysis
```python
from fpl_data.transform import FplApiDataTransformed

data = FplApiDataTransformed()
players_df = data.players_df

# Top 5 scorers this season
top_scorers = players_df.nlargest(5, 'total_points')[['web_name', 'team', 'total_points']]
print(top_scorers)
```
```
      web_name  team  total_points
145      Haaland     9           234
285        Salah    11           212
67        Kane      5           198
123    De Bruyne    9           189
234      Son      13           176
```

### Best Value Players
```python
# Points per million spent
players_df['value'] = players_df['total_points'] / players_df['now_cost'] * 10
best_value = players_df.nlargest(5, 'value')[['web_name', 'total_points', 'now_cost', 'value']]
print(best_value)
```
```
    web_name  total_points  now_cost  value
89    Mitoma           145        55   26.4
156   Rashford         167        65   25.7
201   Toney           134        54   24.8
78    Mac Allister     128        52   24.6
145   Haaland         234        96   24.4
```

## Player History

### Individual Player Deep Dive
```python
from fpl_data.load import get_element_summary

# Get Haaland's performance (example player ID)
summary = get_element_summary(345)

print(f"Current season games: {len(summary['history'])}")
print(f"Season total: {sum(gw['total_points'] for gw in summary['history'])} points")

# Show last 3 gameweeks
for gw in summary['history'][-3:]:
    print(f"GW{gw['round']}: {gw['total_points']} pts, {gw['goals_scored']} goals")
```
```
Current season games: 28
Season total: 234 points

GW26: 12 pts, 2 goals  
GW27: 2 pts, 0 goals
GW28: 18 pts, 3 goals
```

### Past Seasons Summary
```python
past_seasons = summary['history_past']
for season in past_seasons:
    print(f"{season['season_name']}: {season['total_points']} pts in {season['minutes']} mins")
```
```
2022/23: 272 pts in 2769 mins
2021/22: 185 pts in 1801 mins  
2020/21: 201 pts in 2334 mins
```

## Team Analysis

### Team Performance Rankings
```python
team_stats = players_df.groupby('team').agg({
    'total_points': 'sum',
    'goals_scored': 'sum', 
    'clean_sheets': 'sum'
}).sort_values('total_points', ascending=False)

print(team_stats.head())
```
```
      total_points  goals_scored  clean_sheets
team                                         
9              1834           67            12
11             1789           63            10  
1              1678           55            14
5              1645           58             8
13             1612           52            11
```

## Advanced Analysis

### Players in Form
```python
# High form rating + good total points
form_players = players_df[
    (players_df['form'].astype(float) > 8.0) & 
    (players_df['total_points'] > 100)
][['web_name', 'form', 'total_points']].sort_values('form', ascending=False)

print(form_players.head())
```
```
     web_name  form  total_points
145   Haaland   9.4           234
67       Kane   9.1           198  
89     Mitoma   8.8           145
156   Rashford   8.6           167
234        Son   8.3           176
```
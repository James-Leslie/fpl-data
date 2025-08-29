# FPL Data

Python package for loading and transforming Fantasy Premier League API data.

## Installation

```bash
pip install fpl-data
```

## Quick Start

```python
from fpl_data.transform import FplApiDataTransformed

# Get clean pandas DataFrames
data = FplApiDataTransformed()
players_df = data.players_df

# Top scorers this season
top_scorers = players_df.nlargest(10, 'total_points')
print(top_scorers[['web_name', 'team', 'total_points']])
```

## Key Features

✅ **Raw JSON data** - Direct from FPL API endpoints  
✅ **Clean DataFrames** - Pandas-ready with proper types  
✅ **Player history** - Individual gameweek performance  
✅ **Enhanced metrics** - Goal involvements, points per 90min  
✅ **Live fixtures** - Current season schedule and results  

## What's Included

| Module | Purpose | Returns |
|--------|---------|---------|
| `fpl_data.load` | Raw API data | JSON dictionaries |
| `fpl_data.transform` | Clean data | Pandas DataFrames |

## Next Steps

- **[Interactive Notebooks →](https://github.com/James-Leslie/fpl-data/tree/main/notebooks)** - Jupyter tutorials you can run locally
- **[Package API Reference →](api.md)** - Complete function and class documentation
- **[External FPL API Reference →](fpl-api-reference.md)** - Details on the official FPL API endpoints

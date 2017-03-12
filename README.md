# python-rocket-league

Python library for interacting with the official [Rocket League API][1].

[![Build Status](https://travis-ci.org/rocket-league-replays/python-rocket-league?branch=master)](https://travis-ci.org/rocket-league-replays/python-rocket-league)

## Installation

```
pip install python-rocket-league
```

### Python version

The library was written using Python 3.5, but should work with Python 2.7 too, see the test suite for confirmation.

## Usage

```
from rlapi import RocketLeagueAPI

rl = RocketLeagueAPI('xxxxx')  # Replace xxxxx with your user token.
regions = rl.get_regions()
```

## Common options

### `platform`

Must be one of the following values:

* steam
* ps4
* xboxone

These are also available as the following constants (from `rlapi.constants`):

* `PLATFORM_STEAM`
* `PLATFORM_PLAYSTATION`
* `PLATFORM_XBOX`

### `playlist`

Must be one of the following numerical values:

* 10 (Ranked Duels)
* 11 (Ranked Doubles)
* 12 (Ranked Solo Standard)
* 13 (Ranked Standard)

These are also available as the following constants (from `rlapi.constants`):

* `PLAYLIST_RANKED_DUELS`
* `PLAYLIST_RANKED_DOUBLES`
* `PLAYLIST_RANKED_SOLO_STANDARD`
* `PLAYLIST_RANKED_STANDARD`

### `stat_type`

Must be one of the following values:

* assists
* goals
* mvps
* saves
* shots
* wins

These are also available as the following constants (from `rlapi.constants`):

* `STAT_ASSISTS`
* `STAT_GOALS`
* `STAT_MVPS`
* `STAT_SAVES`
* `STAT_SHOTS`
* `STAT_WINS`

### `player_id`

For single values pass the value as a string or integer.

```
player_id = 76561198022035654
```

For multiple values pass the values as strings or integers within a list.  You may request data for a maximum of 100 players per call.

```
player_id = [76561198022035654, 76561198008869772]
```

Values for Xbox One and PS4 are strings, values for Steam are integers ([though strings may work][4]).

## Endpoints

### `get_population()`

Returns the population data for each platform.

#### Response

```
[
	“Steam”: [
		{
			“PlaylistID”: 8,
			“NumPlayers”: 3
		},
		...
	],
	...
]
```

### `get_regions()`

Returns the list of regions available in the game.

#### Response

```
[
	{
		"region": "EU",
		"platforms": "Steam,PS4,XboxOne"
	},
	{
		"region": "USW",
		"platforms": "Steam,PS4,XboxOne"
	},
	...
]
```

### `get_skill_leaderboard(platform, playlist)`

Returns the top 100 entries of the skill leaderboard. Includes the player's username and tier.

#### Response

```
[
	{
		“user_name”: “iOghma”,
		“skill”: 1202,
		“tier”: 12,
	},
	...
]
```

### `get_stats_leaderboard(platform, stat_type)`

Returns the top 100 entries of the stats leaderboard, optionally filtered to a specific stat type. If you do not wish to filter the leaderboard, simply pass `platform` by itself.

#### Response

```
[
	{
		“stat_type”: “assists”,
		“stats”: [
			{
				“assists”: 2950,
				“username”: “Normal Times”,
			},
			{
				“assists”: 2575,
				“username”: “Lyn Pepper”,
			},
			...
		]
	},
	{
		“stat_type”: “goals”,
		“stats”: [
			{
				“goals”: 17789,
				“username”: “MadMassacre510”,
			},
			...
		]
	},
	...
]
```

### `get_player_skills(platform, player_id)`

Return skill values for one or more players.

#### Response

```
[
	{
		“user_name”: “Rocket_League1”,
		“player_skills”: [
			{
				“playlist”: 10,
				“skill”: 217,
				“matches_played”: 2,
				“tier”: 0,
				“tier_max”: 0,
				“division”: 0,
			}
		]
	}
]
```

### `get_player_titles(platform, player_id)`

Returns a list of titles available for a player.  You cannot request data for multiple players with this method.

#### Response

```
[
	{
		“title”: “Season2GrandChampion”,
	},
	...
]
```

### `get_stats_value_for_user(platform, stat_type, player_id)`

Returns stat values for one or more players for a specific stat type.

#### Response

```
[
	{
		“stat_type”: “assists”,
		“stats”: [
			{
				“assists”: 2950,
				“username”: “Normal Times”,
			},
			{
				“assists”: 2575,
				“username”: “Lyn Pepper”,
			},
			...
		]
	}
]
```

### get_stats_values_for_user(platform, player_id)`

Returns all stat values for one or more players.  This is a utility method to allow you to get all of the stats for one or more players without calling `get_stats_value_for_user()` 6 times per player. Each of the players will have their own key in the response, the key will be the player ID for Steam users and the player name for all other platforms.

#### Response

```
{
    76561198024807207: {
        'saves': 14099,
        'wins': 7803,
        'mvps': 3757,
        'shots': 42193,
        'goals': 18017,
        'assists': 9284
    }
}
```

## Running tests

```
pip install .[test]
pytest --cov-report=html --cov=rlapi -v -x -n auto
```

## Support

If you are having a problem with the client library, then you can open an [issue][5].
If you are having a problem with the data that is being returned, then you can post on the [API support forum][6].

## Author

[Daniel Samuels][2] for [Rocket League Replays][3].

[1]: https://api.rocketleague.com/
[2]: https://github.com/danielsamuels/
[3]: https://www.rocketleaguereplays.com/
[4]: http://psyonix.com/forum/viewtopic.php?p=292576#p292576
[5]: [issues/]
[6]: http://www.psyonix.com/forum/viewforum.php?f=40

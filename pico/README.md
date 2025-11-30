# PicoNhl

A library to enable the Raspberry Pi Pico (2) W to call the NHL API and retrieve data about a team and games they are playing or that are on their schedule.

## Basic Usage

```
import pico_nhl

# Connect to wifi somehow... (consider using my pico-wifi repo!)

nhl = PicoNhl(
    team = "SEA",
    scheduleWindow = pico_nhl.SCHEDULE_WINDOW_MONTH
)

while True:
    print("Getting game status...")
    status = nhl.getActiveGameData()

    print(f"Playing: {status.playing}")
    print(f"Team score: {status.teamScore}")

    if status.playing:
        ... do something ...
    else:
        ... do something else ...

    if status.gameState == pico_nhl.GAME_STATE_CRITICAL:
        ... do something impressive! ...
```

## API

### PicoNhl - PUBLIC

Top-level class for fetching data.

#### Constructor Parameters

| Parameter | Default | Description |
|----------|----------|-------------|
| team | `"SEA"` | Three-letter team abbreviation within the NHL API, e.g. `"SEA"`, `"NYR"`, `"NYI"`, `"BOS"` |
| scheduleWindow | `SCHEDULE_WINDOW_MONTH` | Schedule window to pull data for.  Largely useful for reducing the amount of data the pico will need to process.  If running on a Pico W rather than a Pico 2 W, consider using `SCHEDULE_WINDOW_WEEK` |

#### Methods

##### getActiveGame()

Fetches the schedule from the NHL API and gets any game that is currently active.  If no game is currently active, returns `GameData.emptyData()`.

The NHL API keeps the score up to date in almost realtime, but clock information may be behind by 20-30s.

##### getNextGameData()

Fetches the schedule from the NHL API and gets the first game with a start date greater than now.  If no upcoming game is available within the schedule window, returns `GameData.emptyData()`.

**This method uses the time on the Pico W.  Ensure you've set it before using this method.**

### GameData - PUBLIC

Represents the current state of a game being played, if one is being played.  All constructor parameters are accessible by users as properties of the resulting object.

#### Constructor Paramters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| gameState | `str` | NONE PROVIDED | The current state of the game as exposed by the API.  See the game state constants for string values |
| startTimeEpochSeconds | `int\|None` | NONE PROVIDED | 
| teamScore | `int\|None` | NONE PROVIDED | The current score for the team the API is serving.  Will be None if no game is currently being played |
| opponentScore | `int\|None` | NONE PROVIDED | The current score for the other team.  Will be None if no game is currently being played. |

#### Properties

##### playing - `bool`

Whether the game is currently in progress or not.  Returns true if `gameState` is any of:

* `GAME_STATE_PREGAME`
* `GAME_STATE_LIVE`
* `GAME_STATE_CRITICAL`

##### timeSortKey - `int`

Returns `startTimeEpochSeconds`, or `-1` if `startTimeEpochSeconds` is `None`

### Constants - PUBLIC

#### Schedule Windows

The NHL API contains a few different ways to fetch a team's schedule.  This library implements support for fetching it by month or by week.

| Constant | Description |
| -------- | ----------- |
| `SCHEDULE_WINDOW_MONTH` | Fetch all games on the team's schedule for the current month |
| `SCHEDULE_WINDOW_WEEK` | Fetch all games on the team's schedule for the current week |

#### GameState

The NHL API contains several different string values that represent the current state of a game, either scheduled for the future, in progress, or completed.  PicoNhl exports these values as explicitly named variables for ease of use.

Note that some of these values are undocumented and have never been seen by the developer (specifically `CRITICAL` and `POSTPONED`).  I'd recommend handling them, but wouldn't expect to see them in practice.

| Value | API Value | Counts as playing | Description |
| ----- | --------- | ----------------- | ----------- |
| `GAME_STATE_FUTURE` | `"FUT"` | No | A game that is scheduled for the future. |
| `GAME_STATE_PREGAME` | `"PRE"` | Yes | A game that has not yet actually begun play, but _is_ in the process of various pre-game rituals such as warm-ups. |
| `GAME_STATE_LIVE` | `"LIVE"` | Yes | A game that is currently being played |
| `GAME_STATE_CRITICAL` | `"CRIT"` | Yes | A game that is in some critical stage, such as overtime or a shootout.  May not actually exist, never seen in the wild. |
| `GAME_STATE_FINAL` | `"FINAL"`  | No | A game that has finished but has not yet finalized its stats. |
| `GAME_STATE_OFF` | `"OFF"` | No | A game that has completed and has finalized stats. |
| `GAME_STATE_POSTPONED` | `"PPD"` | No | A game that has been postponed.  May not exist, never seen in the wild. |

### TeamData - INTENRAL

Class used to fetch team-specific data for a schedule window.  The major difference between `TeamData` and `PicoNhl` is that `TeamData` will return `None` rather than `GameData.emptyData()` when it cannot find a game.  Feel free to use that instead if that's your jam, but note that it's internal and not intended to have a stable API.  It is subject to change between versions.

#### Constructor Parameters

| Parameter | Default | Description |
|----------|----------|-------------|
| team | `"SEA"` | Three-letter team abbreviation within the NHL API, e.g. `"SEA"`, `"NYR"`, `"NYI"`, `"BOS"` |
| scheduleWindow | `SCHEDULE_WINDOW_MONTH` | Schedule window to pull data for.  Largely useful for reducing the amount of data the pico will need to process.  If running on a Pico 1, consider using `SCHEDULE_WINDOW_WEEK` |

#### Methods

##### fetchActiveGame()

Fetches the schedule from the NHL API and gets any game that is currently active.  If no game is currently active, returns `None`.

The NHL API keeps the score up to date in almost realtime, but clock information may be behind by 20-30s.

##### fetchNextGameData()

Fetches the schedule from the NHL API and gets the first game with a start date greater than now.  If no upcoming game is available within the schedule window, returns `None`.

### NhlApi - INTERNAL

Class with static methods used to make network calls to the NHL API and convert the result to a dict.

#### STATIC - getTeamMonthSchedule(team: str, month: str = 'now')

Calls [Get Month Schedule](https://github.com/Zmalski/NHL-API-Reference?tab=readme-ov-file#get-month-schedule) from the NHL API via `urequests` and parses its JSON response as a `dict` using `ujson`.

The value of `month` is composed into the URL; this value defaults to `'now'`, which gets the current month's schedule.  Note that `now` does not require time to be set on the Pico, the NHL API handles this for us.

#### STATIC - getTeamWeekSchedule(team: str, week: str = 'now')

Calls [Get Week Schedule](https://github.com/Zmalski/NHL-API-Reference?tab=readme-ov-file#get-week-schedule) from the NHL API via `urequests` and parses its JSON response as a `dict` using `ujson`.

The value of `week` is composed into the URL; this value defaults to `'now'`, which gets the current week's schedule.  Note that `now` does not require time to be set on the Pico, the NHL API handles this for us.

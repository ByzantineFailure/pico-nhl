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

##### getActiveGameData()

Fetches the schedule from the NHL API and gets any game that is currently active.  If no game is currently active, returns `GameData.emptyData()`.

The NHL API publishes new game data every 20 seconds, so a score or game state change can take up to 20s (plus any delay upstream of the API) to show up.  See [NHL API Behavior](#nhl-api-behavior).

##### getNextGameData()

Fetches the schedule from the NHL API and gets the first game with a start date greater than now.  If no upcoming game is available within the schedule window, returns `GameData.emptyData()`.

**This method uses the time on the Pico W.  Ensure you've set the Pico's clock to UTC before using this method** (e.g. with `ntptime.settime()`, which sets UTC).  Game start times from the API are in UTC and are compared directly against the Pico's clock, so a clock set to local time will be off by your UTC offset.

### GameData - PUBLIC

Represents the current state of a game being played, if one is being played.  All constructor parameters are accessible by users as properties of the resulting object.

#### Constructor Parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| gameState | `str` | NONE PROVIDED | The current state of the game as exposed by the API.  See the game state constants for string values |
| startTimeEpochSeconds | `int\|None` | NONE PROVIDED | The game's scheduled start time in seconds since the epoch.  Will be None for `GameData.emptyData()` |
| teamScore | `int\|None` | NONE PROVIDED | The current score for the team the API is serving.  Will be None if no game is being played, including during pregame (`PRE`), when the API doesn't report a score yet.  Can go _down_ if a goal is overturned |
| opponentScore | `int\|None` | NONE PROVIDED | The current score for the other team.  Same rules as `teamScore`. |

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

None of these values are officially documented.  The descriptions below come from watching real games (most recently on 2026-10-31); `POSTPONED` has still never been seen, but I'd recommend handling it.

| Value | API Value | Counts as playing | Description |
| ----- | --------- | ----------------- | ----------- |
| `GAME_STATE_FUTURE` | `"FUT"` | No | A game that is scheduled for the future. |
| `GAME_STATE_PREGAME` | `"PRE"` | Yes | A game that has not yet actually begun play, but _is_ in the process of various pre-game rituals such as warm-ups.  Starts at least 15 minutes before the scheduled start and lasts until the opening faceoff, which can be 10+ minutes after the scheduled start.  No score is reported. |
| `GAME_STATE_LIVE` | `"LIVE"` | Yes | A game that is currently being played, including intermissions |
| `GAME_STATE_CRITICAL` | `"CRIT"` | Yes | A game in its final stage.  Seen starting with about 5 minutes left in the 3rd period (even in a 4-1 game) and lasting until the game ended. |
| _(no constant)_ | `"OVER"` | No | Seen for ~20 seconds between `CRIT` and `FINAL`, when the game has just ended.  Not exported as a constant; `playing` is false. |
| `GAME_STATE_FINAL` | `"FINAL"`  | No | A game that has finished but has not yet finalized its stats.  Lasted 23-32 minutes before becoming `OFF`. |
| `GAME_STATE_OFF` | `"OFF"` | No | A game that has completed and has finalized stats. |
| `GAME_STATE_POSTPONED` | `"PPD"` | No | A game that has been postponed.  May not exist, never seen in the wild. |

### TeamData - INTERNAL

Class used to fetch team-specific data for a schedule window.  The major difference between `TeamData` and `PicoNhl` is that `TeamData` will return `None` rather than `GameData.emptyData()` when it cannot find a game.  Feel free to use that instead if that's your jam, but note that it's internal and not intended to have a stable API.  It is subject to change between versions.

#### Constructor Parameters

| Parameter | Default | Description |
|----------|----------|-------------|
| team | `"SEA"` | Three-letter team abbreviation within the NHL API, e.g. `"SEA"`, `"NYR"`, `"NYI"`, `"BOS"` |
| scheduleWindow | `SCHEDULE_WINDOW_MONTH` | Schedule window to pull data for.  Largely useful for reducing the amount of data the pico will need to process.  If running on a Pico 1, consider using `SCHEDULE_WINDOW_WEEK` |

#### Methods

##### fetchActiveGame()

Fetches the schedule from the NHL API and gets any game that is currently active.  If no game is currently active, returns `None`.

##### fetchNextScheduledGame()

Fetches the schedule from the NHL API and gets the first game with a start date greater than now.  If no upcoming game is available within the schedule window, returns `None`.  Like `getNextGameData()`, this requires the Pico's clock to be set to UTC.

### NhlApi - INTERNAL

Class with static methods used to make network calls to the NHL API and convert the result to a dict.

#### STATIC - getTeamMonthSchedule(team: str, month: str = 'now')

Calls [Get Month Schedule](https://github.com/Zmalski/NHL-API-Reference?tab=readme-ov-file#get-month-schedule) from the NHL API via `urequests` and parses its JSON response as a `dict` using `ujson`.

The value of `month` is composed into the URL; this value defaults to `'now'`, which gets the current month's schedule.  Note that `now` does not require time to be set on the Pico, the NHL API handles this for us.

#### STATIC - getTeamWeekSchedule(team: str, week: str = 'now')

Calls [Get Week Schedule](https://github.com/Zmalski/NHL-API-Reference?tab=readme-ov-file#get-week-schedule) from the NHL API via `urequests` and parses its JSON response as a `dict` using `ujson`.

The value of `week` is composed into the URL; this value defaults to `'now'`, which gets the current week's schedule.  Note that `now` does not require time to be set on the Pico, the NHL API handles this for us.

## NHL API Behavior

Observations from polling the API during live games on 2026-10-31.  The API is unofficial, so any of this can change without notice.

* **Data updates every 20 seconds.**  Game state, period and scores change in the API's responses at :00, :20 and :40 seconds past each minute, on both the schedule endpoints this library uses and the game-center endpoints.  Responses are cached by Cloudflare for up to 19 seconds, so polling more often than every 20 seconds doesn't get fresher data.  If you want changes as soon as they're published, poll about 1 second after each 20-second mark (this needs the Pico's clock to be set).
* **`now` URLs redirect.**  `.../week/now` and `.../month/now` answer with a `307` redirect to a dated URL, so the HTTP client must follow redirects.  `week/now` returns the 7 days starting today.  `month/now` was seen returning the month of the team's _next_ game: on 2026-10-31, a team with no games left in October already got November.
* **Endpoints can briefly disagree.**  For up to one 20-second cycle, the week and month schedules and the game-center endpoints can report different states for the same game (e.g. the week schedule showed `FINAL` while the month schedule still showed `OVER`).
* **Scores can decrease** when a goal is overturned on review.

## Testing

Unit tests run on a regular computer with Python 3.10+ and no extra packages.  `tests/micropython_stubs.py` stands in for MicroPython's `urequests` and `utime`, and the tests run the library against real NHL API responses saved in `tests/fixtures/` (see that folder's README for where each one came from).  The `utime` stand-in treats times as UTC, matching a Pico whose clock is set to UTC.

From the repository root:

```
python3 -m unittest discover -s tests -v
```

## Notes

This is a library I built to help my husband out with a project.  You're welcome to use it since it's intended to be reasonably general, but I'm unlikely to take feature requests or make any updates to it based on github requests.  It's intended as a for-purpose abstraction.

If you're looking for some wifi connectivity to use, consider [pico-wifi](https://github.com/ByzantineFailure/pico-wifi)
# Pico Library

This is the Pico library that pairs with the server within this repository.  It has a single class, `PicoNhl`, which may be used to query the API and work with the results easily in Micropython.

## Basic Usage

```
import pico_nhl

# Connect to wifi somehow...

nhl = PicoNhl()

while True:
    print("Getting game status...")
    status = nhl.getGameData()

    print(f"Playing: {status.playing}")
    print(f"Team score: {status.teamScore}")

    if status.playing:
        ... do something ...
    else:
        ... do something else ...
```

## API

### PicoNhl

Top-level class for calling various server API methods

#### Constructor Parameters

| Parameter | Default | Description |
|----------|----------|-------------|
| host | NONE PROVIDED | Fully-qualified host that is running the API. User should add the protocol (http/https) and port if necessary, e.g. `https://www.example.com:4444` |
| prefix | `""` | API path prefix.  Appended to the path of all API methods.  Mostly useful if hosting behind a proxy like nginx |

#### Methods

##### getGameData

Calls `/playing` on the server and returns an instance of `GameData` representing the response.

### GameData

Represents the current state of a game being played, if one is being played.  All constructor parameters are accessible by users as properties of the resulting object.

#### Constructor Paramters

| Parameter | Default | Description |
| --------- | ------- | ----------- |
| teamPlaying | NONE PROVIDED | Whether the team the server is hosting the API for is playing or not |
| gameState | NONE PROVIDED | The current state of the game as exposed by the API.  See the server docs for details |
| teamScore | NONE PROVIDED | The current score for the team the API is serving.  Will be None if no game is currently being played |
| opponentScore | NONE PROVIDED | The current score for the other team.  Will be None if no game is currently being played. |


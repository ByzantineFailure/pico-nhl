# PicoNhl Server

The server used to power the PicoNhl library.  Leverages the NHL public API (unclear if it's intentionally public) to provide information on a single team.

Unofficial NHL API documentation: https://github.com/Zmalski/NHL-API-Reference

## Requirements

Requires Node v21 or later (may work with earlier versions, this is just what I tested).  NPM is required for building the server

## Build

```bash
cd /PATH/TO/REPO/server
npm install && npm run build
```

## Run

The port to listen on and team code (see NHL API Reference) can be specified via environment variables.  Defaults are shown below.

```bash
PORT=55555 TEAM=SEA node /PATH/TO/REPO/server/dist/index.js
```

## API

### `GET /playing`

Proxy for ['Get Months Schedule as of Now'](https://github.com/Zmalski/NHL-API-Reference?tab=readme-ov-file#get-month-schedule-as-of-now).

* No query params
* No path params

Returns:
```typescript
{
    // Whether a game is currently in progress or not
    teamPlaying: bool
    // The state of the current or next game in the schedule. 
    // See GameState for more information
    gameState: GameState
    // Scores are null if no game is being played
    score: {
        teamScore: number|null,
        opponentscore: number|null,
    }
}
```

#### GameState

`GameState` is a string enum that represents where the game actually _is_ in its lifecycle.

| Value | Counts as playing | Description |
| ----- | ----------------- | ----------- |
| `"FUT"` | No | A game that is scheduled for the future. |
| `"PRE"` | Yes | A game that has not yet actually begun play, but _is_ in the process of various pre-game rituals such as warm-ups. |
| `"LIVE"` | Yes | A game that is currently being played |
| `"CRIT"` | Yes | A game that is in some critical stage, such as overtime or a shootout.  May not actually exist, never seen in the wild. |
| `"FINAL"`  | No | A game that has finished but has not yet finalized its stats. |
| `"OFF"` | No | A game that has completed and has finalized stats. |
| `"PPD"` | No | A game that has been postponed.  May not exist, never seen in the wild. |
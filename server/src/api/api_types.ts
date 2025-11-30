/////////////////////////////////////////
/// NHL API Types
////////////////////////////////////////

// This file contains types that represent a subset of the fields returned
// by the NHL API.  If you need a new field from a request that isn't here,
// just add it.

/**
 * Enum representing the "state" a game can be in at any given time.
 */
export enum GameState {
    // The game is scheduled for the future, and not in progress
    Future = "FUT",
    // The game is in the "pregame" phase (warmups, etc.)
    Pregame = "PRE",
    // The game is currently being played.  It could be during a period or intermission
    Live = "LIVE",
    // NOTE:  This state may not actually exist
    // The game is in a "Critical" state - e.g. end of overtime or shootout
    Critical = "CRIT",
    // The game has been completed, but its stats have not been finalized or verified
    Complete = "OFF",
    // The game has been completed, and its stats are final
    Final = "FINAL",
    // NOTE:  This state may or nay not exist
    // The game was/is postponed.  
    Postponed = "PPD",
}

/**
 * A team's schedule over a given time period
 */
export interface TeamMonthSchedule {
    // YYYY-MM formatted months for a schedule
    previousMonth: string;
    currentMonth: string;
    nextMonth: string;

    games: ScheduledGame[];
}

/**
 * Information about a scheduled game
 */
export interface ScheduledGame {
    id: number;
    // Number formatted as "YYYYYYYY" e.g. 20252026
    season: number;
    // YYYY-MM-DD
    gameDate: string;
    // Parseable date; YYYY-MM-DDTHH:MM:SSZ
    startTimeUTC: string;

    gameState: GameState;

    awayTeam: GameTeamData;
    homeTeam: GameTeamData;
}

/**
 * Information about a team within a game
 */
export interface GameTeamData {
    id: number;
    abbrev: string;
    score?: number;
}

/**
 * Information pulled from a specific game indicating its state.
 */
export interface GameBoxScore {
  // Parseable date; YYYY-MM-DDTHH:MM:SSZ
  startTimeUTC: string;
  gameState: GameState;
  // Current status of the clock.  Contains period information, etc.
  clock: {
    running: boolean;
    secondsRemaining: number;
    inIntermission: boolean;
  };
}
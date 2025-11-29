
/**
 * Enum representing the "state" a game can be in at any given time.
 */
export enum GameState {
    Future = "FUT",
    Pregame = "PRE",
    Live = "LIVE",
    Critical = "CRIT",
    Complete = "OFF",
    Final = "FINAL",
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
  startTimeUTC: string;
  gameState: string|GameState;
  clock: {
    running: boolean;
    secondsRemaining: number;
    inIntermission: boolean;
  };
}
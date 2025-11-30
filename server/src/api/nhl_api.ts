import {type GameBoxScore, type ScheduledGame, type TeamMonthSchedule} from './api_types.js';

const NHL_API_BASE = 'https://api-web.nhle.com/v1/';
const TEAM_REPLACE_PATTERN = '%%TEAM%%';
const GAME_ID_REPLACE_PATTERN = '%%GAMEID%%';

const MONTH_SCHEDULE_PATTERN = `${NHL_API_BASE}club-schedule/${TEAM_REPLACE_PATTERN}/month/now`;
const GAME_DATA_PATTERN = `${NHL_API_BASE}gamecenter/${GAME_ID_REPLACE_PATTERN}/boxscore`;

/**
 * Static methods that fetch data from the NHL API.  Minimal processing.
 * 
 * Methods prefer to return null rather than throwing an exception in the event
 * the NHL API gives us trouble.
 */
export class NhlApi {
    /**
     * Gets the "BoxScore" of the NHL game identified by @gameId.  Includes clock state, current score,
     * current game state, etc.
     * 
     * Most of this information is present already on the scheduled game.
     * 
     * @param gameId Numeric game id pulled from a scheduled game (see getTeamMonthSchedule)
     * @returns The entire JSON response from the API parsed as a JS object, typed for fields we need
     */
    static async getBoxScore(gameId: number): Promise<GameBoxScore|null> {
        try {
            const response = await fetch(GAME_DATA_PATTERN.replace(GAME_ID_REPLACE_PATTERN, `${gameId}`));
            return await response.json() as GameBoxScore;
        } catch (error) {
            console.error(`Failed to fetch game ${gameId} from NHL API`, error);
            return null;
        }
    }

    /**
     * Gets the team schedule for the current month (now)
     * @param team A 3-letter team code (e.g. SEA, NYR, BOS, TOR)
     * @returns The entire JSON response from the API parsed as a JS object, typed for fields we need.
     */
    static async getTeamMonthSchedule(team: string): Promise<Array<ScheduledGame>|null> {
        const url = MONTH_SCHEDULE_PATTERN.replace(TEAM_REPLACE_PATTERN, team);

        try {
            const response = await fetch(url);
            const body = await response.json() as TeamMonthSchedule;
            return body.games;
        } catch (error) {
            console.error(`Failed to fetch schedule from NHL API`, error);
            return null;
        }
    }
}
import {type GameBoxScore, type ScheduledGame, type TeamMonthSchedule} from './api_types.js';

const NHL_API_BASE = 'https://api-web.nhle.com/v1/';
const TEAM_REPLACE_PATTERN = '%%TEAM%%';
const GAME_ID_REPLACE_PATTERN = '%%GAMEID%%';

const MONTH_SCHEDULE_PATTERN = `${NHL_API_BASE}club-schedule/${TEAM_REPLACE_PATTERN}/month/now`;
const GAME_DATA_PATTERN = `${NHL_API_BASE}gamecenter/${GAME_ID_REPLACE_PATTERN}/boxscore`;

export class NhlApi {
    static async getBoxScore(gameId: number): Promise<GameBoxScore|null> {
        try {
            const response = await fetch(GAME_DATA_PATTERN.replace(GAME_ID_REPLACE_PATTERN, `${gameId}`));
            return await response.json() as GameBoxScore;
        } catch (error) {
            console.error(`Failed to fetch game ${gameId} from NHL API`, error);
            return null;
        }
    }

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
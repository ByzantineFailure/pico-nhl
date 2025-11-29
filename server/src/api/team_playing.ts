import type { IncomingMessage, ServerResponse } from "http";
import { Handler } from "./handler.js";
import {TeamData} from './team_data.js';

/**
 * Handler which provides a response indicating whether a the team is playing or not.
 */
export class TeamPlaying extends Handler {
    private readonly teamData: TeamData;

    constructor(private readonly team: string = 'SEA') {
        super();
        this.teamData = new TeamData(this.team);
    }

    getPath(): string {
        return '/playing';
    }

    async handle(_: IncomingMessage, res: ServerResponse): Promise<void> {
        try {
            const game = await this.teamData.getLiveScheduledGame();
            this.writeSuccess(res, {
                teamPlaying: !!game, 
                gameState: game?.gameState,
            });
        } catch {
            this.writeError(res, {
                code: 'FETCH_ERROR',
                message: 'Error fetching current team schedule',
            });
        }
    }
}
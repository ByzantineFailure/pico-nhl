import type { IncomingMessage, ServerResponse } from "http";
import { Handler } from "./handler.js";
import {TeamData} from './team_data.js';
import type { GameTeamData, ScheduledGame } from "./api_types.js";

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
                score: getScore(this.team, game)
            });
        } catch {
            this.writeError(res, {
                code: 'FETCH_ERROR',
                message: 'Error fetching current team schedule',
            });
        }
    }
}

function getScore(team: string, game: ScheduledGame|null): {
    teamScore: number|null;
    opponentScore: number|null;
} {
    if (!game) {
        return {
            teamScore: null,
            opponentScore: null,
        };
    }

    const teamIsHomeTeam = game.homeTeam.abbrev === team;

    const teamData = teamIsHomeTeam ? game.homeTeam : game.awayTeam;
    const opponentData = teamIsHomeTeam ? game.awayTeam : game.homeTeam;

    return {
        teamScore: getScoreFromTeamData(teamData),
        opponentScore: getScoreFromTeamData(opponentData)
    };
}

function getScoreFromTeamData(teamData: GameTeamData): number|null {
    if (!teamData.score && teamData.score !== 0) {
        return null;
    } else {
        return teamData.score;
    }
}
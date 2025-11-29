import {GameState, type ScheduledGame, } from './api_types.js';

import { NhlApi } from './nhl_api.js';

export class TeamData {
    constructor(private readonly team: string = 'SEA') {}

    async getLiveScheduledGame(): Promise<ScheduledGame|null> {
        const schedule = await this.fetchSchedule();

        return schedule?.find((game) => {
            return isGameBeingPlayed(game);
        }) || null;
    }

    async fetchSchedule(): Promise<Array<ScheduledGame>|null> {
        const schedule =  await NhlApi.getTeamMonthSchedule(this.team);
        
        // Sort them into chronological order
        return schedule?.sort((a: ScheduledGame, b: ScheduledGame) => {
            return new Date(a.startTimeUTC).getTime() - new Date(b.startTimeUTC).getTime();
        }) || null;
    }
}

function isGameBeingPlayed(game: ScheduledGame) {
    switch(game.gameState) {
        case GameState.Pregame:
        case GameState.Live:
        case GameState.Critical:
            return true;
        case GameState.Future:
        case GameState.Final:
        case GameState.Complete:
        case GameState.Postponed:
        default:
            return false;
    }
}

/*
function isGameInThePast(game: ScheduledGame) {
    switch(game.gameState) {
        case GameState.Future:
        case GameState.Pregame:
        case GameState.Live:
        case GameState.Critical:
        case GameState.Postponed:
            return false;
        case GameState.Final:
        case GameState.Complete:
        default:
            return true;
    }
}


function isGameInTheFuture(game: ScheduledGame) {
    switch(game.gameState) {
        case GameState.Future:
        case GameState.Postponed:
            return true;
        case GameState.Pregame:
        case GameState.Live:
        case GameState.Critical:
        case GameState.Final:
        case GameState.Complete:
        default:
            return false;
    }
}
    */
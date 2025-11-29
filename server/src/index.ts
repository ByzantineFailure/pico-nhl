import http, {IncomingMessage, ServerResponse} from 'http';

import { TeamPlaying, Handler } from './api/index.js';

const PORT = process.env['PORT'] || 55555;
const TEAM = process.env['TEAM'] || 'SEA';
//const TEAM = 'DET';

const handlers: Handler[] = [
    new TeamPlaying(TEAM),
];

const server = http.createServer((req: IncomingMessage, res: ServerResponse) => {
    console.log(`Got request with URL ${req.url}`);

    if (!req.url) {
        Handler.writeNotfound(res);
        return;
    }

    const url = new URL(`http://${req.headers.host ?? 'localhost'}${req.url}`);
    const path = url.pathname.trim();

    for (const handler of handlers) {
        if (handler.getPath() === path) {
            handler.handle(req, res);
            return;
        }
    }

    Handler.writeNotfound(res);
});

server.listen(PORT);

console.log(`Listening on ${PORT}`);
import http, {IncomingMessage, ServerResponse} from 'http';

import { TeamPlaying, Handler } from './handler/index.js';

const PORT = process.env['PORT'] || 55555;
const TEAM = process.env['TEAM'] || 'SEA';
//const TEAM = 'DET';

const handlers: Handler[] = [
    new TeamPlaying(TEAM),
];

const server = http.createServer((req: IncomingMessage, res: ServerResponse) => {
    console.log(`Got request with URL ${req.url}`);

    if (!req.url) {
        Handler.writeNotFound(res);
        return;
    }

    const url = new URL(`http://${req.headers.host ?? 'localhost'}${req.url}`);

    for (const handler of handlers) {
        if (handler.shouldHandle(req, url)) {
            handler.handle(req, res, url);
            return;
        }
    }

    Handler.writeNotFound(res);
});

server.listen(PORT);

console.log(`Listening on ${PORT}`);
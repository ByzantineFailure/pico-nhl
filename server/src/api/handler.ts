import { IncomingMessage, ServerResponse } from "http"

export interface ErrorData {
    code?: string;
    message?: string;
}

/** Interface for handlers */
export abstract class Handler {
    abstract getPath(): string;
    abstract handle(req: IncomingMessage, res: ServerResponse): Promise<void>

    writeSuccess(res: ServerResponse, data: {}) {
        res.statusCode = 200;
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify(data));
    }

    writeBadRequest(res: ServerResponse, data: ErrorData) {
        res.statusCode = 400;
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify(data));
    }

    writeError(res: ServerResponse, data: ErrorData) {
        res.statusCode = 500;
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify(data));
    }

    // Used within main
    static writeNotFound(res: ServerResponse) {
        res.statusCode = 404;
        res.end();
    }
}
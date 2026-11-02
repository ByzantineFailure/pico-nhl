# Test fixtures

Real, unmodified responses from the NHL API's
`https://api-web.nhle.com/v1/club-schedule/{TEAM}/{week|month}/{date}` endpoint:
the dated URL that pico-nhl's `.../week/now` and `.../month/now` requests are
redirected to. They were captured on 2026-10-31 while polling live games, saved
byte-for-byte (after gzip decoding) at the moment each game's state changed.

| Fixture | Game | Team (side) | Window | Game state | Score (away-home) | Captured (UTC) |
| --- | --- | --- | --- | --- | --- | --- |
| `pre_pit_week.json` | PIT @ MTL, 2026020223 | PIT (away) | week | `PRE` | — | 2026-10-31 22:46:32 |
| `pre_mtl_month.json` | PIT @ MTL, 2026020223 | MTL (home) | month | `PRE` | — | 2026-10-31 22:46:32 |
| `live_0-0_mtl_week.json` | PIT @ MTL, 2026020223 | MTL (home) | week | `LIVE`, 1st | 0-0 | 2026-10-31 23:13:21 |
| `live_2-3_pit_week.json` | PIT @ MTL, 2026020223 | PIT (away) | week | `LIVE`, 1st | 2-3 | 2026-10-31 23:35:01 |
| `live_2-2_overturned_pit_week.json` | PIT @ MTL, 2026020223 | PIT (away) | week | `LIVE`, 1st | 2-2 (MTL goal taken back) | 2026-10-31 23:37:41 |
| `live_intermission_mtl_month.json` | PIT @ MTL, 2026020223 | MTL (home) | month | `LIVE`, 1st intermission | 2-2 | 2026-10-31 23:57:01 |
| `crit_lak_week.json` | BUF @ LAK, 2026020221 | LAK (home) | week | `CRIT`, 3rd | 3-2 | 2026-10-31 22:36:21 |
| `over_buf_month.json` | BUF @ LAK, 2026020221 | BUF (away) | month | `OVER`, 3rd | 3-2 | 2026-10-31 22:46:41 |
| `final_lak_week.json` | BUF @ LAK, 2026020221 | LAK (home) | week | `FINAL` | 3-2 | 2026-10-31 22:47:01 |
| `off_buf_week.json` | BUF @ LAK, 2026020221 | BUF (away) | week | `OFF` | 3-2 | 2026-10-31 23:18:41 |

Every window also contains other games for the same team: `FUT` games (no
`score` field) after the game of interest, and `OFF` games before it in the
month windows.

Week windows start on the requested date and run 7 days; month windows cover
the calendar month (`2026-10`), so the month fixtures contain no later games.

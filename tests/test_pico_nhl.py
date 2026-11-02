"""Unit tests for pico_nhl, run under CPython against real NHL API responses.

The fixtures in tests/fixtures/ are real `club-schedule` responses captured on
2026-10-31 (see tests/fixtures/README.md). MicroPython's `urequests` and
`utime` are replaced with stand-ins from micropython_stubs.

Run from the repository root:

    python3 -m unittest discover -s tests -v
"""

import contextlib
import io
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import micropython_stubs as stubs  # noqa: E402

stubs.install()

import pico_nhl  # noqa: E402
from pico_nhl import (  # noqa: E402
    GAME_STATE_CRITICAL,
    GAME_STATE_FINAL,
    GAME_STATE_FUTURE,
    GAME_STATE_LIVE,
    GAME_STATE_OFF,
    GAME_STATE_POSTPONED,
    GAME_STATE_PREGAME,
    NO_TIMESTAMP,
    SCHEDULE_WINDOW_MONTH,
    SCHEDULE_WINDOW_WEEK,
    GameData,
    NhlApi,
    PicoNhl,
    isoUTCTimestampToEpochSeconds,
)

API = "https://api-web.nhle.com/v1/"

# Scheduled start of PIT @ MTL (2026020223), and BUF @ LAK (2026020221).
PIT_MTL_START = stubs.epoch("2026-10-31T23:00:00Z")
BUF_LAK_START = stubs.epoch("2026-10-31T20:00:00Z")


class StubbedTestCase(unittest.TestCase):
    def setUp(self):
        stubs.reset()


class TimestampParsingTests(StubbedTestCase):
    def test_parses_api_start_time(self):
        self.assertEqual(isoUTCTimestampToEpochSeconds("2026-10-31T23:00:00Z"), PIT_MTL_START)

    def test_ignores_fractional_seconds(self):
        self.assertEqual(isoUTCTimestampToEpochSeconds("2026-10-31T23:00:00.123Z"), PIT_MTL_START)

    def test_none_is_no_timestamp(self):
        self.assertEqual(isoUTCTimestampToEpochSeconds(None), NO_TIMESTAMP)

    def test_malformed_is_no_timestamp(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(isoUTCTimestampToEpochSeconds("TBD"), NO_TIMESTAMP)
            self.assertEqual(isoUTCTimestampToEpochSeconds("2026-10-31"), NO_TIMESTAMP)


class GameDataTests(unittest.TestCase):
    def test_playing_states(self):
        for state in (GAME_STATE_PREGAME, GAME_STATE_LIVE, GAME_STATE_CRITICAL):
            with self.subTest(state=state):
                self.assertTrue(GameData(state, None, None, None).playing)

    def test_not_playing_states(self):
        # "OVER" is an undocumented API value seen between CRIT and FINAL; it has no
        # constant and is treated as not playing.
        for state in (GAME_STATE_FUTURE, GAME_STATE_FINAL, GAME_STATE_OFF, GAME_STATE_POSTPONED, "OVER"):
            with self.subTest(state=state):
                self.assertFalse(GameData(state, None, None, None).playing)

    def test_empty_data(self):
        empty = GameData.emptyData()
        self.assertEqual(empty.gameState, GAME_STATE_FUTURE)
        self.assertFalse(empty.playing)
        self.assertIsNone(empty.teamScore)
        self.assertIsNone(empty.opponentScore)
        self.assertIsNone(empty.startTimeEpochSeconds)
        self.assertEqual(empty.timeSortKey, NO_TIMESTAMP)


class NhlApiTests(StubbedTestCase):
    def test_month_schedule_requests_now_by_default(self):
        stubs.serve_fixture("pre_mtl_month.json")
        schedule = NhlApi.getTeamMonthSchedule("MTL")
        self.assertEqual(stubs.requested_urls(), [API + "club-schedule/MTL/month/now"])
        self.assertEqual(schedule["currentMonth"], "2026-10")

    def test_week_schedule_requests_now_by_default(self):
        stubs.serve_fixture("pre_pit_week.json")
        schedule = NhlApi.getTeamWeekSchedule("PIT")
        self.assertEqual(stubs.requested_urls(), [API + "club-schedule/PIT/week/now"])
        self.assertEqual(len(schedule["games"]), 3)

    def test_explicit_time_spec(self):
        stubs.serve_fixture("pre_mtl_month.json")
        NhlApi.getTeamMonthSchedule("MTL", "2026-10")
        stubs.serve_fixture("pre_pit_week.json")
        NhlApi.getTeamWeekSchedule("PIT", "2026-10-31")
        self.assertEqual(stubs.requested_urls(), [
            API + "club-schedule/MTL/month/2026-10",
            API + "club-schedule/PIT/week/2026-10-31",
        ])

    def test_non_200_returns_none(self):
        for status in (404, 500, 503):
            with self.subTest(status=status):
                stubs.serve(status, b"<html>error</html>")
                self.assertIsNone(NhlApi.getTeamMonthSchedule("SEA"))
                self.assertIsNone(NhlApi.getTeamWeekSchedule("SEA"))


class ActiveGameTests(StubbedTestCase):
    """getActiveGameData() for each game state the API reported during real games."""

    def active(self, fixture, team, window):
        stubs.serve_fixture(fixture)
        return PicoNhl(team=team, scheduleWindow=window).getActiveGameData()

    def assertNotPlaying(self, game):
        self.assertFalse(game.playing)
        self.assertEqual(game.gameState, GAME_STATE_FUTURE)
        self.assertIsNone(game.startTimeEpochSeconds)
        self.assertIsNone(game.teamScore)
        self.assertIsNone(game.opponentScore)

    def test_pregame_counts_as_playing_without_scores(self):
        # The API omits `score` entirely during PRE.
        for fixture, team, window in (
            ("pre_pit_week.json", "PIT", SCHEDULE_WINDOW_WEEK),    # PIT is the away team
            ("pre_mtl_month.json", "MTL", SCHEDULE_WINDOW_MONTH),  # MTL is the home team
        ):
            with self.subTest(fixture=fixture):
                game = self.active(fixture, team, window)
                self.assertTrue(game.playing)
                self.assertEqual(game.gameState, GAME_STATE_PREGAME)
                self.assertEqual(game.startTimeEpochSeconds, PIT_MTL_START)
                self.assertIsNone(game.teamScore)
                self.assertIsNone(game.opponentScore)

    def test_requests_the_configured_window(self):
        self.active("pre_pit_week.json", "PIT", SCHEDULE_WINDOW_WEEK)
        self.active("pre_mtl_month.json", "MTL", SCHEDULE_WINDOW_MONTH)
        self.assertEqual(stubs.requested_urls(), [
            API + "club-schedule/PIT/week/now",
            API + "club-schedule/MTL/month/now",
        ])

    def test_live_scoreless_reports_zero_not_none(self):
        game = self.active("live_0-0_mtl_week.json", "MTL", SCHEDULE_WINDOW_WEEK)
        self.assertTrue(game.playing)
        self.assertEqual(game.gameState, GAME_STATE_LIVE)
        self.assertEqual(game.teamScore, 0)
        self.assertEqual(game.opponentScore, 0)

    def test_live_scores_from_away_team_perspective(self):
        game = self.active("live_2-3_pit_week.json", "PIT", SCHEDULE_WINDOW_WEEK)
        self.assertEqual((game.teamScore, game.opponentScore), (2, 3))

    def test_score_can_decrease_after_overturned_goal(self):
        # MTL's third goal was taken back between these two real responses.
        before = self.active("live_2-3_pit_week.json", "PIT", SCHEDULE_WINDOW_WEEK)
        after = self.active("live_2-2_overturned_pit_week.json", "PIT", SCHEDULE_WINDOW_WEEK)
        self.assertEqual(before.opponentScore, 3)
        self.assertEqual(after.opponentScore, 2)
        self.assertTrue(after.playing)

    def test_intermission_is_still_live(self):
        game = self.active("live_intermission_mtl_month.json", "MTL", SCHEDULE_WINDOW_MONTH)
        self.assertTrue(game.playing)
        self.assertEqual(game.gameState, GAME_STATE_LIVE)
        self.assertEqual((game.teamScore, game.opponentScore), (2, 2))

    def test_critical_from_home_team_perspective(self):
        game = self.active("crit_lak_week.json", "LAK", SCHEDULE_WINDOW_WEEK)
        self.assertTrue(game.playing)
        self.assertEqual(game.gameState, GAME_STATE_CRITICAL)
        self.assertEqual(game.startTimeEpochSeconds, BUF_LAK_START)
        self.assertEqual((game.teamScore, game.opponentScore), (2, 3))

    def test_over_is_not_playing(self):
        self.assertNotPlaying(self.active("over_buf_month.json", "BUF", SCHEDULE_WINDOW_MONTH))

    def test_final_and_off_are_not_playing(self):
        self.assertNotPlaying(self.active("final_lak_week.json", "LAK", SCHEDULE_WINDOW_WEEK))
        self.assertNotPlaying(self.active("off_buf_week.json", "BUF", SCHEDULE_WINDOW_WEEK))

    def test_api_error_is_not_playing(self):
        stubs.serve(503, b"")
        self.assertNotPlaying(PicoNhl(team="SEA").getActiveGameData())

    def test_unknown_schedule_window_raises(self):
        with self.assertRaises(Exception):
            PicoNhl(team="SEA", scheduleWindow=99).getActiveGameData()


class NextGameTests(StubbedTestCase):
    """getNextGameData() with utime.time() set to when each fixture was captured."""

    def next_game(self, fixture, team, window, now):
        stubs.serve_fixture(fixture)
        stubs.set_time(now)
        return PicoNhl(team=team, scheduleWindow=window).getNextGameData()

    def test_pregame_game_is_next_until_scheduled_start(self):
        # PRE began well before the scheduled start, so the game in progress is still "next".
        game = self.next_game("pre_pit_week.json", "PIT", SCHEDULE_WINDOW_WEEK, "2026-10-31T22:46:32Z")
        self.assertEqual(game.gameState, GAME_STATE_PREGAME)
        self.assertEqual(game.startTimeEpochSeconds, PIT_MTL_START)

    def test_next_future_game_after_final(self):
        game = self.next_game("off_buf_week.json", "BUF", SCHEDULE_WINDOW_WEEK, "2026-10-31T23:18:41Z")
        self.assertEqual(game.gameState, GAME_STATE_FUTURE)
        self.assertEqual(game.startTimeEpochSeconds, stubs.epoch("2026-11-05T00:30:00Z"))
        self.assertIsNone(game.teamScore)
        self.assertIsNone(game.opponentScore)
        self.assertFalse(game.playing)

    def test_skips_game_already_in_progress(self):
        game = self.next_game("crit_lak_week.json", "LAK", SCHEDULE_WINDOW_WEEK, "2026-10-31T22:36:21Z")
        self.assertEqual(game.startTimeEpochSeconds, stubs.epoch("2026-11-05T03:00:00Z"))

    def test_no_later_game_in_month_window(self):
        # MTL's October schedule ends with the game in progress.
        game = self.next_game("live_intermission_mtl_month.json", "MTL", SCHEDULE_WINDOW_MONTH, "2026-10-31T23:57:01Z")
        self.assertIsNone(game.startTimeEpochSeconds)
        self.assertEqual(game.gameState, GAME_STATE_FUTURE)

    def test_sorts_games_by_start_time(self):
        doc = json.loads(stubs.load_fixture("off_buf_week.json"))
        doc["games"].reverse()
        stubs.serve(200, json.dumps(doc).encode())
        stubs.set_time("2026-10-31T23:18:41Z")
        game = PicoNhl(team="BUF", scheduleWindow=SCHEDULE_WINDOW_WEEK).getNextGameData()
        self.assertEqual(game.startTimeEpochSeconds, stubs.epoch("2026-11-05T00:30:00Z"))


if __name__ == "__main__":
    unittest.main()

import urequests as requests
import utime as time

NO_TIMESTAMP = -1

# Values representing possible game states
GAME_STATE_FUTURE = "FUT"
GAME_STATE_PREGAME = "PRE"
GAME_STATE_LIVE = "LIVE"
GAME_STATE_CRITICAL = "CRIT"
GAME_STATE_FINAL = "FINAL"
GAME_STATE_OFF = "OFF"
GAME_STATE_POSTPONED = "PPD"

# Values representing schedule windows to query.  Useful if you want to use less memory on response
# sizes.
SCHEDULE_WINDOW_MONTH = 0
SCHEDULE_WINDOW_WEEK = 1


class GameData:
    """Class representing game data returned by the PicoNhl class

    This is a strict subset of data present within a team's schedule data/response.
    """

    def __init__(
        self,
        gameState: str,
        startTimeEpochSeconds: int | None,
        teamScore: int | None,
        opponentScore: int | None,
    ):
        self.gameState = gameState
        self.teamScore = teamScore
        self.opponentScore = opponentScore
        self.startTimeEpochSeconds = startTimeEpochSeconds

    def __str__(self):
        return (
            f"Playing: {self.playing}; gameState: {self.gameState}; teamScore: {self.teamScore}; "
            + f"opponentScore: {self.opponentScore}; startTimeEpochSeconds: {self.startTimeEpochSeconds}"
        )

    @property
    def playing(self) -> bool:
        """If the game is in progress or not"""
        return _gameIsBeingPlayed(self.gameState)

    @property
    def timeSortKey(self) -> int:
        """Usable key for sorting games in chronological order"""
        return (
            self.startTimeEpochSeconds
            if self.startTimeEpochSeconds != None
            else NO_TIMESTAMP
        )

    @staticmethod
    def emptyData():
        return GameData(
            startTimeEpochSeconds=None,
            gameState=GAME_STATE_FUTURE,
            teamScore=None,
            opponentScore=None,
        )


class PicoNhl:
    """Class that abstracts away dealing with the NHL API

    Provides methods for retrieving game data and constructing Python-native objects that
    should be easier to work with.
    """

    def __init__(self, team: str = "SEA", scheduleWindow: int = SCHEDULE_WINDOW_MONTH):
        self.team = team
        self.scheduleWindow = scheduleWindow
        self.teamData = TeamData(team=self.team, scheduleWindow=scheduleWindow)

    def getActiveGameData(self) -> GameData:
        """Gets the currently-active game, if one exists.

        Returns GameData.emptyData() if none is being played.
        """
        activeGame = self.teamData.fetchActiveGame()

        if activeGame == None:
            return GameData.emptyData()

        return activeGame

    def getNextGameData(self) -> GameData:
        """Gets the next upcoming game in the team's schedule window, if one exists.

        Returns GameData.emptyData() if there is no upcoming game in the window.
        """
        nextGame = self.teamData.fetchNextScheduledGame()

        if nextGame == None:
            return GameData.emptyData()

        return nextGame


def _gameIsBeingPlayed(gameState: str | None) -> bool:
    """Determines if the a game state represents an active game"""
    return (
        gameState == GAME_STATE_PREGAME
        or gameState == GAME_STATE_LIVE
        or gameState == GAME_STATE_CRITICAL
    )


class TeamData:
    """Class for pulling team-specific data from the NHL API

    Largely responsible for converting raw API results to GameData
    """

    def __init__(self, team: str, scheduleWindow: int):
        self.team = team
        self.scheduleWindow = scheduleWindow

    # We assume there is not more than one active game for a team (for obvious reasons)
    def fetchActiveGame(self) -> GameData | None:
        """Pulls the team's schedule for the current month and gets the first active game"""
        schedule = self._fetchSchedule()

        if schedule == None:
            return None

        return next(
            (game for game in schedule if _gameIsBeingPlayed(game.gameState)), None
        )

    def fetchNextScheduledGame(self) -> GameData | None:
        """Pulls the team's schedule and gets the next upcoming game

        Returns None if the current schedule window doesn't contain a game in the future.
        """
        schedule = self._fetchSchedule()

        if schedule == None:
            return None

        now = time.time()

        schedule.sort(key=lambda game: game.timeSortKey)

        return next((game for game in schedule if game.timeSortKey > now), None)

    def _fetchSchedule(self) -> list[GameData] | None:
        """Pulls the team's schedule"""
        if self.scheduleWindow == SCHEDULE_WINDOW_MONTH:
            schedule = NhlApi.getTeamMonthSchedule(self.team)
        elif self.scheduleWindow == SCHEDULE_WINDOW_WEEK:
            schedule = NhlApi.getTeamWeekSchedule(self.team)
        else:
            raise Exception(
                f"Unrecognized schedule window value: {self.scheduleWindow}"
            )

        if schedule == None:
            return None

        return [self._gameDictToGameData(game) for game in schedule["games"]]

    def _gameDictToGameData(self, gameData: dict) -> GameData:
        startTimeEpochSeconds = isoUTCTimestampToEpochSeconds(gameData["startTimeUTC"])

        if startTimeEpochSeconds == NO_TIMESTAMP:
            startTimeEpochSeconds = None

        teamIsHomeTeam = gameData["homeTeam"]["abbrev"] == self.team
        teamData = gameData["homeTeam"] if teamIsHomeTeam else gameData["awayTeam"]
        opponentData = gameData["awayTeam"] if teamIsHomeTeam else gameData["homeTeam"]

        teamScore = teamData["score"] if "score" in teamData else None
        opponentScore = opponentData["score"] if "score" in opponentData else None

        return GameData(
            startTimeEpochSeconds=startTimeEpochSeconds,
            gameState=gameData["gameState"],
            teamScore=teamScore,
            opponentScore=opponentScore,
        )


################################
### NHL API methods
################################

# API Protocol+Host+path prefix
NHL_API_BASE = "https://api-web.nhle.com/v1/"

# Well-defined pattern to replace with a team abbreviation (e.g. "SEA")
TEAM_REPLACE_PATTERN = "%%TEAM%%"
# Well-defined pattern to replace with a time specifier
TIME_REPLACE_PATTERN = "%%TIME_SPEC%%"
# Fully-qualified url for fetching a team's schedule for the current month
MONTH_SCHEDULE_PATTERN = (
    f"{NHL_API_BASE}club-schedule/{TEAM_REPLACE_PATTERN}/month/{TIME_REPLACE_PATTERN}"
)
# Fully-qualified url for fetching a team's schedule for the current week
WEEK_SCHEDULE_PATTERN = (
    f"{NHL_API_BASE}club-schedule/{TEAM_REPLACE_PATTERN}/week/{TIME_REPLACE_PATTERN}"
)


class NhlApi:
    """Basic API class that directly returns data from the NHL API with minimal modification"""

    @staticmethod
    def getTeamMonthSchedule(team: str, month: str = "now") -> dict | None:
        """Calls /club-schedule/TEAM/month/MONTH for a given team

        Pass "now" (default value) as the time to get it for the current time/date.

        https://github.com/Zmalski/NHL-API-Reference?tab=readme-ov-file#get-month-schedule
        """
        url = MONTH_SCHEDULE_PATTERN.replace(TEAM_REPLACE_PATTERN, team).replace(
            TIME_REPLACE_PATTERN, month
        )

        response = requests.get(url)

        if response.status_code != 200:
            return None

        return response.json()

    @staticmethod
    def getTeamWeekSchedule(team: str, week: str = "now") -> dict | None:
        """Calls /club-schedule/TEAM/week/WEEK for a given team

        Pass "now" (default value) as the time to get it for the current time/date.

        https://github.com/Zmalski/NHL-API-Reference?tab=readme-ov-file#get-week-schedule
        """
        url = WEEK_SCHEDULE_PATTERN.replace(TEAM_REPLACE_PATTERN, team).replace(
            TIME_REPLACE_PATTERN, week
        )

        response = requests.get(url)

        if response.status_code != 200:
            return None

        return response.json()


# Micropython doesn't contain a way to parse an ISO-8601 timestamp natively.
# Asked gemini for this because I can't be arsed to write it myself, then made
# some minor tweaks to error state handling.
def isoUTCTimestampToEpochSeconds(timestamp: str | None) -> int:
    """Converts a UTC timestamp to epoch seconds

    If there's a parsing error or we are passed None, return NO_TIMESTAMP (-1)
    """
    if timestamp == None:
        return NO_TIMESTAMP

    try:
        # 1. Parse Date and Time components
        date_part, time_part = timestamp.split("T")

        # 2. Extract Year, Month, Day
        year, month, day = map(int, date_part.split("-"))

        # 3. Extract Hour, Minute, Second
        # Handle cases where the time includes a fractional second or Z/offset
        if "." in time_part:
            time_part = time_part.split(".")[0]
        if "Z" in time_part:
            time_part = time_part.split("Z")[0]

        hour, minute, second = map(int, time_part.split(":"))

        # 4. Create the time tuple required by time.mktime()
        # The tuple format is: (year, month, mday, hour, minute, second, weekday, yearday)
        # We use arbitrary values (0) for weekday and yearday since mktime calculates them.
        time_tuple = (year, month, day, hour, minute, second, 0, 0)

        # 5. Convert the time tuple to seconds since the epoch
        seconds_since_epoch = time.mktime(time_tuple)

        return seconds_since_epoch

    except ValueError as e:
        print(f"Error parsing timestamp: {e}")
        return NO_TIMESTAMP

import urequests as requests
import pico_wifi

class GameData:
    def __init__(self,
             playing: bool,
             gameState: str,
             teamScore: int|None,
             opponentScore: int|None):
        self.playing = playing
        self.gameState = gameState
        self.teamScore = teamScore
        self.opponentScore = opponentScore

    def __str__(self):
        return f'Playing: {self.playing}; gameState: {self.gameState}; teamScore: {self.teamScore}; opponentScore: {self.opponentScore}'
    

PLAYING_PATH = '/playing'

class PicoNhl:
    def __init__(self,
               host: str,
               prefix: str = ""):
        if host == None or host == "":
            raise Exception("Must provide a host!")

        self.host = host
        self.prefix = prefix
        self._wifi = None
        return

    def getGameData(self) -> GameData:
        url = self.host + self.prefix + PLAYING_PATH

        response = requests.get(url)

        if response.status_code != 200:
            raise Exception("Got non-200 response code from server: " + response.status_code)

        data = response.json()

        return GameData(
            playing=data['teamPlaying'],
            gameState=data['gameState'],
            teamScore=data['score']['teamScore'],
            opponentScore=data['score']['opponentScore'])

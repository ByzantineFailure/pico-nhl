import urequests as requests
import pico_wifi

class GameData:
    def __init__(self,
             playing: bool,
             gameState: str,
             teamScore: int,
             opponentScore: int):
        self.playing = playing
        self.gameState = gameState
        self.teamScore = teamScore
        self.opponentScore = opponentScore
    

PLAYING_PATH = '/playing'

class PicoNhl:
    def __init__(self,
               host: str,
               prefix: str):
        self.host = host
        self.prefix = prefix
        self._wifi = None
        return

    def init(self, credentials: pico_wifi.WifiCredentials|None=None):
        self._wifi = pico_wifi.PicoWifi()
        self._wifi.credentials = credentials
        self._wifi.init()

    def getGameData(self) -> GameData:
        if not self.wifiActive:
            raise Exception("Attempting to get game data before wifi is active.  Call init() first")

        url = self.host + self.prefix + PLAYING_PATH

        response = requests.get(url)

        if response.status_code != 200:
            raise Exception("Got non-200 response code from server: " + response.headers)

        data = response.json()

        return GameData(
            playing=data['teamPlaying'],
            gameState=data['gameState'],
            teamScore=data['score']['teamScore'],
            opponentScore=data['score']['opponentScore'])
        
    @property
    def wifiActive(self) -> bool:
        if self._wifi == None:
            return False

        return self._wifi.connectedToWifi

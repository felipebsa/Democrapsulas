from typing import Literal

HALLS = ("asiatico", "medieval", "cyberpunk", "espaco", "estacoes")

Hall = Literal["asiatico", "medieval", "cyberpunk", "espaco", "estacoes"]

HALL_NAMES = {
    "asiatico": "Salão Asiático",
    "medieval": "Salão Medieval",
    "cyberpunk": "Salão Cyberpunk",
    "espaco": "Salão Espaço",
    "estacoes": "Salão das Estações",
}

#seasons hall: the scenery changes every SEASON_SECONDS, the same for everyone
SEASONS = ("primavera", "verao", "outono", "inverno")
SEASON_SECONDS = 120

TITLE_MAX_LENGTH = 80
CONTENT_MAX_LENGTH = 1000

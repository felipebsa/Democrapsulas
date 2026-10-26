from typing import Literal, get_args

Hall = Literal["asiatico", "medieval", "cyberpunk", "espaco", "estacoes"]
HALLS = get_args(Hall)

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

#column sizes, shared by models and schemas
HALL_MAX_LENGTH = 20
USERNAME_MAX_LENGTH = 20
TITLE_MAX_LENGTH = 80
CONTENT_MAX_LENGTH = 1000

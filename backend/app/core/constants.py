from typing import Literal, get_args

Hall = Literal["asiatico", "medieval", "cyberpunk", "espaco", "estacoes"]
HALLS = get_args(Hall)

#seasons hall: the scenery changes every SEASON_SECONDS, the same for everyone
SEASONS = ("primavera", "verao", "outono", "inverno")
SEASON_SECONDS = 120

#lantern skins, numbered 1..LANTERN_COUNT like the images in frontend/img/lanterns
LANTERN_COUNT = 17

#column sizes, shared by models and schemas
HALL_MAX_LENGTH = 20
USERNAME_MAX_LENGTH = 20
TITLE_MAX_LENGTH = 80
CONTENT_MAX_LENGTH = 1000

from enum import Enum

class Color(Enum):
    BLUE="\033[38;5;20m"
    RED="\033[38;5;9m"
    GREEN="\033[38;5;82m"
    CYAN="\033[38;5;14m"
    ORANGE="\033[38;5;202m"
    RESET="\033[0m"

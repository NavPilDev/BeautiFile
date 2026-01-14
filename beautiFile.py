import sys
import subprocess
from PySide6.QtWidgets import (
    QApplication, QWidget, QFrame,
    QToolButton, QGridLayout
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSize

APPS = [
    ("Valorant", "icons/valorant.png", r"C:\Riot Games\Riot Client\RiotClientServices.exe"),
    ("Steam", "icons/steam.png", r"C:\Program Files (x86)\Steam\Steam.exe"),
    ("Epic Games", "icons/epic.png", r"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win64\EpicGamesLauncher.exe"),
    ("Marvel Rivals", "icons/marvel.png", r"C:\Games\MarvelRivals.exe"),
]



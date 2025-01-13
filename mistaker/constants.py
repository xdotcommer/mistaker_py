from enum import Enum, auto
from typing import Dict


class ErrorType(Enum):
    # Number errors
    ONE_DIGIT_UP = auto()
    ONE_DIGIT_DOWN = auto()
    NUMERIC_KEY_PAD = auto()
    DIGIT_SHIFT = auto()
    MISREAD = auto()
    KEY_SWAP = auto()

    # Date specific errors
    MONTH_DAY_SWAP = auto()
    ONE_DECADE_DOWN = auto()
    Y2K = auto()

    # Word/Name errors
    DROPPED_LETTER = auto()
    DOUBLE_LETTER = auto()
    MISREAD_LETTER = auto()
    MISTYPED_LETTER = auto()
    EXTRA_LETTER = auto()
    MISHEARD_LETTER = auto()


# Mapping dictionaries for various error types
MISREAD_NUMBERS: Dict[str, str] = {
    "0": "8",
    "1": "7",
    "2": "5",
    "3": "8",
    "4": "9",
    "5": "6",
    "6": "5",
    "7": "1",
    "8": "3",
    "9": "4",
}

MISREAD_LETTERS: Dict[str, str] = {
    "A": "E",
    "B": "D",
    "C": "E",
    "D": "B",
    "E": "A",
    "F": "F",
    "G": "C",
    "H": "M",
    "I": "L",
    "J": "Q",
    "K": "X",
    "L": "I",
    "M": "H",
    "N": "N",
    "O": "A",
    "P": "Q",
    "Q": "G",
    "R": "V",
    "S": "Z",
    "T": "I",
    "U": "V",
    "V": "U",
    "W": "W",
    "X": "K",
    "Y": "T",
    "Z": "S",
    " ": " ",
}

MISTYPED_LETTERS: Dict[str, str] = {
    "A": "S",
    "B": "G",
    "C": "V",
    "D": "F",
    "E": "A",
    "F": "G",
    "G": "F",
    "H": "J",
    "I": "U",
    "J": "H",
    "K": "L",
    "L": "P",
    "M": "N",
    "N": "N",
    "O": "H",
    "P": "O",
    "Q": "W",
    "R": "E",
    "S": "D",
    "T": "R",
    "U": "Y",
    "V": "C",
    "W": "Q",
    "X": "C",
    "Y": "U",
    "Z": "X",
    " ": " ",
}

TEN_KEYS: Dict[str, str] = {
    "0": "1",
    "1": "4",
    "2": "5",
    "3": "6",
    "4": "1",
    "5": "2",
    "6": "3",
    "7": "4",
    "8": "5",
    "9": "6",
}

MISHEARD_LETTERS: Dict[str, str] = {
    "A": "AE",
    "E": "EE",
    "I": "E",
    "O": "OU",
    "U": "O",
    "Y": "JA",
    "B": "P",
    "C": "K",
    "D": "T",
    "F": "VA",
    "G": "CH",
    "H": "GH",
    "J": "Y",
    "K": "C",
    "L": "LL",
    "M": "MM",
    "N": "MN",
    "P": "B",
    "Q": "CU",
    "R": "RR",
    "S": "SS",
    "T": "D",
    "V": "F",
    "W": "WH",
    "X": "CKS",
    "Z": "D",
    " ": " ",
}

EXTRA_LETTERS: Dict[str, str] = {
    "A": "E",
    "B": "S",
    "C": "E",
    "D": "T",
    "E": "S",
    "F": "E",
    "G": "UE",
    "H": "S",
    "I": "E",
    "J": "S",
    "K": "S",
    "L": "L",
    "M": "N",
    "N": "E",
    "O": "T",
    "P": "H",
    "Q": "UE",
    "R": "E",
    "S": "S",
    "T": "T",
    "U": "E",
    "V": "E",
    "W": "E",
    "X": "E",
    "Y": "S",
    "Z": "E",
    " ": "",
}

# Add to constants.py with the other dictionaries

# Address components
ADDRESS_SUFFIXES = {"ST", "AVE", "RD", "BLVD", "DR", "LN", "CT", "WAY", "CIR", "PL"}

ADDRESS_UNITS = {"SUITE", "STE", "APT", "APARTMENT", "UNIT", "FL", "FLOOR"}

ADDRESS_DIRECTIONS = {"N", "S", "E", "W", "NE", "NW", "SE", "SW"}

ADDRESS_DIRECTION_MAPPING = {
    "NORTH": "N",
    "SOUTH": "S",
    "EAST": "E",
    "WEST": "W",
    "NORTHEAST": "NE",
    "NORTHWEST": "NW",
    "SOUTHEAST": "SE",
    "SOUTHWEST": "SW",
}

ADDRESS_SUFFIX_MAPPING = {
    "STREET": "ST",
    "AVENUE": "AVE",
    "ROAD": "RD",
    "BOULEVARD": "BLVD",
    "DRIVE": "DR",
    "LANE": "LN",
    "COURT": "CT",
    "WAY": "WAY",
    "CIRCLE": "CIR",
    "PLACE": "PL",
}

UNIT_DESIGNATORS = [
    "APT",
    "APARTMENT",
    "STE",
    "SUITE",
    "UNIT",
    "#",
    "NO",
    "NUMBER",
    "FL",
    "FLOOR",
    "FLAT",
    "LOFT",
    "LOT",
    "SPACE",
    "SP",
    "SLIP",
    "ROOM",
    "RM",
    "DEPT",
    "DEPARTMENT",
    "BOX",
    "BX",
    "BIN",
    "PIER",
    "LEVEL",
    "LVL",
    "BASEMENT",
    "BSMT",
    "UNIT",
    "PENTHOUSE",
    "PH",
    "OFFICE",
    "OFC",
    "BAY",
    "BUILDING",
    "BLDG",
    "HANGAR",
    "HNGR",
    "VILLA",
    "GARAGE",
    "SHOP",
    "STREET",
    "STR",
    "REAR",
    "UPPER",
    "LOWER",
]

from typing import Optional, Dict, Tuple
from collections import OrderedDict
import usaddress
from .word import Word
from .number import Number
from .base import BaseMistaker
from .constants import ErrorType
import re
import random


class Address(BaseMistaker):
    DIRECTIONAL_REPLACEMENTS = [
        "EAST",
        "E",
        "WEST",
        "W",
        "NORTH",
        "N",
        "SOUTH",
        "S",
        "NORTHEAST",
        "NE",
        "NORTHWEST",
        "NW",
        "SOUTHEAST",
        "SE",
        "SOUTHWEST",
        "SW",
        "NORTH-WEST",
        "NORTH-EAST",
        "SOUTH-WEST",
        "SOUTH-EAST",
    ]

    UNIT_TYPE_ABBREVIATIONS = {
        "APARTMENT": "APT",
        "BUILDING": "BLDG",
        "BASEMENT": "BSMT",
        "DEPARTMENT": "DEPT",
        "FLOOR": "FL",
        "FRONT": "FRNT",
        "HANGER": "HNGR",
        "KEY": "KEY",
        "LOBBY": "LBBY",
        "LOT": "LOT",
        "LOWER": "LOWR",
        "OFFICE": "OFC",
        "PENTHOUSE": "PH",
        "PIER": "PIER",
        "REAR": "REAR",
        "ROOM": "RM",
        "SIDE": "SIDE",
        "SLIP": "SLIP",
        "SPACE": "SPC",
        "STOP": "STOP",
        "SUITE": "STE",
        "TRAILER": "TRLR",
        "UNIT": "UNIT",
        "UPPER": "UPPER",
        "#": "#",
    }

    STREET_TYPE_ABBREVIATIONS = {
        "ALLEE": "ALY",
        "ALLEY": "ALY",
        "ALLY": "ALY",
        "ALY": "ALY",
        "ANEX": "ANX",
        "ANNEX": "ANX",
        "ANNX": "ANX",
        "ANX": "ANX",
        "ARC": "ARC",
        "ARCADE": "ARC",
        "AV": "AVE",
        "AVE": "AVE",
        "AVEN": "AVE",
        "AVENU": "AVE",
        "AVENUE": "AVE",
        "AVN": "AVE",
        "AVNUE": "AVE",
        "BAYOO": "BYU",
        "BAYOU": "BYU",
        "BCH": "BCH",
        "BEACH": "BCH",
        "BEND": "BND",
        "BND": "BND",
        "BLF": "BLF",
        "BLUF": "BLF",
        "BLUFF": "BLF",
        "BLUFFS": "BLFS",
        "BOT": "BTM",
        "BOTTM": "BTM",
        "BOTTOM": "BTM",
        "BTM": "BTM",
        "BLVD": "BLVD",
        "BOUL": "BLVD",
        "BOULEVARD": "BLVD",
        "BOULV": "BLVD",
        "BR": "BR",
        "BRANCH": "BR",
        "BRNCH": "BR",
        "BRDGE": "BRG",
        "BRG": "BRG",
        "BRIDGE": "BRG",
        "BRK": "BRK",
        "BROOK": "BRK",
        "BROOKS": "BRKS",
        "BURG": "BG",
        "BURGS": "BGS",
        "BYP": "BYP",
        "BYPA": "BYP",
        "BYPAS": "BYP",
        "BYPASS": "BYP",
        "BYPS": "BYP",
        "CAMP": "CP",
        "CMP": "CP",
        "CP": "CP",
        "CANYN": "CYN",
        "CANYON": "CYN",
        "CNYN": "CYN",
        "CYN": "CYN",
        "CAPE": "CPE",
        "CPE": "CPE",
        "CAUSEWAY": "CSWY",
        "CAUSWAY": "CSWY",
        "CSWY": "CSWY",
        "CEN": "CTR",
        "CENT": "CTR",
        "CENTER": "CTR",
        "CENTR": "CTR",
        "CENTRE": "CTR",
        "CNTER": "CTR",
        "CNTR": "CTR",
        "CTR": "CTR",
        "CENTERS": "CTRS",
        "CIR": "CIR",
        "CIRC": "CIR",
        "CIRCL": "CIR",
        "CIRCLE": "CIR",
        "CRCL": "CIR",
        "CRCLE": "CIR",
        "CIRCLES": "CIRS",
        "CLF": "CLF",
        "CLIFF": "CLF",
        "CLFS": "CLFS",
        "CLIFFS": "CLFS",
        "CLB": "CLB",
        "CLUB": "CLB",
        "COMMON": "CMN",
        "COR": "COR",
        "CORNER": "COR",
        "CORNERS": "CORS",
        "CORS": "CORS",
        "COURSE": "CRSE",
        "CRSE": "CRSE",
        "COURT": "CT",
        "CRT": "CT",
        "CT": "CT",
        "COURTS": "CTS",
        "COVE": "CV",
        "CV": "CV",
        "COVES": "CVS",
        "CK": "CRK",
        "CR": "CRK",
        "CREEK": "CRK",
        "CRK": "CRK",
        "CRECENT": "CRES",
        "CRES": "CRES",
        "CRESCENT": "CRES",
        "CRESENT": "CRES",
        "CRSCNT": "CRES",
        "CRSENT": "CRES",
        "CRSNT": "CRES",
        "CREST": "CRST",
        "CROSSING": "XING",
        "CRSSING": "XING",
        "CRSSNG": "XING",
        "XING": "XING",
        "CROSSROAD": "XRD",
        "CURVE": "CURV",
        "DALE": "DL",
        "DL": "DL",
        "DAM": "DM",
        "DM": "DM",
        "DIV": "DV",
        "DIVIDE": "DV",
        "DV": "DV",
        "DVD": "DV",
        "DR": "DR",
        "DRIV": "DR",
        "DRIVE": "DR",
        "DRV": "DR",
        "DRIVES": "DRS",
        "EST": "EST",
        "ESTATE": "EST",
        "ESTATES": "ESTS",
        "ESTS": "ESTS",
        "EXP": "EXPY",
        "EXPR": "EXPY",
        "EXPRESS": "EXPY",
        "EXPRESSWAY": "EXPY",
        "EXPW": "EXPY",
        "EXPY": "EXPY",
        "EXT": "EXT",
        "EXTENSION": "EXT",
        "EXTN": "EXT",
        "EXTNSN": "EXT",
        "EXTENSIONS": "EXTS",
        "EXTS": "EXTS",
        "FALL": "FALL",
        "FALLS": "FLS",
        "FLS": "FLS",
        "FERRY": "FRY",
        "FRRY": "FRY",
        "FRY": "FRY",
        "FIELD": "FLD",
        "FLD": "FLD",
        "FIELDS": "FLDS",
        "FLDS": "FLDS",
        "FLAT": "FLT",
        "FLT": "FLT",
        "FLATS": "FLTS",
        "FLTS": "FLTS",
        "FORD": "FRD",
        "FRD": "FRD",
        "FORDS": "FRDS",
        "FOREST": "FRST",
        "FORESTS": "FRST",
        "FRST": "FRST",
        "FORG": "FRG",
        "FORGE": "FRG",
        "FRG": "FRG",
        "FORGES": "FRGS",
        "FORK": "FRK",
        "FRK": "FRK",
        "FORKS": "FRKS",
        "FRKS": "FRKS",
        "FORT": "FT",
        "FRT": "FT",
        "FT": "FT",
        "FREEWAY": "FWY",
        "FREEWY": "FWY",
        "FRWAY": "FWY",
        "FRWY": "FWY",
        "FWY": "FWY",
        "GARDEN": "GDN",
        "GARDN": "GDN",
        "GDN": "GDN",
        "GRDEN": "GDN",
        "GRDN": "GDN",
        "GARDENS": "GDNS",
        "GDNS": "GDNS",
        "GRDNS": "GDNS",
        "GATEWAY": "GTWY",
        "GATEWY": "GTWY",
        "GATWAY": "GTWY",
        "GTWAY": "GTWY",
        "GTWY": "GTWY",
        "GLEN": "GLN",
        "GLN": "GLN",
        "GLENS": "GLNS",
        "GREEN": "GRN",
        "GRN": "GRN",
        "GREENS": "GRNS",
        "GROV": "GRV",
        "GROVE": "GRV",
        "GRV": "GRV",
        "GROVES": "GRVS",
        "HARB": "HBR",
        "HARBOR": "HBR",
        "HARBR": "HBR",
        "HBR": "HBR",
        "HRBOR": "HBR",
        "HARBORS": "HBRS",
        "HAVEN": "HVN",
        "HAVN": "HVN",
        "HVN": "HVN",
        "HEIGHT": "HTS",
        "HEIGHTS": "HTS",
        "HGTS": "HTS",
        "HT": "HTS",
        "HTS": "HTS",
        "HIGHWAY": "HWY",
        "HIGHWY": "HWY",
        "HIWAY": "HWY",
        "HIWY": "HWY",
        "HWAY": "HWY",
        "HWY": "HWY",
        "HILL": "HL",
        "HL": "HL",
        "HILLS": "HLS",
        "HLS": "HLS",
        "HLLW": "HOLW",
        "HOLLOW": "HOLW",
        "HOLLOWS": "HOLW",
        "HOLW": "HOLW",
        "HOLWS": "HOLW",
        "INLET": "INLT",
        "INLT": "INLT",
        "IS": "IS",
        "ISLAND": "IS",
        "ISLND": "IS",
        "ISLANDS": "ISS",
        "ISLNDS": "ISS",
        "ISS": "ISS",
        "ISLE": "ISLE",
        "ISLES": "ISLE",
        "JCT": "JCT",
        "JCTION": "JCT",
        "JCTN": "JCT",
        "JUNCTION": "JCT",
        "JUNCTN": "JCT",
        "JUNCTON": "JCT",
        "JCTNS": "JCTS",
        "JCTS": "JCTS",
        "JUNCTIONS": "JCTS",
        "KEY": "KY",
        "KY": "KY",
        "KEYS": "KYS",
        "KYS": "KYS",
        "KNL": "KNL",
        "KNOL": "KNL",
        "KNOLL": "KNL",
        "KNLS": "KNLS",
        "KNOLLS": "KNLS",
        "LAKE": "LK",
        "LK": "LK",
        "LAKES": "LKS",
        "LKS": "LKS",
        "LAND": "LAND",
        "LANDING": "LNDG",
        "LNDG": "LNDG",
        "LNDNG": "LNDG",
        "LA": "LN",
        "LANE": "LN",
        "LANES": "LN",
        "LN": "LN",
        "LGT": "LGT",
        "LIGHT": "LGT",
        "LIGHTS": "LGTS",
        "LF": "LF",
        "LOAF": "LF",
        "LCK": "LCK",
        "LOCK": "LCK",
        "LCKS": "LCKS",
        "LOCKS": "LCKS",
        "LDG": "LDG",
        "LDGE": "LDG",
        "LODG": "LDG",
        "LODGE": "LDG",
        "LOOP": "LOOP",
        "LOOPS": "LOOP",
        "MALL": "MALL",
        "MANOR": "MNR",
        "MNR": "MNR",
        "MANORS": "MNRS",
        "MNRS": "MNRS",
        "MDW": "MDW",
        "MEADOW": "MDW",
        "MDWS": "MDWS",
        "MEADOWS": "MDWS",
        "MEDOWS": "MDWS",
        "MEWS": "MEWS",
        "MILL": "ML",
        "ML": "ML",
        "MILLS": "MLS",
        "MLS": "MLS",
        "MISSION": "MSN",
        "MISSN": "MSN",
        "MSN": "MSN",
        "MSSN": "MSN",
        "MOTORWAY": "MTWY",
        "MNT": "MT",
        "MOUNT": "MT",
        "MT": "MT",
        "MNTAIN": "MTN",
        "MNTN": "MTN",
        "MOUNTAIN": "MTN",
        "MOUNTIN": "MTN",
        "MTIN": "MTN",
        "MTN": "MTN",
        "MNTNS": "MTNS",
        "MOUNTAINS": "MTNS",
        "NCK": "NCK",
        "NECK": "NCK",
        "ORCH": "ORCH",
        "ORCHARD": "ORCH",
        "ORCHRD": "ORCH",
        "OVAL": "OVAL",
        "OVL": "OVAL",
        "OVERPASS": "OPAS",
        "PARK": "PARK",
        "PK": "PARK",
        "PRK": "PARK",
        "PARKS": "PARK",
        "PARKWAY": "PKWY",
        "PARKWY": "PKWY",
        "PKWAY": "PKWY",
        "PKWY": "PKWY",
        "PKY": "PKWY",
        "PARKWAYS": "PKWY",
        "PKWYS": "PKWY",
        "PASS": "PASS",
        "PASSAGE": "PSGE",
        "PATH": "PATH",
        "PATHS": "PATH",
        "PIKE": "PIKE",
        "PIKES": "PIKE",
        "PINE": "PNE",
        "PINES": "PNES",
        "PNES": "PNES",
        "PL": "PL",
        "PLACE": "PL",
        "PLAIN": "PLN",
        "PLN": "PLN",
        "PLAINES": "PLNS",
        "PLAINS": "PLNS",
        "PLNS": "PLNS",
        "PLAZA": "PLZ",
        "PLZ": "PLZ",
        "PLZA": "PLZ",
        "POINT": "PT",
        "PT": "PT",
        "POINTS": "PTS",
        "PTS": "PTS",
        "PORT": "PRT",
        "PRT": "PRT",
        "PORTS": "PRTS",
        "PRTS": "PRTS",
        "PR": "PR",
        "PRAIRIE": "PR",
        "PRARIE": "PR",
        "PRR": "PR",
        "RAD": "RADL",
        "RADIAL": "RADL",
        "RADIEL": "RADL",
        "RADL": "RADL",
        "RAMP": "RAMP",
        "RANCH": "RNCH",
        "RANCHES": "RNCH",
        "RNCH": "RNCH",
        "RNCHS": "RNCH",
        "RAPID": "RPD",
        "RPD": "RPD",
        "RAPIDS": "RPDS",
        "RPDS": "RPDS",
        "REST": "RST",
        "RST": "RST",
        "RDG": "RDG",
        "RDGE": "RDG",
        "RIDGE": "RDG",
        "RDGS": "RDGS",
        "RIDGES": "RDGS",
        "RIV": "RIV",
        "RIVER": "RIV",
        "RIVR": "RIV",
        "RVR": "RIV",
        "RD": "RD",
        "ROAD": "RD",
        "RDS": "RDS",
        "ROADS": "RDS",
        "ROUTE": "RTE",
        "ROW": "ROW",
        "RUE": "RUE",
        "RUN": "RUN",
        "SHL": "SHL",
        "SHOAL": "SHL",
        "SHLS": "SHLS",
        "SHOALS": "SHLS",
        "SHOAR": "SHR",
        "SHORE": "SHR",
        "SHR": "SHR",
        "SHOARS": "SHRS",
        "SHORES": "SHRS",
        "SHRS": "SHRS",
        "SKYWAY": "SKWY",
        "SPG": "SPG",
        "SPNG": "SPG",
        "SPRING": "SPG",
        "SPRNG": "SPG",
        "SPGS": "SPGS",
        "SPNGS": "SPGS",
        "SPRINGS": "SPGS",
        "SPRNGS": "SPGS",
        "SPUR": "SPUR",
        "SPURS": "SPUR",
        "SQ": "SQ",
        "SQR": "SQ",
        "SQRE": "SQ",
        "SQU": "SQ",
        "SQUARE": "SQ",
        "SQRS": "SQS",
        "SQUARES": "SQS",
        "STA": "STA",
        "STATION": "STA",
        "STATN": "STA",
        "STN": "STA",
        "STRA": "STRA",
        "STRAV": "STRA",
        "STRAVE": "STRA",
        "STRAVEN": "STRA",
        "STRAVENUE": "STRA",
        "STRAVN": "STRA",
        "STRVN": "STRA",
        "STRVNUE": "STRA",
        "STREAM": "STRM",
        "STREME": "STRM",
        "STRM": "STRM",
        "ST": "ST",
        "STR": "ST",
        "STREET": "ST",
        "STRT": "ST",
        "STREETS": "STS",
        "SMT": "SMT",
        "SUMIT": "SMT",
        "SUMITT": "SMT",
        "SUMMIT": "SMT",
        "TER": "TER",
        "TERR": "TER",
        "TERRACE": "TER",
        "THROUGHWAY": "TRWY",
        "TRACE": "TRCE",
        "TRACES": "TRCE",
        "TRCE": "TRCE",
        "TRACK": "TRAK",
        "TRACKS": "TRAK",
        "TRAK": "TRAK",
        "TRK": "TRAK",
        "TRKS": "TRAK",
        "TRAFFICWAY": "TRFY",
        "TRFY": "TRFY",
        "TR": "TRL",
        "TRAIL": "TRL",
        "TRAILS": "TRL",
        "TRL": "TRL",
        "TRLS": "TRL",
        "TUNEL": "TUNL",
        "TUNL": "TUNL",
        "TUNLS": "TUNL",
        "TUNNEL": "TUNL",
        "TUNNELS": "TUNL",
        "TUNNL": "TUNL",
        "TPK": "TPKE",
        "TPKE": "TPKE",
        "TRNPK": "TPKE",
        "TRPK": "TPKE",
        "TURNPIKE": "TPKE",
        "TURNPK": "TPKE",
        "UNDERPASS": "UPAS",
        "UN": "UN",
        "UNION": "UN",
        "UNIONS": "UNS",
        "VALLEY": "VLY",
        "VALLY": "VLY",
        "VLLY": "VLY",
        "VLY": "VLY",
        "VALLEYS": "VLYS",
        "VLYS": "VLYS",
        "VDCT": "VIA",
        "VIA": "VIA",
        "VIADCT": "VIA",
        "VIADUCT": "VIA",
        "VIEW": "VW",
        "VW": "VW",
        "VIEWS": "VWS",
        "VWS": "VWS",
        "VILL": "VLG",
        "VILLAG": "VLG",
        "VILLAGE": "VLG",
        "VILLG": "VLG",
        "VILLIAGE": "VLG",
        "VLG": "VLG",
        "VILLAGES": "VLGS",
        "VLGS": "VLGS",
        "VILLE": "VL",
        "VL": "VL",
        "VIS": "VIS",
        "VIST": "VIS",
        "VISTA": "VIS",
        "VST": "VIS",
        "VSTA": "VIS",
        "WALK": "WALK",
        "WALKS": "WALK",
        "WALL": "WALL",
        "WAY": "WAY",
        "WY": "WAY",
        "WAYS": "WAYS",
        "WELL": "WL",
        "WELLS": "WLS",
        "WLS": "WLS",
    }

    UNIT_TYPES = [
        "APARTMENT",
        "APT",
        "SUITE",
        "STE",
        "UNIT",
        "ROOM",
        "RM",
        "FLOOR",
        "FL",
        "#",
    ]

    def __init__(self, text: str = ""):
        if text is None:
            text = ""
        self.text = str(text).strip()
        self.word_mistaker = Word()
        super().__init__(self.text)

    def reformat(self, text: str) -> str:
        """Reformat input text to standard format"""
        if text is None:
            return ""
        return str(text).strip()

    def _empty_components(self) -> dict:
        """Return empty component dictionary."""
        return {
            "building_name": None,
            "street_number": None,
            "street_direction": None,
            "street_name": None,
            "street_type": None,
            "unit_type": None,
            "unit_id": None,
            "city": None,
            "state": None,
            "zip": None,
        }

    def parse(self) -> dict:
        """Parse address into its component parts using usaddress."""
        if not self.text:
            return self._empty_components()

        try:
            tagged_address, _ = usaddress.tag(
                self.text,
                tag_mapping={
                    "BuildingName": "building_name",  # Added this
                    "AddressNumber": "street_number",
                    "StreetNamePreDirectional": "street_direction",
                    "StreetName": "street_name",
                    "StreetNamePostType": "street_type",
                    "OccupancyType": "unit_type",
                    "OccupancyIdentifier": "unit_id",
                    "PlaceName": "city",
                    "StateName": "state",
                    "ZipCode": "zip",
                },
            )

            components = self._empty_components()
            components.update(tagged_address)

            # Clean up the components
            if components.get("building_name"):
                components["building_name"] = components["building_name"].upper()
            if components.get("street_direction"):
                components["street_direction"] = components["street_direction"].upper()
            if components.get("street_name"):
                components["street_name"] = components["street_name"].upper()
            if components.get("street_type"):
                components["street_type"] = components["street_type"].upper()
            if components.get("unit_type"):
                components["unit_type"] = components["unit_type"].upper()
            if components.get("city"):
                components["city"] = components["city"].upper()
            if components.get("state"):
                components["state"] = components["state"].upper()

            # Special handling for unit with pound sign
            if components.get("unit_id") and components["unit_id"].startswith("# "):
                components["unit_type"] = "#"
                components["unit_id"] = components["unit_id"].replace("# ", "")

            return components

        except usaddress.RepeatedLabelError:
            return self._empty_components()

    def mistake(
        self, error_type: Optional[ErrorType] = None, index: Optional[int] = None
    ) -> str:
        """Generate a mistake in the text based on error type"""
        if self.text is None or not self.text:
            return ""

        # Make mistakes in all parts
        result = self.text  # Initialize result with original text
        parts = [
            "street_number",
            "street_direction",
            "street_name",
            "street_type",
            "unit_type",
            "unit_id",
            "city",
            "state",
            "zip",
        ]

        # Update our temporary text as we go
        for part in parts:
            temp_address = Address(result)  # Create new instance with current result
            result = temp_address.make_mistake(part)

        return result

    def make_mistake(self, part: str) -> str:
        """Generate a mistake in the specified address part"""
        components = self.parse()

        if components[part] is None:
            return self.text

        if part in ["street_number", "zip"]:
            mistaken_number = Number.make_mistake(components[part])
            return self.text.replace(components[part], mistaken_number)

        if part == "unit_id":
            match = re.match(r"(\d+)([A-Za-z]*)", components[part])
            if match:
                numeric_part, alpha_part = match.groups()
                mistaken_number = Number.make_mistake(numeric_part)
                new_unit_id = mistaken_number + alpha_part
                return self.text.replace(components[part], new_unit_id)

        if part == "street_name":
            mistaken_name = self.word_mistaker.mistake()
            return self.text.replace(components[part], mistaken_name)

        if part == "street_direction":
            chance = random.random()
            orig_direction = components[part]

            if chance < 0.25:  # Skip direction
                # Case-insensitive removal of direction and surrounding spaces
                return re.sub(
                    rf"\s*{orig_direction}\s*", " ", self.text, flags=re.IGNORECASE
                ).strip()
            elif chance < 0.5:  # Swap direction
                new_direction = random.choice(
                    [d for d in self.DIRECTIONAL_REPLACEMENTS if d != orig_direction]
                )
                # Case-insensitive replacement
                return re.sub(
                    rf"{orig_direction}", new_direction, self.text, flags=re.IGNORECASE
                )
            elif chance < 0.75:  # Word mistake
                word_mistaker = Word(orig_direction)
                mistaken_direction = word_mistaker.mistake()
                # Case-insensitive replacement
                return re.sub(
                    rf"{orig_direction}",
                    mistaken_direction,
                    self.text,
                    flags=re.IGNORECASE,
                )
            else:  # Remain same
                return self.text

        if part == "building_name":
            # Always make mistake for building name
            word_mistaker = Word(components[part])
            mistaken_word = word_mistaker.mistake()
            return re.sub(
                rf"{components[part]}", mistaken_word, self.text, flags=re.IGNORECASE
            )

        if part == "city":
            # 30% chance of mistake for city
            if random.random() < 0.3:
                word_mistaker = Word(components[part])
                mistaken_word = word_mistaker.mistake()
                return re.sub(
                    rf"{components[part]}",
                    mistaken_word,
                    self.text,
                    flags=re.IGNORECASE,
                )
            return self.text

        if part == "state":
            if random.random() < 0.25:
                # Remove state and fix up the surrounding punctuation
                return re.sub(
                    r",?\s*" + components[part] + r"\s*,?", ", ", self.text
                ).strip()
            return self.text

        if part == "street_type":
            chance = random.random()
            orig_type = components[part].upper()

            if chance < 0.3:
                # Find all variations that map to the same abbreviation
                target_abbrev = self.STREET_TYPE_ABBREVIATIONS.get(orig_type, orig_type)
                variations = [
                    k
                    for k, v in self.STREET_TYPE_ABBREVIATIONS.items()
                    if v == target_abbrev and k != orig_type
                ]
                if variations:
                    new_type = random.choice(variations)
                    return re.sub(
                        rf"{components[part]}",
                        new_type.title(),
                        self.text,
                        flags=re.IGNORECASE,
                    )
            elif chance < 0.6:
                # Pick a completely different type
                different_types = set(self.STREET_TYPE_ABBREVIATIONS.values())
                current_abbrev = self.STREET_TYPE_ABBREVIATIONS.get(
                    orig_type, orig_type
                )
                different_types.discard(current_abbrev)
                if different_types:
                    new_abbrev = random.choice(list(different_types))
                    # Get a random full form that maps to this abbreviation
                    full_forms = [
                        k
                        for k, v in self.STREET_TYPE_ABBREVIATIONS.items()
                        if v == new_abbrev and len(k) > 2
                    ]  # avoid abbreviations
                    if full_forms:
                        new_type = random.choice(full_forms)
                        return re.sub(
                            rf"{components[part]}",
                            new_type.title(),
                            self.text,
                            flags=re.IGNORECASE,
                        )
            return self.text

        if part == "unit_type":
            chance = random.random()
            orig_type = components[part].upper()

            if chance < 0.25:  # Random different unit type
                options = [
                    k
                    for k in self.UNIT_TYPE_ABBREVIATIONS.keys()
                    if k != orig_type
                    and k != self.UNIT_TYPE_ABBREVIATIONS.get(orig_type)
                ]
                if options:
                    new_type = random.choice(options)
                    return re.sub(
                        rf"{components[part]}",
                        new_type.title(),
                        self.text,
                        flags=re.IGNORECASE,
                    )

            elif chance < 0.5:  # Forget unit type
                return re.sub(
                    rf"{components[part]}\s+", "", self.text, flags=re.IGNORECASE
                )

            elif chance < 0.75:  # Word mistake
                word_mistaker = Word(components[part])
                mistaken_type = word_mistaker.mistake()
                return re.sub(
                    rf"{components[part]}",
                    mistaken_type,
                    self.text,
                    flags=re.IGNORECASE,
                )

            return self.text  # Keep original (last 25%)

        return self.text

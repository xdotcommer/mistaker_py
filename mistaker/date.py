# mistaker/date.py
from typing import Optional, Tuple
from datetime import datetime
import re
from .base import BaseMistaker
from .constants import ErrorType, MISREAD_NUMBERS, TEN_KEYS


class Date(BaseMistaker):
    """Class for generating date-based mistakes"""

    class DatePart:
        YEAR = 0
        MONTH = 1
        DAY = 2

    def reformat(self, text: str) -> str:
        """
        Convert various date formats to YYYY-MM-DD

        Handles formats:
        - MM/DD/YYYY
        - MM/DD/YY
        - YYYY-MM-DD
        """
        # Try different date patterns
        mm_dd_yyyy = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", str(text))
        mm_dd_yy = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{2})$", str(text))
        yyyy_mm_dd = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", str(text))

        try:
            if mm_dd_yyyy:
                month, day, year = mm_dd_yyyy.groups()
                return f"{year}-{int(month):02d}-{int(day):02d}"

            elif mm_dd_yy:
                month, day, year = mm_dd_yy.groups()
                full_year = f"20{year}"  # Assume 20xx for two-digit years
                return f"{full_year}-{int(month):02d}-{int(day):02d}"

            elif yyyy_mm_dd:
                return text

            else:
                # Try to parse with datetime as fallback
                dt = datetime.strptime(text, "%Y-%m-%d")
                return dt.strftime("%Y-%m-%d")

        except (ValueError, TypeError):
            raise ValueError(f"Unable to parse date: {text}")

    def _split_date(self, date_str: str) -> Tuple[int, int, int]:
        """Split a YYYY-MM-DD date string into (year, month, day)"""
        year, month, day = map(int, date_str.split("-"))
        return year, month, day

    def _join_date(self, year: int, month: int, day: int) -> str:
        """Join date parts into YYYY-MM-DD format"""
        return f"{year:04d}-{month:02d}-{day:02d}"

    def mistake(
        self, error_type: Optional[ErrorType] = None, date_part: Optional[int] = None
    ) -> str:
        """
        Generate a mistake in the date based on common data entry errors

        Args:
            error_type: Type of error to generate. If None, one is chosen randomly
            date_part: Part of date to modify (YEAR, MONTH, or DAY). If None, one is chosen randomly

        Returns:
            Modified date string with the applied error
        """
        self.text = self.reformat(self.text)
        year, month, day = self._split_date(self.text)

        if error_type is None:
            date_errors = [
                ErrorType.ONE_DIGIT_UP,
                ErrorType.ONE_DIGIT_DOWN,
                ErrorType.KEY_SWAP,
                ErrorType.ONE_DECADE_DOWN,
                ErrorType.Y2K,
                ErrorType.MONTH_DAY_SWAP,
                ErrorType.MISREAD,
                ErrorType.NUMERIC_KEY_PAD,
                ErrorType.DIGIT_SHIFT,
            ]
            error_type = self.rand.choice(date_errors)

        if date_part is None:
            date_part = self.rand.choice(
                [self.DatePart.YEAR, self.DatePart.MONTH, self.DatePart.DAY]
            )

        if error_type == ErrorType.ONE_DIGIT_UP:
            if date_part == self.DatePart.YEAR:
                year += 1
            elif date_part == self.DatePart.MONTH:
                month = (month % 12) + 1
            else:  # DAY
                day = (day % 31) + 1

        elif error_type == ErrorType.ONE_DIGIT_DOWN:
            if date_part == self.DatePart.YEAR:
                year -= 1
            elif date_part == self.DatePart.MONTH:
                month = ((month - 2) % 12) + 1
            else:  # DAY
                day = ((day - 2) % 31) + 1

        elif error_type == ErrorType.KEY_SWAP:
            if date_part == self.DatePart.YEAR:
                year_str = str(year)
                if len(year_str) >= 4:
                    year_list = list(year_str)
                    year_list[2], year_list[3] = year_list[3], year_list[2]
                    year = int("".join(year_list))
            elif date_part == self.DatePart.MONTH:
                month = int(str(month).zfill(2)[::-1])
            else:  # DAY
                day = int(str(day).zfill(2)[::-1])

        elif error_type == ErrorType.ONE_DECADE_DOWN:
            year -= 10

        elif error_type == ErrorType.Y2K:
            if year >= 2000:
                year = int(f"00{str(year)[2:4]}")
            else:
                year = int(f"20{str(year)[2:4]}")

        elif error_type == ErrorType.MONTH_DAY_SWAP:
            month, day = day, month

        elif error_type == ErrorType.MISREAD:
            if date_part == self.DatePart.YEAR:
                year_str = list(str(year))
                if year_str[2] in MISREAD_NUMBERS:
                    year_str[2] = MISREAD_NUMBERS[year_str[2]]
                    year = int("".join(year_str))
            elif date_part == self.DatePart.MONTH:
                month_str = str(month).zfill(2)
                if month_str[-1] in MISREAD_NUMBERS:
                    month = int(month_str[:-1] + MISREAD_NUMBERS[month_str[-1]])
            else:  # DAY
                day_str = str(day).zfill(2)
                if day_str[-1] in MISREAD_NUMBERS:
                    day = int(day_str[:-1] + MISREAD_NUMBERS[day_str[-1]])

        elif error_type == ErrorType.NUMERIC_KEY_PAD:
            if date_part == self.DatePart.YEAR:
                year_str = list(str(year))
                if year_str[3] in TEN_KEYS:
                    year_str[3] = TEN_KEYS[year_str[3]]
                    year = int("".join(year_str))
            elif date_part == self.DatePart.MONTH:
                month_str = str(month).zfill(2)
                if month_str[-1] in TEN_KEYS:
                    month = int(month_str[:-1] + TEN_KEYS[month_str[-1]])
            else:  # DAY
                day_str = str(day).zfill(2)
                if day_str[-1] in TEN_KEYS:
                    day = int(day_str[:-1] + TEN_KEYS[day_str[-1]])

        elif error_type == ErrorType.DIGIT_SHIFT:
            day = month
            month = int(str(year)[2:4])
            year = int(f"00{str(year)[0:2]}")

        return self._join_date(year, month, day)

# -*- coding: utf-8 -*-

"""
Unit converter based on the [Pint Python library](https://pint.readthedocs.io/en/stable/).

Usage examples:
- `convert 180 minutes to hrs`
- `convert 100 km to miles`
- `convert 88 mph to kph`
- `convert 32 degrees F to C`
- `convert 3.14159 rad to degrees`
- `convert 100 USD to EUR`
"""


from __future__ import annotations

import json
import re
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

import albert
import inflect
import pint


md_iid = '1.0'
md_version = "1.3"
md_name = "Unit Converter"
md_description = "Convert between units"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python"
md_lib_dependencies = ["pint", "inflect"]
md_maintainers = "@DenverCoder1"


class ConversionResult:
    """A class to represent the result of a unit conversion"""

    def __init__(
        self,
        from_amount: float,
        from_unit: str,
        to_amount: float,
        to_unit: str,
        dimensionality: str,
        source: str = "",
    ):
        """Initialize the ConversionResult

        Args:
            from_amount (float): The amount to convert from
            from_unit (str): The unit to convert from
            to_amount (float): The resulting amount
            to_unit (str): The unit converted to
            dimensionality (str): The dimensionality of the result
            source (str): The source of the conversion for attribution
        """
        self.from_amount = from_amount
        self.from_unit = from_unit
        self.to_amount = to_amount
        self.to_unit = to_unit
        self.dimensionality = dimensionality
        self.source = source
        self.display_names: dict[str, str] = Plugin.config["display_names"]
        self.inflect_engine = inflect.engine()

    def __pluralize_unit(self, unit: str) -> str:
        """Pluralize the unit

        Args:
            unit (str): The unit to pluralize

        Returns:
            str: The pluralized unit
        """
        # if all characters are uppercase, don't pluralize
        if unit.isupper():
            return unit
        return self.inflect_engine.plural(unit)

    def __display_unit_name(self, amount: float, unit: str) -> str:
        """Display the name of the unit with plural if necessary

        Args:
            amount (float): The amount to display
            unit (str): The unit to display

        Returns:
            str: The name of the unit
        """
        unit = self.__pluralize_unit(unit) if amount != 1 else unit
        return self.display_names.get(unit, unit)

    def __format_float(self, num: float) -> str:
        """Format a float to remove trailing zeros and avoid scientific notation

        Args:
            num (float): The number to format

        Returns:
            str: The formatted number
        """
        # format the float to remove trailing zeros and decimal point
        precision: int = Plugin.config["precision"]
        return f"{num:.{precision}f}".rstrip("0").rstrip(".")

    @property
    def formatted_result(self) -> str:
        """Return the formatted result amount and unit"""
        units = self.__display_unit_name(self.to_amount, self.to_unit)
        return f"{self.__format_float(self.to_amount)} {units}"

    @property
    def formatted_from(self) -> str:
        """Return the formatted from amount and unit"""
        units = self.__display_unit_name(self.from_amount, self.from_unit)
        result = f"{self.__format_float(self.from_amount)} {units}"
        if self.source:
            result += f" ({self.source})"
        return result

    @property
    def icon(self) -> str:
        """Return the icon for the result's dimensionality"""
        # strip characters from the dimensionality if not alphanumeric or underscore
        dimensionality = re.sub(r"[^\w]", "", self.dimensionality)
        return f"{dimensionality}.svg"

    def __repr__(self):
        """Return the representation of the result"""
        return f"{self.formatted_from} = {self.formatted_result}"


class UnitConverter:
    """Base class for unit converters"""

    def __init__(self):
        """Initialize the UnitConverter"""
        self.aliases: dict[str, str] = Plugin.config["aliases"]

    def convert(self, amount: float, from_unit: str, to_unit: str) -> ConversionResult:
        """Convert a unit to another unit

        Args:
            amount (float): The amount to convert
            from_unit (str): The unit to convert from
            to_unit (str): The unit to convert to

        Returns:
            ConversionResult: Object containing information about the conversion result
        """
        raise NotImplementedError


class StandardUnitConverter(UnitConverter):
    """Class to convert standard units of measurement"""

    def __init__(self):
        """Initialize the StandardUnitConverter"""
        self.units = pint.UnitRegistry()
        super().__init__()

    def _get_unit(self, unit: str) -> pint.Unit:
        """Check if the unit is a valid unit and return it
        If any aliases are found, replace the unit with the alias
        If the unit is not valid, check if making it lowercase will fix it
        If not, raise the UndefinedUnitError

        Args:
            unit (str): The unit to check

        Returns:
            pint.Unit: The unit

        Raises:
            pint.errors.UndefinedUnitError: If the unit is not valid
        """
        unit = self.aliases.get(unit, unit)
        if unit in self.units:
            # return the unit if it is valid
            return self.units.__getattr__(unit)
        # check if the lowercase version is a valid unit
        return self.units.__getattr__(unit.lower())

    def convert(self, amount: float, from_unit: str, to_unit: str) -> ConversionResult:
        """Convert a unit to another unit

        Args:
            amount (float): The amount to convert
            from_unit (str): The unit to convert from
            to_unit (str): The unit to convert to

        Returns:
            ConversionResult: Object containing information about the conversion result

        Raises:
            pint.errors.UndefinedUnitError: If the unit is not valid
            pint.errors.DimensionalityError: If the units are not compatible
        """
        input_unit = self.units.Quantity(amount, self._get_unit(from_unit))
        output_unit = self._get_unit(to_unit)
        result = input_unit.to(output_unit)
        return ConversionResult(
            from_amount=float(amount),
            from_unit=str(self._get_unit(from_unit)),
            to_amount=result.magnitude,
            to_unit=str(result.units),
            dimensionality=str(self.units._get_dimensionality(result.units)),
        )


class UnknownCurrencyError(Exception):
    """Exception to raise when an unknown currency is passed to convert"""

    def __init__(self, currency: str):
        """Initialize the UnknownCurrencyError

        Args:
            currency (str): The unknown currency
        """
        self.currency = currency
        super().__init__(f"Unknown currency: {currency}")


class CurrencyConverter(UnitConverter):
    """Class to convert currencies"""

    API_URL = "https://open.er-api.com/v6/latest/USD"
    ATTRIBUTION = "Rates by https://www.exchangerate-api.com"

    def __init__(self):
        """Initialize the CurrencyConverter"""
        self.last_update = datetime.now()
        self.currencies = self._get_currencies()
        super().__init__()

    def _get_currencies(self) -> dict[str, float]:
        """Get the currencies from the API

        Returns:
            dict[str, float]: The currencies
        """
        try:
            with urlopen(self.API_URL) as response:
                data = json.loads(response.read().decode("utf-8"))
            if not data or "rates" not in data:
                albert.info("No currencies found")
                return {}
            albert.info(f'Currencies updated')
            return data["rates"]
        except URLError as error:
            albert.warning(f"Error getting currencies: {error}")
            return {}

    def get_currency(self, currency: str) -> str | None:
        """Get the currency name normalized using aliases and capitalization

        Args:
            currency (str): The currency to normalize

        Returns:
            Optional[str]: The currency name or None if not found
        """
        # update the currencies every 24 hours
        if not self.currencies or (datetime.now() - self.last_update).days >= 1:
            self.currencies = self._get_currencies()
            self.last_update = datetime.now()
        currency = self.aliases.get(currency, currency).upper()
        return currency if currency in self.currencies else None

    def convert(self, amount: float, from_unit: str, to_unit: str) -> ConversionResult:
        """Convert a currency to another currency

        Args:
            amount (float): The amount to convert
            from_unit (str): The currency to convert from
            to_unit (str): The currency to convert to

        Returns:
            ConversionResult: Object containing information about the conversion result

        Raises:
            UnknownCurrencyError: If the currency is not valid
        """
        # get the currency rates
        from_currency = self.get_currency(from_unit)
        to_currency = self.get_currency(to_unit)
        # convert the currency
        if from_currency is None:
            raise UnknownCurrencyError(from_unit)
        if to_currency is None:
            raise UnknownCurrencyError(to_unit)
        from_rate = self.currencies[from_currency]
        to_rate = self.currencies[to_currency]
        result = amount * to_rate / from_rate
        return ConversionResult(
            from_amount=float(amount),
            from_unit=from_currency,
            to_amount=result,
            to_unit=to_currency,
            dimensionality="currency",
            source=self.ATTRIBUTION,
        )


class Plugin(albert.TriggerQueryHandler):
    """The plugin class"""

    unit_convert_regex = re.compile(
        r"(?P<from_amount>-?\d+\.?\d*)\s?(?P<from_unit>.*)\s(?:to|in)\s(?P<to_unit>.*)",
        re.I,
    )

    config: dict[str, Any] = {
        # Maximum number of decimal places for precision
        "precision": 12,
        # Unit aliases to replace when parsing
        # Units may be added here to override the default behavior or create aliases for existing units
        # The alias is the key, the string to replace it with is the value
        "aliases": {
            "sec": "second",
            "kph": "km/hour",
            "km/h": "km/hour",
            "mph": "mile/hour",
            "degrees F": "degF",
            "degrees C": "degC",
            "F": "degF",
            "C": "degC",
        },
        # Display names for units
        # Units may be added here to override the default display names
        # The string version of the unit is the key, the display name to replace with is the value
        # Both the unpluralized and the pluralized version should be included
        "display_names": {
            "degree_Celsius": "°C",
            "degree_Celsiuses": "°C",
            "degree_Fahrenheit": "°F",
            "degree_Fahrenheits": "°F",
            "mile / hour": "mph",
            "mile / hours": "mph",
            "kilometer / hour": "km/h",
            "kilometer / hours": "km/h",
            "kilometer_per_hour": "km/h",
            "kilometer_per_hours": "km/h",
        },
    }

    def initialize(self):
        self.unit_converter = StandardUnitConverter()
        self.currency_converter = CurrencyConverter()

    def id(self) -> str:
        return __name__

    def name(self) -> str:
        return md_name

    def description(self) -> str:
        return md_description

    def synopsis(self) -> str:
        return "<amount> <from_unit> to <to_unit>"

    def defaultTrigger(self) -> str:
        return "convert "

    def handleTriggerQuery(self, query: albert.TriggerQuery) -> None:
        query_string = query.string.strip()
        match = self.unit_convert_regex.fullmatch(query_string)
        if match:
            albert.info(f"Matched {query_string}")
            try:
                items = self._get_items(
                    float(match.group("from_amount")),
                    match.group("from_unit").strip(),
                    match.group("to_unit").strip(),
                )
                query.add(items)
            except Exception as error:
                albert.warning(f"Error: {error}")
                tb = "".join(
                    traceback.format_exception(error.__class__, error, error.__traceback__)
                )
                albert.warning(tb)
                albert.info("Something went wrong. Make sure you're using the correct format.")

    def _create_item(self, text: str, subtext: str, icon: str = "") -> albert.Item:
        """Create an albert.Item from a text and subtext

        Args:
            text (str): The text to display
            subtext (str): The subtext to display
            icon (Optional[str]): The icon to display. If not specified, the default icon will be used

        Returns:
            albert.Item: The item to be added to the list of results
        """
        icon_path = Path(__file__).parent / "icons" / icon
        if not icon or not icon_path.exists():
            albert.warning(f"Icon {icon} does not exist")
            icon_path = Path(__file__).parent / "icons" / "unit_converter.svg"
        return albert.Item(
            id=str(icon_path),
            icon=[str(icon_path)],
            text=text,
            subtext=subtext,
            actions=[
                albert.Action(
                    id="copy",
                    text="Copy result to clipboard",
                    callable=lambda: albert.setClipboardText(text=text),
                )
            ],
        )

    def _get_converter(self, from_unit: str, to_unit: str) -> UnitConverter:
        """Get the converter to use

        Args:
            from_unit (str): The unit to convert from
            to_unit (str): The unit to convert to

        Returns:
            UnitConverter: The converter to use
        """
        if (
            self.currency_converter.get_currency(from_unit) is not None
            and self.currency_converter.get_currency(to_unit) is not None
        ):
            return self.currency_converter
        return self.unit_converter

    def _get_items(self, amount: float, from_unit: str, to_unit: str) -> list[albert.Item]:
        """Generate the Albert items to display for the query

        Args:
            amount (float): The amount to convert from
            from_unit (str): The unit to convert from
            to_unit (str): The unit to convert to

        Returns:
            List[albert.Item]: The list of items to display
        """
        try:
            converter = self._get_converter(from_unit, to_unit)
            result = converter.convert(amount, from_unit, to_unit)
            # return the result
            return [
                self._create_item(
                    result.formatted_result,
                    f"Converted from {result.formatted_from}",
                    result.icon,
                )
            ]
        except pint.errors.DimensionalityError as e:
            albert.warning(f"DimensionalityError: {e}")
            return [
                self._create_item(f"Unable to convert {amount} {from_unit} to {to_unit}", str(e))
            ]
        except pint.errors.UndefinedUnitError as e:
            albert.warning(f"UndefinedUnitError: {e}")
            return []
        except UnknownCurrencyError as e:
            albert.warning(f"UnknownCurrencyError: {e}")
            return []

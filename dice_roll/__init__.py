# -*- coding: utf-8 -*-
# Copyright (c) 2024 Jonah Lawrence

from __future__ import annotations

import random
import re
from pathlib import Path

import albert

__doc__ = f"""
Roll any number of dice using the format `_d_`.

Example: "roll 2d6 3d8 1d20"
"""

md_iid = "3.0"
md_version = "2.0"
md_name = "Dice Roll"
md_description = "Roll any number of dice"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/main/dice_roll"
md_authors = "@DenverCoder1"


def get_icon_path(num_sides: int | None) -> str:
    """Get the path to the icon for a die with num_sides sides.

    Args:
        num_sides (Optional[int]): Number of sides on the die or None for the overall total.

    Returns:
        str: The path to the icon.
    """
    icons_path = Path(__file__).parent / "icons"
    # get the icon for the number of sides or d20 if there is no icon for that number
    icon = f"d{num_sides}" if Path(icons_path / f"d{num_sides}.svg").exists() else "d20"
    # use the overall total icon if the number of sides is None
    if num_sides is None:
        icon = "dice"
    # return the path to the icon
    return str(f"file:{icons_path / f'{icon}.svg'}")


def roll_dice(num_dice: int, num_sides: int) -> tuple[int, list[int]]:
    """Roll multiple dice with num_sides sides.

    Args:
        num_dice (int): Number of dice to roll.
        num_sides (int): Number of sides on each die.

    Returns:
        Tuple[int, List[int]]: The total and a list of the rolls.
    """
    rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
    return sum(rolls), rolls


def get_item_from_rolls(
        rolls: list[int],
        sum_rolls: int,
        num_sides: int | None = None) -> albert.Item:
    """Creates an Albert Item from a list of rolls, the total, and the number of sides.
    If num_sides is not provided, an "Overall Total" summary item is created.

    Args:
        rolls (List[int]): List of rolls.
        sum_rolls (int): Total of all rolls.
        num_sides (Optional[int]): Number of sides on each die.

    Returns:
        albert.Item: The item to be added to the list of results.
    """
    return albert.StandardItem(
        id=get_icon_path(num_sides),
        iconUrls=[get_icon_path(num_sides)],
        text=(
            f"Rolled {len(rolls)}d{num_sides} - Total: {sum_rolls}"
            if num_sides
            else f"Overall Total: {sum_rolls}"
        ),
        subtext=f"Rolls: {', '.join(map(str, rolls))}",
        actions=[
            albert.Action(
                id="copytotal",
                text="Copy result to clipboard",
                callable=lambda: albert.setClipboardText(text=str(sum_rolls)),
            ),
            albert.Action(
                id="copyrolls",
                text="Copy result to clipboard",
                callable=lambda: albert.setClipboardText(text=", ".join(map(str, rolls))),
            ),
        ],
    )


def get_items(query_string: str) -> list[albert.Item]:
    """Convert a query string of dice rolls into a list of Albert Items.

    Args:
        query_string (str): The query string to be parsed.

    Returns:
        List[albert.Item]: The list of items to display.
    """
    results = []
    sum_all_rolls = 0
    all_rolls = []
    # get (num_dice, num_sides) pairs from query string
    dice_regex = re.compile(r"(\d+)d(\d+)", re.I)
    matches = dice_regex.findall(query_string)
    # roll each pair
    for match in matches:
        num_dice, num_sides = int(match[0]), int(match[1])
        # get random numbers from 1 to num_sides for each die
        sum_rolls, rolls = roll_dice(num_dice, num_sides)
        # add rolls and total to aggregators
        sum_all_rolls += sum_rolls
        all_rolls.extend(rolls)
        # create item for the dice rolls
        results.append(get_item_from_rolls(rolls, sum_rolls, num_sides))
    # if there are multiple dice types, add a summary item
    if len(matches) > 1:
        # prepend the summary item to the list of results
        results.insert(0, get_item_from_rolls(all_rolls, sum_all_rolls))
    return results


class Plugin(albert.PluginInstance, albert.TriggerQueryHandler):
    """A plugin to roll dice"""

    def __init__(self):
        albert.PluginInstance.__init__(self)
        albert.TriggerQueryHandler.__init__(self)

    def synopsis(self, query):
        return "<amount>d<sides> [<amount>d<sides> ...]"

    def defaultTrigger(self):
        return "roll "

    def configWidget(self):
        return [{ 'type': 'label', 'text': __doc__.strip() }]

    def handleTriggerQuery(self, query: albert.Query) -> None:
        query_string = query.string.strip()
        try:
            items = get_items(query_string)
            query.add(items)
        except Exception:
            query.add([albert.StandardItem(
                id="error",
                iconUrls=[get_icon_path(None)],
                text="Something went wrong.",
                subtext="Make sure you're using the correct format.",
            )])

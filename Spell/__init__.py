# -*- coding: utf-8 -*-

"""
Check spelling of any word in any language you want. Example: spell en great
"""

from albertv0 import Item
from albertv0 import ClipAction
import os
import re
import subprocess

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Spell checker"
__version__ = "2.0"
__trigger__ = "spell "
__author__ = "Marek Mazur"
__dependencies__ = []


dict_file = '~/.local/share/albert/org.albert.extension.python/modules/Spell/dictionaries/{language}.dict'
icon_path = os.path.dirname(__file__) + "/spell.svg"
limit = 5


def handleQuery(query):
    """
    Handle query

    :param str query: Query

    :return list
    """
    if not query.isTriggered:
        return

    if len(query.string.split()) < 2:
        return prepare_error_message("Enter a query in the form of 'spell [language] [phrase]'")

    language, phrase = prepareParams(query)

    if not dictionaryExists(language):
        return prepare_error_message("Dictionary '{language}' not found!".format(language=language))

    results = find_in_dictionary(language, phrase)
    return [prepare_results_item(query, result) for result in results]


def prepareParams(query):
    """
    Prepare params

    :return list
    """
    match = re.search('^spell (?P<language>[^ ]{2,}) (?P<phrase>.*)$', query.rawString)
    if not match:
        return ('', '')
    return (match.group('language'), match.group('phrase'))


def find_in_dictionary(language, phrase):
    """
    Find in dictionary

    :param str language: Language
    :param str phrase  : Phrase

    :return str
    """
    a_dict_file = dict_file.format(language=language)
    cmd = "grep '^{phrase}' -m {limit} {dict_file}".format(phrase=phrase, limit=limit, dict_file=a_dict_file)
    results = ''
    try:
        results = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError:
        pass
    results = results.splitlines()
    return results


def prepare_results_item(query, result):
    """
    Prepare resuls item

    :param str query : Query
    :param str result: Result

    :return Item
    """
    value = result.decode('utf-8').split(' ')[0]
    item = Item(id=__prettyname__, icon=icon_path, completion=query.rawString)
    item.text = value
    item.subtext = result
    item.addAction(ClipAction("Copy result to clipboard", value))
    return item


def prepare_error_message(message):
    """
    Prepare error messae

    :param str message: Message

    :return str
    """
    item = Item(id=__prettyname__, icon=icon_path)
    item.text = __prettyname__
    item.subtext = message
    return item


def dictionaryExists(language):
    """
    Check if dictionary exists

    :param str language: Language

    :return bool
    """
    a_dict_file = dict_file.format(language=language)
    return os.path.exists(os.path.expanduser(a_dict_file))

# -*- coding: utf-8 -*-

"""
Check spelling of any word in any language you want. Example: spell en great
"""
from time import sleep

from albertv0 import Item
from albertv0 import ClipAction
import os
import re
import subprocess

__iid__ = "PythonInterface/v0.2"
__prettyname__ = "Spell checker"
__version__ = "2.0"
__trigger__ = "spell "
__author__ = "Marek Mazur"
__dependencies__ = []


dict_file = os.path.dirname(__file__) + "/dictionaries/{language}.gz"
dicts_path = os.path.dirname(__file__) + "/dictionaries"
icon_path = os.path.dirname(__file__) + "/spell.svg"
limit = 5


def initialize():
    """
    Initialize
    """
    aspellDictionaries = findInstalledAspellDictionaries()
    for language in aspellDictionaries:
        if not dictionaryExists(language):
            dumpAspellDictionary(language)


def findInstalledAspellDictionaries():
    """
    Find installed Aspell dictionaries
    """
    results = ''
    try:
        results = subprocess.check_output(['aspell', 'dump', 'dicts'])
    except subprocess.CalledProcessError:
        pass
    results = results.splitlines()
    return [result.decode('utf-8') for result in results if result.isalpha()]


def dumpAspellDictionary(language):
    """
    Dump aspell dictionary

    :param str language: Language
    """
    command = 'aspell -l {} dump master | aspell -l {} expand | gzip -c > {}/{}.gz'
    command = command.format(language, language, dicts_path, language)
    subprocess.call(command, shell=True)


def handleQuery(query):
    """
    Handle query

    :param str query: Query

    :return list
    """
    if not query.isTriggered:
        return

    if len(query.string.split()) < 2:
        return prepareErrorMessage("Enter a query in the form of 'spell [language] [phrase]'")

    language, phrase = prepareParams(query)

    if not dictionaryExists(language):
        return prepareErrorMessage("Dictionary '{language}' not found!".format(language=language))

    results = findInDictionary(language, phrase)
    return [prepareResultsItem(query, result) for result in results]


def prepareParams(query):
    """
    Prepare params

    :return list
    """
    match = re.search('^spell (?P<language>[^ ]{2,}) (?P<phrase>.*)$', query.rawString)
    if not match:
        return ('', '')
    return (match.group('language'), match.group('phrase'))


def findInDictionary(language, phrase):
    """
    Find in dictionary

    :param str language: Language
    :param str phrase  : Phrase

    :return str
    """
    a_dict_file = dict_file.format(language=language)
    results = ''
    try:
        results = subprocess.check_output(['zgrep', "^{}".format(re.escape(phrase)), '-m', str(limit), a_dict_file])
    except subprocess.CalledProcessError:
        pass
    results = results.splitlines()
    return results


def prepareResultsItem(query, result):
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


def prepareErrorMessage(message):
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

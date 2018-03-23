"""locate adapter extension

Note that it is up to you to ensure that the database is up to date"""

import os
import os.path
import sys
import subprocess
from shutil import which
from albertv0 import *
import re

import yaml

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Clipboard-Snippets"
__version__ = "1.0"
__trigger__ = "cp "
__author__ = "Erik Wasser"
__dependencies__ = []

########################################################################

CLIPBOARD_ARCHIVE_FILENAME = os.path.expanduser("~/.config/albert/org.albert.extension.{}/{}.yaml".format(
  __prettyname__.lower(),
  __prettyname__.lower()
))

########################################################################

def load_configuration(filename):

    new_dict = {}

    with open(filename, 'r') as stream:
        try:
            new_dict = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            return {}

    return new_dict;

########################################################################

def call_editor_line():
    editor_line = 'editor {filename}'

    configuration = load_configuration( CLIPBOARD_ARCHIVE_FILENAME )

    if 'configuration' in configuration and \
        'editor' in configuration['configuration']:

        editor_line = configuration['configuration']['editor']

    return editor_line.format( filename = CLIPBOARD_ARCHIVE_FILENAME ).split(' ')

########################################################################

for iconName in ["edit-paste", "system-search", "search", "text-x-generic"]:
    iconPath = iconLookup(iconName)
    if iconPath:
        break

icon_path_help_about = iconLookup('help-about')

########################################################################

def init_configuration_file(filename):

    configuration_path = os.path.dirname(filename)

    if not os.path.isdir(configuration_path):
        os.makedirs(configuration_path)

    if not os.path.isfile(filename):
        with open( filename, 'w', encoding='utf8') as f:
          f.write(  "#\n"
                    "#   "+ filename + "\n"
                    "#\n"
                    "---\n"
                    "configuration:\n"
                    "  editor: kate {filename}\n"
                    "\n"
                    "snippets:\n"
                    "  date-iso: \"`date +\\\"%Y-%m-%d\\\"`\"\n"
                    "  date-de: \"`date +\\\"%d.%m.%Y\\\"`\"\n"
                    "  perl search+replace: perl -pi -e 's/AAA/BBB/g'\n"
                    "  openssh / How do I extract information from a certificate?: openssl x509 -text -in cert.pem\n"
          )

#   Create the directory and install a mini default configuration file
#   with some examples in it.
init_configuration_file( CLIPBOARD_ARCHIVE_FILENAME )

########################################################################

def fire_command(command):
    out = ''
    try:
        p = subprocess.check_output("{} | xsel --input --clipboard".format(command), shell=True)

    except OSError as e:
        sys.exit("failed to run '{}': %s".format(command, str(e)))

    return

def wrapper_for_fire_command(command):

    def a():
        fire_command(command)

    return a

# pyperclip.copy('The text to be copied to the clipboard.')
# pyperclip.paste()

def handleQuery(query):
    results = []
    if query.isTriggered:
        if len(query.string) >= 1:
            pattern = re.compile(query.string, re.IGNORECASE)
            
            configuration = load_configuration(CLIPBOARD_ARCHIVE_FILENAME)
            
            for key, value in configuration['snippets'].items():
                if pattern.search(key) or pattern.search(value):

                    actions = []

                    m = re.search("^`(.*)`$", value)
                    if m:
                        command = m.group(1)
                        actions.append(
                            FuncAction(
                                "Output of '{}' to clipboard".format(command),
                                wrapper_for_fire_command( command ),
                            )
                        )

                    actions.append(
                        ClipAction("Snippet '{}' to clipboard".format( key ), value ),
                    )

                    results.append(
                        Item(
                            id         = key,
                            icon       = iconPath,
                            text       = pattern.sub(lambda m: "<u>%s</u>" % m.group(0), key),
                            subtext    = value,
                            #completion = "%s%s" % (__trigger__, basename),
                            #completion = 'doof ohren',
                            actions    = actions,
                            ))
        else:
            results.append(
                Item(
                    id         = __prettyname__,
                    icon       = icon_path_help_about,
                    text       = "Searches in your clipboard snippets",
                    subtext    = "Type at least one chars for a search",
                    completion = query.rawString,
                    actions    = [
                        TermAction( "Edit clipboard snippet {}".format(CLIPBOARD_ARCHIVE_FILENAME), call_editor_line() ),
                    ]))

    return results

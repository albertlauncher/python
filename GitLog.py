"""shell adapter extension

"""

import os
import subprocess
from shutil import which
from albertv0 import *
import re

import yaml
import os.path
import glob

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Git-Log-Interface"
__version__ = "1.0"
__trigger__ = "git "
__author__ = "Erik Wasser"
__dependencies__ = []

#   This is our standard configuration, if we don't file a file
#   `~/.config/albert/org.albert.extension.gitlog/config.yaml`.

CONFIG_FILENAME = os.path.expanduser('~/.config/albert/org.albert.extension.gitlog/config.yaml')

#   If you need a configuration, create a new file
#   `~/.config/albert/org.albert.extension.gitlog/config.yaml`
#   and use this as template
#   ---
#   git-directories:
#     - ~/git/source.lab/*/*
#     - ~/git/source.lab/*/*/*

config = {
    'git-directories': [
        '~/*',
        '~/git/*',
    ],
}

########################################################################

def discover_git_directories(directory):

    prefix = os.path.expanduser('~') + '/'

    for i in glob.glob(directory):
       source = i
       target = i
       test_path = os.path.join(i, '.git')
       if os.path.isdir(test_path):
           if target[:len(prefix)] == prefix:
               source = source[len(prefix):]

           yield source, target

import configparser
import os.path

class GitConfig:
    def __init__(self, **kwargs):
        super().__init__()
        self.config = configparser.ConfigParser()

    def read(self, directory):
        configuration_file = os.path.join(directory, '.git/config')
        self.config.read(configuration_file)

### SHAMELESS CODE REUSE FROM https://github.com/johnkchiu/GitLogParser/blob/master/gitLogParser.py

import sys
import re
import subprocess

class GitLogParser:
    def __init__(self, **kwargs):
        super().__init__()
        # array to store dict of commit data
        self.commits = []

    def parse(self, commitLines):
        # dict to store commit data
        commit = {}
        # iterate lines and save
        for nextLine in commitLines:
            if nextLine == '' or nextLine == '\n':
                # ignore empty lines
                pass
            elif bool(re.match('commit', nextLine, re.IGNORECASE)):
                # commit xxxx
                if len(commit) != 0:		## new commit, so re-initialize
                    self.commits.append(commit)
                    commit = {}
                commit = {'hash' : re.match('commit (.*)', nextLine, re.IGNORECASE).group(1) }
            elif bool(re.match('merge:', nextLine, re.IGNORECASE)):
                # Merge: xxxx xxxx
                pass
            elif bool(re.match('author:', nextLine, re.IGNORECASE)):
                # Author: xxxx <xxxx@xxxx.com>
                m = re.compile('Author: (.*) <(.*)>').match(nextLine)
                commit['author'] = m.group(1)
                commit['email'] = m.group(2)
            elif bool(re.match('date:', nextLine, re.IGNORECASE)):
                # Date: xxx
                m = re.compile('Date: +(.*)').match(nextLine)
                commit['date'] = m.group(1)
            elif bool(re.match('    ', nextLine, re.IGNORECASE)):
                # (4 empty spaces)
                if commit.get('message') is None:
                    commit['message'] = nextLine.strip()
                else:
                    commit['message'] = commit['message'] + "\n" + nextLine.strip()
            else:
                print ('ERROR: Unexpected Line: ' + nextLine)

    def parseFromDirectory(self, directory):
        proc = subprocess.Popen(["cd {} && git log".format(directory)], shell=True, stdout=subprocess.PIPE)
        output = map(lambda s: s.decode('utf8'), proc.stdout)
        self.parse(output)

    def search(self, pattern):
        for commit in self.commits:
            if  pattern.search(commit['author']) or \
                pattern.search(commit['email']) or \
                pattern.search(commit['hash']) or \
                pattern.search(commit['message']):
                    yield commit

def handleQueryGitLog(repository_data, s):

    if repository_data is None:
        return []

    parser = GitLogParser()
    parser.parseFromDirectory(repository_data['path'])
    pattern = re.compile(s, re.IGNORECASE)

    results = []

    for commit in parser.search(pattern):
        commit_line = 'Commit {hash}'.format(
            hash     = commit['hash'],
        )

        if repository_data['url']:
            commit_line = "[Commit {hash}]({url}/commit/{hash})".format(
                url     = repository_data['url'],
                hash    = commit['hash'],
            )

        clipboard_content = \
            "{commit}\n"                                                       \
            "Author: {author} <{email}>\n"                                     \
            "Date: {date}\n"                                                   \
            "\n"                                                               \
            "{messages}".format(
                commit   = commit_line,
                hash     = commit['hash'],
                author   = commit['author'], email = commit['email'],
                date     = commit['date'],
                messages = ''.join(map(lambda s: "* " + s + "\n", commit['message'].split("\n"))))

        results.append(
            Item(
                #id=path,
                #icon       = iconPath,
                subtext     = pattern.sub(lambda m: "<u>%s</u>" % m.group(0), commit['date'] + "/" + commit['hash']),
                text        = pattern.sub(lambda m: "<u>%s</u>" % m.group(0), commit['message']),
                #completion = "%s%s" % (__trigger__, basename),
                #completion = 'doof ohren',
                actions     = [
                    ClipAction("Copy snippet to clipboard", clipboard_content )
                ]))

    return results

def handleQueryGits(s):

    pattern = re.compile(s, re.IGNORECASE)
    results = []

    for key,repository_data in gits.items():
        if  pattern.search(key):
            results.append(
                Item(
                    id         = __prettyname__,
                    icon       = iconPath,
                    text       = pattern.sub(lambda m: "<u>%s</u>" % m.group(0), 'GIT ' + key),
                    subtext    = pattern.sub(lambda m: "<u>%s</u>" % m.group(0), repository_data['path']),
                    completion = '{}{} '.format(__trigger__, key),
                    actions    = [],
                )
            )

    return results

def handleQuery(query):
    results = []

    if query.isTriggered:
        if len(query.string) >= 1:

            m = re.search("^(\S+)\s+(.+)", query.string)
            if m:
                repository_name = m.group(1)
                repository_query = m.group(2)
                return handleQueryGitLog(gits.get(repository_name, None), repository_query)
            else:
                return handleQueryGits(query.string)

        else:
            results.append(
                Item(
                    id         = __prettyname__,
                    icon       = iconPath,
                    text       = "Searches in your git logs",
                    subtext    = 'Directories: {}'.format(', '.join(map(lambda x: x['path'], gits.values()))),
                    actions    = [],
                )
            )

    return results

########################################################################

for iconName in ["git", "shell", "konsole"]:
    iconPath = iconLookup(iconName)
    if iconPath:
        break

########################################################################

if os.path.isfile(CONFIG_FILENAME):
    with open(CONFIG_FILENAME) as stream:
        config = yaml.load( stream )

########################################################################

gits = {}

for directory in config['git-directories']:

    for source,target in discover_git_directories(os.path.expanduser(directory)):
        gits[source] = {
            'path': target,
            'url': None,
        }

for name, data in gits.items():
    gitconfig = GitConfig()
    gitconfig.read(data['path'])
    section_name = 'remote "origin"'
    if section_name in gitconfig.config:
        url = gitconfig.config[section_name].get('url', None)
        if url is not None:
            m = re.search('^git@([^:]+):(.*?).git$', url)
            if m:
                data['url'] = 'http://{host}/{path}'.format(
                    host = m.group(1),
                    path = m.group(2),
                )

########################################################################

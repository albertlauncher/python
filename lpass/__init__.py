# -*- coding: utf-8 -*-

"""LastPass Vault Search

Synopsis: <trigger> <filter>"""

from shutil import which
from albertv0 import *
import subprocess
import re
import os

__iid__ = 'PythonInterface/v0.1'
__prettyname__ = 'LastPass'
__version__ = '0.1.0'
__trigger__ = 'lp '
__author__ = 'David Piçarra'
__dependencies__ = ['lpass']

if not which('lpass'):
    raise Exception("`lpass` is not in $PATH.")

ICON_PATH = os.path.dirname(__file__)+"/lastpass.svg"

def handleQuery(query):
    if not query.isTriggered:
      stripped = query.string.strip()

      try:
          lpass = subprocess.check_output(['lpass', 'status'])
      except Exception as e:
          return Item(
              id=__prettyname__,
              icon=ICON_PATH,
              text=f'Not logged in.',
              subtext=f'Please enter your lastpass email address',
              completion=query.rawString,
              actions=[
                  ProcAction("lpass login with given email", ["lpass", "login", stripped]),
              ]
          )


      if stripped:
          try:
              lpass = subprocess.Popen(['lpass', 'ls', '--long'], stdout=subprocess.PIPE)
              try:
                  output = subprocess.check_output(['grep', stripped], stdin=lpass.stdout)
              except subprocess.CalledProcessError as e:
                  return Item(
                      id=__prettyname__,
                      icon=ICON_PATH,
                      text=__prettyname__,
                      subtext=f'No results found for {stripped}',
                      completion=query.rawString
                  )
              items = []
              for line in output.splitlines():
                  match = re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2} (.*) \[id: (\d*)\] \[username: (.*)\]', line.decode("utf-8"))
                  items.append(Item(
                      id=__prettyname__,
                      icon=ICON_PATH,
                      text=match.group(1),
                      subtext=match.group(3),
                      completion=query.rawString,
                      actions=[
                          ProcAction("Copy password to clipboard", ["lpass", "show", "-cp", match.group(2)]),
                          ProcAction("Copy username to clipboard", ["lpass", "show", "-cu", match.group(2)]),
                          ProcAction("Copy notes to clipboard", ["lpass", "show", "-c", "--notes", match.group(2)])
                      ]
                  ))

              return items

          except subprocess.CalledProcessError as e:
              return Item(
                  id=__prettyname__,
                  icon=ICON_PATH,
                  text=f'Error: {str(e.output)}',
                  subtext=str(e),
                  completion=query.rawString,
                  actions=[ClipAction('Copy CalledProcessError to clipboard', str(e))]
              )
          except Exception as e:
              return Item(
                  id=__prettyname__,
                  icon=ICON_PATH,
                  text=f'Generic Exception: {str(e)}',
                  subtext=str(e),
                  completion=query.rawString,
                  actions=[ClipAction('Copy Exception to clipboard', str(e))]
              )
      
      else:
          return Item(
              id=__prettyname__,
              icon=ICON_PATH,
              text=__prettyname__,
              subtext='Search the LastPass vault',
              completion=query.rawString,
          )

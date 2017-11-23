from albertv0 import *
from subprocess import call, check_output
from shutil import which
import random, string

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Clipboard"
__version__ = "1.0"
__trigger__ = "c "
__author__ = "Raghuram Onti Srinivasan"
__dependencies__ = ['copyq']


iconPath = iconLookup('copyq')
if not iconPath:
    iconPath = ":python_module"

if which('copyq') is None:
    raise Exception("'copyq' is not in $PATH.")

def handleQuery(query):
    if query.isTriggered:
        items = []
        splitter =  ''.join((random.choice(string.ascii_uppercase +
            string.digits))*2 for _ in range(5))
        out = check_output(("copyq eval -- \"tab('clipboard'); "
            "for(i=1;i<=10;i++)print(str(read(i-1)) + '{}');\"".format(splitter)),
            shell=True)
        result = str(out)
        for i in result.split(splitter):
            item = Item(id=__prettyname__, icon=iconPath, text=i)
            item.addAction(ProcAction(text="ProcAction",
                commandline=["copyq", "add", i]))
            items.append(item)
        return items

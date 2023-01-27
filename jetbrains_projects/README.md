# Jetbrains-albert-plugin

This is a plugin for the albert launcher(https://albertlauncher.github.io/) which lists and lets you start projects of Jetbrains IDEs such as IntelliJ IDEA, PyCharm, GoLand, etc.

I made this project to maintain this plugin, which was originally part of the albert community plugins. The plugin itself(the python file(s)) is licensed under the GPLv3 license.

DISCLAIMER: I have no affiliation with JetBrains s.r.o. The included fallback logo `jetbrains.svg` is not my property, I am using it under the terms specified [here](https://www.jetbrains.com/company/useterms.html).

## How to install:
If you are using git, you can use the following command which will clone the repository into the right directory (respecting the XDG standard).
```
$ git clone https://github.com/mqus/jetbrains-albert-plugin.git ${XDG_DATA_HOME:-$HOME/.local/share}/albert/org.albert.extension.python/modules/jetbrains-projects
```


If you don't have git, you can simply download a zip archive, extract it and move the folder containing `__init__.py` into the `.local/share/albert/org.albert.extension.python/modules` directory in your home directory, while creating any folders that don't exist yet.

After that, you should have the following structure:
```
[...]
'- modules
   '- <the plugin directory>
      |- __init.py
      '- jetbrains.svg

```

Now, open your albert settings and go to Extensions and then Python. You can then activate the plugin there. You might have to restart albert if it does not show up there at first.

## Contributors:

Thomas Queste (@tomsquest)

@iyzana

@Sharsie

@dsager


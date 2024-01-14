# Jetbrains-albert-plugin

DISCLAIMER: This plugin has no affiliation with JetBrains s.r.o.. The icons are used under the terms specified [here](https://www.jetbrains.com/company/brand/#brand-guidelines).

The plugin itself (the python file(s)) is licensed under the GPLv3 license.

## How to use:

Type `jb ` in the prompt, followed by your search term. Albert should show you a list of matching projects, scraped from your "recently edited" list of your Jetbrains IDEs. It tries to match the path of your project directory (not e.g. any files or contents).

## Creating the project launcher:

For this plugin to find the editors, you need to create a command line launcher for them. This is done by opening the IDE (for example PyCharm) and then going to `Tools -> Create Command-line Launcher...`. This will create a launcher (for example, `charm`) that this plugin will be able to find.

## Authors:

- Thomas Queste (@tomsquest)
- @mqus

## Contributors:

- @iyzana
- @Sharsie
- @dsager

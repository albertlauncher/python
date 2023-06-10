# Albert xkcd Plugin

<a href="https://www.codacy.com/app/bergercookie/xkcd-albert-plugin">
<img src="https://api.codacy.com/project/badge/Grade/126122966e844bed8e61e7cfbf7023c3"/></a>
<a href=https://github.com/bergercookie/xkcd-albert-plugin/blob/master/LICENSE" alt="LICENCE">
<img src="https://img.shields.io/github/license/bergercookie/xkcd-albert-plugin.svg" /></a>

## Description

The xkcd Albert plugin lets you launch an xkcd comic in your browser from the
albert prompt. Here are its main features:

* On toggle (default trigger: `xkcd`) it shows you the comics in newest-first
    order.
* If you want to find a comic with a specific title then you can use fuzzy search to do so):
    * `xkcd some words from the title`

## Demo

![demo_gif](https://github.com/bergercookie/xkcd-albert-plugin/blob/master/misc/demo.gif)

## Motivation

I love reading xkcd. I also wanted to get into developing plugins for Albert
thus this was the perfect opportunity to do so.

## Manual installation instructions

Requirements:

- Albert - [Installation instructions](https://albertlauncher.github.io/docs/installing/)
  - Albert Python Interface: v0.2
- Python version >= 3.5


Download and run the ``install-plugin.sh`` script or run the following to do
that automatically:

``````sh
curl https://raw.githubusercontent.com/bergercookie/xkcd-albert-plugin/master/install-plugin.sh | bash
``````

## Self Promotion

If you find this tool useful, please [star it on
Github](https://github.com/bergercookie/xkcd-albert-plugin)

## TODO List

See [ISSUES list](https://github.com/bergercookie/xkcd-albert-plugin/issues) for
the things that I'm currently either working on or interested in implementing in
the near future. In case there's something you are interesting in working on,
don't hesitate to either ask for clarifications or just do it and directly make
a PR.

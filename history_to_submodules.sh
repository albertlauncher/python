#! /usr/bin/env bash

#set -x
set -e

# Find history dirs
# git log --pretty=format: --name-only  | grep -E '^(.archive/)?[^/]+' -o | sort -u | uniq

git clone --bare git@github.com:albertlauncher/python.git .bare || true

function filter (

    if [[ $# -lt 2 ]]; then
        echo "Error: At least two arguments required."
        return 1
    fi

    local repo_name="$(echo $1 | tr '_' '-')"
    local filter_path="$2"
    shift 2

    declare -a additional_filter_paths
    if [[ $# -gt 0 ]]; then
        additional_filter_paths=$(printf -- "--path %s " "$@")
    fi

    echo "ℹ️" $repo_name $filter_path $additional_filter_paths

    git clone .bare $repo_name
    cd $repo_name
    git filter-repo --subdirectory-filter ${filter_path} ${additional_filter_paths[@]}

    gh repo create "albertlauncher/albert-plugin-python-$repo_name" --public --disable-wiki
    git remote add origin "git@github.com:albertlauncher/albert-plugin-python-$repo_name.git"
    git push -f --set-upstream origin main
    open "https://github.com/albertlauncher/albert-plugin-python-$repo_name"

    cd ..
)


filter arch_wiki                arch_wiki                 .archive/arch_wiki ArchWiki
filter atom_projects            atom_projects             atom_projects.py .archive/atom_projects AtomProjects.py
filter aur                      aur                       .archive/aur AUR
filter base_converter           base_converter            base_converter.py .archive/base_converter BaseConverter.py
filter binance                  binance                   .archive/binance Binance
filter bitfinex                 bitfinex                  .archive/bitfinex Bitfinex
filter bitwarden                bitwarden                 bitwarden.py .archive/bitwarden
filter coingecko                coingecko
filter coinmarketcap            coinmarketcap             .archive/coinmarketcap CoinMarketCap
filter color                    color
filter copyq                    copyq                     copyq.py  .archive/copyq CopyQ.py
filter currency_converter       currency_converter        currency_converter.py .archive/currency_converter Currency.py
filter dango_emoji              dango_emoji               .archive/dango_emoji dangoemoji
filter dango_kao                dango_kao                 .archive/dango_kao dangokao
filter datetime                 datetime                  datetime.py .archive/datetime DateTime.py epoch Epoch.py
filter dice_roll                dice_roll                 .archive/dice_roll
filter docker                   docker                    .archive/docker
filter duckduckgo               duckduckgo
filter emoji                    emoji                     EmojiPicker unicode_emoji .archive/unicode_emoji
filter find                     find                      find .archive/find
filter fortune                  fortune                   fortune.py .archive/fortune Fortune.py
filter gnome_dictionary         gnome_dictionary          gnome_dictionary.py .archive/gnome_dictionary GnomeDictionary.py
filter gnote                    gnote                     gnote.py .archive/gnote Gnote.py
filter goldendict               goldendict                goldendict.py .archive/goldendict GoldenDict.py
filter google_translate         google_translate          google_translate.py .archive/google_translate GoogleTranslate.py
filter googletrans              googletrans               .archive/googletrans
filter inhibit_sleep            inhibit_sleep             .archive/inhibit_sleep
filter ip                       ip                        ip.py .archive/ip Ip.py
filter jetbrains_projects       jetbrains_projects        jetbrains-projects.py  .archive/jetbrains_projects JetbrainsProjects
filter kill                     kill                      kill.py .archive/kill Kill.py
filter locate                   locate                    locate.py .archive/locate Locate.py
filter lpass                    lpass                     .archive/lpass
filter mathematica_eval         mathematica_eval          mathematica_eval.py .archive/mathematica_eval
filter multi_google_translate   multi_google_translate    multi_google_translate.py .archive/multi_google_translate MultiGoogleTranslate.py
filter node_eval                node_eval                 .archive/node_eval
filter npm                      npm                       .archive/npm Npm
filter packagist                packagist                 .archive/packagist Packagist
filter pacman                   pacman                    pacman.py .archive/pacman Pacman.py
filter pass                     pass                      pass.py .archive/pass Pass.py
filter php_eval                 php_eval                  .archive/php_eval
filter pidgin                   pidgin                    pidgin.py .archive/pidgin Pidgin.py
filter pomodoro                 pomodoro                  .archive/pomodoro Pomodoro
filter python_eval              python_eval               python Python
filter rand                     rand                      .archive/rand
filter scrot                    scrot                     scrot.py Scrot.py .archive/scrot
filter syncthing                syncthing
filter tex_to_unicode           tex_to_unicode            tex_to_unicode.py .archive/tex_to_unicode
filter texdoc                   texdoc                    .archive/texdoc
filter timer                    timer                     Timer .archive/timer
filter tomboy                   tomboy                    tomboy.py Tomboy.py .archive/tomboy
filter translators              translators
filter trash                    trash                     trash.py Trash.py .archive/trash
filter unit_converter           unit_converter            .archive/unit_converter
filter units                    units                     units.py Units.py .archive/units
filter virtualbox               virtualbox                virtualbox.py VirtualBox.py .archive/virtualbox
filter vpn                      vpn                       vpn.py .archive/vpn
filter vscode_projects          vscode_projects
filter wikipedia                wikipedia                 Wikipedia Wikipedia.py
filter x_window_switcher        x_window_switcher         window_switcher window_switcher.py  WindowSwitcher.py SwitchApp.py .archive/window_switcher
filter xkcd                     xkcd                      .archive/xkcd
filter youtube                  youtube                   youtube.py Youtube.py .archive/youtube
filter zeal                     zeal                      zeal.py Zeal.py .archive/zeal




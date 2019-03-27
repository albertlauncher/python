# window-switcher-plus
This script provides an advanced window switcher plugin for albert launcher with tokenized search and fuzzy search
so that the order of search terms and exact spelling does not matter. It is based on the original window switcher script which comes preinstalled with Albert 0.16.1
and the gnome-extension switcher: https://github.com/daniellandau/switcher


# Install 
replace the original python script in `/usr/share/albert/org.albert.extension.python/modules/window_switcher.py` with  the one from this repo

# TODO 
improve fuzzy search by imcorporating `fuzzywuzzy.token_set_ratio()`

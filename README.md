# window-switcher-plus
This script provides an advanced window switcher plugin for albert launcher with tokenized search and fuzzy search
so that the order of search terms and exact spelling does not matter. It also is configured to only search among the windows of the current workspace/desktop. The search globally on all workspaces can be initiated by starting the search query with the character '*'.  

# TLDR Featues
  * tokenized search
  * fuzzy search
  * default search only windows in current workspace, put * in front of query to search all windows
  * search on windows WM_CLASS and window title
  * highlight matching search term in results 

# Origins
Thanks to the following existing projects which this script is based on:
  * the original window switcher script which comes preinstalled with Albert 0.16.1 https://github.com/albertlauncher/python/blob/46696a2c196ccf7ecb34f82c33b585197facd29e/window_switcher.py
  * and the gnome-extension switcher: https://github.com/daniellandau/switcher/blob/master/util.js


# Install 
```
cd ~/.local/share/albert/org.albert.extension.python/modules/
git pull https://github.com/vthuongt/window-switcher-plus.git
```
then activate the plugin in the settings 

# TODO 
improve fuzzy search by incorporating `fuzzywuzzy.token_set_ratio()`


# Details on fuzzy search
  * until now the search term is only splitted along spaces into tokens (called fragments in gnome-extension switcher)
  * each token is converted into an regex, i.e. 'asdf' -> 'a[^s]*s[^d]*d[^f]*f' ( same as in function runFilter in gnome-extension switcher)
  * regexes resulting from tokens are applied to wm_class + windows title for each window
  * for each windows compute a score according to regex matches according some heuristic
    * A full match at the beginning is the best match
    * matches at beginning word boundaries are better than in the middle of words
    * matches nearer to the beginning are better than near the end
    * fuzzyness can cause lots of stuff to match, penalize by match length

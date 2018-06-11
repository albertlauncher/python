# Albert launcher spell extension


## Installation
Put extension into right location
```
~/.local/share/albert/org.albert.extension.python/modules/
```

## Preparing dictionaries

Be sure that you have installed needed packages.
```bash
sudo apt install xclip aspell aspell-en aspell-pl aspell-de
```
Dump dictionary of any language you need.
```bash
aspell -l en dump master | aspell -l en expand > ~/.local/share/albert/org.albert.extension.python/modules/Spell/dictionaries/en.dict
aspell -l pl dump master | aspell -l pl expand > ~/.local/share/albert/org.albert.extension.python/modules/Spell/dictionaries/pl.dict
aspell -l de dump master | aspell -l de expand > ~/.local/share/albert/org.albert.extension.python/modules/Spell/dictionaries/de.dict

```
## Usage examples
```
spell en great
spell pl góra
spell de viel
```
